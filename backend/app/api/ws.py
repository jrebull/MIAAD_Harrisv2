"""WebSocket endpoint for live MOHHO simulation.

Key design: the optimization thread runs at full speed and stores ALL
iteration messages in a list.  The send loop walks through that list at
a **fixed pace** (one message every SEND_INTERVAL seconds), so every
single iteration is shown to the client — never skipped.  If the
optimizer finishes before the send loop catches up, the send loop keeps
going until every iteration has been sent; only then does it emit
"complete".  This guarantees a slow, dramatic, cinematic animation.
"""

import asyncio
import json
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.problem import VisaProblem
from app.core.mohho import run_mohho, compute_hypervolume, Fitness3

router = APIRouter()

# Target animation pace.  Adaptive: shorter simulations get more time
# per frame so the total wall-clock stays in a sweet 30–60 s range.
#   max_iter ≤ 100  → 0.40 s/iter → 40 s total
#   max_iter ≤ 200  → 0.25 s/iter → 50 s total
#   max_iter ≤ 500  → 0.12 s/iter → 60 s total
def _send_interval(max_iter: int) -> float:
    if max_iter <= 100:
        return 0.40
    if max_iter <= 200:
        return 0.25
    return 0.12


@router.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        raw = await websocket.receive_text()
        try:
            params = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            await websocket.send_text(json.dumps({
                "type": "error", "message": "JSON inválido en parámetros"
            }))
            await websocket.close()
            return
        pop_size = min(max(int(params.get("pop_size", 30)), 10), 80)
        max_iter = min(max(int(params.get("max_iter", 100)), 20), 500)
        seed = max(int(params.get("seed", 42)), 0)

        problem = VisaProblem()

        # Shared state between threads ─ the optimizer appends, the
        # send loop reads.  `done` is set when the optimizer finishes.
        messages: list[dict] = []
        done = threading.Event()

        def on_iteration(t: int, archive_fitnesses: list[Fitness3],
                         archive_positions: list) -> None:
            hv = compute_hypervolume(archive_fitnesses)
            messages.append({
                "type": "iteration",
                "iteration": t,
                "max_iter": max_iter,
                "archive_size": len(archive_fitnesses),
                "hv": round(hv, 2),
                "pareto_front": [
                    {"f1": round(f[0], 6), "f2": round(f[1], 6), "f3": round(f[2], 0)}
                    for f in archive_fitnesses
                ],
            })

        def run_optimization():
            run_mohho(
                problem, seed=seed,
                pop_size=pop_size, max_iter=max_iter,
                archive_size=100, callback=on_iteration,
            )
            done.set()

        thread = threading.Thread(target=run_optimization, daemon=True)
        thread.start()

        interval = _send_interval(max_iter)
        cursor = 0  # next message index to send

        # Walk through every iteration at a fixed cinematic pace
        while True:
            # Wait for the next message to become available
            while cursor >= len(messages):
                if done.is_set():
                    break  # optimizer finished, no more messages coming
                await asyncio.sleep(0.03)

            # If optimizer is done and we've sent everything, exit
            if cursor >= len(messages):
                break

            await websocket.send_text(json.dumps(messages[cursor]))
            cursor += 1
            await asyncio.sleep(interval)

        await websocket.send_text(json.dumps({"type": "complete"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error", "message": str(e)
            }))
        except Exception:
            pass
