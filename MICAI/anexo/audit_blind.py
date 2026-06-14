"""
BLIND, INDEPENDENT re-derivation of every number asserted by the appendix.
Reads ONLY raw data (pareto_front.csv, the reproduced per-country CSVs) and the
firewall-locked FIFO constants. Does NOT import the figure scripts. Every claim
the figures/captions/text make is recomputed and checked; any mismatch is FAIL.
"""
import csv
from pathlib import Path

A = Path(__file__).resolve().parent
ROOT = A.parents[1]
FAIL = []


def check(name, got, want, tol=0.0):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) else (got == want)
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}: got={got} want={want}"
          + (f" (tol {tol})" if tol else ""))
    if not ok:
        FAIL.append(name)


# ---- 1. combined front from the paper's CSV --------------------------------
P, fifo = [], None
for r in csv.DictReader(open(ROOT / "backend/app/data/results/pareto_front.csv")):
    t = (float(r["f1"]), float(r["f2"]), float(r["f3"]))
    (P.append(t) if r["type"] == "pareto" else None)
    if r["type"] != "pareto":
        fifo = t
print("== FRONT (pareto_front.csv) ==")
check("front size", len(P), 104)
check("FIFO f1", fifo[0], 8.7891, 1e-9)
check("FIFO f2", fifo[1], 13.0, 1e-9)
check("FIFO f3", fifo[2], 1940, 1e-9)

f1s = [p[0] for p in P]; f2s = [p[1] for p in P]; f3s = [p[2] for p in P]
mf1 = min(P, key=lambda p: p[0])
mf2 = min(P, key=lambda p: p[1])
mf3 = min(P, key=lambda p: p[2])
check("min-f1 == (8.7884,13,680)", (round(mf1[0],4), mf1[1], mf1[2]), (8.7884, 13.0, 680.0))
check("min-f2 == (8.9994,2,0)", (round(mf2[0],4), mf2[1], mf2[2]), (8.9994, 2.0, 0.0))
check("min-f3 f3==0", mf3[2], 0.0, 1e-9)
check("zero-waste count == 94", sum(1 for v in f3s if v == 0), 94)

# ---- 2. derived percentages in Panel B / captions --------------------------
print("== DERIVED PERCENTAGES ==")
f2_red = (fifo[1] - mf2[1]) / fifo[1] * 100          # 13->2
check("f2 reduction rounds to 85%", round(f2_red), 85)
f1_cost = (mf2[0] - fifo[0]) / fifo[0] * 100         # equity extreme f1 cost
check("equity f1 cost rounds to 2.4%", round(f1_cost, 1), 2.4)
check("f3 -100% (1940->0)", round((fifo[2]-0)/fifo[2]*100), 100)
check("f1 front-best == 8.7884", round(mf1[0], 4), 8.7884)

# ---- 3. per-country min-f1 policy (reproduced CSV) -------------------------
print("== PER-COUNTRY (country_impact_1to30.csv) ==")
rows, policy = [], {}
for r in csv.reader(open(A / "country_impact_1to30.csv")):
    if r[0] in ("country",):
        continue
    if r[0] == "__policy__":
        policy = dict(x.split("=") for x in r[1:]); continue
    rows.append((r[0], int(r[1]), int(r[2]), int(r[3])))
movers = [r for r in rows if r[3] != 0]
fifo_total = sum(r[1] for r in rows)
moh_total = sum(r[2] for r in rows)
check("policy f1 == 8.7884", round(float(policy["f1"]), 4), 8.7884)
check("policy f3 == 680", round(float(policy["f3"])), 680)
check("countries total == 21", len(rows), 21)
check("movers == 2", len(movers), 2)
check("unchanged == 19", len(rows) - len(movers), 19)
d = {r[0]: r[3] for r in rows}
check("South Korea +2460", d.get("South Korea"), 2460)
check("Afghanistan -1200", d.get("Afghanistan"), -1200)
gross_pos = sum(r[3] for r in movers if r[3] > 0)
check("gross positive flow == 2460", gross_pos, 2460)
check("2460/140000 rounds to 1.8%", round(gross_pos/140000*100, 1), 1.8)

# ---- 4. RECONCILIATION (the killer cross-check) ----------------------------
print("== RECONCILIATION ==")
net = sum(r[3] for r in movers)
check("net realloc == waste delta (1940-680=1260)", net, int(fifo[2]) - 680)
check("FIFO total assigned == 140000 - 1940", fifo_total, 140000 - int(fifo[2]))
check("min-f1 total assigned == 140000 - 680", moh_total, 140000 - 680)

# ---- 5. equity CSV (not shown, but reproduced) sanity ----------------------
print("== EQUITY CSV sanity (kept out of paper) ==")
erows = []
for r in csv.reader(open(A / "country_impact_equity_1to30.csv")):
    if r[0] in ("country", "__policy__"):
        continue
    erows.append((r[0], int(r[3])))
check("equity sum of deltas == 1940 (zero waste vs FIFO)",
      sum(x[1] for x in erows), 1940)

print()
if FAIL:
    print(f"AUDIT FAILED: {len(FAIL)} mismatch(es): {FAIL}")
    raise SystemExit(1)
print("AUDIT CLEAN: every appendix number re-derived from raw data with 0 mismatches.")
