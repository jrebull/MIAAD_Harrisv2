"""Fig. 4 CATEGORICA. Sustituye la version cuyo eje Y ("realized population
movement") presentaba como MEDIDO un valor ESTIPULADO: para las celdas NDS el
codigo ejecutaba moved.append(1.0), no una medicion.

Ahora ambos ejes son categoricos -- paquete de operadores x regla de seleccion --
y no se imprime ningun numero de "movement" para NDS. La fraccion realmente
medida (0.9 % y 1.8 %) se anota SOLO en las celdas de aceptacion gated, que son
las unicas donde el codigo la cuenta.

-> $FIGDIR/mechanism_2x2_annot.pdf   (FIGDIR por entorno; NO escribe en MICAI/figures)
"""
import json, os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 7.5,
                     "axes.linewidth": 0.6, "savefig.bbox": "tight"})
R = Path("app/data/results")
OUT = Path(os.environ.get("FIGDIR", "/tmp"))
fac = json.load(open(R / "factorial_2x2_conditions.json"))
GREEN, RED = "#1a7a3a", "#b00020"

# columnas = paquete de operadores ; filas = regla de seleccion
COL = {"order": 0, "near": 1}
ROW = {"nds": 1, "gated": 0}
# etiquetas sin subindices TeX reducidos: todo el lettering del artwork >= 6 pt
XT = ["HHO moves\n$+$ poly. mutation\n(mutation rate 0.15)",
      "SBX (index 20)\n$+$ poly. mutation\n(mutation rate 1/105)"]
YT = ["gated\nacceptance", "NDS $+$\ncrowding"]

fig, ax = plt.subplots(figsize=(3.05, 2.05))
ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.5, 1.5)
ax.set_xticks([0, 1], XT, fontsize=6.4, linespacing=1.35)
ax.set_yticks([0, 1], YT, fontsize=6.6, linespacing=1.3)
ax.set_xlabel("variation package (C1)", fontsize=7.0)
ax.set_ylabel("selection rule (C2)", fontsize=7.0)
ax.tick_params(length=0, pad=3)
for sp in ("top", "right", "bottom", "left"): ax.spines[sp].set_visible(False)

for name, c in fac["cells"].items():
    x, y = COL[c["operator"]], ROW[c["selection"]]
    win = c["beats_random"]
    ax.add_patch(Rectangle((x - 0.46, y - 0.44), 0.92, 0.88, lw=0.6,
                           ec="0.55", fc=(GREEN if win else RED),
                           alpha=0.075 if win else 0.045, zorder=0))
    ax.scatter(x - 0.34, y + 0.29, s=52, c=(GREEN if win else RED),
               marker=("o" if win else "X"), edgecolors="k", linewidths=0.5, zorder=3)
    sign = "+" if c["vs_random_pct"] >= 0 else "\u2212"
    txt = (f"HV {c['hv_mean']:,.0f}\n"
           f"{sign}{abs(c['vs_random_pct']):.2f}% vs. blind\n"
           f"A12 {c['A12_vs_random']:.2f}")
    ax.text(x - 0.20, y + 0.30, txt,
            fontsize=6.4, ha="left", va="top", linespacing=1.35,
            color=("#145A32" if win else "0.20"), zorder=3)
    # el movimiento SOLO se anota donde de verdad se mide: aceptacion gated
    if c.get("movement_measured") and c["moved_fraction_mean"] is not None:
        ax.text(x, y - 0.42, f"{c['moved_fraction_mean']*100:.2f}% of offspring\nreplace their parent",
                fontsize=6.1, ha="center", va="bottom", color="0.35",
                style="italic", linespacing=1.25, zorder=3)

ax.text(-0.46, 1.48, "only this cell beats blind sampling", fontsize=6.3,
        color=GREEN, ha="left", va="top", style="italic")
OUT.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT / "mechanism_2x2_annot.pdf")
fig.savefig(OUT / "mechanism_2x2_annot.png", dpi=300)
print("FIGDIR =", OUT)
print("celdas:", {k: (v["hv_mean"], v["beats_random"],
                      v["moved_fraction_mean"] if v["selection"] == "gated" else "n/a (stipulated)")
                  for k, v in fac["cells"].items()})
