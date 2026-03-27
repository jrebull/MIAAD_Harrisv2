"""Scenario and data endpoints."""

import json
import logging
import os
from functools import lru_cache

import numpy as np

from fastapi import APIRouter, HTTPException

from app.config import DATA_DIR
from app.core.config import COUNTRIES, CATEGORIES, CATS_DESC, FLAGS, V
from app.core.data import build_groups, compute_spillover, compute_country_caps, demand_source, VISA_DATA
from app.core.decoder import decode
from app.core.problem import VisaProblem
from app.core.fifo import run_baseline
from app.core.models import (
    GroupInfo, AllocationResponse, AllocationRow, Fitness,
    ImpactResponse, ImpactRow,
)

logger = logging.getLogger(__name__)

router = APIRouter()

_problem: VisaProblem | None = None


def get_problem() -> VisaProblem:
    global _problem
    if _problem is None:
        _problem = VisaProblem()
    return _problem


@lru_cache(maxsize=1)
def _load_summary() -> dict:
    path = os.path.join(DATA_DIR, "summary.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail="Archivo summary.json no encontrado")
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_pareto() -> tuple[tuple[float, float, float], ...]:
    import csv
    pts = []
    path = os.path.join(DATA_DIR, "pareto_front.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail="Archivo pareto_front.csv no encontrado")
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] == "pareto":
                pts.append((float(row["f1"]), float(row["f2"]), float(row["f3"])))
    return tuple(sorted(pts, key=lambda p: p[0]))


def _find_knee(front: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    pts = sorted(front, key=lambda p: p[0])
    if len(pts) <= 2:
        return pts[len(pts) // 2]

    f1_vals = [p[0] for p in pts]
    f2_vals = [p[1] for p in pts]
    f1_min, f1_max = min(f1_vals), max(f1_vals)
    f2_min, f2_max = min(f2_vals), max(f2_vals)
    f1_range = f1_max - f1_min
    f2_range = f2_max - f2_min

    if f1_range < 1e-12 or f2_range < 1e-12:
        return pts[len(pts) // 2]

    norm = [((p[0] - f1_min) / f1_range, (p[1] - f2_min) / f2_range) for p in pts]
    p1n = np.array(norm[0])
    p2n = np.array(norm[-1])
    line_vec = p2n - p1n
    line_len = np.linalg.norm(line_vec)
    if line_len < 1e-12:
        return pts[len(pts) // 2]
    line_unit = line_vec / line_len

    max_dist = -1.0
    knee_idx = 0
    for i, pn in enumerate(norm):
        v = np.array(pn) - p1n
        proj = np.dot(v, line_unit)
        perp = v - proj * line_unit
        dist = np.linalg.norm(perp)
        if dist > max_dist:
            max_dist = dist
            knee_idx = i

    return pts[knee_idx]


_allocation_cache: dict[str, tuple[list[list[int]], tuple[float, float, float], int]] = {}


def _compute_mohho_allocation(
    target_f1: float, target_f2: float, target_f3: float = -1.0,
    cache_key: str | None = None,
) -> tuple[list[list[int]], tuple[float, float, float], int]:
    """Find MOHHO allocation closest to target fitness via Monte Carlo."""
    if cache_key and cache_key in _allocation_cache:
        logger.info("Cache hit for allocation '%s'", cache_key)
        return _allocation_cache[cache_key]

    problem = get_problem()
    rng = np.random.default_rng(42)

    # Compute actual ranges from Pareto front for proper normalization
    pareto = _load_pareto()
    if pareto:
        f1_vals = [p[0] for p in pareto]
        f2_vals = [p[1] for p in pareto]
        f3_vals = [p[2] for p in pareto]
        f1_range = max(max(f1_vals) - min(f1_vals), 0.01)
        f2_range = max(max(f2_vals) - min(f2_vals), 0.01)
        f3_range = max(max(f3_vals) - min(f3_vals), 1.0)
    else:
        f1_range, f2_range, f3_range = 1.0, 10.0, 18000.0

    best_alloc: dict[int, int] | None = None
    best_dist = float("inf")
    best_fit = (0.0, 0.0, 0.0)

    for _ in range(50_000):
        hawk = rng.uniform(0, 1, size=len(problem.groups))
        perm = list(np.argsort(hawk, kind="stable"))
        alloc = decode(perm, problem.groups, problem.total_visas,
                       problem.country_caps, problem.category_caps)
        fit = problem.evaluate(alloc)
        d = ((fit[0] - target_f1) / f1_range) ** 2 + ((fit[1] - target_f2) / f2_range) ** 2
        if target_f3 >= 0:
            d += ((fit[2] - target_f3) / f3_range) ** 2
        if d < best_dist:
            best_dist = d
            best_alloc = alloc
            best_fit = fit

    matrix = [[0] * len(CATEGORIES) for _ in range(len(COUNTRIES))]
    for g in problem.groups:
        ci = COUNTRIES.index(g["country"])
        ji = CATEGORIES.index(g["category"])
        matrix[ci][ji] = best_alloc[g["index"]]

    used = V - int(best_fit[2])
    result = (matrix, best_fit, used)

    if cache_key:
        _allocation_cache[cache_key] = result
        logger.info("Cached allocation '%s' (dist=%.6f)", cache_key, best_dist)

    return result


@router.get("/api/scenarios")
def list_scenarios():
    return {
        "scenarios": [
            {"id": "humanitario", "name": "Humanitario", "icon": "hawk",
             "description": "Minimiza f1 (espera ponderada)", "objective": "min_f1"},
            {"id": "equilibrio", "name": "Equilibrio", "icon": "scale",
             "description": "Balance entre objetivos (knee point)", "objective": "knee"},
            {"id": "equidad", "name": "Equidad", "icon": "handshake",
             "description": "Minimiza f2 (brecha entre paises)", "objective": "min_f2"},
            {"id": "max_utilizacion", "name": "Max. Utilizacion", "icon": "check-circle",
             "description": "Minimiza f3 (visas desperdiciadas)", "objective": "min_f3"},
            {"id": "fifo", "name": "FIFO", "icon": "list-ordered",
             "description": "Sistema actual (primero en llegar)", "objective": "baseline"},
        ],
        "total_visas": V,
        "num_countries": len(COUNTRIES),
        "num_categories": len(CATEGORIES),
    }


@router.get("/api/summary")
def get_summary():
    return _load_summary()


@router.get("/api/groups")
def get_groups():
    groups = build_groups()
    result = []
    for g in groups:
        result.append(GroupInfo(
            index=g["index"],
            country=g["country"],
            category=g["category"],
            n=g["n"],
            d=g["d"],
            w=g["w"],
            source=demand_source(g["country"], g["category"]),
        ))
    return {
        "groups": [r.model_dump() for r in result],
        "countries": COUNTRIES,
        "categories": CATEGORIES,
        "cats_desc": CATS_DESC,
        "flags": FLAGS,
        "total_demand": sum(g["n"] for g in groups),
        "total_visas": V,
    }


VALID_SCENARIOS = {"humanitario", "equilibrio", "equidad", "max_utilizacion", "fifo"}


@router.get("/api/allocation/custom")
def get_custom_allocation(f1: float, f2: float, f3: float = -1.0):
    """Compute allocation for arbitrary fitness target (fast: 5000 samples)."""
    problem = get_problem()

    rng = np.random.default_rng(42)
    pareto = _load_pareto()
    if pareto:
        f1_range = max(max(p[0] for p in pareto) - min(p[0] for p in pareto), 0.01)
        f2_range = max(max(p[1] for p in pareto) - min(p[1] for p in pareto), 0.01)
        f3_range = max(max(p[2] for p in pareto) - min(p[2] for p in pareto), 1.0)
    else:
        f1_range, f2_range, f3_range = 1.0, 10.0, 18000.0

    best_alloc = None
    best_dist = float("inf")
    best_fit = (0.0, 0.0, 0.0)

    for _ in range(5_000):
        hawk = rng.uniform(0, 1, size=len(problem.groups))
        perm = list(np.argsort(hawk, kind="stable"))
        alloc = decode(perm, problem.groups, problem.total_visas,
                       problem.country_caps, problem.category_caps)
        fit = problem.evaluate(alloc)
        d = ((fit[0] - f1) / f1_range) ** 2 + ((fit[1] - f2) / f2_range) ** 2
        if f3 >= 0:
            d += ((fit[2] - f3) / f3_range) ** 2
        if d < best_dist:
            best_dist = d
            best_alloc = alloc
            best_fit = fit

    matrix = [[0] * len(CATEGORIES) for _ in range(len(COUNTRIES))]
    for g in problem.groups:
        ci = COUNTRIES.index(g["country"])
        ji = CATEGORIES.index(g["category"])
        matrix[ci][ji] = best_alloc[g["index"]]

    used = V - int(best_fit[2])
    rows = []
    for i, country in enumerate(COUNTRIES):
        cats = {}
        for j, cat in enumerate(CATEGORIES):
            cats[cat] = matrix[i][j]
        rows.append(AllocationRow(
            country=country,
            flag=FLAGS.get(country, ""),
            categories=cats,
            total=sum(matrix[i]),
        ))

    return AllocationResponse(
        scenario="custom",
        fitness=Fitness(f1=best_fit[0], f2=best_fit[1], f3=best_fit[2]),
        visas_used=used,
        utilization=round(used / V * 100, 1),
        rows=rows,
        matrix=matrix,
    )


@router.get("/api/allocation/{scenario}")
def get_allocation(scenario: str):
    if scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Escenario inválido: {scenario}. Válidos: {', '.join(sorted(VALID_SCENARIOS))}")

    problem = get_problem()
    pareto = _load_pareto()
    summary = _load_summary()

    if scenario == "fifo":
        alloc, fit = run_baseline(problem)
        matrix = [[0] * len(CATEGORIES) for _ in range(len(COUNTRIES))]
        for g in problem.groups:
            ci = COUNTRIES.index(g["country"])
            ji = CATEGORIES.index(g["category"])
            matrix[ci][ji] = alloc[g["index"]]
        used = V - int(fit[2])
    else:
        if scenario == "humanitario":
            target = summary["best_f1"]
        elif scenario == "equilibrio":
            knee = _find_knee(pareto)
            target = list(knee)
        elif scenario == "equidad":
            target = summary["best_f2"]
        elif scenario == "max_utilizacion":
            target = summary["best_f3"]
        else:
            target = summary["best_f1"]

        matrix, fit, used = _compute_mohho_allocation(
            target[0], target[1],
            target[2] if len(target) > 2 else -1.0,
            cache_key=scenario,
        )

    rows = []
    for i, country in enumerate(COUNTRIES):
        cats = {}
        for j, cat in enumerate(CATEGORIES):
            cats[cat] = matrix[i][j]
        rows.append(AllocationRow(
            country=country,
            flag=FLAGS.get(country, ""),
            categories=cats,
            total=sum(matrix[i]),
        ))

    return AllocationResponse(
        scenario=scenario,
        fitness=Fitness(f1=fit[0], f2=fit[1], f3=fit[2]),
        visas_used=used,
        utilization=round(used / V * 100, 1),
        rows=rows,
        matrix=matrix,
    )


@router.get("/api/impact/{scenario}")
def get_impact(scenario: str):
    if scenario not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Escenario inválido: {scenario}. Válidos: {', '.join(sorted(VALID_SCENARIOS))}",
        )
    problem = get_problem()
    fifo_alloc, _ = run_baseline(problem)

    fifo_by_country: dict[str, int] = {}
    for g in problem.groups:
        fifo_by_country[g["country"]] = fifo_by_country.get(g["country"], 0) + fifo_alloc[g["index"]]

    alloc_resp = get_allocation(scenario)
    scenario_by_country: dict[str, int] = {}
    for row in alloc_resp.rows:
        scenario_by_country[row.country] = row.total

    max_wait_by_country: dict[str, int] = {}
    for g in problem.groups:
        cur = max_wait_by_country.get(g["country"], 0)
        max_wait_by_country[g["country"]] = max(cur, g["w"])

    rows = []
    for country in COUNTRIES:
        fv = fifo_by_country.get(country, 0)
        sv = scenario_by_country.get(country, 0)
        rows.append(ImpactRow(
            country=country,
            flag=FLAGS.get(country, ""),
            fifo_visas=fv,
            scenario_visas=sv,
            delta=sv - fv,
            max_wait=max_wait_by_country.get(country, 0),
        ))

    rows.sort(key=lambda r: r.delta, reverse=True)
    return ImpactResponse(scenario=scenario, rows=rows)
