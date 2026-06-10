"""
CLEAN DOSE-RESPONSE for the tau gradient (reviewer-2's single change): one operator
family with a continuous disruption knob -- the biased uniform crossover's elite
inheritance probability rho_e -- under FIXED diversity-preserving selection
(NSGA-II skeleton), swept over 11 levels on ALL FIVE structures, 30 seeds each,
scored by hypervolume AND a reference-free-style per-run IGD+ (against the pooled
nondominated union of the sweep itself, so the gradient is checked under a second
metric that does not use the HV reference point).

REGISTERED PREDICTIONS (committed before running; the registration commit precedes
the results commit in the repository):
  R1 (visa, knapsack -- blind sampling strong): mean HV decreases monotonically as
     rho_e -> 1 (less order disruption); Spearman(level tau, mean HV) <= -0.8; and
     the curve crosses the stored random-restart level inside the swept tau range.
  R2 (TSP, flow-shop, set covering -- blind sampling weak): the curve stays at or
     above the stored random-restart level at EVERY rho_e level.
  R3 (all five): the per-run IGD+ gradient agrees in direction with the HV gradient
     (Spearman of opposite sign, |rho| >= 0.6), i.e., the gradient is not an
     artifact of the HV reference point.

Usage:
  python rho_sweep.py --register   # write registration JSON only (commit first)
  python rho_sweep.py             # full sweep (~3 h)

Output: app/data/results/rho_sweep_registration.json / rho_sweep.json
"""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, spearmanr

sys.path.insert(0, str(Path(__file__).parent / "repro"))
import _bootstrap; _bootstrap.bootstrap_engine()

from app.core.config import LB, UB, NUM_GROUPS
from app.core.problem import VisaProblem
from app.core.mohho import (evaluate_hawk, compute_hypervolume, dominates,
                            crowding_distance, HV_REF_POINT)
from compare_nsga2 import fast_nondominated_sort
from second_problem import MOMKP
from more_structures import MOTSP, MOPFSP
from prospective_scp import MOSCP

RESULTS = Path("app/data/results")
RHO_LEVELS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
POP, GEN = 50, 500
SEEDS = list(range(1, 31))
K_TAU = 3000

REGISTRATION = {
    "knob": "rho_e of biased uniform crossover (elite-parent gene probability), "
            "NSGA-II NDS selection fixed, per-gene reset mutation pm=1/d fixed",
    "levels": RHO_LEVELS, "pop": POP, "gen": GEN, "seeds": SEEDS,
    "structures": ["visa", "knapsack", "tsp", "flowshop", "scp"],
    "predictions": {
        "R1": "visa & knapsack (blind sampling strong): mean HV increases with order "
              "disruption, i.e. decreases as rho_e->1; Spearman(level tau, mean HV) "
              "<= -0.8; and the curve crosses the stored random-restart mean inside "
              "the swept tau range",
        "R2": "TSP, flow-shop, set covering (blind sampling weak): mean HV at or "
              "above the stored random-restart mean at every level",
        "R3": "all five: per-run IGD+ gradient direction agrees with HV gradient "
              "(opposite-signed Spearman, |rho| >= 0.6)",
    },
    "note": "Registered before running; commit precedes results.",
}


# ---------------- structures ----------------
def visa_factory():
    prob = VisaProblem()
    return {"dim": NUM_GROUPS, "eval": lambda k: tuple(evaluate_hawk(k, prob)[1]),
            "hv": lambda F: compute_hypervolume(F),
            "rand_mean": None}  # filled from ladder_v5

def generic_factory(prob, ref):
    return {"dim": prob.n, "eval": lambda k: tuple(prob.eval_keys(k)),
            "hv": lambda F: compute_hypervolume(F, ref), "rand_mean": None}


def load_random_baselines():
    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    sp = json.load(open(RESULTS / "second_problem.json"))["methods"]
    ms = json.load(open(RESULTS / "more_structures.json"))
    scp = json.load(open(RESULTS / "prospective_scp.json"))
    return {
        "visa": float(np.mean(lad["random_restart"]["hv_per_seed"])),
        "knapsack": float(np.mean(sp["Random restart"]["per_run_hv"])),
        "tsp": float(np.mean(ms["mo-TSP"]["methods"]["Random restart"]["per_run_hv"])),
        "flowshop": float(np.mean(ms["mo-PFSP"]["methods"]["Random restart"]["per_run_hv"])),
        "scp": float(np.mean(scp["hv_per_seed"]["random_restart"])),
    }


# ---------------- operator + tau ----------------
def biased_uniform(a, b, rho, rng):
    mask = rng.random(len(a)) < rho
    return np.where(mask, a, b)

def spv_tau(parent, child):
    rp = np.argsort(np.argsort(parent)); rc = np.argsort(np.argsort(child))
    t, _ = kendalltau(rp, rc)
    return 0.0 if np.isnan(t) else t

def measure_tau(dim, rho, k=K_TAU, seed=123):
    rng = np.random.default_rng(seed)
    ts = []
    for _ in range(k):
        a = rng.uniform(0, 1, dim); b = rng.uniform(0, 1, dim)
        ts.append(spv_tau(a, biased_uniform(a, b, rho, rng)))
    return float(np.mean(ts))


# ---------------- generic rk-NSGA-II(biased, rho_e) ----------------
def tourney(rank, cd, rng):
    a, b = rng.integers(0, len(rank), size=2)
    if rank[a] < rank[b]: return a
    if rank[b] < rank[a]: return b
    return a if cd[a] >= cd[b] else b

def run_biased(S, rho, seed):
    dim, ev = S["dim"], S["eval"]
    pm = 1.0 / dim
    rng = np.random.default_rng(seed)
    pop = rng.uniform(0, 1, size=(POP, dim))
    fits = [ev(pop[i]) for i in range(POP)]
    for _ in range(GEN):
        fronts, rank = fast_nondominated_sort(fits)
        cd = [0.0] * POP
        for fr in fronts:
            d = crowding_distance([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = d[k]
        off = []
        while len(off) < POP:
            ia = tourney(rank, cd, rng); ib = tourney(rank, cd, rng)
            if (rank[ib], -cd[ib]) < (rank[ia], -cd[ia]):
                ia, ib = ib, ia
            c = biased_uniform(pop[ia], pop[ib], rho, rng) if rng.random() <= 0.9 else pop[ia].copy()
            m = rng.random(dim) < pm
            c = c.copy(); c[m] = rng.uniform(0, 1, int(m.sum()))
            off.append(c)
        off = np.array(off)
        off_fits = [ev(off[i]) for i in range(POP)]
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


# ---------------- IGD+ vs pooled sweep reference ----------------
def nondom(points):
    pts = list({tuple(round(x, 8) for x in p) for p in points})
    return [p for p in pts if not any(dominates(q, p) for q in pts if q != p)]

def igd_plus(front, Z, lo, span):
    F = np.array([[(p[m] - lo[m]) / span[m] for m in range(len(lo))] for p in front])
    out = 0.0
    for z in np.array([[(z[m] - lo[m]) / span[m] for m in range(len(lo))] for z in Z]):
        d = np.maximum(F - z, 0.0)
        out += float(np.min(np.sqrt((d ** 2).sum(axis=1))))
    return out / len(Z)


def main():
    if "--register" in sys.argv:
        json.dump(REGISTRATION, open(RESULTS / "rho_sweep_registration.json", "w"), indent=2)
        print("registration written (commit BEFORE running)")
        return

    rand = load_random_baselines()
    structures = {
        "visa": visa_factory(),
        "knapsack": generic_factory(MOMKP(), (1.0, 1.0, 1.0)),
        "tsp": generic_factory(MOTSP(), (1.0, 1.0, 1.0)),
        "flowshop": generic_factory(MOPFSP(), (1.0, 1.0, 1.0)),
        "scp": generic_factory(MOSCP(), (1.0, 1.0, 1.0)),
    }
    t0 = time.time()
    out = {"registration": REGISTRATION, "random_mean": rand, "structures": {}}
    for sname, S in structures.items():
        taus, hv_levels, fronts_all, igd_levels = [], [], [], []
        per_seed = {}
        for rho in RHO_LEVELS:
            tau = measure_tau(S["dim"], rho)
            hvs, level_fronts = [], []
            for s in SEEDS:
                front = run_biased(S, rho, s)
                hvs.append(S["hv"](front)); level_fronts.append(front)
            taus.append(tau); hv_levels.append(float(np.mean(hvs)))
            per_seed[str(rho)] = hvs; fronts_all.append(level_fronts)
            print(f"{sname} rho={rho:.2f} tau={tau:.3f} HV={np.mean(hvs):,.4f} "
                  f"(rand {rand[sname]:,.4f}) ({time.time()-t0:.0f}s)", flush=True)
        # pooled reference for IGD+ (union over the whole sweep of this structure)
        pool = [p for lvl in fronts_all for fr in lvl for p in fr]
        Z = nondom(pool)
        M = len(Z[0])
        lo = [min(p[m] for p in Z) for m in range(M)]
        hi = [max(p[m] for p in Z) for m in range(M)]
        span = [max(hi[m] - lo[m], 1e-12) for m in range(M)]
        for lvl in fronts_all:
            igd_levels.append(float(np.mean([igd_plus(fr, Z, lo, span) for fr in lvl])))
        rho_hv, p_hv = spearmanr(taus, hv_levels)
        rho_igd, p_igd = spearmanr(taus, igd_levels)
        # crossing vs random (linear interp on tau axis)
        crossing = None
        diffs = [h - rand[sname] for h in hv_levels]
        for i in range(len(diffs) - 1):
            if diffs[i] == 0 or diffs[i] * diffs[i + 1] < 0:
                t1, t2 = taus[i], taus[i + 1]
                d1, d2 = diffs[i], diffs[i + 1]
                crossing = float(t1 + (t2 - t1) * (0 - d1) / (d2 - d1)) if d2 != d1 else float(t1)
                break
        above_all = bool(all(d >= 0 for d in diffs))
        out["structures"][sname] = {
            "rho_levels": RHO_LEVELS, "tau_levels": taus, "hv_mean_levels": hv_levels,
            "igd_plus_mean_levels": igd_levels, "hv_per_seed": per_seed,
            "spearman_tau_hv": float(rho_hv), "spearman_tau_hv_p": float(p_hv),
            "spearman_tau_igd": float(rho_igd), "spearman_tau_igd_p": float(p_igd),
            "random_mean": rand[sname], "crossing_tau": crossing,
            "above_random_at_all_levels": above_all,
            "pooled_ref_size": len(Z),
        }
        print(f"== {sname}: Spearman(tau,HV)={rho_hv:.3f} (p={p_hv:.4f}) | "
              f"Spearman(tau,IGD+)={rho_igd:.3f} | crossing tau={crossing} | "
              f"above_random_all={above_all}", flush=True)
    # verdicts
    st = out["structures"]
    out["verdict"] = {
        "R1_visa": {"holds": bool(st["visa"]["spearman_tau_hv"] <= -0.8 and st["visa"]["crossing_tau"] is not None)},
        "R1_knapsack": {"holds": bool(st["knapsack"]["spearman_tau_hv"] <= -0.8 and st["knapsack"]["crossing_tau"] is not None)},
        "R2_tsp": {"holds": st["tsp"]["above_random_at_all_levels"]},
        "R2_flowshop": {"holds": st["flowshop"]["above_random_at_all_levels"]},
        "R2_scp": {"holds": st["scp"]["above_random_at_all_levels"]},
        "R3_igd_agrees": {"holds": bool(all(
            abs(st[s]["spearman_tau_igd"]) >= 0.6 and
            st[s]["spearman_tau_igd"] * st[s]["spearman_tau_hv"] < 0
            for s in st))},
    }
    out["elapsed_s"] = time.time() - t0
    json.dump(out, open(RESULTS / "rho_sweep.json", "w"), indent=2)
    for k, v in out["verdict"].items():
        print(k, "HOLDS" if v["holds"] else "FAILS")
    print(f"total {out['elapsed_s']:.0f}s -> rho_sweep.json")


if __name__ == "__main__":
    main()
