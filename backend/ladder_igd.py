"""
Re-score the full nine-method visa ladder PER RUN under two reference-point-free
indicators -- IGD+ and the additive epsilon -- against a common reference front
(the nondominated union of all 9x30 per-run fronts). Reviewer-2's single change:
does the tier structure survive when the f2-dominated, reference-point-based
hypervolume is replaced?

Reuses the stored per-run fronts for 6 methods (per_run_fronts.json) and re-runs
the 3 methods whose fronts were not persisted (competent, perm-SPEA2, rk-biased),
sanity-checking their per-run HV against the stored canonical values.

Output: app/data/results/ladder_igd.json (+ per_run_fronts_9.json)
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import friedmanchisquare, rankdata, spearmanr

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core import mohho as M
import competent_mohho as C
from perm_spea2 import run_perm_spea2
from brkga_nsga import run_brkga_nsga2

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))

p = VisaProblem()
def ev(h): return M.evaluate_hawk(h, p)[1]
def HV(F): return M.compute_hypervolume([tuple(x) for x in F])


def main():
    t0 = time.time()
    prf = json.load(open(RESULTS / "per_run_fronts.json"))
    fronts = {k: v["fronts"] for k, v in prf.items()}

    # --- re-run the 3 missing methods, sanity-checking HV against stored values ---
    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    spea = json.load(open(RESULTS / "perm_spea2.json"))
    brk = json.load(open(RESULTS / "brkga_ladder.json"))
    missing = {
        "competent_mohho": (lambda s: C.run_competent_mohho(
            ev, M.NUM_GROUPS, 3, HV, s, 50, 500, pm=0.15, use_sbx=True, arch_cap=100)["front"],
            lad["competent_mohho"]["hv_per_seed"]),
        "perm_spea2": (lambda s: run_perm_spea2(p, s), spea["per_run_hv"]),
        "rk_nsga2_biased": (lambda s: run_brkga_nsga2(p, s), brk["hv_per_seed"]),
    }
    for name, (fn, stored_hv) in missing.items():
        fr, mism = [], 0
        for i, s in enumerate(SEEDS):
            F = [list(map(float, x)) for x in fn(s)]
            fr.append(F)
            if abs(HV(F) - stored_hv[i]) > 1.0:
                mism += 1
        fronts[name] = fr
        print(f"{name}: 30 fronts regenerated, hv_mismatch_runs={mism} "
              f"({time.time()-t0:.0f}s)", flush=True)
    json.dump(fronts, open(RESULTS / "per_run_fronts_9.json", "w"))

    # --- pooled reference front Z9 (numpy nondominated filter) ---
    allp = np.array(sorted({tuple(np.round(pt, 6)) for m in fronts.values()
                            for run in m for pt in run}))
    keep = np.ones(len(allp), dtype=bool)
    for i in range(len(allp)):
        if not keep[i]:
            continue
        dominated = np.all(allp <= allp[i], axis=1) & np.any(allp < allp[i], axis=1)
        if dominated.any():
            keep[i] = False
    Z = allp[keep]
    lo, hi = Z.min(axis=0), Z.max(axis=0)
    span = np.maximum(hi - lo, 1e-12)
    Zn = (Z - lo) / span
    print(f"pooled points={len(allp)}, |Z9|={len(Z)} ({time.time()-t0:.0f}s)", flush=True)

    def igd_plus(front):
        F = (np.array(front) - lo) / span
        d = 0.0
        for z in Zn:
            diff = np.maximum(F - z, 0.0)
            d += float(np.sqrt((diff ** 2).sum(axis=1)).min())
        return d / len(Zn)

    def eps_add(front):
        F = (np.array(front) - lo) / span
        # eps = max over z of min over a of max_m (a_m - z_m)
        worst = -np.inf
        for z in Zn:
            worst = max(worst, float((F - z).max(axis=1).min()))
        return worst

    names = ["nsga2_realcoded", "mohho_realcoded", "rk_nsga2_biased", "random_restart",
             "competent_mohho", "perm_moead", "discrete_mohho", "perm_spea2", "perm_nsga2"]
    igd = {n: [igd_plus(fr) for fr in fronts[n]] for n in names}
    print(f"IGD+ done ({time.time()-t0:.0f}s)", flush=True)
    eps = {n: [eps_add(fr) for fr in fronts[n]] for n in names}
    print(f"eps done ({time.time()-t0:.0f}s)", flush=True)

    def ranks_of(metric, lower_better=True):
        Hm = np.array([metric[n] for n in names])
        sign = 1 if lower_better else -1
        rk = np.array([rankdata(sign * Hm[:, j]) for j in range(Hm.shape[1])]).T
        chi2, pv = friedmanchisquare(*Hm)
        return {n: float(rk[i].mean()) for i, n in enumerate(names)}, float(chi2), float(pv)

    hv_per = {n: [HV(fr) for fr in fronts[n]] for n in names}
    r_hv, chi_hv, p_hv = ranks_of(hv_per, lower_better=False)
    r_igd, chi_igd, p_igd = ranks_of(igd, True)
    r_eps, chi_eps, p_eps = ranks_of(eps, True)
    cd = 3.102 * np.sqrt(9 * 10 / (6 * 30))

    v_hv = [r_hv[n] for n in names]
    rho_igd = float(spearmanr(v_hv, [r_igd[n] for n in names]).statistic)
    rho_eps = float(spearmanr(v_hv, [r_eps[n] for n in names]).statistic)

    out = {"reference": {"size": int(len(Z)), "pooled_from": "9 methods x 30 per-run fronts"},
           "mean_ranks_hv": r_hv, "mean_ranks_igd_plus": r_igd, "mean_ranks_eps": r_eps,
           "friedman": {"hv": [chi_hv, p_hv], "igd_plus": [chi_igd, p_igd],
                        "eps": [chi_eps, p_eps]},
           "nemenyi_cd_005": float(cd),
           "rank_correlation_hv_vs_igd": rho_igd, "rank_correlation_hv_vs_eps": rho_eps,
           "igd_per_seed": igd, "eps_per_seed": eps,
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS / "ladder_igd.json", "w"), indent=2)
    print(f"\nCD={cd:.2f} | Spearman(rankHV, rankIGD+)={rho_igd:.3f} | (rankHV, rankEps)={rho_eps:.3f}")
    print(f"{'method':22s} {'HV':>6s} {'IGD+':>6s} {'eps':>6s}")
    for n in sorted(names, key=lambda x: r_hv[x]):
        print(f"{n:22s} {r_hv[n]:6.2f} {r_igd[n]:6.2f} {r_eps[n]:6.2f}")
    print(f"total {time.time()-t0:.0f}s -> ladder_igd.json")


if __name__ == "__main__":
    main()
