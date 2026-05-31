"""
SUPERPROMPT v2 - Ladder de 6 metodos parametrizado por DECODER (Exp C).

Los seis metodos del paper, reimplementados para aceptar cualquier Decoder
(greedy / C1 fractional / C2 stochastic-skip) bajo el MISMO presupuesto de 25,000
evaluaciones y la MISMA instancia base. Dos representaciones:

  random-key tier  (genome = vec en [0,1]^rk_dim):  rk_random_restart, rk_nsga2, rk_mohho
  permutation tier (genome = (perm, aux en [0,1]^105)): perm_nsga2, perm_moead, discrete_mohho

Con decoder=greedy y uses_aux=False, las versiones permutacionales ignoran aux y
reproducen los metodos publicados (validacion). Con C1/C2 (uses_aux=True) los
metodos permutacionales co-evolucionan el vector aux con operadores reales (SBX +
mutacion gaussiana para los GA/decomposition; blend hacia el lider para el swarm).
"""
import numpy as np

from app.core.config import NUM_GROUPS, LB, UB, POPULATION_SIZE, MAX_ITERATIONS
from app.core.hho import (
    escape_energy, op1_exploration_random, op2_exploration_mean,
    op3_soft_siege, op4_hard_siege, op5_soft_siege_levy, op6_hard_siege_levy,
)
from perm_nsga import ox as perm_ox
from discrete_mohho import ox as d_ox, nswaps as d_nswaps, reverse_seg as d_reverse

POP, GEN = POPULATION_SIZE, MAX_ITERATIONS     # 50, 500
BUDGET = POP * GEN                             # 25,000


# ============================ archive (M=3) ============================
def dominates3(a, b):
    return (a[0] <= b[0] and a[1] <= b[1] and a[2] <= b[2]) and \
           (a[0] < b[0] or a[1] < b[1] or a[2] < b[2])


def crowding3(F):
    n = len(F)
    if n <= 2:
        return [float("inf")] * n
    d = [0.0] * n
    for m in range(3):
        order = sorted(range(n), key=lambda i: F[i][m])
        d[order[0]] = d[order[-1]] = float("inf")
        lo, hi = F[order[0]][m], F[order[-1]][m]
        span = hi - lo
        if span == 0:
            continue
        for k in range(1, n - 1):
            d[order[k]] += (F[order[k + 1]][m] - F[order[k - 1]][m]) / span
    return d


def arch_add(ax, af, x, f, cap, rng):
    for g in af:
        if abs(g[0] - f[0]) < 1e-12 and abs(g[1] - f[1]) < 1e-12 and abs(g[2] - f[2]) < 1e-12:
            return
    for g in af:
        if dominates3(g, f):
            return
    keep = [i for i, g in enumerate(af) if not dominates3(f, g)]
    ax[:] = [ax[i] for i in keep]
    af[:] = [af[i] for i in keep]
    ax.append(x)
    af.append(f)
    if len(af) > cap:
        cd = crowding3(af)
        fin = [i for i in range(len(cd)) if cd[i] != float("inf")]
        drop = min(fin, key=lambda i: cd[i]) if fin else int(rng.integers(len(af)))
        ax.pop(drop)
        af.pop(drop)


def leader(ax, af, rng):
    cd = crowding3(af)
    w = np.array([1e6 if d == float("inf") else d for d in cd])
    if w.sum() == 0:
        return ax[rng.integers(len(ax))]
    return ax[rng.choice(len(ax), p=w / w.sum())]


ARCH = 100


# ============================ real operators ============================
def sbx_gen(p1, p2, rng, eta=20.0):
    c1, c2 = p1.copy(), p2.copy()
    for i in range(len(p1)):
        if rng.random() <= 0.5 and abs(p1[i] - p2[i]) > 1e-12:
            u = rng.random()
            beta = (2 * u) ** (1 / (eta + 1)) if u <= 0.5 else (1 / (2 * (1 - u))) ** (1 / (eta + 1))
            c1[i] = 0.5 * ((1 + beta) * p1[i] + (1 - beta) * p2[i])
            c2[i] = 0.5 * ((1 - beta) * p1[i] + (1 + beta) * p2[i])
    return np.clip(c1, LB, UB), np.clip(c2, LB, UB)


def polymut_gen(x, rng, pm, eta=20.0):
    y = x.copy()
    for i in range(len(x)):
        if rng.random() < pm:
            u = rng.random()
            delta = (2 * u) ** (1 / (eta + 1)) - 1 if u < 0.5 else 1 - (2 * (1 - u)) ** (1 / (eta + 1))
            y[i] = x[i] + delta * (UB - LB)
    return np.clip(y, LB, UB)


def tournament2(rank, cd, rng):
    a, b = rng.integers(0, len(rank), size=2)
    if rank[a] < rank[b]:
        return a
    if rank[b] < rank[a]:
        return b
    return a if cd[a] >= cd[b] else b


def fnd_sort3(fits):
    n = len(fits)
    S = [[] for _ in range(n)]
    nd = [0] * n
    fronts = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if dominates3(fits[p], fits[q]):
                S[p].append(q)
            elif dominates3(fits[q], fits[p]):
                nd[p] += 1
        if nd[p] == 0:
            fronts[0].append(p)
    rank = [0] * n
    i = 0
    while fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in S[p]:
                nd[q] -= 1
                if nd[q] == 0:
                    rank[q] = i + 1
                    nxt.append(q)
        i += 1
        fronts.append(nxt)
    fronts.pop()
    return fronts, rank


# ============================ random-key methods ============================
def rk_random_restart(decoder, problem, seed):
    rng = np.random.default_rng(seed)
    ax, af = [], []
    for _ in range(BUDGET):
        v = rng.uniform(LB, UB, decoder.rk_dim)
        f = problem.evaluate(decoder.decode_rk(v, problem))
        arch_add(ax, af, v, f, ARCH, rng)
    return af


def rk_nsga2(decoder, problem, seed):
    rng = np.random.default_rng(seed)
    d = decoder.rk_dim
    pm = 1.0 / d
    px = rng.uniform(LB, UB, (POP, d))
    fits = [problem.evaluate(decoder.decode_rk(px[i], problem)) for i in range(POP)]
    for _ in range(GEN):
        fronts, rank = fnd_sort3(fits)
        cd = [0.0] * POP
        for fr in fronts:
            dd = crowding3([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = dd[k]
        off = []
        while len(off) < POP:
            p1 = px[tournament2(rank, cd, rng)]
            p2 = px[tournament2(rank, cd, rng)]
            if rng.random() <= 0.9:
                c1, c2 = sbx_gen(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            off.append(polymut_gen(c1, rng, pm))
            if len(off) < POP:
                off.append(polymut_gen(c2, rng, pm))
        off = np.array(off)
        ofits = [problem.evaluate(decoder.decode_rk(off[i], problem)) for i in range(POP)]
        comb = np.vstack([px, off])
        cfits = fits + ofits
        fronts, _ = fnd_sort3(cfits)
        new = []
        for fr in fronts:
            if len(new) + len(fr) <= POP:
                new += fr
            else:
                dd = crowding3([cfits[i] for i in fr])
                order = sorted(range(len(fr)), key=lambda k: dd[k], reverse=True)
                new += [fr[k] for k in order[:POP - len(new)]]
                break
        px = comb[new]
        fits = [cfits[i] for i in new]
    fronts, _ = fnd_sort3(fits)
    return [fits[i] for i in fronts[0]]


def rk_mohho(decoder, problem, seed):
    rng = np.random.default_rng(seed)
    d = decoder.rk_dim
    px = rng.uniform(LB, UB, (POP, d))
    fits = [problem.evaluate(decoder.decode_rk(px[i], problem)) for i in range(POP)]
    ax, af = [], []
    for i in range(POP):
        arch_add(ax, af, px[i].copy(), fits[i], ARCH, rng)
    for t in range(GEN):
        x_mean = px.mean(axis=0)
        for i in range(POP):
            e = escape_energy(t, GEN, rng)
            absE = abs(e)
            rabbit = leader(ax, af, rng)
            if absE >= 1:
                if rng.random() >= 0.5:
                    j = rng.integers(POP)
                    new = op1_exploration_random(px[i], px[j], rng)
                else:
                    new = op2_exploration_mean(px[i], rabbit, x_mean, rng)
            elif rng.random() >= 0.5:
                new = (op3_soft_siege(px[i], rabbit, e, rng) if absE >= 0.5
                       else op4_hard_siege(px[i], rabbit, e, rng))
            else:
                if absE >= 0.5:
                    new, _z = op5_soft_siege_levy(px[i], rabbit, e, rng)
                else:
                    new, _z = op6_hard_siege_levy(px[i], rabbit, e, x_mean, rng)
            fnew = problem.evaluate(decoder.decode_rk(new, problem))
            if dominates3(fnew, fits[i]):
                px[i] = new
                fits[i] = fnew
            arch_add(ax, af, new.copy(), fnew, ARCH, rng)
    return af


# ============================ permutation methods ============================
def _rand_genome(decoder, rng):
    perm = rng.permutation(NUM_GROUPS)
    aux = rng.random(NUM_GROUPS) if decoder.uses_aux else None
    return perm, aux


def _eval_perm(decoder, perm, aux, problem):
    return problem.evaluate(decoder.decode_perm(perm, aux, problem))


def _aux_cross(a1, a2, rng):
    if a1 is None:
        return None, None
    return sbx_gen(a1, a2, rng)


def _aux_mut(a, rng, pm=None):
    if a is None:
        return None
    pm = pm if pm is not None else 1.0 / NUM_GROUPS
    return polymut_gen(a, rng, pm)


def perm_nsga2(decoder, problem, seed):
    rng = np.random.default_rng(seed)
    P = [_rand_genome(decoder, rng) for _ in range(POP)]
    fits = [_eval_perm(decoder, p[0], p[1], problem) for p in P]
    for _ in range(GEN):
        fronts, rank = fnd_sort3(fits)
        cd = [0.0] * POP
        for fr in fronts:
            dd = crowding3([fits[i] for i in fr])
            for k, idx in enumerate(fr):
                cd[idx] = dd[k]
        off = []
        while len(off) < POP:
            i1, i2 = tournament2(rank, cd, rng), tournament2(rank, cd, rng)
            (pa, aa), (pb, ab) = P[i1], P[i2]
            ca = perm_ox(pa, pb, rng)
            cb = perm_ox(pb, pa, rng)
            if decoder.uses_aux:
                na, nb = _aux_cross(aa, ab, rng)
                na, nb = _aux_mut(na, rng), _aux_mut(nb, rng)
            else:
                na = nb = None
            ca = _swap(ca, rng)
            cb = _swap(cb, rng)
            off.append((ca, na))
            if len(off) < POP:
                off.append((cb, nb))
        ofits = [_eval_perm(decoder, o[0], o[1], problem) for o in off]
        comb = P + off
        cfits = fits + ofits
        fronts, _ = fnd_sort3(cfits)
        new = []
        for fr in fronts:
            if len(new) + len(fr) <= POP:
                new += fr
            else:
                dd = crowding3([cfits[i] for i in fr])
                order = sorted(range(len(fr)), key=lambda k: dd[k], reverse=True)
                new += [fr[k] for k in order[:POP - len(new)]]
                break
        P = [comb[i] for i in new]
        fits = [cfits[i] for i in new]
    fronts, _ = fnd_sort3(fits)
    return [fits[i] for i in fronts[0]]


def _swap(perm, rng, pm=0.3):
    y = perm.copy()
    if rng.random() < pm:
        for _ in range(rng.integers(1, 4)):
            i, j = rng.integers(0, len(y), size=2)
            y[i], y[j] = y[j], y[i]
    return y


def perm_moead(decoder, problem, seed, H=13, T=10):
    rng = np.random.default_rng(seed)
    # simplex lattice weights for 3 objectives
    W = []
    for a in range(H + 1):
        for b in range(H + 1 - a):
            W.append([a, b, H - a - b])
    W = np.array(W, float) / H
    N = len(W)
    gens = max(1, BUDGET // N)
    B = [np.argsort(np.linalg.norm(W - W[i], axis=1))[:T] for i in range(N)]
    P = [_rand_genome(decoder, rng) for _ in range(N)]
    fit = [np.array(_eval_perm(decoder, p[0], p[1], problem)) for p in P]
    scale = np.array([10.0, 16.0, 20000.0])
    fn = [f / scale for f in fit]
    z = np.min(np.array(fn), axis=0)
    ax, af = [], []
    for i in range(N):
        arch_add(ax, af, P[i], tuple(fit[i]), ARCH, rng)
    for _ in range(gens):
        for i in range(N):
            k, l = rng.choice(B[i], 2, replace=False)
            (pk, ak), (pl, al) = P[k], P[l]
            child_p = _swap(perm_ox(pk, pl, rng), rng)
            if decoder.uses_aux:
                ca, _cb = _aux_cross(ak, al, rng)
                child_a = _aux_mut(ca, rng)
            else:
                child_a = None
            cf = np.array(_eval_perm(decoder, child_p, child_a, problem))
            cfn = cf / scale
            z = np.minimum(z, cfn)
            for j in B[i]:
                if np.max(W[j] * (cfn - z)) <= np.max(W[j] * (fn[j] - z)):
                    P[j] = (child_p, child_a)
                    fit[j] = cf
                    fn[j] = cfn
            arch_add(ax, af, (child_p, child_a), tuple(cf), ARCH, rng)
    return af


def discrete_mohho(decoder, problem, seed):
    rng = np.random.default_rng(seed)
    P = [_rand_genome(decoder, rng) for _ in range(POP)]
    fits = [_eval_perm(decoder, p[0], p[1], problem) for p in P]
    ax, af = [], []
    for i in range(POP):
        arch_add(ax, af, P[i], fits[i], ARCH, rng)
    for t in range(GEN):
        for i in range(POP):
            e = 2 * (2 * rng.random() - 1) * (1 - t / GEN)
            absE = abs(e)
            rab = leader(ax, af, rng)
            rab_perm, rab_aux = rab
            pi, ai = P[i]
            if absE >= 1:
                if rng.random() < 0.5:
                    j = rng.integers(POP)
                    cp = d_ox(P[j][0], rab_perm, rng)
                else:
                    cp = d_nswaps(pi, int(rng.integers(NUM_GROUPS // 4, NUM_GROUPS // 2)), rng)
            else:
                cp = d_ox(rab_perm, pi, rng)
                k = max(1, int(round(absE * (NUM_GROUPS // 6))))
                cp = d_nswaps(cp, k, rng)
                if rng.random() < 0.5:
                    cp = d_reverse(cp, rng)
            if decoder.uses_aux:
                # blend toward rabbit's aux with energy-scaled gaussian perturbation
                blend = (1 - absE) * np.asarray(rab_aux) + absE * np.asarray(ai)
                ca = np.clip(blend + rng.normal(0, 0.1 * absE, NUM_GROUPS), LB, UB)
            else:
                ca = None
            cf = _eval_perm(decoder, cp, ca, problem)
            arch_add(ax, af, (cp, ca), cf, ARCH, rng)
            if dominates3(cf, fits[i]):
                P[i] = (cp, ca)
                fits[i] = cf
    return af


RUNNERS = {
    "rk_random_restart": rk_random_restart,
    "rk_nsga2": rk_nsga2,
    "rk_mohho": rk_mohho,
    "perm_nsga2": perm_nsga2,
    "perm_moead": perm_moead,
    "discrete_mohho": discrete_mohho,
}
TIER = {
    "rk_random_restart": "random_key", "rk_nsga2": "random_key", "rk_mohho": "random_key",
    "perm_nsga2": "permutation", "perm_moead": "permutation", "discrete_mohho": "permutation",
}
