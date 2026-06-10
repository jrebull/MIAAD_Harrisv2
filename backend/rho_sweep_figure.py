"""Figure for the clean dose-response sweep: panel (a) mean HV as a percentage of
each structure's stored random-restart mean, against the measured per-level tau
(one curve per structure; 100% line = blind sampling); panel (b) per-run IGD+
(normalized to each structure's own sweep maximum) against tau, to show the
gradient direction agrees under a second metric.  -> ../MICAI/figures/rho_sweep.pdf
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
d = json.load(open(R / "rho_sweep.json"))["structures"]

STYLE = {
    "visa":     ("#2E86DE", "o", "-",  "visa"),
    "knapsack": ("#8E44AD", "s", "-",  "knapsack"),
    "tsp":      ("#16A085", "^", "--", "TSP"),
    "flowshop": ("#E67E22", "v", "--", "flow-shop"),
    "scp":      ("#C0392B", "D", "--", "set covering"),
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.4))
for s, (c, m, ls, lab) in STYLE.items():
    taus = d[s]["tau_levels"]
    hv = np.array(d[s]["hv_mean_levels"]) / d[s]["random_mean"] * 100
    ax1.plot(taus, hv, ls, marker=m, ms=4, lw=1.2, color=c, label=lab)
ax1.axhline(100, color="k", lw=1.0, ls=":")
ax1.text(0.985, 100, "blind sampling", fontsize=7.5, va="bottom", ha="right")
ax1.set_xlabel(r"operator order-preservation $\tau$ (per level)")
ax1.set_ylabel("mean HV (% of random restart)")
ax1.grid(alpha=0.25); ax1.legend(fontsize=7.5, loc="best", framealpha=0.9)
ax1.set_title("(a) hypervolume", fontsize=9)

for s, (c, m, ls, lab) in STYLE.items():
    taus = d[s]["tau_levels"]
    igd = np.array(d[s]["igd_plus_mean_levels"])
    igd = igd / igd.max()
    ax2.plot(taus, igd, ls, marker=m, ms=4, lw=1.2, color=c, label=lab)
ax2.set_xlabel(r"operator order-preservation $\tau$ (per level)")
ax2.set_ylabel(r"mean IGD$^{+}$ (relative to sweep max)")
ax2.grid(alpha=0.25)
ax2.set_title(r"(b) IGD$^{+}$ vs pooled sweep reference", fontsize=9)

fig.savefig("../MICAI/figures/rho_sweep.pdf")
fig.savefig("../MICAI/figures/rho_sweep.png", dpi=200)
print("saved rho_sweep.pdf")
for s in STYLE:
    print(f"{s}: Spearman(tau,HV)={d[s]['spearman_tau_hv']:.3f} "
          f"IGD={d[s]['spearman_tau_igd']:.3f} crossing={d[s]['crossing_tau']} "
          f"above_all={d[s]['above_random_at_all_levels']}")
