"""
Publication figures for the MICAI/LNCS paper. English labels, vectorial PDF
(plus PNG backup), serif fonts to match the Springer LNCS body text.

Reads only released artifacts (CSV/JSON in app/data/results) so every figure is
reproducible. Outputs to ../MICAI/figures/.

Figures:
  convergence.pdf     HV mean +/- std vs iteration (30 runs), early-saturation markers
  pareto3d.pdf        combined Pareto front in (f1,f2,f3), colored by f3, FIFO star
  pareto_f1f2.pdf     f1-f2 projection colored by f3 (waste), FIFO dominated
  hv_box.pdf          HV distribution MOHHO vs NSGA-II (30 runs each) + test annotation
  nsga2_overlay.pdf   MOHHO vs NSGA-II combined fronts in f1-f2 (if nsga2_front.json)
"""
import json
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

# Figures are generated at their FINAL physical size in the paper (LNCS
# textwidth = 347pt): convergence at 0.72\textwidth, nsga2_overlay at
# 0.62\textwidth, pareto_f1f2 at 0.49\textwidth. Fonts below are printed sizes.
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "axes.linewidth": 0.6,
    "legend.fontsize": 7,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.major.pad": 2,
    "ytick.major.pad": 2,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})

R = Path("app/data/results")
import os as _os
# FIGDIR evita sobrescribir MICAI/figures/, que esta CONGELADO en el envio
FIG = Path(_os.environ.get("FIGDIR", "../MICAI/figures"))
FIG.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, RED, GREY = "#2E86DE", "#E67E22", "#E74C3C", "#9AA3AF"
millions = FuncFormatter(lambda x, _: f"{x/1e6:.3f}")
# viridis truncated at 0.85 (drops the pale-yellow extreme, invisible in print),
# reversed to keep the original viridis_r orientation (low f3 -> light, high -> dark)
VIRIDIS_T_R = LinearSegmentedColormap.from_list(
    "viridis_t_r", plt.cm.viridis(np.linspace(0.85, 0.0, 256)))


def load_front():
    pareto, fifo = [], None
    for row in csv.DictReader(open(R / "pareto_front.csv")):
        pt = (float(row["f1"]), float(row["f2"]), float(row["f3"]))
        if row["type"] == "pareto":
            pareto.append(pt)
        else:
            fifo = pt
    return np.array(pareto), fifo


def fig_convergence():
    it, mean, std = [], [], []
    for row in csv.DictReader(open(R / "convergence.csv")):
        it.append(int(row["iteration"]))
        mean.append(float(row["hv_mean"]))
        std.append(float(row["hv_std"]))
    it, mean, std = np.array(it), np.array(mean), np.array(std)
    fig, ax = plt.subplots(figsize=(3.55, 2.05))
    ax.fill_between(it, mean - std, mean + std, color=BLUE, alpha=0.18,
                    label=r"$\pm 1$ s.d. (30 runs)")
    ax.plot(it, mean, color=BLUE, lw=1.3, label="mean hypervolume")
    final = mean[-1]
    for frac, lab in [(0.95, "95\u2009%"), (0.99, "99\u2009%")]:
        idx = int(np.argmax(mean >= frac * final))
        ax.axvline(idx, color=GREY, ls=":", lw=0.8)
        ax.text(idx + 7, 0.3082e6, f"{lab} @ it.\u2009{idx}", fontsize=6.8,
                color="#555", ha="left", va="bottom")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Hypervolume")
    ax.yaxis.set_major_formatter(millions)
    ax.text(0.015, 1.02, r"$\times 10^{6}$", transform=ax.transAxes, fontsize=6.8)
    ax.set_xlim(0, it.max())
    ax.legend(loc="lower right", framealpha=0.92, handlelength=1.4,
              borderpad=0.4, labelspacing=0.3)
    ax.grid(alpha=0.25, lw=0.4)
    save(fig, "convergence")


def fig_pareto3d():
    P, fifo = load_front()
    fig = plt.figure(figsize=(5.4, 4.4))
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(P[:, 0], P[:, 1], P[:, 2], c=P[:, 2], cmap="viridis_r",
                    s=14, alpha=0.85, edgecolors="none")
    ax.scatter([fifo[0]], [fifo[1]], [fifo[2]], marker="*", s=170, c=RED,
               edgecolors="k", linewidths=0.5, label="FIFO baseline")
    # extreme solutions
    for m, lab in [(0, "min $f_1$"), (1, "min $f_2$"), (2, "min $f_3$")]:
        e = P[np.argmin(P[:, m])]
        ax.scatter([e[0]], [e[1]], [e[2]], s=55, facecolors="none",
                   edgecolors="k", linewidths=1.0)
    ax.set_xlabel(r"$f_1$  waiting load", labelpad=2)
    ax.set_ylabel(r"$f_2$  disparity (yr)", labelpad=2)
    ax.set_zlabel(r"$f_3$  waste (visas)", labelpad=2)
    ax.view_init(elev=22, azim=-58)
    cb = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.10)
    cb.set_label(r"$f_3$ (wasted visas)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    ax.legend(loc="upper left", fontsize=7.5)
    save(fig, "pareto3d")


def fig_pareto_f1f2():
    P, fifo = load_front()
    fig, ax = plt.subplots(figsize=(2.42, 1.62))
    sc = ax.scatter(P[:, 0], P[:, 1], c=P[:, 2], cmap=VIRIDIS_T_R, s=7,
                    alpha=0.85, edgecolors="#333333", linewidths=0.2)
    ax.scatter([fifo[0]], [fifo[1]], marker="*", s=75, c=RED, edgecolors="k",
               linewidths=0.4, zorder=5)
    # direct label instead of a legend (a legend box would cover the star here)
    ax.annotate("FIFO baseline\n(dominated)", xy=(fifo[0], fifo[1]),
                xytext=(6, -2), textcoords="offset points", fontsize=6.3,
                color="#7B241C", ha="left", va="top")
    ax.set_xlabel(r"$f_1$ — unserved waiting load", fontsize=8.6)
    ax.set_ylabel(r"$f_2$ — disparity (yr)", fontsize=8.6)
    ax.set_xticks([8.80, 8.85, 8.90, 8.95, 9.00])
    ax.set_yticks([2, 4, 6, 8, 10, 12])
    ax.set_ylim(1.4, 13.9)
    ax.tick_params(labelsize=6.8)
    cb = fig.colorbar(sc, ax=ax, pad=0.03)
    cb.set_label(r"$f_3$ — wasted visas", fontsize=8.6)
    cb.ax.tick_params(labelsize=6.8, length=2, pad=2)
    cb.outline.set_linewidth(0.6)
    ax.grid(alpha=0.25, lw=0.4)
    save(fig, "pareto_f1f2")


def fig_hv_box():
    st = json.load(open(R / "stats_test.json"))
    mh = np.array(st["mohho_hv"]) / 1e6
    ng = np.array(st["nsga2_hv"]) / 1e6
    fig, ax = plt.subplots(figsize=(4.0, 3.2))
    parts = ax.violinplot([ng, mh], positions=[1, 2], showmeans=False,
                          showextrema=False, widths=0.8)
    for b, c in zip(parts["bodies"], [ORANGE, BLUE]):
        b.set_facecolor(c)
        b.set_alpha(0.30)
        b.set_edgecolor(c)
    bp = ax.boxplot([ng, mh], positions=[1, 2], widths=0.32, patch_artist=True,
                    showfliers=True, medianprops=dict(color="k", lw=1.2))
    for patch, c in zip(bp["boxes"], [ORANGE, BLUE]):
        patch.set_facecolor(c)
        patch.set_alpha(0.65)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["NSGA-II", "MOHHO"])
    ax.set_ylabel(r"Hypervolume ($\times 10^{6}$)")
    p = st["p_one_sided"]
    a12 = st["A12"]
    ax.set_title(f"Mann--Whitney $p={p:.1e}$,  $A_{{12}}={a12:.2f}$", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "hv_box")


def fig_nsga_overlay():
    f = R / "nsga2_front.json"
    if not f.exists():
        print("skip nsga2_overlay (nsga2_front.json not ready)")
        return
    ng = np.array(json.load(open(f))["front"])
    P, fifo = load_front()
    fig, ax = plt.subplots(figsize=(3.02, 1.97))
    ax.scatter(ng[:, 0], ng[:, 1], s=11, marker="^", facecolors="none",
               edgecolors=ORANGE, linewidths=0.6, alpha=0.8,
               label=f"NSGA-II ({len(ng)} sol.)")
    ax.scatter(P[:, 0], P[:, 1], s=8, marker="o", c=BLUE, alpha=0.7,
               label=f"MOHHO ({len(P)} sol.)", edgecolors="none")
    ax.scatter([fifo[0]], [fifo[1]], marker="*", s=85, c=RED, edgecolors="k",
               linewidths=0.4, zorder=5, label="FIFO baseline")
    ax.set_xlabel(r"$f_1$ — unserved waiting load")
    ax.set_ylabel(r"$f_2$ — disparity (years)")
    ax.set_yticks([2, 4, 6, 8, 10, 12])
    ax.legend(loc="upper right", framealpha=0.92, handletextpad=0.3,
              borderpad=0.4, labelspacing=0.3)
    ax.grid(alpha=0.25, lw=0.4)
    save(fig, "nsga2_overlay")


def save(fig, name):
    fig.tight_layout()
    # el bbox "tight" subestima la extension de las etiquetas rotadas con mathtext
    # y recortaba el parentesis de cierre de "disparity (years)": se anade margen
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=300)
    plt.close(fig)
    print("saved", name)


if __name__ == "__main__":
    fig_convergence()
    fig_pareto3d()
    fig_pareto_f1f2()
    fig_hv_box()
    fig_nsga_overlay()
