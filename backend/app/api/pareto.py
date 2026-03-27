"""Pareto front endpoints."""

import csv
import json
import os

from fastapi import APIRouter

from app.config import DATA_DIR
from app.core.config import V
from app.core.models import ParetoPoint, Fitness

router = APIRouter()


def _load_pareto_csv() -> tuple[list[ParetoPoint], ParetoPoint | None]:
    pts: list[ParetoPoint] = []
    baseline: ParetoPoint | None = None
    path = os.path.join(DATA_DIR, "pareto_front.csv")
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = ParetoPoint(
                f1=float(row["f1"]),
                f2=float(row["f2"]),
                f3=float(row["f3"]),
                visas_used=V - int(float(row["f3"])),
            )
            if row["type"] == "baseline":
                baseline = p
            else:
                pts.append(p)
    pts.sort(key=lambda p: p.f1)
    return pts, baseline


@router.get("/api/pareto")
def get_pareto():
    pts, baseline = _load_pareto_csv()
    return {
        "points": [p.model_dump() for p in pts],
        "baseline": baseline.model_dump() if baseline else None,
        "count": len(pts),
    }


@router.get("/api/pareto/run/{run_idx}")
def get_pareto_run(run_idx: int):
    path = os.path.join(DATA_DIR, f"run_{run_idx:02d}.json")
    if not os.path.exists(path):
        return {"error": f"Run {run_idx} not found"}
    with open(path) as f:
        data = json.load(f)
    points = [
        ParetoPoint(
            f1=p["f1"], f2=p["f2"], f3=p["f3"],
            visas_used=V - int(p["f3"])
        ).model_dump()
        for p in data["pareto_front"]
    ]
    return {
        "run": data["run"],
        "seed": data["seed"],
        "num_pareto": data["num_pareto"],
        "hv_final": data["hv_final"],
        "points": points,
    }
