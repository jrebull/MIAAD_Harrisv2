"""More impactful figures for the paper:
   pareto3d_v2.pdf      -> enhanced 3D front with a drop-line proving FIFO is dominated
   country_impact.pdf   -> policy output: visas gained/lost per country vs FIFO (diverging)
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LinearSegmentedColormap

from app.core.problem import VisaProblem
from app.core.fifo import run_baseline
from app.core.mohho import run_mohho, evaluate_hawk

# Figures generated at FINAL physical size (LNCS textwidth = 347pt):
# pareto3d_v2 at 0.49\textwidth, country_impact at 0.72\textwidth.
plt.rcParams.update({"font.family": "serif", "font.size": 7.5,
                     "axes.linewidth": 0.6, "savefig.bbox": "tight"})
FIG = Path("../MICAI/figures")
R = Path("app/data/results")
BLUE, RED, GREEN, GREY = "#2E86DE", "#E74C3C", "#27AE60", "#9AA3AF"
# viridis truncated at 0.85 (drops the pale-yellow extreme, invisible in print),
# reversed to keep the original viridis_r orientation (low f3 -> light, high -> dark)
VIRIDIS_T_R = LinearSegmentedColormap.from_list(
    "viridis_t_r", plt.cm.viridis(np.linspace(0.85, 0.0, 256)))


def load_front():
    P, fifo = [], None
    for r in csv.DictReader(open(R / "pareto_front.csv")):
        pt = (float(r["f1"]), float(r["f2"]), float(r["f3"]))
        (P.append(pt) if r["type"] == "pareto" else None)
        if r["type"] != "pareto":
            fifo = pt
    return np.array(P), fifo


def fig_pareto3d_v2():
    P, fifo = load_front()
    fig = plt.figure(figsize=(2.55, 2.10))
    ax = fig.add_subplot(111, projection="3d")
    # faint projection on the floor (z=0 plane) to add depth
    zfloor = P[:, 2].min()
    ax.scatter(P[:, 0], P[:, 1], np.full(len(P), zfloor), s=3, c=GREY,
               alpha=0.12, edgecolors="none")
    sc = ax.scatter(P[:, 0], P[:, 1], P[:, 2], c=P[:, 2], cmap=VIRIDIS_T_R,
                    s=9, alpha=0.92, edgecolors="#333333", linewidths=0.2,
                    depthshade=True)
    # FIFO star + drop-line down to the front's f3 level -> visualizes domination
    ax.scatter([fifo[0]], [fifo[1]], [fifo[2]], marker="*", s=110, c=RED,
               edgecolors="k", linewidths=0.5)
    ax.plot([fifo[0], fifo[0]], [fifo[1], fifo[1]], [fifo[2], zfloor],
            color=RED, ls=":", lw=1.0)
    # direct label (a legend box would waste space at this size)
    ax.text(fifo[0], fifo[1], fifo[2] * 1.07, "FIFO baseline\n(dominated)",
            fontsize=6.3, color="#7B241C", ha="right", va="bottom", zorder=10)
    for m in range(3):
        e = P[np.argmin(P[:, m])]
        ax.scatter([e[0]], [e[1]], [e[2]], s=30, facecolors="none",
                   edgecolors="k", linewidths=0.8)
    ax.set_xlabel(r"$f_1$  waiting load", labelpad=-4, fontsize=7.2)
    ax.set_ylabel(r"$f_2$  disparity (yr)", labelpad=-4, fontsize=7.2)
    ax.set_zlabel(r"$f_3$  waste (visas)", labelpad=-6, fontsize=7.2)
    ax.set_xticks([8.8, 8.9, 9.0])
    ax.set_yticks([2, 6, 10])
    ax.set_zticks([0, 1000, 2000])
    ax.tick_params(labelsize=6.3, pad=-3)
    ax.view_init(elev=18, azim=-66)
    ax.xaxis.pane.set_alpha(0.04); ax.yaxis.pane.set_alpha(0.04); ax.zaxis.pane.set_alpha(0.04)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.line.set_linewidth(0.6)
    # no colorbar: color duplicates the z axis (f3); the companion f1-f2
    # projection (pareto_f1f2.pdf) carries the f3 color scale.
    # mplot3d's tight bbox drops projected axis labels -> use fixed margins.
    ax.set_position([-0.02, 0.025, 0.92, 1.01])
    with plt.rc_context({"savefig.bbox": None}):
        fig.savefig(FIG / "pareto3d_v2.pdf")
        fig.savefig(FIG / "pareto3d_v2.png", dpi=300)
    plt.close(fig); print("saved pareto3d_v2")


def fig_country_impact():
    problem = VisaProblem()
    fifo_alloc, _ = run_baseline(problem)
    fifo_c = {}
    for g in problem.groups:
        fifo_c[g["country"]] = fifo_c.get(g["country"], 0) + fifo_alloc[g["index"]]
    # one MOHHO run; pick a balanced full-utilization (f3=0) knee solution
    pos, fit, _ = run_mohho(problem, seed=42)
    f = np.array(fit)
    zero_waste = [i for i in range(len(f)) if f[i, 2] == 0]
    pool = zero_waste if zero_waste else list(range(len(f)))
    sub = f[pool]
    n1 = (sub[:, 0] - sub[:, 0].min()) / (np.ptp(sub[:, 0]) + 1e-9)
    n2 = (sub[:, 1] - sub[:, 1].min()) / (np.ptp(sub[:, 1]) + 1e-9)
    knee = pool[int(np.argmin(n1 + n2))]            # balanced f1/f2 at zero waste
    alloc, fsel = evaluate_hawk(pos[knee], problem)
    moh_c = {}
    for g in problem.groups:
        moh_c[g["country"]] = moh_c.get(g["country"], 0) + alloc[g["index"]]

    EN = {"India": "India", "China": "China", "Filipinas": "Philippines",
          "Mexico": "Mexico", "Afganistan": "Afghanistan", "Irak": "Iraq",
          "Corea del Sur": "South Korea", "Pakistan": "Pakistan", "Iran": "Iran",
          "Taiwan": "Taiwan", "Brasil": "Brazil", "Canada": "Canada",
          "Reino Unido": "United Kingdom", "Nigeria": "Nigeria", "Japon": "Japan",
          "Bangladesh": "Bangladesh", "Colombia": "Colombia", "Alemania": "Germany",
          "Vietnam": "Vietnam", "Etiopia": "Ethiopia", "Resto del Mundo": "Rest of World"}
    countries = sorted(moh_c, key=lambda c: moh_c[c] - fifo_c.get(c, 0))
    delta = [moh_c[c] - fifo_c.get(c, 0) for c in countries]
    y = np.arange(len(countries))
    colors = [BLUE if d >= 0 else RED for d in delta]
    fig, ax = plt.subplots(figsize=(3.42, 3.55))
    ax.barh(y, delta, color=colors, alpha=0.85, edgecolor="k", linewidth=0.3,
            height=0.72)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([EN[c] for c in countries], fontsize=7.0)
    ax.set_ylim(-0.6, len(countries) - 0.4)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):+,}"))
    ax.set_xticks([-6000, -3000, 0, 3000, 6000])
    ax.set_xlim(min(delta) * 1.38, max(delta) * 1.22)
    ax.set_xlabel("Visas reallocated vs. FIFO  (gained $+$ / lost $-$)",
                  fontsize=7.3)
    ax.tick_params(axis="x", labelsize=6.8, length=2, pad=2)
    ax.tick_params(axis="y", length=2, pad=2)
    ax.grid(axis="x", alpha=0.25, lw=0.4)
    ax.spines[["top", "right"]].set_visible(False)
    for yi, d in zip(y, delta):
        ax.text(d + (max(delta) * 0.015 if d >= 0 else min(delta) * 0.015), yi,
                f"{d:+,}", va="center", ha="left" if d >= 0 else "right",
                fontsize=5.9, color="#333")
    fig.savefig(FIG / "country_impact.pdf"); fig.savefig(FIG / "country_impact.png", dpi=300)
    plt.close(fig)
    print(f"saved country_impact | selected policy f=({fsel[0]:.3f},{fsel[1]:.3f},{fsel[2]:.0f}) "
          f"visas={sum(moh_c.values()):,} vs FIFO {sum(fifo_c.values()):,}")


if __name__ == "__main__":
    fig_pareto3d_v2()
    fig_country_impact()
