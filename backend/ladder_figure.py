"""The 'ladder' figure: per-run hypervolume for all nine methods on the base
instance (same 25k-eval budget, same feasibility-preserving decoder), ordered to
show that the representation-operator match -- not the metaheuristic family --
governs performance. Four permutation-native paradigms (swarm, decomposition,
strength-Pareto, GA) cluster at the top. -> ../MICAI/figures/ladder.pdf

Sized for inclusion at 0.71\\textwidth (LNCS textwidth = 347pt): the figure is
generated at its final physical size, so the fonts below are the printed sizes.
Method colors are shared with ladder2.pdf and the other figures (MOHHO blue,
NSGA-II orange, random restart grey, perm-NSGA-II green, ...).
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 7.5,
                     "axes.linewidth": 0.6, "savefig.bbox": "tight"})
R = Path("app/data/results")
st = json.load(open(R / "stats_test.json"))
brk = json.load(open(R / "brkga_ladder.json"))
ctl = json.load(open(R / "controls.json"))
lv5 = json.load(open(R / "ladder_v5.json"))
comp100 = json.load(open(R / "competent_arch100.json"))  # correccion archivo 200->100
md = json.load(open(R / "perm_moead.json"))
dm = json.load(open(R / "discrete_mohho.json"))
sp = json.load(open(R / "perm_spea2.json"))
pn = json.load(open(R / "perm_nsga.json"))

data = [np.array(st["nsga2_hv"]) / 1e6,
        np.array(st["mohho_hv"]) / 1e6,
        np.array(brk["hv_per_seed"]) / 1e6,
        np.array(ctl["random_restart"]["per_seed_hv"]) / 1e6,
        np.array(comp100["hv_per_seed_arch100"]) / 1e6,
        np.array(md["per_run_hv"]) / 1e6,
        np.array(dm["per_run_hv"]) / 1e6,
        np.array(sp["per_run_hv"]) / 1e6,
        np.array(pn["per_run_hv"]) / 1e6]
labels = ["NSGA-II\n(real-coded)", "MOHHO\n(real-coded)", "rk-NSGA-II\n(biased unif.)",
          "Random\nrestart", "NDS-selected\nMO-HHO",
          "perm-\nMOEA/D", "Discrete-\nMOHHO", "perm-\nSPEA2", "perm-\nNSGA-II"]
# unified method palette (see ladder2_figure.py / paper_figures.py)
cols = ["#E67E22", "#2E86DE", "#D68910", "#9AA3AF", "#8E44AD",
        "#16A085", "#1F618D", "#56B4E9", "#27AE60"]
rr_mean = float(np.mean(data[3]))          # blind random-restart mean (310,214)

fig, ax = plt.subplots(figsize=(3.62, 1.42))
parts = ax.violinplot(data, positions=range(1, 10), showmeans=False,
                      showextrema=False, widths=0.85)
for b, c in zip(parts["bodies"], cols):
    b.set_facecolor(c); b.set_alpha(0.30); b.set_edgecolor(c)
bp = ax.boxplot(data, positions=range(1, 10), widths=0.34, patch_artist=True,
                showfliers=True, medianprops=dict(color="k", lw=0.8),
                boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6),
                capprops=dict(lw=0.6),
                flierprops=dict(marker="o", ms=2.2, markeredgewidth=0.5))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.65)
# stagger the two-line labels on two levels so 7 pt type fits nine columns
ax.set_xticks(range(1, 10))
ax.set_xticklabels([l if i % 2 == 0 else "\n\n" + l
                    for i, l in enumerate(labels)], fontsize=6.3, linespacing=1.05)
ax.tick_params(axis="x", length=2, pad=1.5)
ax.tick_params(axis="y", labelsize=6.8, length=2, pad=1.5)
ax.set_ylabel(r"Hypervolume ($\times 10^{6}$)", fontsize=9.2, labelpad=2)
# blind-sampling reference: random-restart mean across the whole ladder
ax.axhline(rr_mean, color="0.35", ls="--", lw=0.7, zorder=1)
ax.text(9.42, rr_mean - 0.0008, "random-restart mean", ha="right", va="top",  # 6.4pt nativos -> >=6 efectivos
        fontsize=6.4, color="0.30", style="italic")
ax.axvspan(0.5, 5.5, color="#E67E22", alpha=0.05)
ax.axvspan(5.5, 9.5, color="#2E86DE", alpha=0.05)
ax.set_ylim(0.272, 0.3295)
lo = ax.get_ylim()[0]
ax.text(3.0, lo + 0.0008, "random-key encoding", ha="center", va="bottom",
        fontsize=6.3, color="#9C5410")
ax.text(7.5, lo + 0.0008, "permutation-native (4 paradigms)", ha="center",
        va="bottom", fontsize=6.3, color="#1B5E9C")
# top tier: NDS-selected MO-HHO + the four permutation-native paradigms
yb = 0.3262
ax.plot([4.62, 9.38], [yb, yb], color="0.45", lw=0.6)
ax.plot([4.62, 4.62], [yb, yb - 0.0012], color="0.45", lw=0.6)
ax.plot([9.38, 9.38], [yb, yb - 0.0012], color="0.45", lw=0.6)
ax.text(7.0, yb + 0.0006, "top tier", ha="center", va="bottom",
        fontsize=6.4, color="0.30", style="italic",
        bbox=dict(fc="white", ec="none", pad=0.4))
ax.set_yticks([0.28, 0.29, 0.30, 0.31, 0.32])
ax.grid(axis="y", alpha=0.22, lw=0.4)
import os
OUT = os.environ.get("FIGDIR", "../MICAI/figures")
fig.savefig(f"{OUT}/ladder.pdf"); fig.savefig(f"{OUT}/ladder.png", dpi=300)
print("FIGDIR =", OUT)
print("saved 9-method ladder | means:", [f"{float(np.mean(x))*1e6:,.0f}" for x in data],
      f"| rr_mean={rr_mean*1e6:,.0f}")
