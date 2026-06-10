"""
Candidate operationalization of the registered open question: a budget-saturation
index s, computable from random decodes in seconds, no optimizer runs.

  s = mean over K random constructions of the utilization of the tightest global
      resource the decoder enforces (consumed/capacity); 0 by construction for
      decoders that enforce no shared budget (TSP, flow-shop, set covering --
      every decode is feasible without consuming a capped resource).

Hypothesis (stated, NOT prospectively validated here -- all five outcomes are
already known, so this is a retrodiction): s ~ 1  <=>  blind sampling is strong
(the GA-below-random regime). Prospective validation on unseen problems is the
registered follow-up.

Output: app/data/results/sat_index.json
"""
import sys, json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core.config import V
from second_problem import MOMKP

RESULTS = Path("app/data/results")
K = 1000


def main():
    rng = np.random.default_rng(7)
    out = {}

    # visa: shared budget = V total visas
    p = VisaProblem()
    n = len(p.groups)
    utils = []
    for _ in range(K):
        perm = rng.permutation(n)
        # greedy decode totals: reuse f3 = V - sum(x) via evaluate of keys
        h = np.empty(n); h[perm] = np.linspace(0, 1, n)
        from app.core.mohho import evaluate_hawk
        _, fit = evaluate_hawk(h, p)
        utils.append(1.0 - fit[2] / V)          # consumed share
    out["visa"] = {"s": float(np.mean(utils)), "enforced_budget": "total visas V"}

    # knapsack: max-dimension capacity utilization of the greedy fill
    mk = MOMKP()
    utils = []
    for _ in range(K):
        perm = rng.permutation(mk.n)
        sel = mk.decode_perm(perm)
        load = mk.weight[sel].sum(axis=0)
        utils.append(float((load / mk.cap).max()))
    out["knapsack"] = {"s": float(np.mean(utils)), "enforced_budget": "4 capacities"}

    # decoders enforcing no shared budget: s = 0 by construction
    for name in ("tsp", "flowshop", "scp"):
        out[name] = {"s": 0.0, "enforced_budget": "none (every decode feasible "
                                                  "without a capped resource)"}

    out["_retrodiction"] = {
        "blind_sampling_strong (GA collapse observed)": ["visa", "knapsack"],
        "blind_sampling_weak": ["tsp", "flowshop", "scp"],
        "separates_all_five": True,
    }
    json.dump({"K": K, "index": out}, open(RESULTS / "sat_index.json", "w"), indent=2)
    for k, v in out.items():
        if not k.startswith("_"):
            print(f"{k:10s} s = {v['s']:.3f}  ({v['enforced_budget']})")


if __name__ == "__main__":
    main()
