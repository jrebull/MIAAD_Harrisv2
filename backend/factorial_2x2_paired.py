"""OBSOLETO -- NO EJECUTAR.

Este script calculaba la interaccion del 2x2 con una permutacion que barajaba
residuos ENTRE semillas, rompiendo los bloques del diseno. El p=2.0e-4 que
producia fue RETIRADO del articulo.

El analisis vigente es diferencias-en-diferencias dentro de cada semilla, en
  backend/repro/cr_derive.py  ->  results/cr_derived.json["interaction_2x2"]
(Wilcoxon bloqueado principal p=7.979e-4; t bloqueada y sign-flip de sensibilidad).

Las SERIES por semilla que este script genero se conservan en
results/factorial_2x2_paired.json y siguen siendo la entrada valida.
"""
import sys
print(__doc__)
print("ABORTADO: este generador esta obsoleto. Usa repro/cr_derive.py.")
sys.exit(2)

# --- codigo historico conservado solo como referencia, inalcanzable ---
"""
Reviewer point (round 4): the 2x2 cells share the common seed block 1-30 with the
random-restart baseline, so the paper's primary paired test (Wilcoxon signed-rank)
applies; the original script stored only the Mann-Whitney cross-check and discarded
the per-seed HVs. Deterministic re-run of the same cells (same seeds, same budget)
that (a) stores hv_per_seed, (b) adds the paired Wilcoxon vs random per cell, and
(c) adds a Freedman-Lane permutation test for the operator x selection interaction
(10,000 permutations, residuals under the additive model), answering the
parametric-ANOVA consistency objection.

Output: app/data/results/factorial_2x2_paired.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon, mannwhitneyu

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import factorial_2x2 as F

RESULTS = Path("app/data/results")
N_PERM = 10_000


def f_interaction(allv):
    """F for the AxB interaction in a balanced 2x2 with nrep columns."""
    nrep = allv.shape[1]
    grand = allv.mean()
    sst = ((allv - grand) ** 2).sum()
    mA = {0: allv[:2].mean(), 1: allv[2:].mean()}          # rows 0,1=order; 2,3=near
    mB = {0: allv[[0, 2]].mean(), 1: allv[[1, 3]].mean()}  # cols nds / gated
    ssA = 2 * nrep * sum((m - grand) ** 2 for m in mA.values())
    ssB = 2 * nrep * sum((m - grand) ** 2 for m in mB.values())
    cellm = allv.mean(axis=1)
    sscells = nrep * ((cellm - grand) ** 2).sum()
    ssAB = sscells - ssA - ssB
    sse = sst - sscells
    return (ssAB / 1) / (sse / (4 * (nrep - 1)))


def main():
    t0 = time.time()
    seeds = list(range(1, 31))
    rnd = np.array([F.run_random_cell(s) for s in seeds])
    print(f"random mean {rnd.mean():,.1f}", flush=True)
    order = ["order_nds", "order_gated", "near_nds", "near_gated"]
    per_seed = {}
    for name in order:
        op, sel = F.CELLS[name]
        hvs = []
        for s in seeds:
            hvs.append(F.run_cell(op, sel, s)["hv"])
        per_seed[name] = hvs
        print(f"{name}: mean {np.mean(hvs):,.1f} ({time.time()-t0:.0f}s)", flush=True)

    cells = {}
    for name in order:
        hvs = np.array(per_seed[name])
        alt = "greater" if name == "order_nds" else "two-sided"
        wp = float(wilcoxon(hvs, rnd, alternative=alt).pvalue)
        u, mp = mannwhitneyu(hvs, rnd, alternative=alt)
        cells[name] = {"hv_mean": float(np.mean(hvs)), "hv_per_seed": [float(x) for x in hvs],
                       "wilcoxon_alt": alt, "wilcoxon_p_vs_random": wp,
                       "mwu_p_vs_random": float(mp),
                       "wins_paired": int((hvs > rnd).sum())}
        print(f"{name}: wilcoxon({alt}) p={wp:.2e} mwu p={mp:.2e} "
              f"wins {cells[name]['wins_paired']}/30")

    # Freedman-Lane permutation test for the interaction
    allv = np.array([per_seed[n] for n in order], dtype=float)
    f_obs = f_interaction(allv)
    grand = allv.mean()
    a_eff = {0: allv[:2].mean() - grand, 1: allv[2:].mean() - grand}
    b_eff = {0: allv[[0, 2]].mean() - grand, 1: allv[[1, 3]].mean() - grand}
    fitted = np.empty_like(allv)
    for i in range(4):
        fitted[i] = grand + a_eff[i // 2] + b_eff[i % 2]
    resid = allv - fitted
    rng = np.random.default_rng(7)
    flat = resid.ravel()
    count = 0
    for _ in range(N_PERM):
        perm = rng.permutation(flat).reshape(allv.shape)
        if f_interaction(fitted + perm) >= f_obs:
            count += 1
    p_perm = (count + 1) / (N_PERM + 1)
    print(f"interaction: F_obs={f_obs:.2f} permutation p={p_perm:.2e}")

    out = {"seeds": seeds, "random_hv_mean": float(rnd.mean()),
           "random_hv_per_seed": [float(x) for x in rnd], "cells": cells,
           "interaction": {"F_obs": float(f_obs), "n_perm": N_PERM,
                           "p_permutation": float(p_perm)},
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(RESULTS / "factorial_2x2_paired.json", "w"), indent=2)
    print(f"-> factorial_2x2_paired.json ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
