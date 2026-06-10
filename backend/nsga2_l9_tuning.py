"""
Reviewer-3's Q1 (rounds 3-4): does 'blind sampling beats the real-coded NSGA-II'
survive when NSGA-II gets ITS OWN tuning budget, equal to MOHHO's L9 design?

Same L9(3^4) protocol as Section 5: nine configurations, scored on fresh seeds
(201-210, disjoint from the 1-30 evaluation block, mirroring the Taguchi setup),
best configuration confirmed on the canonical 30-seed block and compared against
blind random restart (paired Wilcoxon). Run on the visa instance AND the knapsack
(the two structures where the collapse was observed).

Factors (3 levels each), total budget fixed at 25,000 evaluations:
  A: population N in {25, 50, 100}   (T = 25000/N)
  B: SBX eta_c in {2, 20, 100}
  C: crossover prob p_c in {0.6, 0.9, 1.0}
  D: mutation prob p_m in {0.5/d, 1/d, 5/d}

Output: app/data/results/nsga2_l9.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core.mohho import compute_hypervolume
import compare_nsga2 as cn
import second_problem as sp

RESULTS = Path("app/data/results")
L9 = [(0,0,0,0),(0,1,1,1),(0,2,2,2),(1,0,1,2),(1,1,2,0),(1,2,0,1),
      (2,0,2,1),(2,1,0,2),(2,2,1,0)]
N_LV = [25, 50, 100]
ETA_LV = [2.0, 20.0, 100.0]
PC_LV = [0.6, 0.9, 1.0]
PMF_LV = [0.5, 1.0, 5.0]          # multiplier of 1/d
TUNE_SEEDS = list(range(201, 211))
EVAL_SEEDS = list(range(1, 31))
BUDGET = 25_000


def run_visa(problem, cfg, seed):
    n, eta, pc, pmf = cfg
    cn.POP, cn.GEN = n, BUDGET // n
    cn.ETA_C, cn.PC, cn.PM = eta, pc, pmf / cn.NUM_GROUPS
    front = cn.run_nsga2(problem, seed)
    return compute_hypervolume([tuple(x) for x in front])


def run_knap(problem, cfg, seed):
    n, eta, pc, pmf = cfg
    sp.POP, sp.GEN = n, BUDGET // n
    sp.ETA, sp.PC, sp.PM = eta, pc, pmf / sp.N
    front = sp.run_nsga_realcoded(problem, seed)
    return compute_hypervolume(front, (1.0, 1.0, 1.0))


def tune(tag, runner, problem, rand_per_seed):
    t0 = time.time()
    rows = []
    for r, (a, b, c, d) in enumerate(L9):
        cfg = (N_LV[a], ETA_LV[b], PC_LV[c], PMF_LV[d])
        hv = [runner(problem, cfg, s) for s in TUNE_SEEDS]
        rows.append({"config": {"N": cfg[0], "T": BUDGET // cfg[0], "eta_c": cfg[1],
                                "pc": cfg[2], "pm_mult": cfg[3]},
                     "mean_hv_tune": float(np.mean(hv))})
        print(f"  {tag} L9 row {r+1}: N={cfg[0]} eta={cfg[1]} pc={cfg[2]} "
              f"pmx{cfg[3]} -> {np.mean(hv):,.4f} ({time.time()-t0:.0f}s)", flush=True)
    best_i = int(np.argmax([r["mean_hv_tune"] for r in rows]))
    bc = rows[best_i]["config"]
    cfg = (bc["N"], bc["eta_c"], bc["pc"], bc["pm_mult"])
    conf = [runner(problem, cfg, s) for s in EVAL_SEEDS]
    stat, p_less = wilcoxon(conf, rand_per_seed, alternative="less")
    _, p_two = wilcoxon(conf, rand_per_seed, alternative="two-sided")
    out = {"rows": rows, "best_row": best_i + 1, "best_config": bc,
           "confirmation_hv_per_seed": conf,
           "confirmation_mean": float(np.mean(conf)),
           "random_mean": float(np.mean(rand_per_seed)),
           "diff_vs_random_pct": float(100 * (np.mean(conf) - np.mean(rand_per_seed))
                                       / np.mean(rand_per_seed)),
           "p_below_random_one_sided": float(p_less),
           "p_vs_random_two_sided": float(p_two)}
    print(f"== {tag}: best row {best_i+1} {bc} -> confirm {np.mean(conf):,.4f} "
          f"vs random {np.mean(rand_per_seed):,.4f} ({out['diff_vs_random_pct']:+.2f}%, "
          f"p_below={p_less:.2e}) ({time.time()-t0:.0f}s)", flush=True)
    return out


def main():
    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    spm = json.load(open(RESULTS / "second_problem.json"))["methods"]
    out = {}
    out["visa"] = tune("visa", run_visa, VisaProblem(),
                       lad["random_restart"]["hv_per_seed"])
    out["knapsack"] = tune("knapsack", run_knap, sp.MOMKP(),
                           spm["Random restart"]["per_run_hv"])
    json.dump(out, open(RESULTS / "nsga2_l9.json", "w"), indent=2)
    print("-> nsga2_l9.json")


if __name__ == "__main__":
    main()
