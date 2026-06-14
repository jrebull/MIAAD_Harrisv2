"""
Appendix hero figure for the MICAI compact paper.
Panel A: 3D dominance (104-solution combined front, seeds 1-30, FIFO floating).
Panel B: FIFO -> front 'before/after' on each of the three objectives.

ALL numbers come from backend/app/data/results/pareto_front.csv (the paper's
seed 1-30 combined front) and the firewall-locked FIFO baseline. Light theme,
colorblind-safe, vector PDF -> LNCS-appropriate (legible in B&W).
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]          # .../Harris2
CSV = ROOT / "backend/app/data/results/pareto_front.csv"
OUT = Path(__file__).resolve().parent

# --- load the paper's combined front + FIFO baseline -------------------------
pts, fifo = [], None
for r in csv.DictReader(open(CSV)):
    p = (float(r["f1"]), float(r["f2"]), float(r["f3"]))
    if r["type"] == "pareto":
        pts.append(p)
    else:
        fifo = p
P = np.array(pts)
f1, f2, f3 = P[:, 0], P[:, 1], P[:, 2]
assert fifo == (8.7891, 13.0, 1940.0), f"FIFO mismatch: {fifo}"
assert len(P) == 104, len(P)

# representative front points (firewall-covered)
i_f1 = int(f1.argmin())   # 8.7884, 13.0, 680  -> strictly dominates FIFO
i_f2 = int(f2.argmin())   # 8.9994, 2.0,  0    -> radical equity
i_f3 = int(f3.argmin())   # 8.7888, 13.0, 0
n_zero = int((f3 == 0).sum())   # 94

INK = "#1A2330"; GRID = "#C9D2DD"
FIFO_C = "#C0392B"; FRONT_C = "#1F5C8B"; GOOD = "#1E8449"

plt.rcParams.update({
    "font.size": 9, "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": INK,
    "font.family": "serif",
})

fig = plt.figure(figsize=(7.0, 8.2))
gs = fig.add_gridspec(2, 1, height_ratios=[1.32, 1.0], hspace=0.16)

# ===================== PANEL A : 3D dominance ================================
axA = fig.add_subplot(gs[0], projection="3d")
axA.set_facecolor("white"); axA.xaxis.pane.set_alpha(0); axA.yaxis.pane.set_alpha(0)
axA.zaxis.pane.set_alpha(0)
for ax_ in (axA.xaxis, axA.yaxis, axA.zaxis):
    ax_._axinfo["grid"].update(color=GRID, linewidth=0.6)

sc = axA.scatter(f1, f2, f3, c=f3, cmap="viridis", s=24, alpha=0.95,
                 edgecolors="white", linewidths=0.2, depthshade=True)
# FIFO star, floating, with a drop-line down to the front plane
axA.scatter([fifo[0]], [fifo[1]], [fifo[2]], marker="*", s=460, c=FIFO_C,
            edgecolors="white", linewidths=1.0, zorder=12)
axA.plot([fifo[0], fifo[0]], [fifo[1], fifo[1]], [fifo[2], 60], ls=":",
         color=FIFO_C, lw=1.4, zorder=8)
axA.text(fifo[0], fifo[1], fifo[2] + 130,
         "FIFO (current system)\n— dominated —", color=FIFO_C, fontsize=8.5,
         weight="bold", ha="center")

def ring(idx, txt, dz=70):
    p = P[idx]
    axA.scatter(*p, marker="o", s=85, facecolors="none", edgecolors=INK,
                linewidths=1.4, zorder=11)
    axA.text(p[0], p[1], p[2] + dz, txt, color=INK, fontsize=7.6, weight="bold")
ring(i_f2, "min $f_2$\n(equity)")
ring(i_f1, "min $f_1$")
ring(i_f3, "min $f_3$")

axA.set_xlabel("\n$f_1$  waiting load", fontsize=9)
axA.set_ylabel("\n$f_2$  disparity (yr)", fontsize=9)
axA.set_zlabel("\n$f_3$  wasted visas", fontsize=9)
axA.set_zlim(0, 2100)
axA.view_init(elev=18, azim=-58)
cb = fig.colorbar(sc, ax=axA, shrink=0.45, aspect=14, pad=0.11)
cb.set_label("$f_3$ (wasted visas)", fontsize=8)
cb.ax.tick_params(labelsize=7)
axA.set_title("(a)  The recovered front Pareto-dominates FIFO",
              fontsize=9.5, weight="bold", pad=-2, loc="left")

# ===================== PANEL B : before / after =============================
gsB = gs[1].subgridspec(3, 1, hspace=0.62)
specs = [
    # name, fifo, front, worst, best, fmt, extra, gain_text
    ("$f_3$  wasted visas", 1940, 0, 1940, 0, "{:,.0f}",
     "94 of 104 front solutions reach 0", "-100%"),
    ("$f_2$  max disparity (yr)", 13.0, 2.0, 13.0, 2.0, "{:.1f}",
     "equity extreme; costs only +2.4% in $f_1$", "-85%"),
    ("$f_1$  unserved waiting load", 8.7891, 8.7884, 8.9994, 8.7884, "{:.4f}",
     "FIFO already near-optimal here; front is marginally better", "≈ tied"),
]
for k, (name, vf, vt, worst, best, fmt, extra, gain) in enumerate(specs):
    ax = fig.add_subplot(gsB[k])
    lo, hi = min(worst, best), max(worst, best)
    pad = (hi - lo) * 0.18 or 1
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(-1, 1)
    ax.axhline(0, color=GRID, lw=6, zorder=0, solid_capstyle="round")
    tied = abs(vf - vt) < (hi - lo) * 0.02   # f1: markers coincide
    if not tied:
        arr = FancyArrowPatch((vf, 0), (vt, 0), arrowstyle="-|>", mutation_scale=16,
                              lw=2.2, color=GOOD, zorder=3, shrinkA=0, shrinkB=0)
        ax.add_patch(arr)
    ax.scatter([vf], [0], s=230, marker="*", color=FIFO_C, edgecolors="white",
               linewidths=1.0, zorder=5)
    ax.scatter([vt], [0], s=120, color=FRONT_C, edgecolors="white",
               linewidths=1.0, zorder=6)
    # value labels: FIFO above, front below; when tied, push apart horizontally
    fdx, tdx = (0.05, -0.05) if tied else (0.0, 0.0)
    ax.annotate("FIFO " + fmt.format(vf), (vf, 0),
                xytext=(vf + fdx * (hi - lo), 0.46), ha="center", va="bottom",
                fontsize=8.2, color=FIFO_C, weight="bold")
    ax.annotate("front " + fmt.format(vt), (vt, 0),
                xytext=(vt + tdx * (hi - lo), -0.46), ha="center", va="top",
                fontsize=8.2, color=FRONT_C, weight="bold")
    # objective name to the LEFT, outside the track (no collision)
    ax.set_ylabel(name, rotation=0, ha="right", va="center", labelpad=12,
                  fontsize=9, fontweight="bold")
    # park the big gain label on whichever top corner the FIFO star is NOT near
    gx, gha = (0.005, "left") if vf > (lo + hi) / 2 else (0.995, "right")
    ax.text(gx, 0.95, gain, transform=ax.transAxes, fontsize=11,
            weight="bold", va="top", ha=gha, color=GOOD)
    ax.text(0.995, 0.06, extra, transform=ax.transAxes, fontsize=7.3,
            va="bottom", ha="right", color="#5A6B7E", style="italic")
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks([])
    if k == 0:
        ax.set_title("(b)  From FIFO to the front, objective by objective"
                     "  (star = FIFO, dot = front best)",
                     fontsize=9.5, weight="bold", loc="left", pad=6)

fig.suptitle("")
fig.savefig(OUT / "fig_anexo_main.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig_anexo_main.png", dpi=170, bbox_inches="tight")
print(f"OK | FIFO={fifo} | minf1={P[i_f1]} | minf2={P[i_f2]} | "
      f"minf3={P[i_f3]} | zero-waste={n_zero}/104")
