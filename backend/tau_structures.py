"""
Artifact for the paper sentence "we re-confirmed tau on each problem's keys
(SBX ~0.99, HHO ~0)": measure SPV order-preservation of the real-coded operators
at each structure's key dimension (visa d=105, MOMKP d=120, mo-TSP d=100,
mo-PFSP d=50), same 3,000-trial protocol as operator_order.py.

Output: app/data/results/tau_structures.json
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau

from app.core.config import LB, UB
from app.core import hho
from compare_nsga2 import sbx, poly_mutate

RESULTS = Path("app/data/results")
K = 3000
DIMS = {"visa": 105, "knapsack": 120, "tsp": 100, "flowshop": 50}


def tau(parent, child):
    rp = np.argsort(np.argsort(parent))
    rc = np.argsort(np.argsort(child))
    t, _ = kendalltau(rp, rc)
    return 0.0 if np.isnan(t) else t


def main():
    out = {"trials": K, "structures": {}}
    for name, d in DIMS.items():
        rng = np.random.default_rng(123)
        res = {}
        ops = {
            "sbx": lambda xi, r: sbx(xi, r.uniform(LB, UB, d), r)[0],
            "poly_mutation": lambda xi, r: poly_mutate(xi, r),
            "hho_soft_besiege": lambda xi, r: hho.op3_soft_siege(xi, r.uniform(LB, UB, d), 0.7, r),
            "hho_hard_besiege": lambda xi, r: hho.op4_hard_siege(xi, r.uniform(LB, UB, d), 0.3, r),
        }
        for op, fn in ops.items():
            ts = [tau(x, fn(x, rng)) for x in (rng.uniform(LB, UB, d) for _ in range(K))]
            res[op] = {"mean_tau": float(np.mean(ts)), "std_tau": float(np.std(ts))}
        sbx_mean = (res["sbx"]["mean_tau"] + res["poly_mutation"]["mean_tau"]) / 2
        hho_mean = (res["hho_soft_besiege"]["mean_tau"] + res["hho_hard_besiege"]["mean_tau"]) / 2
        out["structures"][name] = {"dim": d, "operators": res,
                                   "sbx_family_mean": sbx_mean, "hho_family_mean": hho_mean}
        print(f"{name} (d={d}): SBX-family tau={sbx_mean:.3f}  HHO-besiege tau={hho_mean:.3f}")
    json.dump(out, open(RESULTS / "tau_structures.json", "w"), indent=2)
    print("saved tau_structures.json")


if __name__ == "__main__":
    main()
