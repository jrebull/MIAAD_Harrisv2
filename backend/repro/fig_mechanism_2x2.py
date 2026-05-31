"""Genera MICAI/figures/mechanism_2x2.pdf (matplotlib, B&W-safe): x=operator tau,
y=realized moved fraction, marker verde si gana a random / rojo si no.
Numeros leidos de factorial_2x2_conditions.json + tau_by_method.json. Run desde backend/."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path("app/data/results")
FIG = Path("/Users/haowei/Documents/MIAAD/SMART/Harris2/MICAI/figures")
fac = json.load(open(R / "factorial_2x2_conditions.json"))
tau = json.load(open(R / "tau_by_method.json"))["methods"]
tau_order = tau["competent_mohho"]["tau_mean"]
tau_near = tau["nsga2_realcoded"]["tau_mean"]
GREEN, RED = "#1a7a3a", "#b00020"

fig, ax = plt.subplots(figsize=(5.6, 4.2))
for name, cell in fac["cells"].items():
    x = tau_order if cell["operator"] == "order" else tau_near
    y = cell["moved_fraction_mean"]
    win = cell["beats_random"]
    ax.scatter(x, y, s=170, c=(GREEN if win else RED), marker=("o" if win else "X"),
               edgecolors="k", linewidths=0.6, zorder=3)
    ax.annotate(name, (x, y), textcoords="offset points", xytext=(9, 6), fontsize=8.3)
ax.axvline(0.5, color="grey", lw=0.6, ls=":"); ax.axhline(0.5, color="grey", lw=0.6, ls=":")
ax.set_xlabel(r"operator order-preservation $\tau$  (low $=$ changes decoded order)", fontsize=9)
ax.set_ylabel("realized population movement / iter", fontsize=9)
ax.set_xlim(-0.6, 1.15); ax.set_ylim(-0.1, 1.15)
ax.set_title("Two conditions isolated (2x2): only the low-tau,\nhigh-movement cell beats random", fontsize=9.5)
fig.tight_layout()
FIG.mkdir(parents=True, exist_ok=True)
fig.savefig(FIG / "mechanism_2x2.pdf"); fig.savefig(FIG / "mechanism_2x2.png", dpi=200)
print("saved mechanism_2x2.pdf | tau_order=%.3f tau_near=%.3f" % (tau_order, tau_near))
