"""Figure for the clean dose-response sweep: panel (a) mean HV as a percentage of
each structure's stored random-restart mean, against the measured per-level tau
(one curve per structure; 100% line = blind sampling); panel (b) per-run IGD+
(normalized to each structure's own sweep maximum) against tau, to show the
gradient direction agrees under a second metric.  -> ../MICAI/figures/rho_sweep.pdf

Sized for inclusion at \\textwidth (LNCS textwidth = 347pt); fonts below are
printed sizes.
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
d = json.load(open(R / "rho_sweep.json"))["structures"]

STYLE = {
    "visa":     ("#2E86DE", "o", "-",  "visa"),
    "knapsack": ("#8E44AD", "s", "-",  "knapsack"),
    "tsp":      ("#16A085", "^", "--", "TSP"),
    "flowshop": ("#E67E22", "v", "--", "flow-shop"),
    "scp":      ("#C0392B", "D", "--", "set covering"),
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.95, 2.18))
for s, (c, m, ls, lab) in STYLE.items():
    taus = d[s]["tau_levels"]
    hv = np.array(d[s]["hv_mean_levels"]) / d[s]["random_mean"] * 100
    ax1.plot(taus, hv, ls, marker=m, ms=2.8, lw=0.9, color=c, label=lab)
ax1.axhline(100, color="k", lw=0.8, ls=":")
ax1.set_ylim(92.5, 166)
ax1.annotate("blind sampling", xy=(0.475, 99.6), xytext=(0.518, 94.0),
             fontsize=6.3, ha="left", va="center", color="0.15",
             arrowprops=dict(arrowstyle="-", color="0.4", lw=0.6,
                             shrinkA=1, shrinkB=1))
# the one visible dose effect in HV: the knapsack falls only at tau = 1
kx = d["knapsack"]["tau_levels"][-1]
ky = d["knapsack"]["hv_mean_levels"][-1] / d["knapsack"]["random_mean"] * 100
ax1.annotate("drop only\nat $\\tau=1$", xy=(kx, ky + 1.2), xytext=(0.93, 131),
             fontsize=6.3, color="#6C3483", ha="center", va="top",
             arrowprops=dict(arrowstyle="-", color="#8E44AD", lw=0.6,
                             shrinkA=1, shrinkB=2))
ax1.set_xlabel(r"operator order-preservation $\tau$ (per level)", fontsize=7.2)
ax1.set_ylabel("Mean HV (% of random restart)", fontsize=7.3)
ax1.tick_params(labelsize=6.8, length=2, pad=2)
ax1.grid(alpha=0.25, lw=0.4)
ax1.legend(fontsize=6.3, loc="center left", bbox_to_anchor=(0.02, 0.42),
           framealpha=0.9, handlelength=1.7, labelspacing=0.3,
           borderpad=0.4, edgecolor="0.8")
ax1.set_title("(a) hypervolume", fontsize=7.5)

for s, (c, m, ls, lab) in STYLE.items():
    taus = d[s]["tau_levels"]
    igd = np.array(d[s]["igd_plus_mean_levels"])
    igd = igd / igd.max()
    ax2.plot(taus, igd, ls, marker=m, ms=2.8, lw=0.9, color=c, label=lab)
ax2.set_xlabel(r"operator order-preservation $\tau$ (per level)", fontsize=7.2)
ax2.set_ylabel(r"Mean IGD$^{+}$ (relative to sweep max)", fontsize=7.3)
ax2.tick_params(labelsize=6.8, length=2, pad=2)
ax2.grid(alpha=0.25, lw=0.4)
ax2.set_title(r"(b) IGD$^{+}$ vs pooled sweep reference", fontsize=7.5)
for a in (ax1, ax2):
    a.spines[["top", "right"]].set_visible(False)
fig.subplots_adjust(wspace=0.30)

fig.savefig("../MICAI/figures/rho_sweep.pdf")
fig.savefig("../MICAI/figures/rho_sweep.png", dpi=300)
print("saved rho_sweep.pdf")
for s in STYLE:
    print(f"{s}: Spearman(tau,HV)={d[s]['spearman_tau_hv']:.3f} "
          f"IGD={d[s]['spearman_tau_igd']:.3f} crossing={d[s]['crossing_tau']} "
          f"above_all={d[s]['above_random_at_all_levels']}")
