"""WebSocket endpoint for live MOHHO simulation."""

import asyncio
import json
import queue
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.problem import VisaProblem
from app.core.mohho import run_mohho, compute_hypervolume, Fitness3

router = APIRouter()


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

        # Stream messages as they arrive from the computation thread
        while True:
            while msg_queue.empty():
                await asyncio.sleep(0.05)

            msg = msg_queue.get()
            if msg is None:
                break
            await websocket.send_text(json.dumps(msg))

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
