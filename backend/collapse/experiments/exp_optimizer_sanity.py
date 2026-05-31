"""
SUPERPROMPT v2 - Experimento A: gate de sanidad de los optimizers (Seccion 3).

Que random restart (combined HV) compita con MOHHO real-coded es una bandera roja.
Antes de atribuir nada al decoder hay que descartar que un optimizer este ROTO.

  (1) MOHHO real-coded sobre ZDT1, ZDT2, DTLZ2 vs NSGA-II canonico. Se compara el
      HV alcanzado contra el HV del frente VERDADERO analitico (mismo estimador de
      HV) -> ceiling honesto. Si MOHHO no recupera frentes conocidos donde DEBERIA,
      esta mal implementado.
  (2) perm-NSGA-II (OX+swap) y Discrete-MOHHO (energy-besiege) -- los MISMOS
      operadores del paper -- sobre un TSP mono-objetivo de juguete con optimo
      conocido (10 ciudades en circulo). Si no se acercan al optimo, los operadores
      permutacionales estan rotos.
  (3) random restart sobre el visa: confirmar que NO hace busqueda (solo
      muestrea+decodifica+archiva), descartando busqueda local oculta.

Veredicto por optimizer: sano | sospechoso | roto.
Salida: app/data/results/expA_optimizer_sanity.json

Ejecutar desde backend/:  python3 -m collapse.experiments.exp_optimizer_sanity
"""
import inspect
import json
import time
from pathlib import Path

import numpy as np

from app.core.hho import (
    escape_energy,
    op1_exploration_random, op2_exploration_mean,
    op3_soft_siege, op4_hard_siege,
    op5_soft_siege_levy, op6_hard_siege_levy,
)
from compare_nsga2 import sbx, poly_mutate, tournament
from perm_nsga import ox as perm_ox, PM as PERM_PM
from discrete_mohho import ox as d_ox, nswaps as d_nswaps, reverse_seg as d_reverse

RESULTS = Path("app/data/results")
SEED_BASE = 1                      # benchmarks nuevos: seed base 1 documentado


# =====================================================================
#  Helpers multi-objetivo genericos (M objetivos)
# =====================================================================
def dominates_m(a, b):
    le = all(a[k] <= b[k] for k in range(len(a)))
    lt = any(a[k] < b[k] for k in range(len(a)))
    return le and lt


def crowding_m(F):
    n = len(F)
    if n <= 2:
        return [float("inf")] * n
    M = len(F[0])
    dist = [0.0] * n
    for m in range(M):
        order = sorted(range(n), key=lambda i: F[i][m])
        dist[order[0]] = dist[order[-1]] = float("inf")
        lo, hi = F[order[0]][m], F[order[-1]][m]
        span = hi - lo
        if span == 0:
            continue
        for k in range(1, n - 1):
            dist[order[k]] += (F[order[k + 1]][m] - F[order[k - 1]][m]) / span
    return dist


def archive_add(arc_x, arc_f, x, f, cap):
    for af in arc_f:
        if all(abs(af[k] - f[k]) < 1e-12 for k in range(len(f))):
            return
    for af in arc_f:
        if dominates_m(af, f):
            return
    keep = [i for i, af in enumerate(arc_f) if not dominates_m(f, af)]
    arc_x[:] = [arc_x[i] for i in keep]
    arc_f[:] = [arc_f[i] for i in keep]
    arc_x.append(np.asarray(x).copy())
    arc_f.append(tuple(f))
    if len(arc_f) > cap:
        cd = crowding_m(arc_f)
        fin = [i for i in range(len(cd)) if cd[i] != float("inf")]
        drop = min(fin, key=lambda i: cd[i]) if fin else 0
        arc_x.pop(drop)
        arc_f.pop(drop)


def hv2d(front, ref):
    """Exact 2D dominated hypervolume (minimization; ref = upper bound)."""
    pts = [p for p in front if p[0] < ref[0] and p[1] < ref[1]]
    if not pts:
        return 0.0
    pts = sorted(set((p[0], p[1]) for p in pts))      # ascending f1, then f2
    nd = []                                           # nondominated staircase
    best_y = float("inf")
    for x, y in pts:
        if y < best_y:
            nd.append((x, y))
            best_y = y
    hv = 0.0
    for i, (x, y) in enumerate(nd):
        x_next = nd[i + 1][0] if i + 1 < len(nd) else ref[0]
        hv += (x_next - x) * (ref[1] - y)
    return hv


def hv3d(front, ref):
    pts = [p for p in front if all(p[k] < ref[k] for k in range(3))]
    if not pts:
        return 0.0
    pts.sort(key=lambda p: p[0])

    def _hv2(slab, r2):
        s = sorted(slab, key=lambda p: p[0])
        h = 0.0
        prev = r2[1]
        for a, b in s:
            if a < r2[0] and b < prev:
                h += (r2[0] - a) * (prev - b)
                prev = b
        return h

    hv = 0.0
    for i, p in enumerate(pts):
        nx = pts[i + 1][0] if i + 1 < len(pts) else ref[0]
        slab = [(q[1], q[2]) for q in pts[:i + 1]]
        hv += (nx - p[0]) * _hv2(slab, (ref[1], ref[2]))
    return hv


# =====================================================================
#  Benchmarks continuos
# =====================================================================
def zdt1(x):
    n = len(x)
    f1 = x[0]
    g = 1 + 9 * np.sum(x[1:]) / (n - 1)
    f2 = g * (1 - np.sqrt(f1 / g))
    return (float(f1), float(f2))


def zdt2(x):
    n = len(x)
    f1 = x[0]
    g = 1 + 9 * np.sum(x[1:]) / (n - 1)
    f2 = g * (1 - (f1 / g) ** 2)
    return (float(f1), float(f2))


def dtlz2(x):
    M = 3
    k = len(x) - M + 1
    xm = x[M - 1:]
    g = float(np.sum((xm - 0.5) ** 2))
    f1 = (1 + g) * np.cos(x[0] * np.pi / 2) * np.cos(x[1] * np.pi / 2)
    f2 = (1 + g) * np.cos(x[0] * np.pi / 2) * np.sin(x[1] * np.pi / 2)
    f3 = (1 + g) * np.sin(x[0] * np.pi / 2)
    return (float(f1), float(f2), float(f3))


BENCH = {
    "ZDT1": {"fn": zdt1, "n": 30, "M": 2, "ref": (1.1, 1.1)},
    "ZDT2": {"fn": zdt2, "n": 30, "M": 2, "ref": (1.1, 1.1)},
    "DTLZ2": {"fn": dtlz2, "n": 12, "M": 3, "ref": (1.1, 1.1, 1.1)},
}


def true_front_hv(name):
    cfg = BENCH[name]
    if name == "ZDT1":
        f1 = np.linspace(0, 1, 4000)
        front = [(a, 1 - np.sqrt(a)) for a in f1]
        return hv2d(front, cfg["ref"])
    if name == "ZDT2":
        f1 = np.linspace(0, 1, 4000)
        front = [(a, 1 - a ** 2) for a in f1]
        return hv2d(front, cfg["ref"])
    if name == "DTLZ2":
        # dense sample of the unit-sphere octant
        rng = np.random.default_rng(0)
        th = rng.uniform(0, np.pi / 2, 60000)
        ph = rng.uniform(0, np.pi / 2, 60000)
        front = [(float(np.sin(t) * np.cos(p)),
                  float(np.sin(t) * np.sin(p)),
                  float(np.cos(t))) for t, p in zip(th, ph)]
        return hv3d(front, cfg["ref"])


# ---- generic real-coded MOHHO (mismas op. de app.core.hho) ----
def mohho_continuous(fn, n, M, ref, seed, pop=100, gen=250, cap=100):
    rng = np.random.default_rng(seed)
    pop_x = rng.random((pop, n))
    fits = [fn(pop_x[i]) for i in range(pop)]
    arc_x, arc_f = [], []
    for i in range(pop):
        archive_add(arc_x, arc_f, pop_x[i], fits[i], cap)

    def leader():
        cd = crowding_m(arc_f)
        w = np.array([1e6 if d == float("inf") else d for d in cd])
        if w.sum() == 0:
            return arc_x[rng.integers(len(arc_x))]
        return arc_x[rng.choice(len(arc_x), p=w / w.sum())]

    for t in range(gen):
        x_mean = pop_x.mean(axis=0)
        for i in range(pop):
            e = escape_energy(t, gen, rng)
            absE = abs(e)
            rabbit = leader()
            if absE >= 1:
                if rng.random() >= 0.5:
                    j = rng.integers(pop)
                    new = op1_exploration_random(pop_x[i], pop_x[j], rng)
                else:
                    new = op2_exploration_mean(pop_x[i], rabbit, x_mean, rng)
                cands = [new]
            elif rng.random() >= 0.5:
                new = (op3_soft_siege(pop_x[i], rabbit, e, rng) if absE >= 0.5
                       else op4_hard_siege(pop_x[i], rabbit, e, rng))
                cands = [new]
            else:
                if absE >= 0.5:
                    y, _z = op5_soft_siege_levy(pop_x[i], rabbit, e, rng)
                else:
                    y, _z = op6_hard_siege_levy(pop_x[i], rabbit, e, x_mean, rng)
                cands = [y]            # FE-parity: one trial point per hawk
            new = cands[0]
            fnew = fn(new)
            if dominates_m(fnew, fits[i]):
                pop_x[i] = new
                fits[i] = fnew
            for c in cands:
                archive_add(arc_x, arc_f, c, fn(c), cap)
    return arc_f


# ---- canonical NSGA-II (mismas op. de compare_nsga2) ----
def nsga2_continuous(fn, n, M, ref, seed, pop=100, gen=250):
    rng = np.random.default_rng(seed)

    def fnd_sort(fits):
        N = len(fits)
        S = [[] for _ in range(N)]
        ndom = [0] * N
        fronts = [[]]
        for p in range(N):
            for q in range(N):
                if p == q:
                    continue
                if dominates_m(fits[p], fits[q]):
                    S[p].append(q)
                elif dominates_m(fits[q], fits[p]):
                    ndom[p] += 1
            if ndom[p] == 0:
                fronts[0].append(p)
        rank = [0] * N
        i = 0
        while fronts[i]:
            nxt = []
            for p in fronts[i]:
                for q in S[p]:
                    ndom[q] -= 1
                    if ndom[q] == 0:
                        rank[q] = i + 1
                        nxt.append(q)
            i += 1
            fronts.append(nxt)
        fronts.pop()
        return fronts, rank

    pm = 1.0 / n          # proper per-variable mutation rate for this benchmark dim

    def polymut(x, eta=20.0):
        y = x.copy()
        for i in range(n):
            if rng.random() < pm:
                u = rng.random()
                delta = ((2 * u) ** (1 / (eta + 1)) - 1 if u < 0.5
                         else 1 - (2 * (1 - u)) ** (1 / (eta + 1)))
                y[i] = x[i] + delta
        return np.clip(y, 0.0, 1.0)

    px = rng.random((pop, n))
    fits = [fn(px[i]) for i in range(pop)]
    for _ in range(gen):
        fronts, rank = fnd_sort(fits)
        cd = [0.0] * pop
        for fr in fronts:
            d = crowding_m([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = d[k]
        off = []
        while len(off) < pop:
            p1 = px[tournament(rank, cd, rng)]
            p2 = px[tournament(rank, cd, rng)]
            if rng.random() <= 0.9:
                c1, c2 = sbx(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            off.append(polymut(c1))
            if len(off) < pop:
                off.append(polymut(c2))
        off = np.array(off)
        ofits = [fn(off[i]) for i in range(pop)]
        comb = np.vstack([px, off])
        cfits = fits + ofits
        fronts, _ = fnd_sort(cfits)
        new_idx = []
        for fr in fronts:
            if len(new_idx) + len(fr) <= pop:
                new_idx += fr
            else:
                d = crowding_m([cfits[i] for i in fr])
                order = sorted(range(len(fr)), key=lambda k: d[k], reverse=True)
                new_idx += [fr[k] for k in order[:pop - len(new_idx)]]
                break
        px = comb[new_idx]
        fits = [cfits[i] for i in new_idx]
    fronts, _ = fnd_sort(fits)
    return [fits[i] for i in fronts[0]]


def run_continuous_block(seeds=(1, 2, 3), pop=100, gen=500):
    # Budget generoso (50k evals) para un chequeo de convergencia INEQUIVOCO: el
    # gate evalua correctitud de implementacion, no el presupuesto-visa. ZDT de 30
    # variables converge lento con SBX+poly; a 25k ambos metodos quedan a media
    # convergencia (es un artefacto de budget, no de implementacion).
    block = {"_meta": {"budget_evals": pop * gen, "pop": pop, "gen": gen, "seeds": list(seeds)}}
    for name in BENCH:
        cfg = BENCH[name]
        hv_fn = hv2d if cfg["M"] == 2 else hv3d
        true_hv = true_front_hv(name)
        mh, ng = [], []
        for s in seeds:
            af = mohho_continuous(cfg["fn"], cfg["n"], cfg["M"], cfg["ref"], s,
                                  pop=pop, gen=gen)
            mh.append(hv_fn(af, cfg["ref"]))
            nf = nsga2_continuous(cfg["fn"], cfg["n"], cfg["M"], cfg["ref"], s,
                                  pop=pop, gen=gen)
            ng.append(hv_fn(nf, cfg["ref"]))
        mh_mean = float(np.mean(mh))
        ng_mean = float(np.mean(ng))
        ratio_true = mh_mean / true_hv if true_hv else 0.0
        ratio_nsga = mh_mean / ng_mean if ng_mean else 0.0
        nsga_over_true = ng_mean / true_hv if true_hv else 0.0
        # MOHHO verdict is anchored to recovery of the KNOWN true front, NOT to the
        # NSGA reference (NSGA may itself be the weaker method on a given benchmark).
        if ratio_true >= 0.85:
            verdict = "sano"
        elif ratio_true >= 0.60:
            verdict = "sospechoso"
        else:
            verdict = "roto"
        nsga_self = "sano" if nsga_over_true >= 0.70 else (
            "sospechoso" if nsga_over_true >= 0.40 else "debil")
        block[name] = {
            "M": cfg["M"], "n": cfg["n"], "ref": list(cfg["ref"]),
            "true_front_hv": true_hv,
            "mohho_hv_mean": mh_mean, "nsga2_hv_mean": ng_mean,
            "mohho_per_seed": mh, "nsga2_per_seed": ng,
            "mohho_over_true": ratio_true, "nsga2_over_true": nsga_over_true,
            "mohho_over_nsga2": ratio_nsga,
            "veredicto_mohho_realcoded": verdict,
            "nsga2_self_check": nsga_self,
        }
        print(f"  {name}: MOHHO/true={ratio_true:.3f} ({verdict}) | "
              f"NSGA/true={nsga_over_true:.3f} ({nsga_self}) | MOHHO/NSGA={ratio_nsga:.2f}")
    return block


# =====================================================================
#  TSP mono-objetivo de juguete (optimo conocido)
# =====================================================================
def circle_tsp(ncity=10, radius=1.0):
    ang = np.linspace(0, 2 * np.pi, ncity, endpoint=False)
    coords = np.stack([radius * np.cos(ang), radius * np.sin(ang)], axis=1)
    D = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
    opt = 2 * ncity * radius * np.sin(np.pi / ncity)   # convex polygon perimeter
    return D, opt


def tour_len(perm, D):
    return float(sum(D[perm[i], perm[(i + 1) % len(perm)]] for i in range(len(perm))))


def perm_ea_tsp(D, seed, pop=50, gen=300):
    """Single-objective EA with perm-NSGA-II operators (OX + swap)."""
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    P = [rng.permutation(n) for _ in range(pop)]
    f = [tour_len(p, D) for p in P]
    best = min(f)
    for _ in range(gen):
        order = np.argsort(f)
        elite = [P[i] for i in order[:max(2, pop // 5)]]
        newP = list(elite)
        while len(newP) < pop:
            a = elite[rng.integers(len(elite))]
            b = P[rng.integers(pop)]
            child = perm_ox(a, b, rng)
            if rng.random() < 0.6:
                for _ in range(rng.integers(1, 4)):
                    i, j = rng.integers(0, n, size=2)
                    child[i], child[j] = child[j], child[i]
            newP.append(child)
        P = newP
        f = [tour_len(p, D) for p in P]
        best = min(best, min(f))
    return best


def discrete_mohho_tsp(D, seed, pop=50, gen=300):
    """Single-objective TSP driven by Discrete-MOHHO permutation moves."""
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    P = [rng.permutation(n) for _ in range(pop)]
    f = [tour_len(p, D) for p in P]
    best_i = int(np.argmin(f))
    rabbit = P[best_i].copy()
    best = f[best_i]
    for t in range(gen):
        for i in range(pop):
            e = 2 * (2 * rng.random() - 1) * (1 - t / gen)
            absE = abs(e)
            if absE >= 1:
                if rng.random() < 0.5:
                    j = rng.integers(pop)
                    child = d_ox(P[j], rabbit, rng)
                else:
                    child = d_nswaps(P[i], int(rng.integers(max(2, n // 4),
                                                            max(3, n // 2))), rng)
            else:
                child = d_ox(rabbit, P[i], rng)
                k = max(1, int(round(absE * (n // 6 + 1))))
                child = d_nswaps(child, k, rng)
                if rng.random() < 0.5:
                    child = d_reverse(child, rng)
            fc = tour_len(child, D)
            if fc < f[i]:
                P[i] = child
                f[i] = fc
            if fc < best:
                best = fc
                rabbit = child.copy()
    return best


def run_tsp_block(seeds=(1, 2, 3, 4, 5)):
    D, opt = circle_tsp(10)
    block = {"ncity": 10, "known_optimum": opt}
    for label, fn in [("perm_nsga2_ops", perm_ea_tsp),
                      ("discrete_mohho_ops", discrete_mohho_tsp)]:
        bests = [fn(D, s) for s in seeds]
        bmean = float(np.mean(bests))
        bmin = float(np.min(bests))
        gap_mean = (bmean - opt) / opt
        gap_min = (bmin - opt) / opt
        verdict = "sano" if gap_min <= 0.02 and gap_mean <= 0.05 else (
            "sospechoso" if gap_min <= 0.10 else "roto")
        block[label] = {
            "best_per_seed": bests, "best_mean": bmean, "best_min": bmin,
            "gap_mean_vs_opt": gap_mean, "gap_min_vs_opt": gap_min,
            "veredicto": verdict,
        }
        print(f"  TSP {label}: best_min={bmin:.4f} opt={opt:.4f} "
              f"gap_min={gap_min*100:.2f}% gap_mean={gap_mean*100:.2f}% -> {verdict}")
    return block


def random_restart_check():
    """Confirma que random restart solo muestrea+decodifica+archiva (sin busqueda)."""
    from controls import run_random
    src = inspect.getsource(run_random)
    has_operators = any(tok in src for tok in ["op1", "op2", "sbx", "ox(", "swap",
                                               "local", "2-opt", "neighbor"])
    has_population_dynamics = "pop[" in src or "x_mean" in src
    controls = json.load(open(RESULTS / "controls.json"))
    return {
        "source_does_search": has_operators or has_population_dynamics,
        "mechanism": ("draw uniform random keys -> SPV -> greedy decode -> "
                      "crowding-pruned archive. No operators, no population "
                      "dynamics, no local search."),
        "combined_front_hv": controls["random_restart"]["combined_front_hv"],
        "combined_front_size": controls["random_restart"]["combined_front_size"],
        "veredicto": "confirmado_muestreo_puro" if not (
            has_operators or has_population_dynamics) else "REVISAR",
    }


def main():
    t0 = time.time()
    print("== Exp A: continuous benchmarks (MOHHO real-coded vs NSGA-II) ==")
    cont = run_continuous_block()
    print("== Exp A: toy TSP (permutation operators) ==")
    tsp = run_tsp_block()
    print("== Exp A: random restart structural check ==")
    rr = random_restart_check()
    print(f"  random restart: {rr['veredicto']} (HV {rr['combined_front_hv']:,.0f})")

    realcoded_verdicts = [v["veredicto_mohho_realcoded"] for k, v in cont.items()
                          if k != "_meta"]
    mohho_overall = ("roto" if realcoded_verdicts.count("roto") >= 2 else
                     "sospechoso" if "roto" in realcoded_verdicts
                     or realcoded_verdicts.count("sospechoso") >= 2 else "sano")
    perm_ok = (tsp["perm_nsga2_ops"]["veredicto"] != "roto" and
               tsp["discrete_mohho_ops"]["veredicto"] != "roto")

    out = {
        "seed_base": SEED_BASE,
        "continuous_benchmarks": cont,
        "toy_tsp": tsp,
        "random_restart": rr,
        "veredicto_global": {
            "mohho_realcoded": mohho_overall,
            "permutation_operators": "sano" if perm_ok else "roto",
            "random_restart": rr["veredicto"],
            "gate_passed": mohho_overall != "roto" and perm_ok,
            "implicacion": (
                "MOHHO real-coded recupera frentes conocidos con HV razonable y los "
                "operadores permutacionales alcanzan el optimo del TSP: el ladder NO "
                "esta contaminado por implementacion rota; el 'random restart "
                "competitivo' no es artefacto de codigo. Procede el diagnostico de "
                "colapso (Exp B/C/D)." if (mohho_overall != "roto" and perm_ok) else
                "Algun optimizer sale roto: el ladder queda en suspenso hasta "
                "re-implementar. Ver resumen ejecutivo."),
        },
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "expA_optimizer_sanity.json", "w"),
              indent=2, ensure_ascii=False)
    print(f"\nGATE passed: {out['veredicto_global']['gate_passed']} "
          f"(MOHHO {mohho_overall}, perm {'sano' if perm_ok else 'roto'}) "
          f"| {out['elapsed_s']:.0f}s -> expA_optimizer_sanity.json")


if __name__ == "__main__":
    main()
