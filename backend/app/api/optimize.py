"""On-demand optimization endpoint."""

from fastapi import APIRouter

from app.core.config import V
from app.core.problem import VisaProblem
from app.core.mohho import run_mohho, compute_hypervolume
from app.core.models import OptimizeRequest, Fitness

router = APIRouter()


@router.post("/api/optimize")
def run_optimization(req: OptimizeRequest):
    problem = VisaProblem()
    positions, fitnesses, hv_history = run_mohho(
        problem,
        seed=req.seed,
        pop_size=req.pop_size,
        max_iter=req.max_iter,
        archive_size=100,
    )

    points = [
        {"f1": round(f[0], 6), "f2": round(f[1], 6), "f3": round(f[2], 0),
         "visas_used": V - int(f[2])}
        for f in fitnesses
    ]

    return {
        "num_pareto": len(fitnesses),
        "hv_final": round(hv_history[-1], 2) if hv_history else 0,
        "points": points,
        "hv_history": [round(h, 2) for h in hv_history],
    }
