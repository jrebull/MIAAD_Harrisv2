"""WebSocket endpoint for live MOHHO simulation."""

import asyncio
import json
import queue
import threading
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.problem import VisaProblem
from app.core.mohho import run_mohho, compute_hypervolume, Fitness3

router = APIRouter()

# Minimum interval (seconds) between sending messages to the client.
# This ensures the frontend animation plays at a visible, dramatic pace.
MIN_SEND_INTERVAL = 0.35  # ~3 messages per second


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
        msg_queue: queue.Queue[dict | None] = queue.Queue()

        def on_iteration(t: int, archive_fitnesses: list[Fitness3],
                         archive_positions: list) -> None:
            hv = compute_hypervolume(archive_fitnesses)
            msg_queue.put({
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
            msg_queue.put(None)  # Sentinel: optimization done

        thread = threading.Thread(target=run_optimization, daemon=True)
        thread.start()

        last_send = 0.0

        # Stream messages at a controlled pace
        while True:
            # Wait for at least one message
            while msg_queue.empty():
                await asyncio.sleep(0.03)

            msg = msg_queue.get()
            if msg is None:
                break

            # Throttle: wait until MIN_SEND_INTERVAL has passed since last send
            now = time.monotonic()
            wait = MIN_SEND_INTERVAL - (now - last_send)
            if wait > 0:
                await asyncio.sleep(wait)

            # If multiple messages queued up during the wait, skip to the latest
            latest = msg
            while not msg_queue.empty():
                peek = msg_queue.get()
                if peek is None:
                    # Sentinel found while skipping — send latest, then break
                    await websocket.send_text(json.dumps(latest))
                    last_send = time.monotonic()
                    latest = None
                    break
                latest = peek

            if latest is None:
                break  # Sentinel was hit

            await websocket.send_text(json.dumps(latest))
            last_send = time.monotonic()

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
