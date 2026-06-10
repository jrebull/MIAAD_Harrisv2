"""
The missing ladder cell (reviewer-requested): a random-key NSGA-II whose variation
operators are BRKGA-style -- parameterized (biased) uniform crossover on the keys
plus per-gene random-reset mutation -- instead of SBX + polynomial mutation.

This is a PREDICTIVE test of the two-condition rule, declared before running:
  - Condition 1 (operator changes the decoded order): biased uniform crossover
    swaps whole keys, so the child's SPV order should sit far from the parent's
    (tau well below the SBX 0.99); measured below with the operator_order protocol.
  - Condition 2 (selection preserves diversity): unchanged NSGA-II non-dominated
    sorting + crowding.
  PREDICTION: the method beats blind random restart and lands in/near the
  permutation top tier. If instead it stays at the real-coded NSGA-II level,
  the rule is falsified on a method not used to formulate it.

Everything else is held fixed: same SPV+greedy decoder, same budget
(50 x 500 = 25,000 evaluations), same seeds 1-30, same HV reference point.

Output: app/data/results/brkga_ladder.json
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, mannwhitneyu, wilcoxon

from app.core.config import LB, UB, NUM_GROUPS
from app.core.problem import VisaProblem
from app.core.mohho import evaluate_hawk, compute_hypervolume
from compare_nsga2 import fast_nondominated_sort, tournament, nondominated
from app.core.mohho import crowding_distance

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))
POP, GEN = 50, 500
RHO_E = 0.7          # BRKGA elite-inheritance probability
PM = 1.0 / NUM_GROUPS  # per-gene random-reset probability
PC = 0.9


def biased_uniform(p_better, p_other, rng):
    mask = rng.random(NUM_GROUPS) < RHO_E
    return np.where(mask, p_better, p_other)


def reset_mutate(x, rng):
    y = x.copy()
    mask = rng.random(NUM_GROUPS) < PM
    y[mask] = rng.uniform(LB, UB, int(mask.sum()))
    return y


def spv_tau(parent, child):
    rp = np.argsort(np.argsort(parent))
    rc = np.argsort(np.argsort(child))
    t, _ = kendalltau(rp, rc)
    return 0.0 if np.isnan(t) else t


def measure_tau(k=3000, seed=123):
    rng = np.random.default_rng(seed)
    tx, tm = [], []
    for _ in range(k):
        a = rng.uniform(LB, UB, NUM_GROUPS)
        b = rng.uniform(LB, UB, NUM_GROUPS)
        tx.append(spv_tau(a, biased_uniform(a, b, rng)))
        tm.append(spv_tau(a, reset_mutate(a, rng)))
    return {"biased_uniform_xover": {"mean_tau": float(np.mean(tx)), "std_tau": float(np.std(tx))},
            "reset_mutation": {"mean_tau": float(np.mean(tm)), "std_tau": float(np.std(tm))}}


def run_brkga_nsga2(problem, seed):
    rng = np.random.default_rng(seed)
    pop = rng.uniform(LB, UB, size=(POP, NUM_GROUPS))
    fits = [evaluate_hawk(pop[i], problem)[1] for i in range(POP)]
    for _ in range(GEN):
        fronts, rank = fast_nondominated_sort(fits)
        cd = [0.0] * POP
        for fr in fronts:
            d = crowding_distance([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = d[k]
        off = []
        while len(off) < POP:
            ia = tournament(rank, cd, rng); ib = tournament(rank, cd, rng)
            # bias toward the better-ranked parent (BRKGA elite side)
            if (rank[ib], -cd[ib]) < (rank[ia], -cd[ia]):
                ia, ib = ib, ia
            if rng.random() <= PC:
                c = biased_uniform(pop[ia], pop[ib], rng)
            else:
                c = pop[ia].copy()
            off.append(reset_mutate(c, rng))
        off = np.array(off)
        off_fits = [evaluate_hawk(off[i], problem)[1] for i in range(POP)]
        comb = np.vstack([pop, off]); comb_fits = fits + off_fits
        fronts, _ = fast_nondominated_sort(comb_fits)
        new_idx = []
        for fr in fronts:
            if len(new_idx) + len(fr) <= POP:
                new_idx += fr
            else:
                d = crowding_distance([comb_fits[i] for i in fr])
                order = sorted(range(len(fr)), key=lambda k: d[k], reverse=True)
                new_idx += [fr[k] for k in order[:POP - len(new_idx)]]
                break
        pop = comb[new_idx]; fits = [comb_fits[i] for i in new_idx]
    fronts, _ = fast_nondominated_sort(fits)
    return [fits[i] for i in fronts[0]]


def a12(x, y):
    gt = sum(1 for a in x for b in y if a > b)
    eq = sum(1 for a in x for b in y if a == b)
    return (gt + 0.5 * eq) / (len(x) * len(y))


def main():
    t0 = time.time()
    print("Operator order-preservation (3000 trials):")
    taus = measure_tau()
    for k, v in taus.items():
        print(f"  {k}: tau = {v['mean_tau']:.3f} +/- {v['std_tau']:.3f}")

    problem = VisaProblem()
    hv_per_seed, all_front = [], []
    for s in SEEDS:
        ts = time.time()
        front = run_brkga_nsga2(problem, s)
        hv = compute_hypervolume(front)
        hv_per_seed.append(hv); all_front += [tuple(p) for p in front]
        print(f"  seed {s:2d}: {len(front):3d} sols, HV={hv:,.0f}  ({time.time()-ts:.1f}s)", flush=True)
    combined = nondominated(all_front)

    ladder = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    rnd = ladder["random_restart"]["hv_per_seed"]
    pn = ladder["perm_nsga2"]["hv_per_seed"]
    rc = ladder["nsga2_realcoded"]["hv_per_seed"]

    def paired(name, other):
        stat, p = wilcoxon(hv_per_seed, other, alternative="two-sided")
        return {"vs": name, "wilcoxon_p_two_sided": float(p), "a12": a12(hv_per_seed, other),
                "mean_diff_pct": 100 * (np.mean(hv_per_seed) - np.mean(other)) / np.mean(other)}

    out = {
        "prediction": "Declared a priori: biased-uniform xover changes decoded order "
                      "(condition 1) and NDS selection preserves diversity (condition 2) "
                      "=> method should beat blind random restart and approach the "
                      "permutation tier.",
        "protocol": {"pop": POP, "gen": GEN, "evals": POP * GEN, "seeds": SEEDS,
                     "rho_e": RHO_E, "pm": PM, "pc": PC,
                     "operators": "BRKGA-style biased uniform crossover + per-gene reset mutation",
                     "selection": "NSGA-II NDS + crowding (unchanged)"},
        "operator_tau": taus,
        "hv_per_seed": hv_per_seed,
        "hv_mean": float(np.mean(hv_per_seed)), "hv_std": float(np.std(hv_per_seed)),
        "cv_pct": 100 * float(np.std(hv_per_seed) / np.mean(hv_per_seed)),
        "combined_front_hv": compute_hypervolume(combined),
        "combined_front_size": len(combined),
        "paired": [paired("random_restart", rnd), paired("perm_nsga2", pn),
                   paired("nsga2_realcoded", rc)],
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "brkga_ladder.json", "w"), indent=2)
    print(f"\nmean HV = {out['hv_mean']:,.0f} (random restart {np.mean(rnd):,.0f}, "
          f"perm-NSGA-II {np.mean(pn):,.0f}, real-coded {np.mean(rc):,.0f})")
    for p in out["paired"]:
        print(f"  vs {p['vs']}: diff={p['mean_diff_pct']:+.2f}%  p={p['wilcoxon_p_two_sided']:.2e}  A12={p['a12']:.3f}")
    print(f"total {time.time()-t0:.0f}s -> brkga_ladder.json")


if __name__ == "__main__":
    main()
