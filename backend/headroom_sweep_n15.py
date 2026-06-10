"""
Close the open search-headroom question: extend the capacity sweep from 5 to 15
levels so the Spearman test has resolving power. Same machinery as
headroom_sweep.py (MOMKP capacity knob, 10 seeds, random / real-coded swarm /
perm-NSGA-II), denser grid, plus an exact-style permutation p-value (the n=5
run had exact two-sided p=0.083, inconclusive).

Output: app/data/results/headroom_sweep_n15.json
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

from app.core.mohho import compute_hypervolume
import second_problem as sp

RESULTS = Path("app/data/results")
FRACS = [round(0.15 + 0.05 * i, 2) for i in range(15)]   # 0.15 .. 0.85
S = 10
REF = sp.REF


def make_problem(frac):
    p = sp.MOMKP(seed=7)
    p.cap = frac * p.weight.sum(axis=0)
    return p


def mean_hv(fn, prob, seeds):
    return float(np.mean([compute_hypervolume(fn(prob, s), REF) for s in seeds]))


def perm_pvalue(x, y, n_perm=200_000, seed=0):
    """Two-sided permutation p-value for Spearman rho."""
    rng = np.random.default_rng(seed)
    obs = spearmanr(x, y).statistic
    y = np.asarray(y)
    count = 0
    for _ in range(n_perm):
        r = spearmanr(x, rng.permutation(y)).statistic
        if abs(r) >= abs(obs) - 1e-12:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def main():
    t0 = time.time(); seeds = list(range(1, S + 1)); out = []
    for frac in FRACS:
        prob = make_problem(frac)
        rnd = mean_hv(sp.run_random, prob, seeds)
        hho = mean_hv(sp.run_hho_realcoded, prob, seeds)
        best = mean_hv(sp.run_permnsga, prob, seeds)
        headroom = (best - rnd) / best if best > 0 else 0.0
        capture = (hho - rnd) / (best - rnd) if best > rnd else float("nan")
        out.append({"frac": frac, "random": rnd, "swarm": hho, "best": best,
                    "headroom_pct": 100 * headroom, "swarm_capture_pct": 100 * capture})
        print(f"frac={frac}: headroom={100*headroom:5.1f}%  swarm_capture={100*capture:5.1f}%  "
              f"(rnd={rnd:.4f} hho={hho:.4f} best={best:.4f})  ({time.time()-t0:.0f}s)", flush=True)
    hr = [r["headroom_pct"] for r in out]; cap = [r["swarm_capture_pct"] for r in out]
    rho, p_perm = perm_pvalue(hr, cap)
    p_asym = spearmanr(hr, cap).pvalue
    json.dump({"fracs": FRACS, "seeds": S, "sweep": out,
               "spearman_rho": float(rho),
               "perm_p_two_sided": float(p_perm), "asymptotic_p": float(p_asym),
               "n_perm": 200_000, "elapsed_s": time.time() - t0},
              open(RESULTS / "headroom_sweep_n15.json", "w"), indent=2)
    print(f"\nSpearman(capture vs headroom) rho={rho:.3f} perm_p={p_perm:.4f} "
          f"asym_p={p_asym:.4f}  total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
