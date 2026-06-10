"""
Companion cell to brkga_nsga.py: a faithful multi-objective BRKGA. The first cell
(NSGA-II skeleton + biased uniform crossover, no mutants) TIED blind random restart
(309,970 vs 310,214, p=0.79) -- so before drawing conclusions we test the canonical
BRKGA recipe, which adds the diversity mechanism the first cell lacked: a mutant
(immigrant) fraction of fresh random keys every generation.

Design (Goncalves & Resende 2011, lifted to multi-objective via NDS ranking):
  - population 50, 500 generations (same 25,000-evaluation budget),
  - elite set = top 20% by (NDS rank, crowding),
  - 15% mutants: fresh uniform random keys,
  - remaining 65% by biased uniform crossover (elite parent gene w.p. 0.7),
  - same SPV+greedy decoder, seeds 1-30, same HV reference point.

Output: app/data/results/brkga_full.json
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

from app.core.config import LB, UB, NUM_GROUPS
from app.core.problem import VisaProblem
from app.core.mohho import evaluate_hawk, compute_hypervolume, crowding_distance
from compare_nsga2 import fast_nondominated_sort, nondominated
from brkga_nsga import biased_uniform, a12

RESULTS = Path("app/data/results")
SEEDS = list(range(1, 31))
POP, GEN = 50, 500
ELITE_FRAC, MUTANT_FRAC, RHO_E = 0.20, 0.15, 0.7
N_ELITE = int(POP * ELITE_FRAC)
N_MUT = int(POP * MUTANT_FRAC)


def sort_by_nds_crowding(fits):
    fronts, rank = fast_nondominated_sort(fits)
    cd = [0.0] * len(fits)
    for fr in fronts:
        d = crowding_distance([fits[i] for i in fr])
        for k, idx in enumerate(fr):
            cd[idx] = d[k]
    return sorted(range(len(fits)), key=lambda i: (rank[i], -cd[i]))


def run_brkga(problem, seed):
    rng = np.random.default_rng(seed)
    pop = rng.uniform(LB, UB, size=(POP, NUM_GROUPS))
    fits = [evaluate_hawk(pop[i], problem)[1] for i in range(POP)]
    for _ in range(GEN):
        order = sort_by_nds_crowding(fits)
        elite_idx = order[:N_ELITE]
        nonelite_idx = order[N_ELITE:]
        new = [pop[i].copy() for i in elite_idx]
        new += [rng.uniform(LB, UB, NUM_GROUPS) for _ in range(N_MUT)]
        while len(new) < POP:
            e = pop[elite_idx[rng.integers(0, N_ELITE)]]
            o = pop[nonelite_idx[rng.integers(0, len(nonelite_idx))]]
            new.append(biased_uniform(e, o, rng))
        pop = np.array(new)
        # elites keep their fitness; re-evaluate the rest
        fits = fits_elite = [fits[i] for i in elite_idx]
        fits = fits_elite + [evaluate_hawk(pop[i], problem)[1] for i in range(N_ELITE, POP)]
    fronts, _ = fast_nondominated_sort(fits)
    return [fits[i] for i in fronts[0]]


def main():
    t0 = time.time()
    problem = VisaProblem()
    hv_per_seed, all_front = [], []
    for s in SEEDS:
        ts = time.time()
        front = run_brkga(problem, s)
        hv = compute_hypervolume(front)
        hv_per_seed.append(hv); all_front += [tuple(p) for p in front]
        print(f"  seed {s:2d}: {len(front):3d} sols, HV={hv:,.0f}  ({time.time()-ts:.1f}s)", flush=True)
    combined = nondominated(all_front)

    ladder = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    cell1 = json.load(open(RESULTS / "brkga_ladder.json"))

    def paired(name, other):
        stat, p = wilcoxon(hv_per_seed, other, alternative="two-sided")
        return {"vs": name, "wilcoxon_p_two_sided": float(p), "a12": a12(hv_per_seed, other),
                "mean_diff_pct": 100 * (np.mean(hv_per_seed) - np.mean(other)) / np.mean(other)}

    out = {
        "protocol": {"pop": POP, "gen": GEN, "evals": POP * GEN, "seeds": SEEDS,
                     "elite_frac": ELITE_FRAC, "mutant_frac": MUTANT_FRAC, "rho_e": RHO_E,
                     "design": "canonical BRKGA (elites copied, mutants, biased uniform "
                               "crossover), multi-objective via NDS+crowding elite ranking"},
        "hv_per_seed": hv_per_seed,
        "hv_mean": float(np.mean(hv_per_seed)), "hv_std": float(np.std(hv_per_seed)),
        "cv_pct": 100 * float(np.std(hv_per_seed) / np.mean(hv_per_seed)),
        "combined_front_hv": compute_hypervolume(combined),
        "combined_front_size": len(combined),
        "paired": [paired("random_restart", ladder["random_restart"]["hv_per_seed"]),
                   paired("perm_nsga2", ladder["perm_nsga2"]["hv_per_seed"]),
                   paired("nsga2_realcoded", ladder["nsga2_realcoded"]["hv_per_seed"]),
                   paired("brkga_cell1_no_mutants", cell1["hv_per_seed"])],
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "brkga_full.json", "w"), indent=2)
    print(f"\nmean HV = {out['hv_mean']:,.0f}")
    for p in out["paired"]:
        print(f"  vs {p['vs']}: diff={p['mean_diff_pct']:+.2f}%  p={p['wilcoxon_p_two_sided']:.2e}  A12={p['a12']:.3f}")
    print(f"total {time.time()-t0:.0f}s -> brkga_full.json")


if __name__ == "__main__":
    main()
