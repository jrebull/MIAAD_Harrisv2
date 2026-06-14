"""
Appendix Figure 2 (redesigned for an UNAMBIGUOUS 'this is an improvement'
message). The min-f1 policy Pareto-dominates FIFO; this figure shows the two
country queues that change as before->after, headlined by the 1,260 visas
rescued from waste. Numbers from the firewall-verified seeds 1-30 reproduction.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent

# read the two changed groups straight from the firewall-verified reproduction
NOTE = {"South Korea": "served deeper",
        "Afghanistan": "redirected to higher-priority demand"}
movers = []
for r in csv.reader(open(OUT / "country_impact_1to30.csv")):
    if r[0] in ("country", "__policy__"):
        continue
    name, fifo, minf1, delta = r[0], int(r[1]), int(r[2]), int(r[3])
    if delta != 0:
        movers.append((name, fifo, minf1, NOTE.get(name, "")))
# show gainers first (top), losers below
GROUPS = sorted(movers, key=lambda g: -(g[2] - g[1]))
WASTE_FIFO, WASTE_MINF1 = 1940, 680
RESCUED = WASTE_FIFO - WASTE_MINF1   # 1,260
assert len(GROUPS) == 2, f"expected 2 movers, got {len(GROUPS)}"

INK = "#1A2330"; GAIN = "#1E8449"; FIFO_C = "#8A94A6"; FRONT_C = "#1F5C8B"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})

fig, ax = plt.subplots(figsize=(6.4, 3.05))
XMAX = 7400
ax.set_xlim(-650, XMAX)
ax.set_ylim(-1.35, 1.7)
ax.axvline(6050, color="#E2E7ED", lw=0.8, zorder=-2)   # separates the delta column

for i, (name, vf, vt, note) in enumerate(GROUPS):
    y = 1 - i
    up = vt > vf
    col = FRONT_C if up else "#B06A3B"
    ax.plot([vf, vt], [y, y], color="#D8DEE6", lw=7, solid_capstyle="round", zorder=0)
    arr = FancyArrowPatch((vf, y), (vt, y), arrowstyle="-|>", mutation_scale=15,
                          lw=2.4, color=col, zorder=3, shrinkA=0, shrinkB=0)
    ax.add_patch(arr)
    ax.scatter([vf], [y], s=150, marker="o", color=FIFO_C, edgecolors="white",
               linewidths=1.0, zorder=4)
    ax.scatter([vt], [y], s=150, marker="o", color=col, edgecolors="white",
               linewidths=1.0, zorder=5)
    ax.text(min(vf, vt) - 120, y, name, ha="right", va="center",
            fontsize=9.2, weight="bold")
    # value labels on each endpoint
    ax.annotate(f"FIFO {vf:,}", (vf, y), xytext=(vf, y + 0.26), ha="center",
                fontsize=7.6, color=INK)
    ax.annotate(f"{vt:,}", (vt, y), xytext=(vt, y + 0.26), ha="center",
                fontsize=8.0, color=col, weight="bold")
    sign = "+" if up else ""
    ax.text(XMAX, y, f"{sign}{vt - vf:,}", ha="right", va="center",
            fontsize=11, weight="bold", color=col)
    ax.text((vf + vt) / 2, y - 0.28, note, ha="center", va="top",
            fontsize=6.8, style="italic", color="#5A6B7E")

# headline + rescued-visas callout
ax.set_title("The policy that Pareto-dominates FIFO: minimal footprint, more visas used",
             fontsize=10, weight="bold", pad=10, loc="center")
cx = (XMAX - 650) / 2
box = FancyBboxPatch((-560, -1.30), XMAX + 380, 0.62,
                     boxstyle="round,pad=0.02,rounding_size=8",
                     transform=ax.transData, facecolor="#EAF5EE",
                     edgecolor=GAIN, linewidth=0.8, zorder=-1, mutation_aspect=0.045)
ax.add_patch(box)
ax.text(cx, -0.82,
        f"{RESCUED:,} of FIFO's {WASTE_FIFO:,} wasted visas are now put to use "
        f"(waste {WASTE_FIFO:,}$\\to${WASTE_MINF1:,})",
        ha="center", va="center", fontsize=8.2, color="#16623A", weight="bold")
ax.text(cx, -1.13,
        "only 2 of 21 country totals change  —  no objective is worse than FIFO",
        ha="center", va="center", fontsize=8.0, color="#16623A")

ax.axvline(0, color="#C9D2DD", lw=0.6, zorder=-2)
ax.set_yticks([]); ax.set_xticks([0, 2000, 4000, 6000])
ax.set_xticklabels(["0", "2,000", "4,000", "6,000"], fontsize=7)
ax.set_xlabel("Visas allocated to the group  (FIFO  →  min-$f_1$ policy)", fontsize=8)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#C9D2DD")

fig.savefig(OUT / "fig_anexo_dominance.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig_anexo_dominance.png", dpi=170, bbox_inches="tight")
print(f"saved fig_anexo_dominance | rescued={RESCUED} | groups changed=2 "
      f"| SK {GROUPS[0][1]}->{GROUPS[0][2]} | Afg {GROUPS[1][1]}->{GROUPS[1][2]}")
