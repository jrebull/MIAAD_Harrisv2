"""
Semi-greedy multistart control (GRASP-style construction) for the visa ladder
(reviewer-3's ask): anchors 'blind sampling is strong here' in the GRASP /
heuristic-bias literature instead of leaving it as a surprise.

Construction: order groups by a value-based restricted candidate list on the
waiting weight w_g (the f1-greedy criterion; alpha ~ U(0,1) drawn per
construction, reactive-lite, so no alpha tuning), decode with the same greedy
decoder, feed the same crowding-pruned archive as random restart. Same budget:
25,000 constructions per seed, seeds 1-30.

Output: app/data/results/grasp_control.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core.mohho import evaluate_hawk, compute_hypervolume, update_archive

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))
BUDGET = 25_000
ARCHIVE = 100


def construct(w, rng, alpha):
    """Value-based RCL on waiting weight: at each step choose uniformly among
    unserved groups with w >= w_max - alpha*(w_max - w_min)."""
    n = len(w)
    remaining = list(range(n))
    order = np.empty(n, dtype=int)
    wv = np.asarray(w, dtype=float)
    for k in range(n):
        ws = wv[remaining]
        thr = ws.max() - alpha * (ws.max() - ws.min())
        rcl = [g for g, val in zip(remaining, ws) if val >= thr]
        pick = rcl[rng.integers(0, len(rcl))]
        order[k] = pick
        remaining.remove(pick)
    return order


def keys_of(order, n):
    h = np.empty(n)
    h[order] = np.linspace(0.0, 1.0, n)
    return h


def main():
    t0 = time.time()
    p = VisaProblem()
    w = [g["w"] for g in p.groups]
    n = len(w)
    hv_per_seed, all_front = [], []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        ap, af = [], []
        for _ in range(BUDGET):
            alpha = rng.random()
            order = construct(w, rng, alpha)
            h = keys_of(order, n)
            _, fit = evaluate_hawk(h, p)
            update_archive(ap, af, h, fit, ARCHIVE, rng)
        hv = compute_hypervolume(af)
        hv_per_seed.append(hv); all_front += [tuple(map(float, x)) for x in af]
        print(f"seed {s:2d}: {len(af):3d} sols HV={hv:,.0f} ({time.time()-t0:.0f}s)", flush=True)

    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    rnd = lad["random_restart"]["hv_per_seed"]
    pn = lad["perm_nsga2"]["hv_per_seed"]

    def paired(name, other, alt="two-sided"):
        return {"vs": name, "p": float(wilcoxon(hv_per_seed, other, alternative=alt).pvalue),
                "mean_diff_pct": float(100 * (np.mean(hv_per_seed) - np.mean(other)) / np.mean(other))}

    out = {"protocol": {"budget": BUDGET, "seeds": SEEDS, "archive": ARCHIVE,
                       "construction": "value-based RCL on waiting weight w_g, "
                                       "alpha~U(0,1) per construction"},
           "hv_per_seed": hv_per_seed,
           "hv_mean": float(np.mean(hv_per_seed)), "hv_std": float(np.std(hv_per_seed)),
           "paired": [paired("random_restart", rnd), paired("perm_nsga2", pn)],
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS / "grasp_control.json", "w"), indent=2)
    print(f"\nGRASP mean HV = {out['hv_mean']:,.0f} (random {np.mean(rnd):,.0f}, "
          f"perm-NSGA-II {np.mean(pn):,.0f})")
    for q in out["paired"]:
        print(f"  vs {q['vs']}: diff={q['mean_diff_pct']:+.2f}% p={q['p']:.2e}")
    print(f"total {time.time()-t0:.0f}s -> grasp_control.json")


if __name__ == "__main__":
    main()
