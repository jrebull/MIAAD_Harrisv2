"""
Pareto local search control (reviewer-3, rounds 3-4): is the permutation tier just
local search? Archive-based PLS over the swap neighborhood: keep the same size-100
crowding-pruned archive; repeatedly pick an unexplored archive member, evaluate a
random sample of 50 of its swap neighbors, archive the nondominated; restart from
a fresh random permutation when every member is explored. Same 25,000-evaluation
budget, seeds 1-30, visa instance.

Output: app/data/results/pls_control.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core.config import NUM_GROUPS
from app.core.mohho import evaluate_hawk, compute_hypervolume, update_archive

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))
BUDGET = 25_000
ARCH = 100
NEIGH = 50


def keys_of(order):
    h = np.empty(NUM_GROUPS); h[order] = np.linspace(0.0, 1.0, NUM_GROUPS)
    return h


def run_pls(problem, seed):
    rng = np.random.default_rng(seed)
    ap, af, explored = [], [], []
    evals = 0

    def add(perm):
        nonlocal evals
        h = keys_of(perm)
        _, fit = evaluate_hawk(h, problem)
        evals += 1
        before = len(af)
        update_archive(ap, af, perm.copy(), fit, ARCH, rng)
        if len(af) != before or not explored:
            pass
        return fit

    start = rng.permutation(NUM_GROUPS)
    add(start)
    pool = [start]
    explored_ids = set()
    while evals < BUDGET:
        # pick an unexplored archive member (positions stored in ap)
        cand = [i for i in range(len(ap)) if id(ap[i]) not in explored_ids]
        if not cand:
            fresh = rng.permutation(NUM_GROUPS)
            add(fresh)
            cand = [len(ap) - 1] if ap else []
            if not cand:
                continue
        i = cand[int(rng.integers(0, len(cand)))]
        base = ap[i]
        explored_ids.add(id(base))
        for _ in range(min(NEIGH, BUDGET - evals)):
            a, b = rng.integers(0, NUM_GROUPS, size=2)
            nb = np.array(base).copy(); nb[a], nb[b] = nb[b], nb[a]
            add(nb)
    return af


def main():
    t0 = time.time()
    problem = VisaProblem()
    hv = []
    for s in SEEDS:
        af = run_pls(problem, s)
        hv.append(compute_hypervolume(af))
        print(f"seed {s:2d}: {len(af):3d} sols HV={hv[-1]:,.0f} ({time.time()-t0:.0f}s)",
              flush=True)
    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    rnd = lad["random_restart"]["hv_per_seed"]
    pn = lad["perm_nsga2"]["hv_per_seed"]
    out = {"protocol": {"budget": BUDGET, "neigh_sample": NEIGH, "archive": ARCH},
           "hv_per_seed": hv, "hv_mean": float(np.mean(hv)),
           "hv_std": float(np.std(hv)),
           "vs_random": {"diff_pct": float(100 * (np.mean(hv) - np.mean(rnd)) / np.mean(rnd)),
                         "p_two_sided": float(wilcoxon(hv, rnd).pvalue)},
           "vs_perm_nsga2": {"diff_pct": float(100 * (np.mean(hv) - np.mean(pn)) / np.mean(pn)),
                             "p_two_sided": float(wilcoxon(hv, pn).pvalue)},
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS / "pls_control.json", "w"), indent=2)
    print(f"\nPLS mean {np.mean(hv):,.0f} (random {np.mean(rnd):,.0f}, "
          f"perm-NSGA-II {np.mean(pn):,.0f})")
    print("vs random:", out["vs_random"], "| vs perm:", out["vs_perm_nsga2"])


if __name__ == "__main__":
    main()
