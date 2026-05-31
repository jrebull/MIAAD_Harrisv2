"""v6 reframe part 2: B6 (abstract 'above every random-key'), B1 (competent row in
tab:ladder), B9 (fig:ladder2 clean-two-tier, full only), intro central-contribution,
contribution (iv), §6.4 closer, conclusions 'above every random-key'. All literal,
read-fresh, report hit/miss per file. Numbers (competent row) read from ladder_v5.json."""
import json
from pathlib import Path

B = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
cm = json.load(open("app/data/results/ladder_v5.json"))["methods"]["competent_mohho"]


def fn(x): return f"{x:,.0f}".replace(",", "{,}")


ALL = ["main_submission.tex", "main.tex", "main_reducida_submission.tex", "main_reducida.tex"]
FULL = ["main_submission.tex", "main.tex"]

# competent row for tab:ladder (top/random-key block)
ROW = (r"Competent MO-HHO   & swarm    & $" + fn(cm["hv_mean"]) + r" \pm " + fn(cm["hv_std"]) +
       r"$ & " + f"{cm['cv_pct']:.2f}" + r"\,\% & " + fn(cm["combined_front_hv"]) +
       r" & " + str(cm["combined_front_size"]) + r"\\")
ROW_ANCHOR = r"Random restart     & ---      & $309{,}821 \pm 2{,}513$ & 0.81\,\% & 316{,}383 & 81\\"

CAP_OLD = (r"Top block: random-key encoding. Bottom block: permutation-native, spanning three distinct paradigms (swarm, decomposition, dominance/GA), which cluster within about $1\,\%$ and dominate every random-key method. Best per column in bold; ``perm-'' abbreviates ``permutation-''.")
CAP_NEW = (r"Top block: random-key encoding (including a \emph{competent} MO-HHO that reaches the top tier); bottom block: permutation-native. A competent random-key method matches the permutation tier, so the encoding is not the performance divider---non-degenerate search is. Best per column in bold; ``perm-'' abbreviates ``permutation-''.")

# B6 abstract
AB_OLD = r"under which matching operators to the representation lifts three distinct paradigms (genetic algorithm, decomposition, and swarm) above every random-key method, our representation-matched Discrete-MOHHO being the most stable."
AB_NEW = r"under which a competent random-key swarm and three permutation-native paradigms (genetic algorithm, decomposition, and swarm) all reach the top tier---so the encoding is not the performance divider---our representation-matched Discrete-MOHHO being the most stable."

# conclusions 'above every random-key'
CC_OLD = r"Matching operators to the representation lifts three distinct paradigms (a GA, a decomposition method, and a Harris Hawks optimizer) to within about $1\,\%$ of one another and above every random-key method;"
CC_NEW = r"Matching operators to the representation lifts three permutation-native paradigms (a GA, a decomposition method, and a Harris Hawks optimizer) to within about $1\,\%$ of one another, and a competent random-key swarm joins them above blind sampling---so the divider is non-degenerate search, not the encoding;"

# §6.4 'lifts three different paradigms above every random-key method' (the eta-sweep para, full+reduced)
S64_OLD = r"Acting \emph{directly} on permutations lifts \emph{three different paradigms} above every random-key method:"
S64_NEW = r"Acting \emph{directly} on permutations lifts \emph{three different paradigms} above blind sampling (a competent random-key swarm does too; the encoding is not the divider):"

# B9 fig:ladder2 (full only)
FL_OLD = r"all three random-key methods (NSGA-II, the MOHHO swarm, and random restart) sit below the three permutation-native methods---a clean two-tier split."
FL_NEW = r"the naive random-key methods (NSGA-II, the MOHHO swarm, and random restart) sit below the permutation-native methods; a competent random-key swarm, by contrast, joins the top tier (Section~\ref{sec:twoconditions}), so the divide is non-degenerate search, not the encoding."

EDITS_ALL = [("B6_abstract", AB_OLD, AB_NEW), ("CC_concl", CC_OLD, CC_NEW), ("S64", S64_OLD, S64_NEW)]
EDITS_FULL = [("B9_figladder2", FL_OLD, FL_NEW)]

for f in ALL:
    p = B / f; s = p.read_text(); rep = []
    # tab:ladder row + caption
    if "Competent MO-HHO" not in s and ROW_ANCHOR in s:
        s = s.replace(ROW_ANCHOR, ROW_ANCHOR + "\n" + ROW, 1); rep.append("row")
    if CAP_OLD in s:
        s = s.replace(CAP_OLD, CAP_NEW, 1); rep.append("cap")
    for name, o, n in EDITS_ALL:
        if o in s:
            s = s.replace(o, n, 1); rep.append(name)
        else:
            rep.append(name + ":MISS")
    if f in FULL:
        for name, o, n in EDITS_FULL:
            if o in s:
                s = s.replace(o, n, 1); rep.append(name)
            else:
                rep.append(name + ":MISS")
    p.write_text(s)
    print(f, "->", " ".join(rep))
