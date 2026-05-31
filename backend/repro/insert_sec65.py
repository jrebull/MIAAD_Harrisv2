"""Inserta §6.5 (factorial 2x2) en los 4 .tex con numeros LEIDOS del JSON.
Todos los valores se formatean a strings ANTES de construir el LaTeX (sin logica
en f-strings). Full: prosa+tabla+figura. Reducida: prosa+tabla."""
import json
from math import floor, log10
from pathlib import Path

BASE = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI")
d = json.load(open("app/data/results/factorial_2x2_conditions.json"))
c = d["cells"]; a = d["anova"]; rnd = d["random_restart"]["hv_mean"]
on, og, nn, ng = c["order_nds"], c["order_gated"], c["near_nds"], c["near_gated"]


def hv(x):
    return "$" + f"{x:,.0f}".replace(",", "{,}") + "$"


def pct(x):
    return f"${x:+.2f}\\,\\%$"


def psci(p):
    if p < 1e-3:
        e = floor(log10(p)); m = p / 10 ** e
        return f"{m:.1f}\\times10^{{{e}}}"
    return f"{p:.2f}"


# precompute every string
on_hv, og_hv, nn_hv, ng_hv, r_hv = hv(on["hv_mean"]), hv(og["hv_mean"]), hv(nn["hv_mean"]), hv(ng["hv_mean"]), hv(rnd)
on_pct, og_pct, nn_pct, ng_pct = pct(on["vs_random_pct"]), pct(og["vs_random_pct"]), pct(nn["vs_random_pct"]), pct(ng["vs_random_pct"])
on_a, og_a, nn_a, ng_a = f"{on['A12_vs_random']:.2f}", f"{og['A12_vs_random']:.2f}", f"{nn['A12_vs_random']:.2f}", f"{ng['A12_vs_random']:.2f}"
on_p = psci(on["mwu_p_greater_random"])
gated_move_pct = f"{og['moved_fraction_mean'] * 100:.1f}"
eta_op, eta_sel, eta_int = f"{a['eta2_operator_A']:.3f}", f"{a['eta2_selection_B']:.3f}", f"{a['eta2_interaction_AxB']:.3f}"
F_int = f"{a['F_interaction']:.1f}"
p_int = psci(a["p_interaction"])
# single-condition loss range (abs of the two single-condition cells)
losses = sorted(abs(x) for x in (og["vs_random_pct"], nn["vs_random_pct"]))
loss_lo, loss_hi = f"{losses[0]:.1f}", f"{losses[1]:.1f}"

ANCHOR = r"\subsection{Generalization across instances}"

PROSE = (
    r"\subsection{Isolating the two conditions: a controlled $2\times2$}" "\n"
    r"\label{sec:twoconditions}" "\n"
    r"The seven-method ladder establishes the two-condition rule by observation; we now isolate each condition with a controlled $2\times2$ on a single real-coded random-key skeleton---same greedy decoder, instance, $25{,}000$-evaluation budget, and 30 seeds---varying only the \emph{operator} (order-changing HHO moves with mutation, $\tau\!\approx\!0$, versus near-identity SBX, $\tau\!=\!0.99$) and the \emph{selection} (diversity-preserving non-dominated sorting versus dominance-gated acceptance). "
    r"Table~\ref{tab:factorial2x2} shows that \textbf{only the cell satisfying both conditions beats blind random restart} ("
    + on_hv + r" versus " + r_hv + r"~\HV, " + on_pct + r", Mann--Whitney $p=" + on_p + r"$, $A_{12}=" + on_a + r"$); dropping \emph{either} condition falls below blind sampling. "
    r"Gated acceptance freezes the population (only $" + gated_move_pct + r"\,\%$ of individuals move per iteration), and near-identity SBX leaves the decoded order almost unchanged even when the population does move. "
    r"Crucially, the two conditions are \emph{synergistic, not additive}: a two-factor analysis of variance finds a significant operator$\times$selection interaction ($\eta^2=" + eta_int + r"$, $F=" + F_int + r"$, $p=" + p_int + r"$), alongside main effects of $\eta^2=" + eta_op + r"$ (operator) and $\eta^2=" + eta_sel + r"$ (selection). "
    r"Neither condition alone lifts performance above blind sampling---both single-condition cells lose by $" + loss_lo + r"$--$" + loss_hi + r"\,\%$---so the gain is genuinely a joint effect of changing the decoded order \emph{and} preserving diversity. %FIGREF%" "\n\n"
)

FIGREF = (r"Figure~\ref{fig:mech2x2} maps each cell onto its operator $\tau$ and realized "
          r"population movement, isolating the winning cell in the low-$\tau$, high-movement corner.")

TABLE = (
    r"\begin{table}[t]" "\n" r"\centering" "\n"
    r"\caption{Controlled $2\times2$ isolating the two conditions on one real-coded random-key skeleton (visa decoder, 30 seeds, $25{,}000$ evaluations). Only the cell that both changes the decoded order and preserves diversity beats blind random restart (" + r_hv + r"~\HV); the operator$\times$selection interaction is significant. Best in bold.}" "\n"
    r"\label{tab:factorial2x2}" "\n" r"\small" "\n"
    r"\begin{tabular}{llrrr}" "\n" r"\toprule" "\n"
    r"\textbf{Operator} & \textbf{Selection} & \textbf{Mean \HV} & \textbf{vs.\ random} & \textbf{$A_{12}$}\\" "\n"
    r"\midrule" "\n"
    r"order-changing ($\tau\!\approx\!0$) & diversity (NDS) & $\mathbf{" + on_hv.strip("$") + r"}$ & $\mathbf{" + on_pct.strip("$") + r"}$ & $\mathbf{" + on_a + r"}$\\" "\n"
    r"order-changing ($\tau\!\approx\!0$) & gated            & " + og_hv + r" & " + og_pct + r" & $" + og_a + r"$\\" "\n"
    r"near-identity ($\tau\!=\!0.99$)     & diversity (NDS) & " + nn_hv + r" & " + nn_pct + r" & $" + nn_a + r"$\\" "\n"
    r"near-identity ($\tau\!=\!0.99$)     & gated            & " + ng_hv + r" & " + ng_pct + r" & $" + ng_a + r"$\\" "\n"
    r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n"
)

FIGURE = (
    r"\begin{figure}[t]" "\n" r"\centering" "\n"
    r"\includegraphics[width=0.68\textwidth]{mechanism_2x2.pdf}" "\n"
    r"\caption{Mechanism of the two conditions across the $2\times2$ cells: operator order-preservation $\tau$ (x) versus realized population movement per iteration (y), bubble height encoding \HV. Only the order-changing, diversity-preserving cell occupies the favorable low-$\tau$, high-movement corner and beats blind sampling.}" "\n"
    r"\label{fig:mech2x2}" "\n" r"\end{figure}" "\n"
)

for fn in ["main_submission.tex", "main.tex", "main_reducida_submission.tex", "main_reducida.tex"]:
    p = BASE / fn; s = p.read_text()
    if "tab:factorial2x2" in s:
        print(fn, "already inserted"); continue
    if ANCHOR not in s:
        print(fn, "ANCHOR MISS"); continue
    full = fn in ("main_submission.tex", "main.tex")
    prose = PROSE.replace("%FIGREF%", FIGREF if full else "")
    block = prose + TABLE + (FIGURE if full else "") + "\n"
    s = s.replace(ANCHOR, block + ANCHOR, 1)
    p.write_text(s)
    print(fn, "inserted full=" + str(full))
