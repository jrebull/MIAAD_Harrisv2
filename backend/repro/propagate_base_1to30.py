"""Propaga al paper los pocos numeros que cambian al regenerar el ESTUDIO
PRINCIPAL a seeds 1-30 (rerun_base): frente combinado 92->104, zero-waste
82/92->94/104, extremo Min-f2 (f1 9.0016->8.9994), extremo Min-f3
(8.851/8.06 -> 8.996/2.46) y conteo por corrida ~38->~42. Todos verificados
contra summary.json/run_XX/pareto_front.csv regenerados. Reporta hit/miss por
archivo. NO inventa numeros."""
from pathlib import Path

B = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
TARGETS = ["main_submission.tex", "main.tex",
           "main_reducida_submission.tex", "main_reducida.tex"]

E = [
 # combined front size 92 -> 104
 (r"yields a front of \textbf{92 non-dominated solutions}",
  r"yields a front of \textbf{104 non-dominated solutions}"),
 (r"The 92-solution combined Pareto front",
  r"The 104-solution combined Pareto front"),
 # zero-waste count 82/92 -> 94/104
 (r"82 of the 92 front solutions reach $f_3=0$",
  r"94 of the 104 front solutions reach $f_3=0$"),
 # tab:extremes Min-f2 f1 9.0016 -> 8.9994
 (r"Min.\ $f_2$ (most equitable) & 9.0016 & 2.0 & 0",
  r"Min.\ $f_2$ (most equitable) & 8.9994 & 2.0 & 0"),
 # tab:extremes Min-f3 (8.851, 8.06) -> (8.996, 2.46)
 (r"Min.\ $f_3$ (full use) & 8.851 & 8.06 & 0",
  r"Min.\ $f_3$ (full use) & 8.996 & 2.46 & 0"),
 # per-run front size ~38 -> ~42
 (r"holds only about 38 solutions per run",
  r"holds only about 42 solutions per run"),
]

for fn in TARGETS:
    p = B / fn
    if not p.exists():
        print(f"{fn}: NO EXISTE"); continue
    s = p.read_text(); hits = 0; miss = []
    for i, (o, n) in enumerate(E):
        if o in s:
            s = s.replace(o, n); hits += 1
        elif n in s:
            pass  # ya aplicado
        else:
            miss.append(i)
    p.write_text(s)
    print(f"{fn}: {hits}/{len(E)} applied; MISS edits {miss}")
