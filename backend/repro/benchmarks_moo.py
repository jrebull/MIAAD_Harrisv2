"""
benchmarks_moo.py — Self-contained MO benchmarks (ZDT1, ZDT2, DTLZ2), exact HV,
a generalized MOHHO (reusing the REAL engine operators from app.core.hho) with a
SELECTABLE acceptance policy, and a compact NSGA-II reference.

Purpose: decide which MOHHO acceptance policy is SOUND (does not collapse on the
concave ZDT2 front), so the visa-ladder MOHHO can be repaired on a principled basis.

Run from the repo so that `import app.core...` resolves (see _bootstrap below).
"""
from __future__ import annotations
import os, sys
import numpy as np

# ---- bootstrap: locate backend/app/core regardless of CWD ----
def _bootstrap_engine():
    try:
        import app.core.hho  # noqa
        return
    except Exception:
        pass
    here = os.path.abspath(os.path.dirname(__file__))
    for up in range(0, 7):
        base = os.path.abspath(os.path.join(here, *([".."] * up))) if up else here
        cand = os.path.join(base, "backend")
        if os.path.isdir(os.path.join(cand, "app", "core")):
            sys.path.insert(0, cand); return
        if os.path.isdir(os.path.join(base, "app", "core")):
            sys.path.insert(0, base); return
    # last resort: common absolute path
    for p in ("/Users/haowei/Documents/MIAAD/SMART/Harris2/backend",
              "/home/claude/app"):
        if os.path.isdir(os.path.join(p, "app", "core")):
            sys.path.insert(0, p); return
    raise ImportError("No pude localizar backend/app/core. Corre desde el repo "
                      "o ajusta el bootstrap.")

_bootstrap_engine()
from app.core.hho import (  # REAL engine operators — diagnosis must use these
    escape_energy, op1_exploration_random, op2_exploration_mean,
    op3_soft_siege, op4_hard_siege, op5_soft_siege_levy, op6_hard_siege_levy,
)

# ============================ benchmark objectives ============================
def zdt1(x: np.ndarray):
    n = len(x); f1 = float(x[0])
    g = 1.0 + 9.0 * float(np.sum(x[1:])) / (n - 1)
    f2 = g * (1.0 - np.sqrt(f1 / g))
    return (f1, float(f2))

def zdt2(x: np.ndarray):
    n = len(x); f1 = float(x[0])
    g = 1.0 + 9.0 * float(np.sum(x[1:])) / (n - 1)
    f2 = g * (1.0 - (f1 / g) ** 2)
    return (f1, float(f2))

def dtlz2(x: np.ndarray, M: int = 3):
    n = len(x); k = n - M + 1
    xm = x[M - 1:]
    g = float(np.sum((xm - 0.5) ** 2))
    f = []
    for i in range(M):
        prod = (1.0 + g)
        for j in range(M - 1 - i):
            prod *= np.cos(x[j] * np.pi / 2.0)
        if i > 0:
            prod *= np.sin(x[M - 1 - i] * np.pi / 2.0)
        f.append(float(prod))
    return tuple(f)

BENCHMARKS = {
    "ZDT1": dict(fn=zdt1, dim=30, M=2, ref=(1.1, 1.1)),
    "ZDT2": dict(fn=zdt2, dim=30, M=2, ref=(1.1, 1.1)),
    "DTLZ2": dict(fn=lambda x: dtlz2(x, 3), dim=12, M=3, ref=(1.1, 1.1, 1.1)),
}

# ============================ exact hypervolume ===============================
def hv_2d(points, ref):
    pts = sorted((p for p in points if p[0] < ref[0] and p[1] < ref[1]),
                 key=lambda p: p[0])
    hv = 0.0; prev = ref[1]
    for f1, f2 in pts:
        if f2 < prev:
            hv += (ref[0] - f1) * (prev - f2); prev = f2
    return hv

def hv_3d(points, ref):
    pts = sorted((p for p in points if all(p[m] < ref[m] for m in range(3))),
                 key=lambda p: p[0])
    hv = 0.0
    for i, p in enumerate(pts):
        f1_next = pts[i + 1][0] if i + 1 < len(pts) else ref[0]
        w = f1_next - p[0]
        slice_pts = [(q[1], q[2]) for q in pts[: i + 1]]
        hv += w * hv_2d(slice_pts, (ref[1], ref[2]))
    return hv

def hv_any(points, ref):
    return hv_2d(points, ref) if len(ref) == 2 else hv_3d(points, ref)

def true_front_hv(name: str, n: int = 2000):
    b = BENCHMARKS[name]; ref = b["ref"]
    t = np.linspace(0, 1, n)
    if name == "ZDT1":
        pts = [(f, 1 - np.sqrt(f)) for f in t]
    elif name == "ZDT2":
        pts = [(f, 1 - f ** 2) for f in t]
    else:  # DTLZ2 sphere, first octant
        rng = np.random.default_rng(0)
        u = rng.random((n, 2))
        th = u[:, 0] * np.pi / 2; ph = u[:, 1] * np.pi / 2
        pts = [(np.cos(a) * np.cos(b2), np.cos(a) * np.sin(b2), np.sin(a))
               for a, b2 in zip(th, ph)]
    return hv_any(pts, ref)

# ============================ MO helpers (general M) ==========================
def dominates(a, b):
    return all(a[m] <= b[m] for m in range(len(a))) and any(a[m] < b[m] for m in range(len(a)))

def crowding(fits):
    n = len(fits)
    if n <= 2:
        return [float("inf")] * n
    M = len(fits[0]); dist = [0.0] * n
    for m in range(M):
        order = sorted(range(n), key=lambda i: fits[i][m])
        dist[order[0]] = dist[order[-1]] = float("inf")
        lo, hi = fits[order[0]][m], fits[order[-1]][m]
        span = hi - lo
        if span == 0:
            continue
        for k in range(1, n - 1):
            if dist[order[k]] != float("inf"):
                dist[order[k]] += (fits[order[k + 1]][m] - fits[order[k - 1]][m]) / span
    return dist

def archive_add(pos_list, fit_list, new_pos, new_fit, max_size, rng):
    for f in fit_list:
        if all(abs(f[m] - new_fit[m]) < 1e-12 for m in range(len(f))):
            return
    dom_by_new = []
    for i, f in enumerate(fit_list):
        if dominates(f, new_fit):
            return
        if dominates(new_fit, f):
            dom_by_new.append(i)
    for i in sorted(dom_by_new, reverse=True):
        pos_list.pop(i); fit_list.pop(i)
    pos_list.append(new_pos.copy()); fit_list.append(new_fit)
    if len(pos_list) > max_size:
        cd = crowding(fit_list)
        fin = [i for i in range(len(cd)) if cd[i] != float("inf")]
        j = min(fin, key=lambda i: cd[i]) if fin else 0
        pos_list.pop(j); fit_list.pop(j)

def select_leader(pos_list, fit_list, rng):
    cd = crowding(fit_list)
    w = np.array([1e6 if d == float("inf") else d for d in cd], dtype=float)
    if w.sum() == 0:
        return pos_list[rng.integers(len(pos_list))]
    return pos_list[rng.choice(len(pos_list), p=w / w.sum())]

# ============================ generalized MOHHO ===============================
ACCEPTANCE = ("canonical", "gated", "pareto_improving_restart")

def run_mohho_generic(eval_fn, dim, M, ref, seed, pop=100, gen=500,
                      archive_size=100, acceptance="gated", stagnation=40):
    """Mirrors app.core.mohho step logic, but with a SELECTABLE acceptance policy.
    - canonical: X(t+1)=new always (standard HHO)
    - gated: move only if new dominates current (CURRENT engine behavior)
    - pareto_improving_restart: move if new not dominated by current (accept
      incomparable/better) + reinit hawks stagnant `stagnation` iters
    Budget = pop*gen single-trial evaluations (FE parity, like the engine)."""
    assert acceptance in ACCEPTANCE
    rng = np.random.default_rng(seed)
    pop_pos = rng.uniform(0, 1, size=(pop, dim))
    fits = [tuple(eval_fn(pop_pos[i])) for i in range(pop)]
    arch_pos, arch_fit = [], []
    for i in range(pop):
        archive_add(arch_pos, arch_fit, pop_pos[i], fits[i], archive_size, rng)
    last_move = np.zeros(pop, dtype=int)

    def accept(i, new_pos):
        fit_new = tuple(eval_fn(new_pos))
        moved = False
        if acceptance == "canonical":
            pop_pos[i] = new_pos; fits[i] = fit_new; moved = True
        elif acceptance == "gated":
            if dominates(fit_new, fits[i]):
                pop_pos[i] = new_pos; fits[i] = fit_new; moved = True
        else:  # pareto_improving_restart
            if not dominates(fits[i], fit_new):
                pop_pos[i] = new_pos; fits[i] = fit_new; moved = True
        archive_add(arch_pos, arch_fit, new_pos, fit_new, archive_size, rng)
        return moved

    hv_hist, moved_hist = [], []
    for t in range(gen):
        x_mean = pop_pos.mean(axis=0)
        moved_count = 0
        for i in range(pop):
            e = escape_energy(t, gen, rng); ae = abs(e)
            leader = select_leader(arch_pos, arch_fit, rng)
            if ae >= 1:
                if rng.random() >= 0.5:
                    new = op1_exploration_random(pop_pos[i], pop_pos[rng.integers(pop)], rng)
                else:
                    new = op2_exploration_mean(pop_pos[i], leader, x_mean, rng)
            elif rng.random() >= 0.5:
                new = op3_soft_siege(pop_pos[i], leader, e, rng) if ae >= 0.5 \
                      else op4_hard_siege(pop_pos[i], leader, e, rng)
            else:
                if ae >= 0.5:
                    y, _z = op5_soft_siege_levy(pop_pos[i], leader, e, rng)
                else:
                    y, _z = op6_hard_siege_levy(pop_pos[i], leader, e, x_mean, rng)
                new = y
            moved = accept(i, new)
            if moved:
                moved_count += 1; last_move[i] = t
            elif acceptance == "pareto_improving_restart" and (t - last_move[i]) >= stagnation:
                pop_pos[i] = rng.uniform(0, 1, size=dim); fits[i] = tuple(eval_fn(pop_pos[i]))
                last_move[i] = t
        moved_hist.append(moved_count / pop)
        hv_hist.append(hv_any(arch_fit, ref))
    return dict(hv=hv_any(arch_fit, ref), archive=len(arch_fit),
                moved_fraction_mean=float(np.mean(moved_hist)),
                hv_hist=hv_hist, moved_hist=moved_hist)

# ============================ compact NSGA-II (reference) =====================
def _fast_nd_sort(fits):
    n = len(fits); S = [[] for _ in range(n)]; nd = [0] * n; fronts = [[]]
    for p in range(n):
        for q in range(n):
            if dominates(fits[p], fits[q]): S[p].append(q)
            elif dominates(fits[q], fits[p]): nd[p] += 1
        if nd[p] == 0: fronts[0].append(p)
    i = 0
    while fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in S[p]:
                nd[q] -= 1
                if nd[q] == 0: nxt.append(q)
        i += 1; fronts.append(nxt)
    fronts.pop()
    return fronts

def run_nsga2_generic(eval_fn, dim, M, ref, seed, pop=100, gen=500,
                      eta_c=20.0, eta_m=20.0):
    rng = np.random.default_rng(seed)
    pc = 0.9; pm = 1.0 / dim
    P = rng.uniform(0, 1, size=(pop, dim))
    F = [tuple(eval_fn(P[i])) for i in range(pop)]

    def sbx(a, b):
        c1, c2 = a.copy(), b.copy()
        for j in range(dim):
            if rng.random() <= 0.5 and abs(a[j] - b[j]) > 1e-14:
                x1, x2 = min(a[j], b[j]), max(a[j], b[j])
                u = rng.random()
                beta = 1.0 + 2.0 * (x1 - 0) / (x2 - x1 + 1e-30)
                alpha = 2.0 - beta ** (-(eta_c + 1))
                bq = (u * alpha) ** (1 / (eta_c + 1)) if u <= 1 / alpha \
                     else (1 / (2 - u * alpha)) ** (1 / (eta_c + 1))
                c1[j] = 0.5 * ((x1 + x2) - bq * (x2 - x1))
                c2[j] = 0.5 * ((x1 + x2) + bq * (x2 - x1))
        return np.clip(c1, 0, 1), np.clip(c2, 0, 1)

    def mutate(c):
        for j in range(dim):
            if rng.random() < pm:
                u = rng.random()
                d = (2 * u) ** (1 / (eta_m + 1)) - 1 if u < 0.5 \
                    else 1 - (2 * (1 - u)) ** (1 / (eta_m + 1))
                c[j] = min(1.0, max(0.0, c[j] + d))
        return c

    for _ in range(gen):
        # offspring
        Q = []
        while len(Q) < pop:
            i, j = rng.integers(pop), rng.integers(pop)
            a = P[i] if dominates(F[i], F[j]) or rng.random() < 0.5 else P[j]
            k, l = rng.integers(pop), rng.integers(pop)
            b = P[k] if dominates(F[k], F[l]) or rng.random() < 0.5 else P[l]
            c1, c2 = sbx(a, b) if rng.random() < pc else (a.copy(), b.copy())
            Q.append(mutate(c1));  Q.append(mutate(c2))
        Q = np.array(Q[:pop]); FQ = [tuple(eval_fn(q)) for q in Q]
        R = np.vstack([P, Q]); FR = F + FQ
        fronts = _fast_nd_sort(FR)
        newP, newF = [], []
        for fr in fronts:
            if len(newP) + len(fr) <= pop:
                for idx in fr: newP.append(R[idx]); newF.append(FR[idx])
            else:
                cd = crowding([FR[i] for i in fr])
                order = sorted(range(len(fr)), key=lambda z: cd[z], reverse=True)
                for z in order[: pop - len(newP)]:
                    newP.append(R[fr[z]]); newF.append(FR[fr[z]])
                break
        P = np.array(newP); F = newF
    nd = _fast_nd_sort(F)[0]
    return dict(hv=hv_any([F[i] for i in nd], ref), archive=len(nd))
