"""Pareto front endpoints."""

import csv
import json
import os
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Query

from app.config import DATA_DIR
from app.core.config import V
from app.core.models import ParetoPoint, Fitness

router = APIRouter()


@lru_cache(maxsize=1)
def _load_pareto_csv() -> tuple[tuple[dict, ...], dict | None]:
    pts: list[ParetoPoint] = []
    baseline: ParetoPoint | None = None
    path = os.path.join(DATA_DIR, "pareto_front.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail="Archivo pareto_front.csv no encontrado")
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
    return (
        tuple(p.model_dump() for p in pts),
        baseline.model_dump() if baseline else None,
    )


@router.get("/api/pareto")
def get_pareto():
    pts, baseline = _load_pareto_csv()
    return {
        "points": list(pts),
        "baseline": baseline,
        "count": len(pts),
    }


@lru_cache(maxsize=30)
def _load_run(run_idx: int) -> dict:
    path = os.path.join(DATA_DIR, f"run_{run_idx:02d}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Corrida {run_idx} no encontrada")
    with open(path) as f:
        return json.load(f)


@router.get("/api/pareto/run/{run_idx}")
def get_pareto_run(run_idx: int):
    if run_idx < 0 or run_idx > 99:
        raise HTTPException(status_code=400, detail="Índice de corrida debe ser entre 0 y 99")
    data = _load_run(run_idx)
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
