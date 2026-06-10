"""
Reviewer-3's ablation: does Discrete-MOHHO's escape-energy schedule add anything
measurable, or is the 'hawk' label decorative? Constant-schedule variant: the
|E|>=1 exploration branch fires with its run-average probability (~0.153,
computed by Monte Carlo from e = 2*U(-1,1)*(1-t/T)), and the besiege swap count
is fixed at the run-average k (instead of |E|-scaled). Everything else identical
(OX toward leader, reversal dives, same archive, budget, seeds 1-30).

Output: app/data/results/discrete_e_ablation.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.problem import VisaProblem
from app.core.mohho import (compute_hypervolume, update_archive, select_leader,
                            dominates)
import discrete_mohho as DM

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))


def schedule_constants(n_mc=200_000, seed=11):
    rng = np.random.default_rng(seed)
    t = rng.random(n_mc)                      # t/GEN uniform over the run
    e = 2 * (2 * rng.random(n_mc) - 1) * (1 - t)
    absE = np.abs(e)
    p_explore = float((absE >= 1).mean())
    k_mean = float(absE[absE < 1].mean() * (DM.NUM_GROUPS // 6))
    return p_explore, max(1, int(round(k_mean)))


def step_const(pop, i, fit_i, ap, af, rng, problem, p_explore, k_const):
    rabbit = select_leader(ap, af, rng)
    if rng.random() < p_explore:
        if rng.random() < 0.5:
            j = rng.integers(DM.POP)
            child = DM.ox(pop[j], rabbit, rng)
        else:
            child = DM.nswaps(pop[i], int(rng.integers(DM.NUM_GROUPS // 4,
                                                       DM.NUM_GROUPS // 2)), rng)
    else:
        child = DM.ox(rabbit, pop[i], rng)
        child = DM.nswaps(child, k_const, rng)
        if rng.random() < 0.5:
            child = DM.reverse_seg(child, rng)
    fit = DM.eval_perm(child, problem)
    update_archive(ap, af, child, fit, DM.ARCH, rng)
    if dominates(fit, fit_i):
        return child, fit
    return pop[i], fit_i


def run_const(problem, seed, p_explore, k_const):
    rng = np.random.default_rng(seed)
    pop = [rng.permutation(DM.NUM_GROUPS) for _ in range(DM.POP)]
    fits = [DM.eval_perm(pop[i], problem) for i in range(DM.POP)]
    ap, af = [], []
    for i in range(DM.POP):
        update_archive(ap, af, pop[i], fits[i], DM.ARCH, rng)
    for _ in range(DM.GEN):
        for i in range(DM.POP):
            pop[i], fits[i] = step_const(pop, i, fits[i], ap, af, rng, problem,
                                         p_explore, k_const)
    return af


def main():
    t0 = time.time()
    p_explore, k_const = schedule_constants()
    print(f"constants: p_explore={p_explore:.3f}, k_const={k_const}")
    problem = VisaProblem()
    hv = []
    for s in SEEDS:
        af = run_const(problem, s, p_explore, k_const)
        hv.append(compute_hypervolume(af))
        print(f"seed {s:2d}: HV={hv[-1]:,.0f} ({time.time()-t0:.0f}s)", flush=True)
    dm = json.load(open(RESULTS / "discrete_mohho.json"))["per_run_hv"]
    _, p_two = wilcoxon(hv, dm, alternative="two-sided")
    out = {"constants": {"p_explore": p_explore, "k_const": k_const},
           "hv_per_seed": hv, "hv_mean": float(np.mean(hv)),
           "hv_std": float(np.std(hv)),
           "scheduled_mean": float(np.mean(dm)),
           "diff_pct": float(100 * (np.mean(hv) - np.mean(dm)) / np.mean(dm)),
           "p_two_sided_vs_scheduled": float(p_two),
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS / "discrete_e_ablation.json", "w"), indent=2)
    print(f"\nconstant-schedule mean {np.mean(hv):,.0f} vs scheduled {np.mean(dm):,.0f} "
          f"({out['diff_pct']:+.2f}%, p={p_two:.3f})")


if __name__ == "__main__":
    main()
