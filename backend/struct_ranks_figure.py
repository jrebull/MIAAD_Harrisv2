"""Rank "bump chart" across the four structures: mean Friedman rank (lower is
better) of the six core ladder methods on visa / knapsack / TSP / flow-shop.
Replaces the cross-structure rank table in the compact paper version.

Numbers read from omnibus_visa_paired.json (visa, 6 methods) and
structures_v6.json:sanity_recomputed_6method_ranks (the other three). Run from
backend/. -> ../MICAI/figures/struct_ranks.pdf

Sized for inclusion at 0.86\\textwidth (LNCS textwidth = 347pt): fonts below are
printed sizes. Method colors shared with ladder.pdf / ladder2.pdf. The story the
figure carries: a permutation-native method is best on every structure (stars),
while the real-coded NSGA-II falls below blind random restart only on the
budget-saturating selection landscapes (left, shaded) and is competitive on the
sequencing ones (right).
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 7.5,
                     "axes.linewidth": 0.6, "savefig.bbox": "tight"})
R = Path("app/data/results")
visa = json.load(open(R / "omnibus_visa_paired.json"))["avg_rank"]
rest = json.load(open(R / "structures_v6.json"))["sanity_recomputed_6method_ranks"]

# canonical method order + the two key spellings used by the two JSONs
METHODS = [
    ("perm-NSGA-II",        "perm-NSGA-II",         "#27AE60", "perm-NSGA-II"),
    ("perm-MOEA/D",         "perm-MOEA/D",          "#16A085", "perm-MOEA/D"),
    ("Discrete-MOHHO",      "Discrete-MOHHO",       "#1F618D", "Discrete-MOHHO"),
    ("MOHHO",               "MOHHO (real-coded)",   "#2E86DE", "MOHHO (real-coded)"),
    ("Random restart",      "Random restart",       "#9AA3AF", "Random restart"),
    ("NSGA-II",             "NSGA-II (real-coded)", "#E67E22", "NSGA-II (real-coded)"),
]
STRUCTS = ["visa", "knapsack", "TSP", "flow-shop"]
XLAB = ["Visa", "Knapsack", "TSP", "Flow-shop"]
PERM_NATIVE = {"perm-NSGA-II", "perm-MOEA/D", "Discrete-MOHHO"}

ranks = {}
for kv, ks, col, label in METHODS:
    ranks[label] = [visa[kv]] + [rest[s][ks] for s in STRUCTS[1:]]

fig, ax = plt.subplots(figsize=(4.15, 1.46))
x = range(len(STRUCTS))
best_per_struct = {i: min(ranks[l][i] for _, _, _, l in METHODS)
                   for i in x}
for kv, ks, col, label in METHODS:
    y = ranks[label]
    native = label.startswith(("perm-", "Discrete"))
    ax.plot(x, y, color=col, lw=1.1 if native else 0.9,
            ls="-" if native else "--", marker="o", ms=3.2,
            markeredgecolor="k", markeredgewidth=0.35, zorder=3,
            clip_on=False)
    # star the structure(s) where this method is the single best
    for i in x:
        if abs(y[i] - best_per_struct[i]) < 1e-9:
            ax.scatter(i, y[i], marker="*", s=110, color=col,
                       edgecolors="k", linewidths=0.4, zorder=4, clip_on=False)

# direct labels on the right edge (flow-shop ranks), stacked downward in data
# coords where they collide (the y-axis is inverted: larger rank = lower)
right = sorted(((ranks[l][-1], col, l) for _, _, col, l in METHODS))
ypos, min_gap = [], 0.55
for r, _, _ in right:
    y = r if not ypos else max(r, ypos[-1] + min_gap)
    ypos.append(y)
for (r, col, label), y in zip(right, ypos):
    ax.text(3.13, y, label, fontsize=6.8, color=col,
            va="center", ha="left", clip_on=False)

# landscape families: shaded budget-saturating block vs sequencing block
ax.axvspan(-0.35, 1.5, color="#E67E22", alpha=0.05)
ax.axvspan(1.5, 3.35, color="#2E86DE", alpha=0.035)
ax.text(0.575, 6.6, "budget-saturating (selection)", ha="center", va="bottom",
        fontsize=6.8, color="#9C5410", style="italic")
ax.text(2.5, 6.6, "sequencing", ha="center", va="bottom",
        fontsize=6.8, color="#1B5E9C", style="italic")

ax.set_xlim(-0.35, 3.35)
ax.set_ylim(6.75, 0.55)            # rank 1 (best) on top
ax.set_xticks(list(x))
ax.set_xticklabels(XLAB, fontsize=7.0)
ax.set_yticks([1, 2, 3, 4, 5, 6])
ax.set_ylabel("Mean Friedman rank\n(1 $=$ best of six)", fontsize=7.3,
              linespacing=1.25)
ax.tick_params(labelsize=6.8, length=2, pad=2)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.22, lw=0.4)

FIG = Path("../MICAI/figures")
fig.savefig(FIG / "struct_ranks.pdf"); fig.savefig(FIG / "struct_ranks.png", dpi=300)
print("saved struct_ranks.pdf")
for _, _, _, label in METHODS:
    print(f"  {label:24s}", " ".join(f"{v:4.2f}" for v in ranks[label]))
