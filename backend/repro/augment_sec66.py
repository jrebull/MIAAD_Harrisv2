"""Augmenta §6.6 con la colocacion del MO-HHO competente (random-key) en las 4
estructuras, leyendo structures_v6.json. NO recomputa Tabla 8 (queda como la
comparacion publicada de 6 metodos); anade el matiz de 7 metodos en prosa."""
import json
from pathlib import Path

BASE = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
d = json.load(open("app/data/results/structures_v6.json"))
pl = d["placement"]


def pos(st): return pl[st]["competent_position_of_7"]
def rk(st): return f'{pl[st]["competent_avg_rank"]:.2f}'


# sentence built from JSON
SENT = (r" We further placed the competent random-key MO-HHO of Section~\ref{sec:twoconditions} on all four structures (seven methods, same 30-seed budget): it is \emph{never} the single best---a permutation-native method still wins every structure---yet it is no mere also-ran, ranking "
        f"{pos('knapsack')}nd of seven on the knapsack (mean rank {rk('knapsack')}, above two permutation-native methods) and "
        f"{pos('visa')}th/{pos('flow-shop')}th/{pos('TSP')}th on the visa, flow-shop, and TSP. "
        r"So the cross-structure regularity is sharper than ``permutation beats random-key'': what wins is \emph{non-degenerate} search, and a competent random-key method joins the top tier rather than sitting in a separate encoding-defined tier.")

FULL_ANCHOR = r"All four omnibus tests reject equality decisively (Friedman $\chi^2$ from $112$ to $150$, $p<10^{-21}$, critical difference $1.38$)."
RED_ANCHOR = r"with the family second-order among matched methods (all four omnibus tests reject equality, $\chi^2=112$--$150$, $p<10^{-21}$)."

for fn in ["main_submission.tex", "main.tex"]:
    p = BASE / fn; s = p.read_text()
    if "competent random-key MO-HHO of Section" in s:
        print(fn, "already"); continue
    if FULL_ANCHOR in s:
        s = s.replace(FULL_ANCHOR, FULL_ANCHOR + SENT, 1); p.write_text(s); print(fn, "OK")
    else:
        print(fn, "ANCHOR MISS")
for fn in ["main_reducida_submission.tex", "main_reducida.tex"]:
    p = BASE / fn; s = p.read_text()
    if "competent random-key MO-HHO of Section" in s:
        print(fn, "already"); continue
    if RED_ANCHOR in s:
        s = s.replace(RED_ANCHOR, RED_ANCHOR + SENT, 1); p.write_text(s); print(fn, "OK")
    else:
        print(fn, "ANCHOR MISS")
