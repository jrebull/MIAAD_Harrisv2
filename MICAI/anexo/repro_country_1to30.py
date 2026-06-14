"""
Reproduce a PAPER-CONSISTENT per-country reallocation (seeds 1-30), replacing
the seed-42 reporte_final policy that backend/paper_figures2.py used.

Steps:
  1. Run MOHHO for seeds 1..30, collect (position, fitness) from each archive.
  2. Non-dominated filter -> combined front; verify it matches the firewall
     (104 solutions; min-f1 = 8.7884/13/680; min-f2 = 8.9994/2/0; 94 zero-waste).
  3. Select the min-f1 solution -- the canonical policy the paper says DOMINATES
     FIFO -- recover its allocation, aggregate visas per country.
  4. Diff vs the FIFO baseline allocation. Write country_impact_1to30.csv.

Run from .../Harris2/backend with its venv active:
    python ../MICAI/anexo/repro_country_1to30.py
"""
import csv
from pathlib import Path
import numpy as np

from app.core.problem import VisaProblem
from app.core.fifo import run_baseline
from app.core.mohho import run_mohho, evaluate_hawk

OUT = Path(__file__).resolve().parent
SEEDS = range(1, 31)

EN = {"India": "India", "China": "China", "Filipinas": "Philippines",
      "Mexico": "Mexico", "Afganistan": "Afghanistan", "Irak": "Iraq",
      "Corea del Sur": "South Korea", "Pakistan": "Pakistan", "Iran": "Iran",
      "Taiwan": "Taiwan", "Brasil": "Brazil", "Canada": "Canada",
      "Reino Unido": "United Kingdom", "Nigeria": "Nigeria", "Japon": "Japan",
      "Bangladesh": "Bangladesh", "Colombia": "Colombia", "Alemania": "Germany",
      "Vietnam": "Vietnam", "Etiopia": "Ethiopia", "Resto del Mundo": "Rest of World"}


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def main():
    problem = VisaProblem()

    # --- FIFO per-country baseline ------------------------------------------
    fifo_alloc, fifo_fit = run_baseline(problem)
    fifo_c = {}
    for g in problem.groups:
        fifo_c[g["country"]] = fifo_c.get(g["country"], 0) + fifo_alloc[g["index"]]
    print(f"FIFO fitness: {tuple(round(v,4) for v in fifo_fit)} "
          f"| total assigned {sum(fifo_c.values()):,}")

    # --- combined front over seeds 1..30 ------------------------------------
    pool_pos, pool_fit = [], []
    for s in SEEDS:
        pos, fit, _ = run_mohho(problem, seed=s)
        pool_pos.extend(pos)
        pool_fit.extend(fit)
    print(f"pooled archive points: {len(pool_fit)} over {len(SEEDS)} seeds")

    # non-dominated filter (keep positions aligned)
    F = np.array(pool_fit)
    keep = []
    for i in range(len(F)):
        if not any(dominates(F[j], F[i]) for j in range(len(F)) if j != i):
            keep.append(i)
    # drop duplicates in objective space
    seen, uniq = set(), []
    for i in keep:
        key = tuple(np.round(F[i], 6))
        if key not in seen:
            seen.add(key); uniq.append(i)
    front_fit = F[uniq]
    print(f"combined front (non-dominated, unique): {len(uniq)} solutions")

    # --- firewall sanity checks ---------------------------------------------
    mf1 = front_fit[front_fit[:, 0].argmin()]
    mf2 = front_fit[front_fit[:, 1].argmin()]
    n_zero = int((front_fit[:, 2] == 0).sum())
    print(f"min-f1 {mf1} | min-f2 {mf2} | zero-waste {n_zero}/{len(uniq)}")
    assert abs(mf1[0] - 8.7884) < 1e-3 and mf1[1] == 13.0 and mf1[2] == 680, mf1
    assert abs(mf2[0] - 8.9994) < 1e-3 and mf2[1] == 2.0 and mf2[2] == 0, mf2

    # --- emit per-country deltas for two representative front policies -------
    def emit(label, idx_in_uniq, fname):
        gi = uniq[idx_in_uniq]
        alloc, fsel = evaluate_hawk(pool_pos[gi], problem)
        moh_c = {}
        for g in problem.groups:
            moh_c[g["country"]] = moh_c.get(g["country"], 0) + alloc[g["index"]]
        rows = [(EN.get(c, c), int(fifo_c.get(c, 0)), int(moh_c[c]),
                 int(moh_c[c] - fifo_c.get(c, 0))) for c in moh_c]
        rows.sort(key=lambda r: r[3])
        with open(OUT / fname, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["country", "fifo_visas", "mohho_visas", "delta"])
            w.writerows(rows)
            w.writerow(["__policy__", f"f1={fsel[0]:.4f}", f"f2={fsel[1]:.4f}",
                        f"f3={fsel[2]:.0f}"])
        moved = sum(1 for r in rows if r[3] != 0)
        print(f"\n[{label}] policy f=({fsel[0]:.4f},{fsel[1]:.4f},{fsel[2]:.0f}) "
              f"| total {sum(moh_c.values()):,} | countries moved: {moved} -> {fname}")
        for r in rows:
            if r[3] != 0:
                print(f"    {r[0]:<16} FIFO {r[1]:>7,}  MOHHO {r[2]:>7,}  delta {r[3]:+,}")

    emit("min-f1 / dominates FIFO", int(front_fit[:, 0].argmin()),
         "country_impact_1to30.csv")
    emit("min-f2 / equity extreme", int(front_fit[:, 1].argmin()),
         "country_impact_equity_1to30.csv")


if __name__ == "__main__":
    main()
