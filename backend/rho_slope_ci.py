"""
Equivalence-style bound for the 'flat in tau' claim (reviewer-2): bootstrap 95% CI
of the OLS slope of mean HV (as % of each structure's random-restart mean) versus
the per-level tau, per structure, resampling the 30 common seeds. Reported as
%-points per 0.1 tau, so 'flat' becomes a bounded statement instead of an
accepted null.

Output: app/data/results/rho_slope_ci.json
"""
import json
from pathlib import Path
import numpy as np

RESULTS = Path("app/data/results")
B = 10_000
rng = np.random.default_rng(7)


def main():
    d = json.load(open(RESULTS / "rho_sweep.json"))["structures"]
    out = {}
    for s, x in d.items():
        taus = np.array(x["tau_levels"])
        rand = x["random_mean"]
        per_seed = np.array([x["hv_per_seed"][str(r)] for r in x["rho_levels"]])  # levels x seeds
        per_seed = 100.0 * per_seed / rand
        n_seeds = per_seed.shape[1]
        tc = taus - taus.mean()
        denom = (tc ** 2).sum()
        slopes = np.empty(B)
        for b in range(B):
            idx = rng.integers(0, n_seeds, n_seeds)
            m = per_seed[:, idx].mean(axis=1)
            slopes[b] = (tc * (m - m.mean())).sum() / denom
        lo, hi = np.percentile(slopes, [2.5, 97.5])
        # express per 0.1 tau
        out[s] = {"slope_pct_per_0p1_tau_ci95": [float(lo) * 0.1, float(hi) * 0.1],
                  "slope_point": float(np.median(slopes)) * 0.1}
        print(f"{s:10s} slope (%-pts of random per 0.1 tau): "
              f"{out[s]['slope_point']:+.3f}  CI95 [{out[s]['slope_pct_per_0p1_tau_ci95'][0]:+.3f}, "
              f"{out[s]['slope_pct_per_0p1_tau_ci95'][1]:+.3f}]")
    json.dump({"bootstrap": B, "structures": out},
              open(RESULTS / "rho_slope_ci.json", "w"), indent=2)
    print("-> rho_slope_ci.json")


if __name__ == "__main__":
    main()
