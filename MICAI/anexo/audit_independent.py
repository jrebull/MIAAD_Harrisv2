"""
INDEPENDENT blind re-derivation. No hardcoded 'expected' values -- it recomputes
everything from raw sources and PRINTS what it finds, so a human/auditor compares
against the figures. Also probes a subtlety the first audit skipped: is the
min-f1 policy's per-country allocation UNIQUE, or an artifact of which optimal
solution we happened to pick?
"""
import csv
from collections import Counter
from pathlib import Path
import numpy as np

from app.core.problem import VisaProblem
from app.core.fifo import run_baseline
from app.core.mohho import run_mohho, evaluate_hawk

ROOT = Path(__file__).resolve().parents[2]


def dom(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def country_vec(alloc, problem):
    d = {}
    for g in problem.groups:
        d[g["country"]] = d.get(g["country"], 0) + alloc[g["index"]]
    return d


problem = VisaProblem()

# ---- FIFO, recomputed from the model (not read from any CSV) ----------------
fifo_alloc, fifo_fit = run_baseline(problem)
fifo_c = country_vec(fifo_alloc, problem)
print("FIFO fitness (recomputed):", tuple(round(v, 4) for v in fifo_fit))
print("FIFO visas used:", sum(fifo_c.values()), "| wasted:", 140000 - sum(fifo_c.values()))

# ---- combined front, recomputed --------------------------------------------
pos, fit = [], []
for s in range(1, 31):
    p, f, _ = run_mohho(problem, seed=s)
    pos.extend(p); fit.extend(f)
F = np.array(fit)
nd = [i for i in range(len(F)) if not any(dom(F[j], F[i]) for j in range(len(F)) if j != i)]
seen, uniq = set(), []
for i in nd:
    k = tuple(np.round(F[i], 6))
    if k not in seen:
        seen.add(k); uniq.append(i)
U = F[[i for i in uniq]]
print("\nFRONT (recomputed): size =", len(uniq))
print("  f1 min/max:", round(U[:, 0].min(), 4), round(U[:, 0].max(), 4))
print("  f2 min/max:", U[:, 1].min(), U[:, 1].max())
print("  f3 min/max:", U[:, 2].min(), U[:, 2].max())
print("  count f3==0:", int((U[:, 2] == 0).sum()))
print("  min-f1 point:", U[U[:, 0].argmin()])
print("  min-f2 point:", U[U[:, 1].argmin()])

# ---- UNIQUENESS PROBE: all positions achieving the min-f1 objective ---------
target = tuple(U[U[:, 0].argmin()])
print("\nUNIQUENESS of the min-f1 policy (objective =", tuple(round(v,4) for v in target), "):")
matching = [i for i in range(len(F)) if tuple(np.round(F[i], 6)) == tuple(np.round(target, 6))]
print("  # archive positions hitting that exact objective:", len(matching))
deltas_seen = Counter()
for i in matching:
    alloc, _ = evaluate_hawk(pos[i], problem)
    c = country_vec(alloc, problem)
    delta = tuple(sorted((k, c[k] - fifo_c.get(k, 0)) for k in c if c[k] != fifo_c.get(k, 0)))
    deltas_seen[delta] += 1
print("  distinct per-country reallocation patterns among them:", len(deltas_seen))
for patt, n in deltas_seen.items():
    print(f"    (x{n})", patt)

print("\n>>> If >1 distinct pattern, the per-country figure is ONE representative, "
      "not THE unique answer -- caption must say so.")
