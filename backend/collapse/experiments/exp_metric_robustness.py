"""
SUPERPROMPT v2 - Experimento D: colapso por metrica (H_met, Seccion 6).

Descarta que 'random restart competitivo' sea artefacto de un HV insensible por
reference point inflado.

  D.1 Barrido de reference points sobre el HV PER-RUN de los 6 metodos (el HV
      per-run es lo que discrimina los tiers; el HV del frente combinado no). Para
      cada ref point: media per-run y RANKING de los 6 metodos. ¿Se preserva el
      orden / la estructura de tiers?
  D.2 Metricas independientes del reference point: IGD+ y epsilon-aditivo binario,
      con Z = union no-dominada de los SEIS frentes combinados (no solo MOHHO+NSGA).
      ¿Se preserva el ranking de tiers bajo metricas no-HV?
  D.3 Sensibilidad del HV a f2: recomputa HV fijando f1,f3 a sus medianas y variando
      solo f2. ¿Que fraccion del HV depende solo de f2?

Salida: app/data/results/expD_metric_robustness.json
        + MICAI/figures/collapse/expD_refpoint_rankings.html
Ejecutar desde backend/:  python3 -m collapse.experiments.exp_metric_robustness
"""
import csv
import json
import time
from pathlib import Path

import numpy as np

from app.core.problem import VisaProblem
from app.core.mohho import compute_hypervolume, run_mohho, dominates
from compare_nsga2 import run_nsga2, nondominated
from controls import run_random, MOHHO_SEEDS
from perm_nsga import run_perm_nsga
from perm_moead import run_perm_moead
from discrete_mohho import run_discrete_mohho, SEEDS as DM_SEEDS

RESULTS = Path("app/data/results")
FIGDIR = Path("../MICAI/figures/collapse")
PRF = RESULTS / "per_run_fronts.json"


# ----------------- per-run fronts (regenerados con seeds publicados) -----------------
def build_per_run_fronts(problem):
    if PRF.exists():
        return json.load(open(PRF))
    data = {}
    # MOHHO: reuse stored per-run fronts (run_00..29)
    mh = []
    for i in range(30):
        d = json.load(open(RESULTS / f"run_{i:02d}.json"))
        mh.append([list(map(float, p)) for p in d["pareto_front"]])
    data["mohho_realcoded"] = {"tier": "random_key", "fronts": mh}

    def regen(run_fn, seeds, tier, tag):
        fronts = []
        t0 = time.time()
        for s in seeds:
            r = run_fn(problem, s)
            # run_mohho returns (pos, fits, hv); others return fits list
            fits = r[1] if isinstance(r, tuple) else r
            fronts.append([list(map(float, p)) for p in fits])
            print(f"    {tag} seed {s}: {len(fronts[-1])} sols ({time.time()-t0:.0f}s)")
        return {"tier": tier, "fronts": fronts}

    print("  regen nsga2_realcoded..."); data["nsga2_realcoded"] = regen(
        run_nsga2, list(range(1, 31)), "random_key", "nsga2")
    print("  regen random_restart..."); data["random_restart"] = regen(
        run_random, MOHHO_SEEDS, "random_key", "random")
    print("  regen perm_nsga2..."); data["perm_nsga2"] = regen(
        run_perm_nsga, list(range(1, 31)), "permutation", "permNSGA")
    print("  regen perm_moead..."); data["perm_moead"] = regen(
        run_perm_moead, list(range(1, 31)), "permutation", "permMOEAD")
    print("  regen discrete_mohho..."); data["discrete_mohho"] = regen(
        run_discrete_mohho, DM_SEEDS, "permutation", "discMOHHO")
    json.dump(data, open(PRF, "w"))
    return data


# ------------------------------- D.1 ref-point sweep -------------------------------
def ref_sweep(prf):
    refs = {
        "baseline_(10,16,20000)": (10.0, 16.0, 20000.0),
        "fitted_(9.1,13.5,2100)": (9.1, 13.5, 2100.0),
        "tight_(9.0,13.2,1000)": (9.0, 13.2, 1000.0),
        "mid_(9.5,14.5,8000)": (9.5, 14.5, 8000.0),
        "f3_collapsed_(9.1,13.5,700)": (9.1, 13.5, 700.0),
    }
    out = {}
    methods = list(prf.keys())
    for name, rp in refs.items():
        means = {}
        for m in methods:
            hvs = [compute_hypervolume([tuple(p) for p in fr], rp) for fr in prf[m]["fronts"]]
            means[m] = float(np.mean(hvs))
        ranking = sorted(methods, key=lambda m: -means[m])
        # tier check: are all permutation methods above all random_key methods?
        perm_min = min(means[m] for m in methods if prf[m]["tier"] == "permutation")
        rk_max = max(means[m] for m in methods if prf[m]["tier"] == "random_key")
        out[name] = {
            "ref_point": list(rp),
            "per_run_hv_mean": means,
            "ranking": ranking,
            "perm_tier_above_rk_tier": bool(perm_min > rk_max),
            "rank_of_random_restart": ranking.index("random_restart") + 1,
            "rank_of_mohho": ranking.index("mohho_realcoded") + 1,
        }
    return out, refs


# ------------------------------- D.2 IGD+ / epsilon -------------------------------
def normalize_sets(sets, lo, span):
    return {k: np.array([[(p[i] - lo[i]) / span[i] for i in range(3)] for p in v])
            for k, v in sets.items()}


def igd_plus(A, Z):
    # IGD+ : mean over z of min over a of sqrt(sum max(a_i - z_i,0)^2)
    tot = 0.0
    for z in Z:
        diff = np.maximum(A - z, 0.0)
        d = np.sqrt((diff ** 2).sum(axis=1))
        tot += d.min()
    return float(tot / len(Z))


def eps_additive(A, Z):
    # binary additive epsilon I_eps+(A,Z) = max_z min_a max_i (a_i - z_i)
    worst = -1e9
    for z in Z:
        best = min(float(np.max(a - z)) for a in A)
        worst = max(worst, best)
    return worst


def refpoint_free_metrics(combined):
    # Z = nondominated union of all six combined fronts
    allp = []
    for f in combined.values():
        allp += [tuple(p) for p in f]
    Z = nondominated(allp)
    lo = [min(p[i] for p in allp) for i in range(3)]
    hi = [max(p[i] for p in allp) for i in range(3)]
    span = [max(hi[i] - lo[i], 1e-9) for i in range(3)]
    norm = normalize_sets({**combined, "Z": [tuple(z) for z in Z]}, lo, span)
    Zn = norm.pop("Z")
    out = {"Z_size": len(Z), "Z_from": "union no-dominada de los SEIS frentes combinados"}
    igd = {m: igd_plus(norm[m], Zn) for m in norm}
    eps = {m: eps_additive(norm[m], Zn) for m in norm}
    out["IGD_plus"] = igd
    out["epsilon_additive"] = eps
    out["IGD_plus_ranking"] = sorted(igd, key=lambda m: igd[m])      # smaller better
    out["epsilon_ranking"] = sorted(eps, key=lambda m: eps[m])       # smaller better
    return out


# ------------------------------- D.3 f2 sensitivity -------------------------------
def f2_sensitivity(combined, ref=(10.0, 16.0, 20000.0)):
    out = {}
    for m, f in combined.items():
        F = np.array(f, float)
        full = compute_hypervolume([tuple(p) for p in F], ref)
        med1, med3 = float(np.median(F[:, 0])), float(np.median(F[:, 2]))
        # fix f1,f3 to medians, vary only f2
        F2 = F.copy()
        F2[:, 0] = med1
        F2[:, 2] = med3
        hv_f2only = compute_hypervolume([tuple(p) for p in F2], ref)
        out[m] = {"hv_full": full, "hv_f2only": hv_f2only,
                  "f2only_over_full": round(hv_f2only / full, 4) if full else None}
    return out


def fig_heatmap(sweep, path):
    refs = list(sweep.keys())
    methods = list(next(iter(sweep.values()))["per_run_hv_mean"].keys())
    # normalize per ref to [0,1] for color
    data = []
    for ri, r in enumerate(refs):
        mm = sweep[r]["per_run_hv_mean"]
        vals = list(mm.values())
        lo, hi = min(vals), max(vals)
        for mi, m in enumerate(methods):
            v = mm[m]
            norm = (v - lo) / (hi - lo) if hi > lo else 0.5
            rank = sweep[r]["ranking"].index(m) + 1
            data.append([mi, ri, round(norm, 3), rank])
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Exp D - Ranking por reference point</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;margin:0;padding:24px;color:#1a1a1a}}
h2{{color:#003DA5;margin:0 0 4px}}.sub{{color:#666;margin:0 0 16px;font-size:13px;max-width:900px}}#c{{width:1000px;height:460px}}</style>
</head><body>
<h2>Robustez del ranking de los 6 metodos al reference point (HV per-run)</h2>
<p class="sub">Color = HV per-run normalizado por fila (mas oscuro = mejor); el numero es el RANK (1=mejor) del metodo bajo ese reference point. Si el ranking de tiers se mantiene al variar el reference point, 'random restart competitivo' NO es artefacto de un HV insensible.</p>
<div id="c"></div>
<script>
var methods={json.dumps(methods)}, refs={json.dumps(refs)};
var data={json.dumps([[d[0],d[1],d[2],d[3]] for d in data])};
var ch=echarts.init(document.getElementById('c'));
ch.setOption({{
 tooltip:{{formatter:p=>methods[p.data[0]]+' @ '+refs[p.data[1]]+'<br>rank '+p.data[3]}},
 grid:{{left:170,right:30,bottom:90,top:30}},
 xAxis:{{type:'category',data:methods,axisLabel:{{rotate:25,fontSize:11}}}},
 yAxis:{{type:'category',data:refs,axisLabel:{{fontSize:11}}}},
 visualMap:{{min:0,max:1,show:false,inRange:{{color:['#eef3fb','#003DA5']}}}},
 series:[{{type:'heatmap',data:data.map(d=>[d[0],d[1],d[2]]),
   label:{{show:true,formatter:p=>'#'+data[p.dataIndex][3],color:'#fff',fontWeight:600}},
   itemStyle:{{borderColor:'#fff',borderWidth:2}}}}]
}});
</script></body></html>"""
    path.write_text(html)


def main():
    t0 = time.time()
    problem = VisaProblem()
    FIGDIR.mkdir(parents=True, exist_ok=True)

    print("building per-run fronts (regen with published seeds)...")
    prf = build_per_run_fronts(problem)

    # validation: per-run HV at baseline ref matches stored stats where available
    base = (10.0, 16.0, 20000.0)
    val = {}
    mh_hv = [compute_hypervolume([tuple(p) for p in fr], base) for fr in prf["mohho_realcoded"]["fronts"]]
    try:
        stored = json.load(open(RESULTS / "stats_test.json"))["mohho_hv"]
        val["mohho_meanHV_regen_vs_stored"] = [round(float(np.mean(mh_hv)), 1),
                                               round(float(np.mean(stored)), 1)]
    except Exception:
        pass

    print("D.1 reference-point sweep (per-run HV ranking)...")
    sweep, refs = ref_sweep(prf)
    for name, s in sweep.items():
        print(f"  {name}: rank1={s['ranking'][0]} | perm>rk tier: {s['perm_tier_above_rk_tier']} "
              f"| rand restart rank {s['rank_of_random_restart']}")

    print("D.2 reference-free metrics (IGD+, epsilon; Z from 6 methods)...")
    combined = json.load(open(RESULTS / "collapse_fronts.json"))["fronts"]
    rf = refpoint_free_metrics(combined)
    print(f"  IGD+ ranking: {rf['IGD_plus_ranking']}")
    print(f"  epsilon ranking: {rf['epsilon_ranking']}")

    print("D.3 HV sensitivity to f2...")
    f2s = f2_sensitivity(combined)
    frac = float(np.mean([v["f2only_over_full"] for v in f2s.values()]))
    print(f"  mean HV(f2-only)/HV(full) = {frac:.3f}")

    # tier preservation summary
    tiers_preserved = all(s["perm_tier_above_rk_tier"] for s in sweep.values())
    igd_tier = _tier_preserved(rf["IGD_plus_ranking"], prf)
    eps_tier = _tier_preserved(rf["epsilon_ranking"], prf)

    h_met = ("REFUTADA: el ranking/tier es robusto al reference point y se preserva "
             "bajo IGD+ y epsilon (metricas sin reference point); 'random restart "
             "competitivo' NO es artefacto de un HV insensible."
             if tiers_preserved and igd_tier and eps_tier else
             "PARCIAL/CONFIRMADA: el ranking cambia con el reference point o no se "
             "preserva bajo IGD+/epsilon; parte del resultado HV puede ser sensible "
             "a la metrica. Ver detalle.")

    out = {
        "validation": val,
        "D1_refpoint_sweep": sweep,
        "D1_tiers_preserved_all_refpoints": tiers_preserved,
        "D2_reference_free_metrics": rf,
        "D2_IGDplus_tier_preserved": igd_tier,
        "D2_epsilon_tier_preserved": eps_tier,
        "D3_f2_sensitivity": f2s,
        "D3_mean_hv_f2only_over_full": round(frac, 4),
        "D3_note": ("Si HV(f2-only)/HV(full) ~ 1, el HV esta casi enteramente "
                    "determinado por la cobertura de f2 -> el claim aplica al eje f2."),
        "H_met_verdict": h_met,
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "expD_metric_robustness.json", "w"),
              indent=2, ensure_ascii=False)
    fig_heatmap(sweep, FIGDIR / "expD_refpoint_rankings.html")
    print(f"\nH_met: {h_met[:60]}... | f2-fraction {frac:.2f} | {out['elapsed_s']:.0f}s")
    print("-> expD_metric_robustness.json + heatmap")


def _tier_preserved(ranking, prf):
    # all permutation methods ranked above all random_key methods
    pos = {m: i for i, m in enumerate(ranking)}
    perm_worst = max(pos[m] for m in prf if prf[m]["tier"] == "permutation")
    rk_best = min(pos[m] for m in prf if prf[m]["tier"] == "random_key")
    return bool(perm_worst < rk_best)


if __name__ == "__main__":
    main()
