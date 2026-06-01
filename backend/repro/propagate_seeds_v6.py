"""Propaga los reemplazos de unificacion de seeds (1-30) de main_submission.tex a
los otros 3 .tex. Cada par es (old,new) LITERAL; reporta hit/miss por archivo y por
edit. Las versiones reducidas pueden tener variantes mas cortas: las que fallen se
listan para tratarlas aparte. NO inventa numeros; todos vienen de los edits ya
verificados en el full submission."""
from pathlib import Path

B = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
TARGETS = ["main.tex", "main_reducida_submission.tex", "main_reducida.tex"]

E = [
 # --- Table 7 rows ---
 ("MOHHO              & swarm    & $302{,}379 \\pm 7{,}455$ & 2.47\\,\\% & 321{,}446 & 92\\\\",
  "MOHHO              & swarm    & $302{,}756 \\pm 7{,}138$ & 2.36\\,\\% & 320{,}984 & 104\\\\"),
 ("Random restart     & ---      & $309{,}821 \\pm 2{,}513$ & 0.81\\,\\% & 316{,}383 & 81\\\\",
  "Random restart     & ---      & $310{,}214 \\pm 2{,}735$ & 0.88\\,\\% & 317{,}673 & 65\\\\"),
 ("Competent MO-HHO   & swarm    & $316{,}347 \\pm 6{,}683$ & 2.11\\,\\% & 321{,}800 & 207\\\\",
  "Competent MO-HHO   & swarm    & $316{,}347 \\pm 6{,}683$ & 2.11\\,\\% & 321{,}800 & \\textbf{207}\\\\"),
 ("Discrete-MOHHO              & swarm    & $316{,}637 \\pm 1{,}720$  & \\textbf{0.54\\,\\%} & 321{,}354 & \\textbf{149}\\\\",
  "Discrete-MOHHO              & swarm    & $316{,}792 \\pm 2{,}258$  & 0.71\\,\\% & 321{,}408 & 137\\\\"),
 ("perm-NSGA-II                & GA       & $\\mathbf{318{,}151 \\pm 1{,}855}$ & 0.58\\,\\% & \\textbf{321{,}935} & 148\\\\",
  "perm-NSGA-II                & GA       & $\\mathbf{318{,}151 \\pm 1{,}855}$ & \\textbf{0.58\\,\\%} & \\textbf{321{,}935} & 148\\\\"),
 # --- Table 5 ---
 ("Mean \\HV\\ $\\pm\\,\\sigma$ (30 runs) & --- & $\\mathbf{302{,}379 \\pm 7{,}455}$ & $293{,}367 \\pm 6{,}996$\\\\",
  "Mean \\HV\\ $\\pm\\,\\sigma$ (30 runs) & --- & $\\mathbf{302{,}756 \\pm 7{,}138}$ & $293{,}367 \\pm 6{,}996$\\\\"),
 ("Coefficient of variation & --- & 2.47\\,\\% & \\textbf{2.38\\,\\%}\\\\",
  "Coefficient of variation & --- & \\textbf{2.36\\,\\%} & 2.38\\,\\%\\\\"),
 ("Combined-front \\HV & --- & \\textbf{321{,}446} & 316{,}060\\\\",
  "Combined-front \\HV & --- & \\textbf{320{,}984} & 316{,}060\\\\"),
 ("Non-dominated solutions & 1 & 92 & 92\\\\",
  "Non-dominated solutions & 1 & 104 & 92\\\\"),
 ("$\\IGD$ vs.\\ $Z$ (smaller better) & --- & \\textbf{0.0052} & 0.0080\\\\",
  "$\\IGD$ vs.\\ $Z$ (smaller better) & --- & 0.0212 & \\textbf{0.0071}\\\\"),
 ("Spacing (smaller better) & --- & \\textbf{0.0099} & 0.0463\\\\",
  "Spacing (smaller better) & --- & \\textbf{0.0106} & 0.0463\\\\"),
 ("Significance vs.\\ MOHHO & dominated & --- & $p\\approx1.3\\times10^{-5}$\\\\",
  "Significance vs.\\ MOHHO & dominated & --- & $p\\approx1.8\\times10^{-6}$\\\\"),
 # --- prose ---
 ("MOHHO attains a higher mean hypervolume ($+3.1\\,\\%$), a smaller $\\IGD$, and more uniform spacing; the gap is significant (one-sided Mann--Whitney $p\\approx1.3\\times10^{-5}$, $A_{12}=0.82$).",
  "MOHHO attains a higher mean hypervolume ($+3.2\\,\\%$) and more uniform spacing (NSGA-II edges it on $\\IGD$ to the combined reference front); the hypervolume gap is significant (one-sided Mann--Whitney $p\\approx1.8\\times10^{-6}$, $A_{12}=0.85$)."),
 ("\\emph{Random restart}---blind sampling with no search---already reaches a mean \\HV\\ of $309{,}821$: $5.6\\,\\%$ \\emph{above} NSGA-II and $2.5\\,\\%$ \\emph{above} the classic real-coded MOHHO (the naive swarm wins on only $9/30$ paired seeds).",
  "\\emph{Random restart}---blind sampling with no search---already reaches a mean \\HV\\ of $310{,}214$: $5.7\\,\\%$ \\emph{above} NSGA-II and $2.5\\,\\%$ \\emph{above} the classic real-coded MOHHO (the naive swarm wins on only $10/30$ paired seeds)."),
 ("the \\emph{canonical} two-point Lévy dive does not beat random restart either---$308{,}926$ at the matched $25{,}050$-evaluation budget ($-0.3\\,\\%$, paired Wilcoxon $p=0.77$), only a \\emph{tie} at its $42\\,\\%$-over-budget native schedule ($+0.4\\,\\%$, $p=0.21$).",
  "the \\emph{canonical} two-point Lévy dive does not beat random restart either---$309{,}180$ at the matched $25{,}050$-evaluation budget ($-0.3\\,\\%$, paired Wilcoxon $p=0.74$), only a \\emph{tie} at its $42\\,\\%$-over-budget native schedule ($+0.1\\,\\%$, $p=0.45$)."),
 ("leaves the real-coded GA's mean \\HV\\ at $305{,}293$---still below blind random restart ($309{,}821$) and far below the permutation tier",
  "leaves the real-coded GA's mean \\HV\\ at $305{,}293$---still below blind random restart ($310{,}214$) and far below the permutation tier"),
 ("permutation-MOEA/D (decomposition) $314{,}846$, and our \\textbf{Discrete-MOHHO} (swarm) $316{,}637$.",
  "permutation-MOEA/D (decomposition) $314{,}846$, and our \\textbf{Discrete-MOHHO} (swarm) $316{,}792$."),
 ("The three cluster within about $1\\,\\%$ of one another, yet all sit $1.6$--$2.7\\,\\%$ above the best random-key method (random restart)---more than the spread \\emph{among} the matched paradigms.",
  "The three cluster within about $1\\,\\%$ of one another, yet all sit $1.5$--$2.6\\,\\%$ above blind random restart---more than the spread \\emph{among} the matched paradigms."),
 ("Discrete-MOHHO improves on classic MOHHO by $+4.7\\,\\%$ (paired Wilcoxon $p=9.3\\times10^{-10}$, better on all $30/30$ seeds) and is the \\emph{most stable} method (CV $0.54\\,\\%$, versus $0.58\\,\\%$ for permutation-NSGA-II and $2.47\\,\\%$ for classic MOHHO), making it the most dependable choice for a single-run decision. The marginal mean lead belongs to permutation-NSGA-II ($+0.48\\,\\%$ over Discrete-MOHHO, $A_{12}=0.27$).",
  "Discrete-MOHHO improves on classic MOHHO by $+4.6\\,\\%$ (paired Wilcoxon $p=9.3\\times10^{-10}$, better on all $30/30$ seeds). The two most stable methods are the matched ones: permutation-NSGA-II (CV $0.58\\,\\%$) and Discrete-MOHHO (CV $0.71\\,\\%$), both far tighter than classic MOHHO ($2.36\\,\\%$); permutation-NSGA-II also holds the marginal mean lead ($+0.43\\,\\%$ over Discrete-MOHHO). Discrete-MOHHO is thus the most stable \\emph{swarm} and a dependable single-run choice, though permutation-NSGA-II is both the strongest and the steadiest overall."),
 # convergence (§convergence)
 ("Over the 30 runs the \\HV\\ distribution is narrow (mean $302{,}379$, standard deviation $7{,}455$), a coefficient of variation (CV) of \\textbf{2.47\\,\\%}, evidence of a stable and reproducible algorithm.",
  "Over the 30 runs the \\HV\\ distribution is narrow (mean $302{,}756$, standard deviation $7{,}138$), a coefficient of variation (CV) of \\textbf{2.36\\,\\%}, evidence of a stable and reproducible algorithm."),
 # abstract
 ("all reach the top tier---so the encoding is not the divider---our representation-matched Discrete-MOHHO being the most stable.",
  "all reach the top tier---so the encoding is not the divider---with permutation-NSGA-II the strongest and steadiest and our representation-matched Discrete-MOHHO the most stable swarm."),
 # policy-front parenthetical
 ("(The MOHHO, Discrete-MOHHO, and permutation-NSGA-II combined fronts agree within $0.2\\,\\%$ in hypervolume (Table~\\ref{tab:ladder}), so the policy menu does not hinge on the optimizer choice---the recommended single-run optimizer, Discrete-MOHHO, yields an essentially equivalent front.)",
  "(The MOHHO, Discrete-MOHHO, and permutation-NSGA-II combined fronts agree within $0.3\\,\\%$ in hypervolume (Table~\\ref{tab:ladder}), so the policy menu does not hinge on the optimizer choice---the recommended single-run optimizer yields an essentially equivalent front.)"),
 # fig:ladder caption
 ("the metaheuristic family (GA vs.\\ Harris Hawks) matters far less than the representation. Discrete-MOHHO is the tightest distribution (most stable).}",
  "the metaheuristic family (GA vs.\\ Harris Hawks) matters far less than the representation. permutation-NSGA-II and Discrete-MOHHO are the tightest distributions (most stable).}"),
 # §6.6 typo + claim
 ("yet it is no mere also-ran, ranking 1nd of seven on the knapsack (mean rank 1.13, above two permutation-native methods) and 2th/2th/5th on the visa, flow-shop, and TSP.",
  "yet it is no mere also-ran, ranking 1st of seven on the knapsack (mean rank 1.13, above every permutation-native method---the single best optimizer there) and 2nd, 2nd, and 5th on the visa, flow-shop, and TSP."),
 ("Our \\textbf{Discrete-MOHHO} is top-two on three of the four structures and the most stable of the matched methods, which is why we recommend it for single-run decisions even where perm-NSGA-II edges it on the mean.",
  "Our \\textbf{Discrete-MOHHO} is a strong, low-variance matched optimizer (the steadiest swarm), though permutation-NSGA-II is both the strongest and the steadiest matched method overall."),
 # Discussion
 ("and when a single dependable run matters---as in decision support---prefer the most stable optimizer, here Discrete-MOHHO.",
  "and when a single dependable run matters---as in decision support---prefer a low-variance matched optimizer, here permutation-NSGA-II (steadiest overall) or Discrete-MOHHO (steadiest swarm)."),
 # Conclusions
 ("the Discrete-MOHHO we introduce improves on classic MOHHO by $4.7\\,\\%$ ($p=9.3\\times10^{-10}$) and is the most stable optimizer of all (CV $0.54\\,\\%$), within $0.5\\,\\%$ of the best.",
  "the Discrete-MOHHO we introduce improves on classic MOHHO by $4.6\\,\\%$ ($p=9.3\\times10^{-10}$) and is the most stable \\emph{swarm} (CV $0.71\\,\\%$), within $0.5\\,\\%$ of the best (permutation-NSGA-II, the strongest and steadiest overall at CV $0.58\\,\\%$)."),
]

for fn in TARGETS:
    p = B / fn; s = p.read_text(); hits = 0; miss = []
    for i, (o, n) in enumerate(E):
        if o in s:
            s = s.replace(o, n); hits += 1
        elif n in s:
            pass  # already applied
        else:
            miss.append(i)
    p.write_text(s)
    print(f"{fn}: {hits}/{len(E)} applied; MISS edits {miss}")
