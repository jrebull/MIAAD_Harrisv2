"""
SUPERPROMPT v2 - Decoders de control para Exp C (H_dec).

El greedy del paper satura: cada grupo visitado recibe su maximo factible, asi que
la imagen del decoder es solo el subconjunto saturante de F. Para aislar si el
'representation governs' es un artefacto de esa saturacion, definimos dos decoders
que NO colapsan al subconjunto saturante:

  C1 (fractional, no-saturante): genotipo extendido con intensidades alpha_g en
     [0,1]. Para cada grupo visitado, x_g = floor(alpha_g * cap_g). Abre el espacio
     a soluciones que dejan headroom (slack) -> duplica la dimension del genotipo.

  C2 (stochastic-skip, intermedio): greedy con probabilidad de SALTAR un grupo
     (dejarlo en 0) controlada por una key adicional. Mas suave que C1.

Los tres (greedy/C1/C2) preservan feasibility por construccion: cap_g se calcula
sobre residuales (n_g, V_rem, P_c - usage_c, K_cat - usage_cat) y x_g <= cap_g, de
modo que ningun residual se vuelve negativo (analogo a la Proposicion 1 del paper).
"""
import math

import numpy as np

from app.core.config import NUM_GROUPS
from app.core.decoder import spv


def _greedy_core(order, problem, intensity=None, skip=None):
    """Asignacion sobre 'order' respetando R1-R6. intensity/skip por indice de grupo."""
    x = {g["index"]: 0 for g in problem.groups}
    v_rem = problem.total_visas
    cu = {}
    ku = {}
    lookup = {g["index"]: g for g in problem.groups}
    for gi in order:
        g = lookup[gi]
        c, cat = g["country"], g["category"]
        cap = min(g["n"], v_rem,
                  problem.country_caps[c] - cu.get(c, 0),
                  problem.category_caps[cat] - ku.get(cat, 0))
        if cap < 0:
            cap = 0
        if skip is not None and skip[gi]:
            xg = 0
        elif intensity is not None:
            xg = int(math.floor(intensity[gi] * cap))
        else:
            xg = cap
        x[gi] = xg
        v_rem -= xg
        cu[c] = cu.get(c, 0) + xg
        ku[cat] = ku.get(cat, 0) + xg
    return x


class Decoder:
    name = "base"
    rk_dim = NUM_GROUPS          # genotype length for random-key methods
    uses_aux = False             # whether permutation methods carry an aux vector

    def decode_rk(self, vec, problem):
        raise NotImplementedError

    def decode_perm(self, perm, aux, problem):
        raise NotImplementedError


class GreedyDecoder(Decoder):
    name = "greedy"
    rk_dim = NUM_GROUPS
    uses_aux = False

    def decode_rk(self, vec, problem):
        return _greedy_core(spv(np.asarray(vec[:NUM_GROUPS])), problem)

    def decode_perm(self, perm, aux, problem):
        return _greedy_core(list(perm), problem)


class FractionalDecoder(Decoder):
    name = "C1_fractional"
    rk_dim = 2 * NUM_GROUPS
    uses_aux = True

    def decode_rk(self, vec, problem):
        vec = np.asarray(vec)
        order = spv(vec[:NUM_GROUPS])
        alpha = np.clip(vec[NUM_GROUPS:2 * NUM_GROUPS], 0.0, 1.0)
        return _greedy_core(order, problem, intensity=alpha)

    def decode_perm(self, perm, aux, problem):
        alpha = np.clip(np.asarray(aux), 0.0, 1.0)
        return _greedy_core(list(perm), problem, intensity=alpha)


class StochasticSkipDecoder(Decoder):
    name = "C2_stochastic_skip"
    rk_dim = 2 * NUM_GROUPS
    uses_aux = True

    def decode_rk(self, vec, problem):
        vec = np.asarray(vec)
        order = spv(vec[:NUM_GROUPS])
        skip = vec[NUM_GROUPS:2 * NUM_GROUPS] < 0.5     # key<0.5 => saltar
        return _greedy_core(order, problem, skip=skip)

    def decode_perm(self, perm, aux, problem):
        skip = np.asarray(aux) < 0.5
        return _greedy_core(list(perm), problem, skip=skip)


DECODERS = {
    "greedy": GreedyDecoder(),
    "C1_fractional": FractionalDecoder(),
    "C2_stochastic_skip": StochasticSkipDecoder(),
}


# ---------------- feasibility verification (Proposicion 1 analoga) -------------
def check_feasibility(alloc, problem):
    """Devuelve lista de violaciones de R1-R6 (vacia si factible)."""
    viol = []
    lookup = {g["index"]: g for g in problem.groups}
    cu, ku = {}, {}
    total = 0
    for gi, xg in alloc.items():
        g = lookup[gi]
        if xg < 0:
            viol.append(f"R: x_{gi} < 0 ({xg})")
        if xg > g["n"]:
            viol.append(f"R(demand): x_{gi}={xg} > n={g['n']}")
        cu[g["country"]] = cu.get(g["country"], 0) + xg
        ku[g["category"]] = ku.get(g["category"], 0) + xg
        total += xg
    if total > problem.total_visas:
        viol.append(f"R(total): sum x={total} > V={problem.total_visas}")
    for c, u in cu.items():
        if u > problem.country_caps[c]:
            viol.append(f"R(country {c}): {u} > {problem.country_caps[c]}")
    for cat, u in ku.items():
        if u > problem.category_caps[cat]:
            viol.append(f"R(category {cat}): {u} > {problem.category_caps[cat]}")
    return viol
