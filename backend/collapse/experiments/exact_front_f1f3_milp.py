"""
SUPERPROMPT v2 - Frente exacto bi-objetivo (f1, f3) via epsilon-constraint + MILP
(Seccion 5, C2.2 / Q1). Reemplaza el MILP defectuoso del v1.

f1 y f3 son LINEALES en x:
    f1 = (sum_g (n_g - x_g) w_g) / sum_g n_g        (denominador constante)
    f3 = V - sum_g x_g
Minimizar f1  <=>  maximizar  sum_g x_g w_g.
Minimizar f3  <=>  maximizar  sum_g x_g.
Conflicto: los grupos con w_g = 0 (priority date = T_actual) no aportan a f1 pero
si reducen f3; minimizar f1 es indiferente a ellos -> puede dejar visas sin usar.
Por eso (f1, f3) tienen un frente bi-objetivo no trivial.

f2 es fraccional/discontinua -> NO entra al MILP; se evalua a posteriori sobre cada
solucion (f1,f3) del frente exacto.

Metodo: para una rejilla de epsilon (cota superior de f3), resolver
    max  sum_g x_g w_g
    s.t. sum_g x_g >= V - epsilon              (f3 <= epsilon)
         sum_g x_g <= V                         (R: total)
         sum_{g in c} x_g <= P_c   for all c    (R: per-country cap)
         sum_{g in cat} x_g <= K_cat for all cat(R: per-category spillover cap)
         0 <= x_g <= n_g, entero                (R: demanda)
Cada solucion es f1-optima para su nivel de f3 -> punto exacto del frente (f1,f3).

Salida: app/data/results/expC_Q1_nonsaturating.json
Ejecutar desde backend/:  python3 -m collapse.experiments.exact_front_f1f3_milp
"""
import csv
import json
import time
from pathlib import Path

import pulp

from app.core.problem import VisaProblem
from app.core.mohho import dominates

RESULTS = Path("app/data/results")


def solve_max_weight(problem, util_floor):
    """max sum x_g w_g  s.t. sum x_g >= util_floor y caps. Devuelve x (dict) o None."""
    prob = pulp.LpProblem("maxweight", pulp.LpMaximize)
    x = {}
    for g in problem.groups:
        x[g["index"]] = pulp.LpVariable(f"x_{g['index']}", lowBound=0,
                                        upBound=g["n"], cat="Integer")
    # objective: maximize weighted allocation (= minimize f1)
    prob += pulp.lpSum(x[g["index"]] * g["w"] for g in problem.groups)
    # total
    prob += pulp.lpSum(x.values()) <= problem.total_visas
    prob += pulp.lpSum(x.values()) >= util_floor
    # per-country caps
    by_c = {}
    by_cat = {}
    for g in problem.groups:
        by_c.setdefault(g["country"], []).append(g["index"])
        by_cat.setdefault(g["category"], []).append(g["index"])
    for c, idxs in by_c.items():
        prob += pulp.lpSum(x[i] for i in idxs) <= problem.country_caps[c]
    for cat, idxs in by_cat.items():
        prob += pulp.lpSum(x[i] for i in idxs) <= problem.category_caps[cat]
    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != "Optimal":
        return None
    return {i: int(round(v.value())) for i, v in x.items()}


def greedy_front():
    front = []
    for r in csv.DictReader(open(RESULTS / "pareto_front.csv")):
        if r["type"] == "pareto":
            front.append((float(r["f1"]), float(r["f2"]), float(r["f3"])))
    return front


def main():
    t0 = time.time()
    problem = VisaProblem()
    V = problem.total_visas

    # maximum achievable utilization (min f3) -> solve with floor 0, then push
    x_full = solve_max_weight(problem, 0)
    if x_full is None:
        raise RuntimeError("MILP unsolved at util_floor=0 (CBC failure); cannot proceed.")
    max_util = sum(x_full.values())
    print(f"max weighted allocation uses {max_util}/{V} visas "
          f"(min achievable f3 in this objective = {V - max_util})")

    # epsilon grid on f3 (waste). util_floor = V - eps.
    eps_grid = sorted(set([0, 50, 100, 200, 340, 500, 680, 1000, 1500, 1940,
                           3000, 5000, 8000, 12000, 20000, V - max_util, V]))
    pts = []
    for eps in eps_grid:
        floor = max(0, V - eps)
        x = solve_max_weight(problem, floor)
        if x is None:
            continue
        f1 = problem.f1(x)
        f2 = problem.f2(x)              # a posteriori (fraccional, fuera del MILP)
        f3 = problem.f3(x)
        slack = f3
        pts.append({"eps": eps, "f1": round(f1, 6), "f2": round(f2, 6),
                    "f3": round(f3, 1), "slack_V": round(slack, 1),
                    "sum_x": sum(x.values())})
        print(f"  eps={eps:6d} -> f1={f1:.5f} f2={f2:.4f} f3={f3:.0f} (slack_V={slack:.0f})")

    # exact bi-objective (f1,f3) Pareto front
    bi = [(p["f1"], p["f3"]) for p in pts]
    exact_front = []
    for i, a in enumerate(bi):
        if not any((b[0] <= a[0] and b[1] <= a[1]) and (b[0] < a[0] or b[1] < a[1])
                   for j, b in enumerate(bi) if j != i):
            exact_front.append(pts[i])
    # dedup
    seen = set()
    uniq = []
    for p in exact_front:
        key = (p["f1"], p["f3"])
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    exact_front = sorted(uniq, key=lambda p: p["f1"])

    # ---- Q1: ¿alguna solucion MILP con slack_V>0 es NO-dominada en (f1,f2,f3) vs
    #         el frente greedy de 92 soluciones? (recorre TODOS los puntos resueltos,
    #         no solo el frente (f1,f3), para no perder los que mejoran f2 a costa de
    #         waste). f2 es incidental (no optimizada): basta para probar EXISTENCIA. ----
    g_front = greedy_front()
    g_best_f1 = min(g[0] for g in g_front)
    g_best_f2 = min(g[1] for g in g_front)
    contra = []
    seen_c = set()
    for p in pts:
        if p["slack_V"] <= 0:
            continue
        cand = (p["f1"], p["f2"], p["f3"])
        if any(dominates(g, cand) for g in g_front):
            continue
        # tambien excluir empates exactos con un punto greedy (no es 'nuevo')
        if any(abs(g[0] - cand[0]) < 1e-9 and abs(g[1] - cand[1]) < 1e-9
               and abs(g[2] - cand[2]) < 1e-6 for g in g_front):
            continue
        key = (round(p["f1"], 6), round(p["f2"], 4), round(p["f3"], 0))
        if key in seen_c:
            continue
        seen_c.add(key)
        # caracterizar la mejora vs lo mejor del greedy
        p2 = dict(p)
        p2["f1_improvement_vs_greedy_best_f1"] = round(g_best_f1 - p["f1"], 6)
        p2["f2_improvement_vs_greedy_best_f2"] = round(g_best_f2 - p["f2"], 4)
        p2["meaningful_f2_gain"] = (p["f2"] < g_best_f2 - 0.5)
        contra.append(p2)

    # ¿hay contraejemplos PRACTICAMENTE significativos (no solo en el 5o decimal de f1)?
    meaningful = [c for c in contra
                  if abs(c["f1_improvement_vs_greedy_best_f1"]) > 1e-3
                  or c["meaningful_f2_gain"]]
    claim_holds = len(contra) == 0
    out = {
        "method": "epsilon-constraint sobre f3 + MILP (CBC); f1,f3 lineales; f2 a posteriori",
        "instance": "base 105 grupos (no sub-instancia)",
        "V": V,
        "max_weighted_utilization": max_util,
        "min_f3_under_f1opt": V - max_util,
        "eps_grid": eps_grid,
        "all_solved_points": pts,
        "exact_bi_objective_front_f1f3": exact_front,
        "exact_front_size": len(exact_front),
        "Q1_question": ("Existen optimos no-saturantes (slack_V>0) que sean NO-dominados "
                        "en (f1,f2,f3) respecto al frente greedy de 92 soluciones?"),
        "greedy_best_f1": g_best_f1,
        "greedy_best_f2": g_best_f2,
        "Q1_nondominated_nonsaturating_contraejemplos": contra,
        "Q1_n_contraejemplos": len(contra),
        "Q1_n_contraejemplos_significativos": len(meaningful),
        "Q1_contraejemplos_significativos": meaningful,
        "claim_holds": claim_holds,
        "claim_interpretation": (
            "claim_holds=true: TODAS las soluciones no-dominadas saturan (slack_V=0). "
            "claim_holds=false: existen optimos no-saturantes no-dominados respecto al "
            "frente greedy. MATIZ DE MAGNITUD: distinguir contraejemplos en el eje f1 "
            "degenerado (mejora < 1e-3, sin sentido practico) de los PRACTICAMENTE "
            "significativos (mejora de f2 > 0.5 anios a costa de waste). Ver "
            "Q1_n_contraejemplos_significativos."),
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "expC_Q1_nonsaturating.json", "w"),
              indent=2, ensure_ascii=False)
    print(f"\nexact (f1,f3) front: {len(exact_front)} pts | "
          f"Q1 contraejemplos no-saturantes no-dominados: {len(contra)} | "
          f"claim_holds={claim_holds}")
    print(f"-> expC_Q1_nonsaturating.json ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
