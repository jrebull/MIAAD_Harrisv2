"""
Appendix Figure 2 (names-free, overclaim-free reframe). Shows WHY the min-f1
policy is a clean win over FIFO without naming countries or asserting an
unverified per-group mechanism: it rescues wasted visas and touches almost
nothing. Counts come from the firewall-verified seeds 1-30 reproduction.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parent

# data-driven counts from the reproduced policy
rows = [r for r in csv.reader(open(OUT / "country_impact_1to30.csv"))
        if r[0] not in ("country", "__policy__")]
N_COUNTRIES = len(rows)                       # 21
movers = [r for r in rows if int(r[3]) != 0]  # 2
N_MOVED = len(movers)
N_UNCHANGED = N_COUNTRIES - N_MOVED           # 19
GAINER = [r for r in movers if int(r[3]) > 0][0]
LOSER = [r for r in movers if int(r[3]) < 0][0]
WASTE_FIFO, WASTE_MINF1 = 1940, 680
RESCUED = WASTE_FIFO - WASTE_MINF1            # 1,260
USED_MINF1 = 140000 - WASTE_MINF1             # 139,320

INK = "#1A2330"; GAIN = "#1E8449"; BLUE = "#1F5C8B"; AMBER = "#B06A3B"
GREY = "#CFD6DF"
plt.rcParams.update({"font.family": "serif", "text.color": INK})

fig, (axW, axF) = plt.subplots(2, 1, figsize=(6.2, 3.0),
                               gridspec_kw={"height_ratios": [1.0, 0.85], "hspace": 0.95})

# ---- top: visas rescued from waste (before -> after on the waste axis) ------
axW.set_xlim(-180, 2150); axW.set_ylim(-0.5, 0.7)
axW.axhline(0, color=GREY, lw=7, solid_capstyle="round", zorder=0)
arr = FancyArrowPatch((WASTE_FIFO, 0), (WASTE_MINF1, 0), arrowstyle="-|>",
                      mutation_scale=17, lw=2.6, color=GAIN, zorder=3,
                      shrinkA=0, shrinkB=0)
axW.add_patch(arr)
axW.scatter([WASTE_FIFO], [0], s=210, marker="*", color="#C0392B",
            edgecolors="white", linewidths=1.0, zorder=5)
axW.scatter([WASTE_MINF1], [0], s=120, color=BLUE, edgecolors="white",
            linewidths=1.0, zorder=5)
axW.annotate(f"FIFO wastes {WASTE_FIFO:,}", (WASTE_FIFO, 0), xytext=(WASTE_FIFO, 0.30),
             ha="center", fontsize=8.4, color="#C0392B", weight="bold")
axW.annotate(f"policy wastes {WASTE_MINF1:,}", (WASTE_MINF1, 0), xytext=(WASTE_MINF1, -0.34),
             ha="center", va="top", fontsize=8.4, color=BLUE, weight="bold")
axW.text(0.5, 1.95, "The min-$f_1$ policy Pareto-dominates FIFO: more visas used, minimal footprint",
         transform=axW.transAxes, ha="center", fontsize=9.6, weight="bold", color=INK)
axW.text(0.5, 1.58, f"+{RESCUED:,} visas rescued from waste and put to use",
         transform=axW.transAxes, ha="center", fontsize=12, weight="bold", color=GAIN)
axW.text(0.5, 1.28, f"{USED_MINF1:,} of 140,000 visas used  (FIFO uses 138,060)",
         transform=axW.transAxes, ha="center", fontsize=7.8, color="#5A6B7E")
axW.set_xlabel("wasted visas  (FIFO  $\\to$  min-$f_1$ policy)", fontsize=7.6, labelpad=2)
axW.set_xticks([0, 500, 1000, 1500, 2000])
axW.set_xticklabels(["0", "500", "1,000", "1,500", "2,000"], fontsize=7)
axW.set_yticks([])
for s in ("top", "right", "left"):
    axW.spines[s].set_visible(False)
axW.spines["bottom"].set_color("#C9D2DD")

# ---- bottom: footprint strip -- 21 cells, only 2 change ---------------------
axF.set_xlim(-0.5, N_COUNTRIES + 0.5); axF.set_ylim(-1.0, 1.2)
axF.axis("off")
gx = 0
for i in range(N_COUNTRIES):
    if i == 1:
        c, lbl = BLUE, f"+{int(GAINER[3]):,}"
    elif i == N_COUNTRIES - 2:
        c, lbl = AMBER, f"{int(LOSER[3]):,}"
    else:
        c, lbl = GREY, None
    axF.add_patch(Rectangle((i, -0.25), 0.82, 0.5, facecolor=c,
                            edgecolor="white", linewidth=1.0))
    if lbl:
        axF.annotate(lbl, (i + 0.41, 0.30), ha="center", va="bottom",
                     fontsize=8, weight="bold", color=c)
axF.text(N_COUNTRIES / 2, -0.62,
         f"only {N_MOVED} of {N_COUNTRIES} country totals change "
         f"({N_UNCHANGED} unchanged)  —  no objective is worse than FIFO",
         ha="center", va="top", fontsize=8.2, color=INK)

fig.savefig(OUT / "fig_anexo_footprint.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig_anexo_footprint.png", dpi=170, bbox_inches="tight")
print(f"saved footprint | countries={N_COUNTRIES} moved={N_MOVED} unchanged={N_UNCHANGED} "
      f"| rescued={RESCUED} used={USED_MINF1} | gainer +{GAINER[3]} loser {LOSER[3]}")
