"""
SUPERPROMPT v2 - Regenera los frentes combinados (PUNTOS) de los SEIS metodos del
ladder, con sus seeds publicados, y valida que el HV combinado reproduce el del
paper. Solo MOHHO (pareto_front.csv) y NSGA-II real (nsga2_front.json) tenian
puntos guardados; el resto solo tenia HV/estadisticos. Se necesitan puntos para:
  - Exp B: PCA de dimensionalidad efectiva y cobertura por tier.
  - Exp D: frente de referencia Z formado por la union de los SEIS metodos.

Salida: app/data/results/collapse_fronts.json
Ejecutar desde backend/:  python3 -m collapse.experiments.dump_fronts
"""
import csv
import json
import time
from pathlib import Path

import numpy as np

from app.core.problem import VisaProblem
from app.core.mohho import compute_hypervolume
from compare_nsga2 import nondominated

from controls import run_random, MOHHO_SEEDS
from perm_nsga import run_perm_nsga
from perm_moead import run_perm_moead
from discrete_mohho import run_discrete_mohho, SEEDS as DM_SEEDS

RESULTS = Path("app/data/results")


def mohho_front():
    front = []
    for r in csv.DictReader(open(RESULTS / "pareto_front.csv")):
        if r["type"] == "pareto":
            front.append((float(r["f1"]), float(r["f2"]), float(r["f3"])))
    return front


def fifo_point():
    for r in csv.DictReader(open(RESULTS / "pareto_front.csv")):
        if r["type"] == "fifo":
            return (float(r["f1"]), float(r["f2"]), float(r["f3"]))
    return None


def combined(run_fn, seeds, problem, tag):
    allp = []
    t0 = time.time()
    for s in seeds:
        af = run_fn(problem, s)
        allp += [tuple(map(float, p)) for p in af]
        print(f"  {tag} seed {s}: cum {len(allp)} pts ({time.time()-t0:.0f}s)")
    front = [tuple(p) for p in nondominated(allp)]
    return front


def main():
    problem = VisaProblem()
    t0 = time.time()

    fronts = {}
    tiers = {}

    # ---- random-key tier ----
    print("MOHHO real-coded (from csv)")
    fronts["mohho_realcoded"] = mohho_front()
    tiers["mohho_realcoded"] = "random_key"

    print("NSGA-II real-coded (from nsga2_front.json)")
    fronts["nsga2_realcoded"] = [tuple(p) for p in
                                 json.load(open(RESULTS / "nsga2_front.json"))["front"]]
    tiers["nsga2_realcoded"] = "random_key"

    print("random restart (seeds 42-71)")
    fronts["random_restart"] = combined(run_random, MOHHO_SEEDS, problem, "random")
    tiers["random_restart"] = "random_key"

    # ---- permutation tier ----
    print("perm-NSGA-II (seeds 1-30)")
    fronts["perm_nsga2"] = combined(run_perm_nsga, list(range(1, 31)), problem, "permNSGA")
    tiers["perm_nsga2"] = "permutation"

    print("perm-MOEA/D (seeds 1-30)")
    fronts["perm_moead"] = combined(run_perm_moead, list(range(1, 31)), problem, "permMOEAD")
    tiers["perm_moead"] = "permutation"

    print("Discrete-MOHHO (seeds 42-71)")
    fronts["discrete_mohho"] = combined(run_discrete_mohho, DM_SEEDS, problem, "discMOHHO")
    tiers["discrete_mohho"] = "permutation"

    # ---- validation against published combined HV ----
    published = {
        "mohho_realcoded": json.load(open(RESULTS / "summary.json"))["combined_pareto_size"],
        "random_restart": json.load(open(RESULTS / "controls.json"))["random_restart"]["combined_front_hv"],
        "perm_nsga2": json.load(open(RESULTS / "perm_nsga.json"))["combined_front_hv"],
        "perm_moead": json.load(open(RESULTS / "perm_moead.json"))["combined_front_hv"],
        "discrete_mohho": json.load(open(RESULTS / "discrete_mohho.json"))["combined_front_hv"],
    }
    validation = {}
    for m, front in fronts.items():
        hv = compute_hypervolume([tuple(p) for p in front])
        entry = {"size": len(front), "combined_hv": hv}
        if m == "random_restart":
            entry["published_hv"] = published["random_restart"]
            entry["hv_match"] = abs(hv - published["random_restart"]) < 1.0
        elif m in ("perm_nsga2", "perm_moead", "discrete_mohho"):
            entry["published_hv"] = published[m]
            entry["hv_match"] = abs(hv - published[m]) < 1.0
        validation[m] = entry
        print(f"  {m}: size={len(front)} HV={hv:,.1f}"
              + (f" published={entry.get('published_hv'):,.1f} match={entry.get('hv_match')}"
                 if "published_hv" in entry else ""))

    out = {
        "tiers": tiers,
        "fronts": {m: [list(p) for p in f] for m, f in fronts.items()},
        "fifo": list(fifo_point()),
        "hv_ref_point": [10.0, 16.0, 20000.0],
        "validation": validation,
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "collapse_fronts.json", "w"), indent=2)
    print(f"\n-> collapse_fronts.json ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
