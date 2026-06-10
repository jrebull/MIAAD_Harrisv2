"""
PROSPECTIVE validation of the two-condition diagnostic on a FIFTH, unseen problem.

Protocol (registered BEFORE any optimizer runs; see prospective_scp_registration.json
and its git commit, which precedes the results commit):

  Problem: tri-objective set covering (mo-SCP). Universe of 150 elements, 120 sets,
  three independent uniform cost vectors. Decoder: walk sets in SPV order, add a set
  iff it covers at least one still-uncovered element; the union of all sets covers
  the universe, so every decoded solution is a full cover (feasible by construction).
  Objectives: normalized total cost of the cover under each of the three cost
  vectors (all minimized). Step-3 classification: SELECTION landscape (the decoded
  object is a subset; order is only the instrument).

  Registered predictions (graded two-condition diagnostic, calibrated on the visa
  problem and three replication structures, none of which is an SCP):
    P1: real-coded NSGA-II (SBX+poly, tau~0.99) finishes significantly BELOW blind
        random restart (paired Wilcoxon, one-sided p<0.05).
    P2: rk-NSGA-II (biased uniform crossover, tau~0.63) finishes within 2% of blind
        random restart's mean HV AND significantly below perm-NSGA-II (p<0.05).
    P3: perm-NSGA-II (OX+swap, order renewal) finishes significantly ABOVE blind
        random restart (one-sided p<0.05).
    P4: competent random-key MO-HHO (HHO moves tau~0 + NDS) finishes significantly
        ABOVE blind random restart (one-sided p<0.05).

Usage:
  python prospective_scp.py --register   # write the registration JSON only
  python prospective_scp.py             # run 5 methods x 30 seeds, check P1-P4

Outputs: app/data/results/prospective_scp_registration.json
         app/data/results/prospective_scp.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.mohho import compute_hypervolume
import second_problem as sp
import competent_mohho as C

RESULTS = Path("app/data/results")
N_SETS, M_ELEM = 120, 150          # n matches second_problem.N so its runners reuse
POP, GEN = 50, 500
SEEDS = list(range(1, 31))
RHO_E, PM_RESET = 0.7, 1.0 / N_SETS
REF = (1.0, 1.0, 1.0)


class MOSCP:
    def __init__(self, seed=7):
        rng = np.random.default_rng(seed)
        cov = rng.random((N_SETS, M_ELEM)) < 0.04
        for e in range(M_ELEM):                 # guarantee global coverage
            if not cov[:, e].any():
                cov[rng.integers(0, N_SETS), e] = True
        self.cov = cov
        self.cost = rng.uniform(10, 100, size=(N_SETS, 3))
        self.cmax = self.cost.sum(axis=0)
        self.n = N_SETS

    def decode_perm(self, perm):
        covered = np.zeros(M_ELEM, dtype=bool); sel = []
        for i in perm:
            new = self.cov[i] & ~covered
            if new.any():
                sel.append(int(i)); covered |= self.cov[i]
                if covered.all():
                    break
        return sel

    def eval_perm(self, perm):
        sel = self.decode_perm(perm)
        c = self.cost[sel].sum(axis=0) / self.cmax
        return (float(c[0]), float(c[1]), float(c[2]))

    def eval_keys(self, keys):
        return self.eval_perm(np.argsort(keys))


REGISTRATION = {
    "problem": {"name": "mo-SCP", "n_sets": N_SETS, "m_elements": M_ELEM,
                "cost_vectors": 3, "instance_seed": 7,
                "decoder": "SPV order; add set iff it covers a new element; "
                           "full cover by construction",
                "landscape_class_step3": "selection"},
    "budget": {"pop": POP, "gen": GEN, "evals": POP * GEN, "seeds": SEEDS},
    "predictions": {
        "P1": "real-coded NSGA-II (SBX, tau~0.99) significantly BELOW random restart "
              "(paired Wilcoxon one-sided p<0.05)",
        "P2": "rk-NSGA-II (biased uniform, tau~0.63) within 2% of random restart's "
              "mean HV AND significantly below perm-NSGA-II (p<0.05)",
        "P3": "perm-NSGA-II significantly ABOVE random restart (one-sided p<0.05)",
        "P4": "competent random-key MO-HHO significantly ABOVE random restart "
              "(one-sided p<0.05)",
    },
    "note": "Registered before running any optimizer on this problem; the git "
            "commit of this file precedes the results commit.",
}


def run_rk_biased(prob, seed):
    """NSGA-II skeleton, BRKGA-style biased uniform crossover + reset mutation."""
    rng = np.random.default_rng(seed)
    pop = rng.uniform(0, 1, size=(POP, N_SETS))
    fits = [prob.eval_keys(pop[i]) for i in range(POP)]
    from compare_nsga2 import fast_nondominated_sort
    from app.core.mohho import crowding_distance
    for _ in range(GEN):
        fronts, rank = fast_nondominated_sort(fits)
        cd = [0.0] * POP
        for fr in fronts:
            d = crowding_distance([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = d[k]
        off = []
        while len(off) < POP:
            ia = sp.tourney(rank, cd, rng); ib = sp.tourney(rank, cd, rng)
            if (rank[ib], -cd[ib]) < (rank[ia], -cd[ia]):
                ia, ib = ib, ia
            if rng.random() <= 0.9:
                mask = rng.random(N_SETS) < RHO_E
                c = np.where(mask, pop[ia], pop[ib])
            else:
                c = pop[ia].copy()
            m = rng.random(N_SETS) < PM_RESET
            c = c.copy(); c[m] = rng.uniform(0, 1, int(m.sum()))
            off.append(c)
        off = np.array(off)
        off_fits = [prob.eval_keys(off[i]) for i in range(POP)]
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
    from compare_nsga2 import fast_nondominated_sort as fns
    fronts, _ = fns(fits)
    return [fits[i] for i in fronts[0]]


def run_competent(prob, seed):
    return C.run_competent_mohho(prob.eval_keys, prob.n, 3,
                                 lambda F: compute_hypervolume(F, REF),
                                 seed, POP, GEN, pm=0.15, use_sbx=True)["front"]


def a12(x, y):
    gt = sum(1 for a in x for b in y if a > b)
    eq = sum(1 for a in x for b in y if a == b)
    return (gt + 0.5 * eq) / (len(x) * len(y))


def main():
    if "--register" in sys.argv:
        json.dump(REGISTRATION, open(RESULTS / "prospective_scp_registration.json", "w"),
                  indent=2)
        print("registration written (commit this BEFORE running results)")
        return

    prob = MOSCP()
    METHODS = {
        "random_restart": sp.run_random,
        "nsga2_realcoded": sp.run_nsga_realcoded,
        "rk_nsga2_biased": run_rk_biased,
        "perm_nsga2": sp.run_permnsga,
        "competent_mohho": run_competent,
    }
    t0 = time.time(); hv = {}
    for name, fn in METHODS.items():
        hv[name] = []
        for s in SEEDS:
            front = fn(prob, s)
            hv[name].append(compute_hypervolume(front, REF))
        print(f"{name:18s} mean HV = {np.mean(hv[name]):.4f} +/- {np.std(hv[name]):.4f}"
              f"  ({time.time()-t0:.0f}s)", flush=True)

    rnd, rc, rkb, pn, comp = (hv["random_restart"], hv["nsga2_realcoded"],
                              hv["rk_nsga2_biased"], hv["perm_nsga2"],
                              hv["competent_mohho"])

    def w(x, y, alternative):
        return float(wilcoxon(x, y, alternative=alternative).pvalue)

    p1_p = w(rc, rnd, "less")
    p2_gap = abs(np.mean(rkb) - np.mean(rnd)) / np.mean(rnd)
    p2_p_vs_perm = w(rkb, pn, "less")
    p3_p = w(pn, rnd, "greater")
    p4_p = w(comp, rnd, "greater")
    verdict = {
        "P1": {"holds": p1_p < 0.05, "p_one_sided": p1_p, "a12": a12(rc, rnd)},
        "P2": {"holds": (p2_gap < 0.02) and (p2_p_vs_perm < 0.05),
               "gap_vs_random_pct": 100 * p2_gap, "p_below_perm": p2_p_vs_perm,
               "p_vs_random_two_sided": w(rkb, rnd, "two-sided"),
               "a12_vs_random": a12(rkb, rnd)},
        "P3": {"holds": p3_p < 0.05, "p_one_sided": p3_p, "a12": a12(pn, rnd)},
        "P4": {"holds": p4_p < 0.05, "p_one_sided": p4_p, "a12": a12(comp, rnd)},
    }
    out = {"registration": REGISTRATION,
           "hv_mean": {k: float(np.mean(v)) for k, v in hv.items()},
           "hv_std": {k: float(np.std(v)) for k, v in hv.items()},
           "hv_per_seed": hv, "verdict": verdict,
           "all_hold": all(v["holds"] for v in verdict.values()),
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS / "prospective_scp.json", "w"), indent=2)
    for k, v in verdict.items():
        print(k, "HOLDS" if v["holds"] else "FAILS", v)
    print("ALL PREDICTIONS HOLD" if out["all_hold"] else "SOME PREDICTION FAILED",
          f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
