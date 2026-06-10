"""
Round-3 statistical hardening (reviewer-2 asks):
  (a) Friedman+Nemenyi omnibus over ALL NINE ladder methods on the common
      30-seed block (the previous omnibus covered the six core methods only).
  (b) Paired two-sided Wilcoxon for the headline MOHHO vs NSGA-II comparison
      (seeds are common, so the paired test is the right model).
  (c) Holm correction over the named family of headline pairwise tests.
  (d) Exact one-sided sign test for the 5/5 directionally consistent
      perturbed-demand instances.

Output: app/data/results/stats_round3.json
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import friedmanchisquare, rankdata, wilcoxon

RESULTS = Path("app/data/results")

lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
spea = json.load(open(RESULTS / "perm_spea2.json"))
brk = json.load(open(RESULTS / "brkga_ladder.json"))

nine = {
    "nsga2_realcoded": lad["nsga2_realcoded"]["hv_per_seed"],
    "naive_mohho": lad["naive_mohho"]["hv_per_seed"],
    "rk_nsga2_biased": brk["hv_per_seed"],
    "random_restart": lad["random_restart"]["hv_per_seed"],
    "competent_mohho": lad["competent_mohho"]["hv_per_seed"],
    "perm_moead": lad["perm_moead"]["hv_per_seed"],
    "discrete_mohho": lad["discrete_mohho"]["hv_per_seed"],
    "perm_spea2": spea["per_run_hv"],
    "perm_nsga2": lad["perm_nsga2"]["hv_per_seed"],
}
H = np.array(list(nine.values()))            # 9 x 30
chi2, p = friedmanchisquare(*H)
k, n = H.shape
ranks = np.array([rankdata(-H[:, j]) for j in range(n)]).T   # 9 x 30, rank 1 best
mean_ranks = {m: float(ranks[i].mean()) for i, m in enumerate(nine)}
cd = 3.102 * np.sqrt(k * (k + 1) / (6 * n))  # Nemenyi q_alpha(9, inf)/sqrt(2)=3.102 at 0.05

# (b) paired Wilcoxon MOHHO vs NSGA-II
mo, ng = nine["naive_mohho"], nine["nsga2_realcoded"]
w_two = float(wilcoxon(mo, ng, alternative="two-sided").pvalue)
w_one = float(wilcoxon(mo, ng, alternative="greater").pvalue)

# (c) Holm over the named headline family
family = {
    "mohho_vs_nsga2_paired_two_sided": w_two,
    "competent_vs_random": 5.7e-4,
    "cell2x2_vs_random": 5.5e-5,
    "interaction_2x2": 8.0e-5,
    "discrete_vs_mohho": 9.3e-10,
    "perm_nsga2_vs_random": float(wilcoxon(nine["perm_nsga2"], nine["random_restart"],
                                           alternative="greater").pvalue),
    "perm_spea2_vs_random": float(wilcoxon(nine["perm_spea2"], nine["random_restart"],
                                           alternative="greater").pvalue),
    "perm_moead_vs_random": float(wilcoxon(nine["perm_moead"], nine["random_restart"],
                                           alternative="greater").pvalue),
    "random_vs_nsga2": float(wilcoxon(nine["random_restart"], nine["nsga2_realcoded"],
                                      alternative="greater").pvalue),
    "random_vs_mohho": float(wilcoxon(nine["random_restart"], nine["naive_mohho"],
                                      alternative="greater").pvalue),
    "scp_perm_vs_random": 9.3e-10,
    "scp_competent_vs_random": 9.3e-10,
}
m = len(family)
order = sorted(family.items(), key=lambda kv: kv[1])
holm = {}
all_survive = True
for i, (name, pv) in enumerate(order):
    thr = 0.05 / (m - i)
    holm[name] = {"p": pv, "holm_threshold": thr, "survives": bool(pv <= thr)}
    if pv > thr:
        all_survive = False
        break  # Holm stops at first failure; remaining are not rejected
# mark any untested (after a failure) explicitly
tested = set(holm)
for name, pv in family.items():
    if name not in tested:
        holm[name] = {"p": pv, "holm_threshold": None, "survives": False}

# (d) exact sign test for 5/5 directional consistency
sign_p = 0.5 ** 5

out = {
    "friedman_9methods": {"chi2": float(chi2), "p": float(p), "k": k, "n": n,
                          "mean_ranks": mean_ranks, "nemenyi_cd_005": float(cd)},
    "mohho_vs_nsga2": {"paired_wilcoxon_two_sided": w_two,
                       "paired_wilcoxon_one_sided_greater": w_one},
    "holm_family": {"m": m, "results": holm, "all_headline_survive": all_survive},
    "sign_test_5of5_one_sided": sign_p,
}
json.dump(out, open(RESULTS / "stats_round3.json", "w"), indent=2)
print(f"Friedman (9 methods, 30 seeds): chi2={chi2:.1f} p={p:.2e} CD={cd:.2f}")
for mname, r in sorted(mean_ranks.items(), key=lambda kv: kv[1]):
    print(f"  rank {r:5.2f}  {mname}")
print(f"MOHHO vs NSGA-II paired Wilcoxon: two-sided p={w_two:.2e}, one-sided p={w_one:.2e}")
print(f"Holm (m={m}): all headline survive = {all_survive}")
for name, h in holm.items():
    print(f"  {name}: p={h['p']:.2e} thr={h['holm_threshold']} -> {h['survives']}")
print(f"sign test 5/5: p={sign_p:.4f}")
