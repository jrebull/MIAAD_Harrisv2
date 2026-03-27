"""Convergence data endpoints."""

import csv
import json
import os

from fastapi import APIRouter

from app.config import DATA_DIR
from app.core.models import ConvergenceResponse

router = APIRouter()


@router.get("/api/convergence")
def get_convergence():
    path = os.path.join(DATA_DIR, "convergence.csv")
    iterations, hv_mean, hv_std = [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            iterations.append(int(row["iteration"]))
            hv_mean.append(float(row["hv_mean"]))
            hv_std.append(float(row["hv_std"]))
    return ConvergenceResponse(
        iterations=iterations, hv_mean=hv_mean, hv_std=hv_std
    )


@router.get("/api/convergence/runs")
def get_all_runs_hv():
    """Return final HV for each run (for boxplot/violin)."""
    runs = []
    i = 0
    while True:
        path = os.path.join(DATA_DIR, f"run_{i:02d}.json")
        if not os.path.exists(path):
            break
        with open(path) as f:
            data = json.load(f)
        runs.append({
            "run": i,
            "seed": data["seed"],
            "hv_final": data["hv_final"],
            "num_pareto": data["num_pareto"],
        })
        i += 1
    return {"runs": runs}
