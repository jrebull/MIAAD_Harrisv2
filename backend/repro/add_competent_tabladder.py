"""Anade la fila del MO-HHO competente (random-key, top tier) a tab:ladder en los
4 .tex y reframea el caption. Numeros LEIDOS de ladder_v5.json (cero drift)."""
import json
from pathlib import Path

BASE = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
cm = json.load(open("app/data/results/ladder_v5.json"))["methods"]["competent_mohho"]
mean = cm["hv_mean"]; std = cm["hv_std"]; cv = cm["cv_pct"]
comb = cm["combined_front_hv"]; nsol = cm["combined_front_size"]


def fnum(x):
    return f"{x:,.0f}".replace(",", "{,}")


row = (r"Competent MO-HHO   & swarm    & $" + fnum(mean) + r" \pm " + fnum(std) +
       r"$ & " + f"{cv:.2f}" + r"\,\% & " + fnum(comb) + r" & " + str(nsol) + r"\\" + "\n")

# insert after the "Random restart ... \\" line (last top-block row), before \midrule
anchor = r"Random restart     & ---      & $309{,}367 \pm"  # may differ; use looser anchor
ANCHOR = "Random restart     & ---      & $309{,}821 \\pm 2{,}513$ & 0.81\\,\\% & 316{,}383 & 81\\\\"

OLD_CAP = (r"Top block: random-key encoding. Bottom block: permutation-native, spanning three distinct paradigms (swarm, decomposition, dominance/GA), which cluster within about $1\,\%$ and dominate every random-key method.")
NEW_CAP = (r"Top block: random-key encoding (including a \emph{competent} MO-HHO that reaches the top tier); bottom block: permutation-native. A competent random-key method matches the permutation tier, so the encoding is not the performance divider---non-degenerate search is.")

for fn in ["main_submission.tex", "main.tex", "main_reducida_submission.tex", "main_reducida.tex"]:
    p = BASE / fn; s = p.read_text(); st = []
    if "Competent MO-HHO" in s:
        print(fn, "row already present"); continue
    if ANCHOR in s:
        s = s.replace(ANCHOR, ANCHOR + "\n" + row.rstrip("\n"), 1); st.append("row")
    else:
        st.append("row:MISS")
    if OLD_CAP in s:
        s = s.replace(OLD_CAP, NEW_CAP, 1); st.append("caption")
    else:
        st.append("caption:MISS")
    p.write_text(s)
    print(fn, "->", " ".join(st))
