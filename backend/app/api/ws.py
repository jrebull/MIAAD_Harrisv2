"""WebSocket endpoint for live MOHHO simulation.

Key design: the optimization thread runs at full speed and stores ALL
iteration messages in a list.  The send loop streams every one of those
messages to the client as soon as it is available (a tiny sleep keeps the
event loop cooperative without throttling delivery).  The **frontend** then
buffers the frames and plays them back at a cinematic, user-controllable
pace (pause / 0.5x / 1x / 2x).  Every iteration is still shown — never
skipped — and "complete" is only emitted once every frame has been sent.
"""

import asyncio
import json
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.problem import VisaProblem
from app.core.mohho import run_mohho, compute_hypervolume, Fitness3

router = APIRouter()

# Stream frames as fast as they are produced; the client controls the
# cinematic playback pace.  A tiny sleep keeps the event loop cooperative.
STREAM_INTERVAL = 0.02


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
                "iteration": t + 1,
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

        cursor = 0  # next message index to send

        # Stream every iteration to the client as soon as it is available.
        while True:
            # Wait for the next message to become available
            while cursor >= len(messages):
                if done.is_set():
                    break  # optimizer finished, no more messages coming
                await asyncio.sleep(0.02)

            # If optimizer is done and we've sent everything, exit
            if cursor >= len(messages):
                break

            await websocket.send_text(json.dumps(messages[cursor]))
            cursor += 1
            await asyncio.sleep(STREAM_INTERVAL)

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
