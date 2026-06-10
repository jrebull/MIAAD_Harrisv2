"""The 'ladder2' figure: per-run hypervolume for seven methods on the MOMKP
(second, structurally distinct problem; same budget, 30 seeds). Mirrors
ladder_figure.py but reads second_problem.json plus the competent MO-HHO
per-seed HV from structures_v6.json. On the knapsack the competent random-key
swarm is the single best method (mean rank 1.13 of 7), so the divide is
non-degenerate search, not the encoding.  -> ../MICAI/figures/ladder2.pdf
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 9, "savefig.bbox": "tight"})
R = Path("app/data/results")
M = json.load(open(R / "second_problem.json"))["methods"]
comp = json.load(open(R / "structures_v6.json"))["structures"]["knapsack"]["competent_hv_per_seed"]

order = ["NSGA-II (real-coded)", "Random restart", "MOHHO (real-coded)", None,
         "Discrete-MOHHO", "perm-MOEA/D", "perm-NSGA-II"]
data = [np.array(M[k]["per_run_hv"]) if k else np.array(comp) for k in order]
labels = ["NSGA-II\n(real-coded)", "Random\nrestart", "MOHHO\n(real-coded)",
          "Competent\nMO-HHO", "Discrete-\nMOHHO", "perm-\nMOEA/D", "perm-\nNSGA-II"]
cols = ["#E67E22", "#9AA3AF", "#E8B04B", "#8E44AD", "#2E86DE", "#16A085", "#27AE60"]

fig, ax = plt.subplots(figsize=(7.6, 3.5))
parts = ax.violinplot(data, positions=range(1, 8), showmeans=False,
                      showextrema=False, widths=0.85)
for b, c in zip(parts["bodies"], cols):
    b.set_facecolor(c); b.set_alpha(0.30); b.set_edgecolor(c)
bp = ax.boxplot(data, positions=range(1, 8), widths=0.34, patch_artist=True,
                showfliers=True, medianprops=dict(color="k", lw=1.1))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.65)
ax.set_xticks(range(1, 8)); ax.set_xticklabels(labels, fontsize=7.2)
ax.set_ylabel("Hypervolume (normalized)")
ax.axvspan(0.5, 4.5, color="#E67E22", alpha=0.05)
ax.axvspan(4.5, 7.5, color="#2E86DE", alpha=0.05)
lo = ax.get_ylim()[0]
ax.text(2.5, lo, "random-key encoding", ha="center", va="bottom", fontsize=7.5, color="#9C5410")
ax.text(6.0, lo, "permutation-native (3 paradigms)", ha="center", va="bottom", fontsize=7.5, color="#1B5E9C")
ax.grid(axis="y", alpha=0.25)
fig.savefig("../MICAI/figures/ladder2.pdf"); fig.savefig("../MICAI/figures/ladder2.png", dpi=200)
print("saved MOMKP ladder2 (7 methods) | means:",
      [f"{float(np.mean(x)):.4f}" for x in data])
