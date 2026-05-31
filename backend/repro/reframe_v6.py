"""v6 reframe: propaga la regla de dos condiciones (non-degenerate search) al titulo,
abstract, §6.4, conclusiones. Reemplazos LITERALES exactos; reporta hit/miss por
archivo. NO toca numeros verificados. Tabla 8/§6.6 se hacen aparte (tras FASE 2)."""
from pathlib import Path

BASE = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
ALL = ["main_submission.tex", "main.tex", "main_reducida_submission.tex", "main_reducida.tex"]

# (old, new) -- exact unique substrings
REPL = [
 # B1 title
 ("Representation, Not Metaheuristic, Governs Feasibility-Preserving Multi-Objective Optimization: A Study on United States Employment-Based Visa Allocation",
  "Non-Degenerate Search, Not the Encoding or the Metaheuristic Family, Governs Decoder-Based Multi-Objective Optimization: A United States Employment-Based Visa Allocation Study"),
 # B2 running head
 ("Representation Governs Decoder-Based Multi-Objective Search",
  "Non-Degenerate Search Governs Decoder-Based MO Optimization"),
 # B3 abstract thesis opener
 (r"Across \emph{four} structurally distinct multi-objective problems, performance is governed far more by the match between representation and search operators than by the metaheuristic family.",
  r"Across \emph{four} structurally distinct multi-objective problems, what governs performance is neither the encoding nor the metaheuristic family but whether the search is \emph{non-degenerate}: a method beats blind sampling only when its operators change the decoded order \emph{and} its selection preserves population diversity."),
 # abstract "six-method" -> seven-method
 ("A controlled six-method ladder isolates the cause:",
  "A controlled seven-method ladder isolates the cause:"),
 # B4 abstract "above every random-key method"
 (r"under which matching operators to the representation lifts three distinct paradigms (genetic algorithm, decomposition, and swarm) above every random-key method, our representation-matched Discrete-MOHHO being the most stable.",
  r"under which a competent random-key swarm and three permutation-native paradigms (genetic algorithm, decomposition, and swarm) all reach the top tier---so the encoding is not the divider---our representation-matched Discrete-MOHHO being the most stable."),
 # B4 §6.4 close: governing claim
 (r"makes the pattern unmistakable: performance is governed by the \emph{feasibility-preserving decoder} and the \emph{representation--operator match}, not by the metaheuristic family.",
  r"makes the pattern unmistakable: performance is governed by whether the search is \emph{non-degenerate}---operators that change the decoded order together with selection that preserves diversity---not by the encoding (random-key versus permutation) or the metaheuristic family."),
 # B4 §6.4: "match is first-order (random-key->permutation jump)"
 (r"the operator--representation \emph{match} is first-order (the random-key$\to$permutation jump), whereas",
  r"the two conditions (order-changing operators and diversity-preserving selection) are first-order---a competent random-key swarm satisfies both and joins the top tier, so the encoding itself is not the divider---whereas"),
 # B7 conclusions: "above every random-key method"
 (r"Matching operators to the representation lifts three distinct paradigms (a GA, a decomposition method, and a Harris Hawks optimizer) to within about $1\,\%$ of one another and above every random-key method;",
  r"Matching operators to the representation lifts three permutation-native paradigms (a GA, a decomposition method, and a Harris Hawks optimizer) to within about $1\,\%$ of one another, and a competent random-key swarm joins them above blind sampling---so the divider is non-degenerate search, not the encoding;"),
 # conclusions "controlled six-method ladder"
 ("Our central result comes from a controlled six-method ladder:",
  "Our central result comes from a controlled seven-method ladder:"),
]

for fn in ALL:
    p = BASE / fn; s = p.read_text(); hits = []
    for i, (o, n) in enumerate(REPL):
        if o in s:
            s = s.replace(o, n, 1); hits.append(str(i))
        else:
            hits.append(f"{i}:MISS")
    p.write_text(s)
    print(fn, "->", " ".join(hits))
