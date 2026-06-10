"""Genera MICAI/figures/mechanism_2x2.pdf (matplotlib, B&W-safe): x=operator tau,
y=realized moved fraction, marker verde si gana a random / rojo si no.
Numeros leidos de factorial_2x2_conditions.json + tau_by_method.json. Run desde backend/.

Sized for inclusion at 0.68\\textwidth (LNCS textwidth = 347pt); fonts below are
printed sizes. Win/lose is encoded twice (color AND marker shape) for B&W."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 7.5,
                     "axes.linewidth": 0.6, "savefig.bbox": "tight"})
R = Path("app/data/results")
FIG = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI/figures")
fac = json.load(open(R / "factorial_2x2_conditions.json"))
tau = json.load(open(R / "tau_by_method.json"))["methods"]
tau_order = tau["competent_mohho"]["tau_mean"]
tau_near = tau["nsga2_realcoded"]["tau_mean"]
GREEN, RED = "#1a7a3a", "#b00020"
PAPER_LABEL = {"order_nds": "order-changing + NDS",
               "order_gated": "order-changing + gated",
               "near_nds": "near-identity + NDS",
               "near_gated": "near-identity + gated"}

fig, ax = plt.subplots(figsize=(3.32, 2.42))
ax.set_xlim(-0.6, 1.15); ax.set_ylim(-0.1, 1.15)
# hint the four quadrants; tint the only favorable one (low tau, high movement)
ax.axvline(0.5, color="grey", lw=0.5, ls=":")
ax.axhline(0.5, color="grey", lw=0.5, ls=":")
ax.axvspan(-0.6, 0.5, ymin=(0.5 + 0.1) / 1.25, color=GREEN, alpha=0.055, lw=0)
ax.text(-0.575, 0.545, "both conditions met", fontsize=6.3, color=GREEN,
        ha="left", va="bottom", style="italic")
HEAD2 = {"order_nds": "order-changing\n+ NDS",
         "order_gated": "order-changing\n+ gated",
         "near_nds": "near-identity\n+ NDS",
         "near_gated": "near-identity\n+ gated"}
for name, cell in fac["cells"].items():
    x = tau_order if cell["operator"] == "order" else tau_near
    y = cell["moved_fraction_mean"]
    win = cell["beats_random"]
    right = x > 0.5                       # keep labels inside the frame
    top = y > 0.5
    dx = -9 if right else 9
    ha = "right" if right else "left"
    ax.scatter(x, y, s=85, c=(GREEN if win else RED), marker=("o" if win else "X"),
               edgecolors="k", linewidths=0.5, zorder=3)
    block = HEAD2[name] + "\n" + f"HV {cell['hv_mean']:,.0f}" + \
        ("\nbeats blind sampling" if win else "")
    # blocks hang below the top markers and sit above the bottom ones
    ax.annotate(block, (x, y), textcoords="offset points",
                xytext=(dx, 3 if top else -1), fontsize=6.6,
                ha=ha, va="top" if top else "bottom", linespacing=1.25,
                color=("#145A32" if win else "0.20"))
ax.set_xlabel("operator order-preservation $\\tau$\n(low $=$ changes the decoded order)",
              fontsize=7.2, linespacing=1.3)
ax.set_ylabel("Realized population movement / iter", fontsize=7.3)
ax.tick_params(labelsize=6.8, length=2, pad=2)
ax.spines[["top", "right"]].set_visible(False)
FIG.mkdir(parents=True, exist_ok=True)
fig.savefig(FIG / "mechanism_2x2.pdf"); fig.savefig(FIG / "mechanism_2x2.png", dpi=300)
print("saved mechanism_2x2.pdf | tau_order=%.3f tau_near=%.3f" % (tau_order, tau_near))
