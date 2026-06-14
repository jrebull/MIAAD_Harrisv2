"""
Secondary appendix panel: per-country reallocation vs FIFO, for ONE chosen
front policy. Reads a CSV produced by repro_country_1to30.py (seeds 1-30,
firewall-verified front), so every number is paper-consistent.

Usage:
    python fig_anexo_country.py country_impact_1to30.csv "min-$f_1$ policy (dominates FIFO)"
"""
import csv
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = Path(__file__).resolve().parent
csv_name = sys.argv[1] if len(sys.argv) > 1 else "country_impact_1to30.csv"
subtitle = sys.argv[2] if len(sys.argv) > 2 else ""
stem = Path(csv_name).stem

rows, policy = [], ""
for r in csv.reader(open(OUT / csv_name)):
    if r[0] == "country":
        continue
    if r[0] == "__policy__":
        policy = " ".join(r[1:]); continue
    rows.append((r[0], int(r[1]), int(r[2]), int(r[3])))

rows.sort(key=lambda x: x[3])
n_zero = sum(1 for r in rows if r[3] == 0)
total_n = len(rows)
# when the reallocation is sparse, drop the unchanged rows and annotate them
compact = n_zero > 6
note = ""
if compact:
    moved_visas = sum(r[3] for r in rows if r[3] > 0)
    rows = [r for r in rows if r[3] != 0]
    note = (f"{n_zero} of {total_n} country totals unchanged.\n"
            f"FIFO is dominated by moving only {moved_visas:,} visas "
            f"({moved_visas/140000*100:.1f}% of supply) between {len(rows)} groups.")
countries = [r[0] for r in rows]
delta = np.array([r[3] for r in rows])
y = np.arange(len(countries))

GAIN, LOSS = "#1F5C8B", "#C0392B"
INK = "#1A2330"
colors = [GAIN if d > 0 else (LOSS if d < 0 else "#B8C0CA") for d in delta]

plt.rcParams.update({"font.family": "serif", "font.size": 9, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
fig_h = 5.4 if not compact else max(1.8, 0.55 * len(countries) + 1.4)
fig, ax = plt.subplots(figsize=(5.6, fig_h))
ax.barh(y, delta, color=colors, alpha=0.9, edgecolor="white", linewidth=0.4,
        height=0.55 if compact else 0.8)
ax.axvline(0, color=INK, lw=0.9)
ax.set_yticks(y); ax.set_yticklabels(countries, fontsize=8)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):+,}"))
lo, hi = delta.min(), delta.max()
span = max(abs(lo), abs(hi)) or 1
ax.set_xlim(lo - span * 0.30, hi + span * 0.30)
ax.set_xlabel("Visas reallocated vs. FIFO  (gained $+$ / lost $-$)", fontsize=8.5)
ax.grid(axis="x", alpha=0.22)
ax.spines[["top", "right"]].set_visible(False)
for yi, d in zip(y, delta):
    if d == 0:
        ax.text(span * 0.012, yi, "+0", va="center", ha="left",
                fontsize=6.6, color="#7A8492")
    else:
        ax.text(d + (span * 0.018 if d > 0 else -span * 0.018), yi, f"{d:+,}",
                va="center", ha="left" if d > 0 else "right",
                fontsize=6.8, color=INK)
if subtitle:
    ax.set_title(subtitle, fontsize=9, weight="bold", pad=6)
if note:
    ax.text(0.5, -0.34 if compact else -0.16, note, transform=ax.transAxes,
            ha="center", va="top", fontsize=7.6, style="italic", color="#41506A")
fig.tight_layout()
fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
fig.savefig(OUT / f"{stem}.png", dpi=170, bbox_inches="tight")
print(f"saved {stem}.pdf/.png | policy {policy} | "
      f"moved {(delta != 0).sum()} countries | range [{lo:+,}, {hi:+,}]")
