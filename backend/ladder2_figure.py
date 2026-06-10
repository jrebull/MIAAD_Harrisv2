"""The 'ladder2' figure: per-run hypervolume for seven methods on the MOMKP
(second, structurally distinct problem; same budget, 30 seeds). Mirrors
ladder_figure.py but reads second_problem.json plus the competent MO-HHO
per-seed HV from structures_v6.json. On the knapsack the competent random-key
swarm is the single best method (mean rank 1.13 of 7), so the divide is
non-degenerate search, not the encoding.  -> ../MICAI/figures/ladder2.pdf

Sized for inclusion at 0.78\\textwidth (LNCS textwidth = 347pt); fonts below are
printed sizes. Method colors shared with ladder.pdf (unified palette).
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
M = json.load(open(R / "second_problem.json"))["methods"]
comp = json.load(open(R / "structures_v6.json"))["structures"]["knapsack"]["competent_hv_per_seed"]

order = ["NSGA-II (real-coded)", "Random restart", "MOHHO (real-coded)", None,
         "Discrete-MOHHO", "perm-MOEA/D", "perm-NSGA-II"]
data = [np.array(M[k]["per_run_hv"]) if k else np.array(comp) for k in order]
labels = ["NSGA-II\n(real-coded)", "Random\nrestart", "MOHHO\n(real-coded)",
          "Competent\nMO-HHO", "Discrete-\nMOHHO", "perm-\nMOEA/D", "perm-\nNSGA-II"]
# unified method palette (see ladder_figure.py)
cols = ["#E67E22", "#9AA3AF", "#2E86DE", "#8E44AD", "#1F618D", "#16A085", "#27AE60"]

fig, ax = plt.subplots(figsize=(3.80, 1.55))
parts = ax.violinplot(data, positions=range(1, 8), showmeans=False,
                      showextrema=False, widths=0.85)
for b, c in zip(parts["bodies"], cols):
    b.set_facecolor(c); b.set_alpha(0.30); b.set_edgecolor(c)
bp = ax.boxplot(data, positions=range(1, 8), widths=0.34, patch_artist=True,
                showfliers=True, medianprops=dict(color="k", lw=0.8),
                boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6),
                capprops=dict(lw=0.6),
                flierprops=dict(marker="o", ms=2.2, markeredgewidth=0.5))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.65)
ax.set_xticks(range(1, 8))
ax.set_xticklabels([l if i % 2 == 0 else "\n\n" + l
                    for i, l in enumerate(labels)], fontsize=6.5, linespacing=1.05)
ax.tick_params(axis="x", length=2, pad=1.5)
ax.tick_params(axis="y", labelsize=6.8, length=2, pad=1.5)
ax.set_ylabel("Hypervolume (normalized)", fontsize=7.3, labelpad=2)
ax.axvspan(0.5, 4.5, color="#E67E22", alpha=0.05)
ax.axvspan(4.5, 7.5, color="#2E86DE", alpha=0.05)
ax.set_ylim(0.172, 0.293)
lo = ax.get_ylim()[0]
ax.text(2.5, lo + 0.0018, "random-key encoding", ha="center", va="bottom",
        fontsize=6.3, color="#9C5410")
ax.text(6.0, lo + 0.0018, "permutation-native (3 paradigms)", ha="center",
        va="bottom", fontsize=6.3, color="#1B5E9C")
# single best method on this structure: the competent random-key swarm
ax.annotate("best here\n(mean rank 1.13)", xy=(4.0, float(np.max(data[3])) + 0.002),
            xytext=(2.95, 0.2855), fontsize=6.0, color="0.30", style="italic",
            ha="right", va="top",
            arrowprops=dict(arrowstyle="-", color="0.45", lw=0.6,
                            shrinkA=1, shrinkB=1))
ax.grid(axis="y", alpha=0.22, lw=0.4)
fig.savefig("../MICAI/figures/ladder2.pdf"); fig.savefig("../MICAI/figures/ladder2.png", dpi=300)
print("saved MOMKP ladder2 (7 methods) | means:",
      [f"{float(np.mean(x)):.4f}" for x in data])
