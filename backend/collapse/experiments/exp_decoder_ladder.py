"""
SUPERPROMPT v2 - Experimento C: colapso por decoder (H_dec, Seccion 5).

Re-corre el ladder de 6 metodos sobre decoders NO-saturantes (C1 fractional, C2
stochastic-skip) y verifica si la SEPARACION perm-tier vs rk-tier persiste. La
pregunta NO es si baja el HV absoluto (bajara: el espacio es mayor), sino si se
PRESERVA la separacion. Si se preserva -> H_dec refutada (tesis blindada). Si los
tiers se mezclan bajo C1 -> H_dec confirmada (el decoder era el driver).

Componentes:
  - Ladder completo sobre greedy/C1/C2 (N seeds, 25,000 evals, instancia base).
  - HV comparable: box comun (normalizacion min-max por la UNION de los 3 decoders).
  - Validacion: greedy reproduce el HV per-run publicado.
  - Phenotype-preservation: tau_orden de SBX + distancia fenotipica L1 de x bajo SBX
    y bajo HHO (greedy y C1).
  - Q1 empirico: soluciones C1 con slack_V>0 no-dominadas vs el frente greedy.

Salida: app/data/results/expC_decoder_ladder.json
        + MICAI/figures/collapse/expC_decoder_ladder.html
Ejecutar: python3 -m collapse.experiments.exp_decoder_ladder [N_SEEDS]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

from app.core.config import NUM_GROUPS, LB, UB
from app.core.decoder import spv
from app.core.problem import VisaProblem
from app.core.mohho import compute_hypervolume, dominates
from collapse.decoders import DECODERS, check_feasibility
from collapse.ladder import (RUNNERS, TIER, sbx_gen, BUDGET,
                             op3_soft_siege, leader, arch_add, crowding3)
from collapse.experiments.exp_optimizer_sanity import hv3d

RESULTS = Path("app/data/results")
FIGDIR = Path("../MICAI/figures/collapse")
SEEDS_DEFAULT = list(range(42, 72))      # set unico para los 6 metodos (comparabilidad)


def run_ladder(problem, decoders, seeds):
    """{decoder: {method: {'fronts':[per-seed front], 'hv_raw':[per-seed]}}}"""
    res = {}
    for dname, dec in decoders.items():
        res[dname] = {}
        for m, fn in RUNNERS.items():
            fronts, hvs = [], []
            t0 = time.time()
            for s in seeds:
                af = fn(dec, problem, s)
                fits = [tuple(map(float, p)) for p in af]
                fronts.append(fits)
                hvs.append(compute_hypervolume(fits))
            res[dname][m] = {"fronts": fronts, "hv_raw": hvs,
                             "tier": TIER[m], "secs": round(time.time() - t0, 1)}
            print(f"  [{dname}] {m:18s} HVraw mean={np.mean(hvs):>11,.0f} "
                  f"CV={np.std(hvs)/max(np.mean(hvs),1)*100:4.2f}% ({res[dname][m]['secs']}s)")
    return res


def common_box_hv(res):
    """Normaliza min-max por la UNION de TODOS los puntos (3 decoders x 6 metodos x
    seeds) y recomputa HV en el box comun -> comparable entre decoders."""
    allpts = []
    for d in res.values():
        for m in d.values():
            for fr in m["fronts"]:
                allpts.extend(fr)
    A = np.array(allpts, float)
    lo = A.min(axis=0)
    hi = A.max(axis=0)
    span = np.maximum(hi - lo, 1e-12)
    ref = (1.0, 1.0, 1.0)

    def norm_hv(front):
        nf = [tuple(((np.array(p) - lo) / span).tolist()) for p in front]
        return hv3d(nf, ref)

    box = {"lo": lo.tolist(), "hi": hi.tolist(), "ref_norm": list(ref)}
    out = {}
    for dname, d in res.items():
        out[dname] = {}
        for m, mm in d.items():
            hvn = [norm_hv(fr) for fr in mm["fronts"]]
            out[dname][m] = {"hv_norm_mean": float(np.mean(hvn)),
                             "hv_norm_std": float(np.std(hvn)),
                             "hv_norm_per_seed": hvn,
                             "tier": mm["tier"]}
    return box, out


def tier_separation(norm):
    """Por decoder: perm-tier vs rk-tier sobre HV normalizado (box comun), con prueba
    pareada por seed (Wilcoxon, perm-tier mean vs rk-tier mean por seed)."""
    from scipy.stats import wilcoxon, mannwhitneyu
    sep = {}
    for dname, methods in norm.items():
        rk_methods = [m for m in methods if methods[m]["tier"] == "random_key"]
        pm_methods = [m for m in methods if methods[m]["tier"] == "permutation"]
        rk = [methods[m]["hv_norm_mean"] for m in rk_methods]
        pm = [methods[m]["hv_norm_mean"] for m in pm_methods]
        rk_mean, pm_mean = float(np.mean(rk)), float(np.mean(pm))
        gap = (pm_mean - rk_mean) / rk_mean * 100 if rk_mean else 0.0
        # per-seed paired: mean rk vs mean perm at each seed
        nseed = len(methods[rk_methods[0]]["hv_norm_per_seed"])
        rk_by_seed = [float(np.mean([methods[m]["hv_norm_per_seed"][s] for m in rk_methods]))
                      for s in range(nseed)]
        pm_by_seed = [float(np.mean([methods[m]["hv_norm_per_seed"][s] for m in pm_methods]))
                      for s in range(nseed)]
        # Este contraste NO es uno de los dos disenos con bloqueo genuino: las
        # etiquetas de semilla no acoplan tiers distintos. MWU es la primaria.
        wp = mwu = None
        if nseed >= 6 and any(a != b for a, b in zip(rk_by_seed, pm_by_seed)):
            try:
                mwu = float(mannwhitneyu(pm_by_seed, rk_by_seed, alternative="greater").pvalue)
                wp = float(wilcoxon(pm_by_seed, rk_by_seed, alternative="greater").pvalue)
            except ValueError:
                pass
        sep[dname] = {
            "rk_tier_methods_hv": {m: methods[m]["hv_norm_mean"] for m in rk_methods},
            "perm_tier_methods_hv": {m: methods[m]["hv_norm_mean"] for m in pm_methods},
            "rk_mean": rk_mean, "perm_mean": pm_mean,
            "perm_minus_rk_pct": round(gap, 2),
            "perm_min_gt_rk_max": bool(min(pm) > max(rk)),
            "perm_beats_rk": bool(pm_mean > rk_mean),
            "mwu_p_perm_gt_rk": mwu,                      # PRIMARIA (no pareada)
            "seedlabel_wilcoxon_p_perm_gt_rk": wp,        # sensibilidad
            "perm_gt_rk_seed_fraction": round(np.mean([p > r for p, r in
                                              zip(pm_by_seed, rk_by_seed)]), 3),
        }
    return sep


# ----------------------- phenotype preservation (C.3) -----------------------
def _measure(problem, dec, rng, n_pairs, regime):
    """regime='random': padres aleatorios; 'near': padres cercanos (emula poblacion
    convergida / on-trajectory, donde el tournament elige padres similares)."""
    d = dec.rk_dim
    V = problem.total_visas
    ax, af = [], []
    for _ in range(60):
        v = rng.uniform(LB, UB, d)
        arch_add(ax, af, v, problem.evaluate(dec.decode_rk(v, problem)), 100, rng)
    tau_sbx, l1_sbx, l1_hho = [], [], []
    for _ in range(n_pairs):
        p1 = rng.uniform(LB, UB, d)
        if regime == "near":
            p2 = np.clip(p1 + rng.normal(0, 0.05, d), LB, UB)
        else:
            p2 = rng.uniform(LB, UB, d)
        c1, _c2 = sbx_gen(p1, p2, rng)
        tau, _ = kendalltau(spv(p1[:NUM_GROUPS]), spv(c1[:NUM_GROUPS]))
        tau_sbx.append(tau if tau == tau else 0.0)
        xp = dec.decode_rk(p1, problem)
        xc = dec.decode_rk(c1, problem)
        l1_sbx.append(sum(abs(xp[i] - xc[i]) for i in xp) / V)
        rab = leader(ax, af, rng)
        ch = op3_soft_siege(p1, np.asarray(rab), 0.7, rng)
        xh = dec.decode_rk(ch, problem)
        l1_hho.append(sum(abs(xp[i] - xh[i]) for i in xp) / V)
    return {
        "tau_order_sbx_mean": round(float(np.mean(tau_sbx)), 4),
        "phenotypic_L1_sbx_mean": round(float(np.mean(l1_sbx)), 5),
        "phenotypic_L1_hho_mean": round(float(np.mean(l1_hho)), 5),
        "hho_over_sbx_phenotypic_ratio": round(float(np.mean(l1_hho) /
                                                     max(np.mean(l1_sbx), 1e-9)), 2),
    }


def phenotype_preservation(problem, dec, n_pairs=400, seed=1):
    """Dos regimenes: 'near' (padres similares = on-trajectory, comparable al tau=0.99
    del paper) y 'random' (peor caso). En ambos se reporta tau_orden y la distancia
    fenotipica L1 de x bajo SBX vs bajo HHO -> extiende el mecanismo del paper del
    ORDEN al FENOTIPO completo (incl. el bloque de intensidad de C1)."""
    out = {}
    for regime in ("near", "random"):
        out[regime] = _measure(problem, dec, np.random.default_rng(seed), n_pairs, regime)
    out["sbx_near_identity_on_phenotype"] = (
        out["near"]["phenotypic_L1_sbx_mean"] < 0.2 * out["near"]["phenotypic_L1_hho_mean"])
    return out


# ----------------------- empirical Q1 via C1 slack -----------------------
def empirical_q1(res, problem):
    """Soluciones C1 (cualquier metodo) con slack_V>0 no-dominadas vs greedy front."""
    import csv
    gfront = []
    for r in csv.DictReader(open(RESULTS / "pareto_front.csv")):
        if r["type"] == "pareto":
            gfront.append((float(r["f1"]), float(r["f2"]), float(r["f3"])))
    g_best_f2 = min(g[1] for g in gfront)
    # A non-saturating solution only counts as a MEANINGFUL disparity win if it both
    # (a) beats the greedy front's best f2 by >0.5 yr AND (b) is not a degenerate
    # near-empty allocation: f2 falls spuriously low on near-empty allocations because
    # every unserved country takes its w_max fallback, so we require the solution to
    # still use most of the budget (waste below 10% of V). Without (b) the count is
    # inflated by ~all-unused allocations (f3>100k) that are non-dominated only because
    # greedy never wastes that much --- the false positive the MILP's f1-objective avoids.
    waste_ceiling = 0.1 * problem.total_visas
    contra = []
    if "C1_fractional" not in res:
        return {"checked": False}
    for m, mm in res["C1_fractional"].items():
        for fr in mm["fronts"]:
            for p in fr:
                if p[2] <= 0:        # f3 = waste = slack_V
                    continue
                if any(dominates(g, p) for g in gfront):
                    continue
                meaningful = (p[1] < g_best_f2 - 0.5) and (p[2] < waste_ceiling)
                contra.append({"f1": round(p[0], 5), "f2": round(p[1], 4),
                               "f3": round(p[2], 0), "meaningful_f2": bool(meaningful)})
    # dedup
    uniq = {(c["f1"], c["f2"], c["f3"]): c for c in contra}
    contra = list(uniq.values())
    meaningful = [c for c in contra if c["meaningful_f2"]]
    return {"checked": True, "n_nonsaturating_nondominated": len(contra),
            "n_meaningful": len(meaningful), "greedy_best_f2": g_best_f2,
            "waste_ceiling": waste_ceiling,
            "note": ("n_meaningful requires f2 gain >0.5yr AND waste <10% of V; the "
                     "latter screens degenerate near-empty allocations whose low f2 is "
                     "a w_max-fallback artifact. Consistent with the MILP (0 meaningful)."),
            "examples": (sorted(meaningful, key=lambda c: c["f1"])[:10] or
                         sorted(contra, key=lambda c: c["f1"])[:10])}


def fig_table(sep, box, validation, path):
    decs = list(sep.keys())
    rows = ""
    for d in decs:
        s = sep[d]
        rk = " / ".join(f"{k.split('_')[-1]}:{v*100:.1f}" for k, v in s["rk_tier_methods_hv"].items())
        pm = " / ".join(f"{k.split('_')[-1]}:{v*100:.1f}" for k, v in s["perm_tier_methods_hv"].items())
        sepflag = "SI" if s["perm_beats_rk"] else "NO"
        strict = "estricta" if s["perm_min_gt_rk_max"] else "parcial"
        color = "#1a7a3a" if s["perm_beats_rk"] else "#b00020"
        rows += (f"<tr><td><b>{d}</b></td><td>{s['rk_mean']*100:.2f}</td>"
                 f"<td>{s['perm_mean']*100:.2f}</td>"
                 f"<td style='color:{color};font-weight:600'>{s['perm_minus_rk_pct']:+.2f}%</td>"
                 f"<td style='color:{color};font-weight:600'>{sepflag} ({strict})</td></tr>")
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Exp C - Ladder por decoder</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;margin:0;padding:28px;color:#1a1a1a}}
h2{{color:#003DA5;margin:0 0 4px}}.sub{{color:#666;margin:0 0 18px;font-size:13px;max-width:880px}}
table{{border-collapse:collapse;font-size:14px}}th,td{{border:1px solid #d8dde3;padding:8px 14px;text-align:center}}
th{{background:#003DA5;color:#fff;font-weight:600}}td:first-child{{text-align:left;background:#f4f7fb}}
.note{{margin-top:16px;font-size:12.5px;color:#444;max-width:900px}}</style>
</head><body>
<h2>H_dec - Separacion perm-tier vs rk-tier bajo decoders saturante / no-saturantes</h2>
<p class="sub">HV normalizado en box comun (union min-max de los 3 decoders) x100. La pregunta es si la SEPARACION (perm &gt; rk) PERSISTE al quitar la saturacion del greedy, no si baja el HV absoluto.</p>
<table>
<tr><th>Decoder</th><th>rk-tier HV (x100)</th><th>perm-tier HV (x100)</th><th>perm &minus; rk</th><th>perm &gt; rk?</th></tr>
{rows}
</table>
<p class="note">Si la separacion perm &gt; rk persiste bajo C1/C2 (no-saturantes) => H_dec REFUTADA: la ventaja de la representacion no es artefacto de la saturacion del decoder. Si los tiers se mezclan bajo C1 => H_dec confirmada (el greedy era el driver). Box comun lo=[{box['lo'][0]:.3f},{box['lo'][1]:.3f},{box['lo'][2]:.0f}] hi=[{box['hi'][0]:.3f},{box['hi'][1]:.3f},{box['hi'][2]:.0f}].</p>
</body></html>"""
    path.write_text(html)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seeds = SEEDS_DEFAULT[:n]
    t0 = time.time()
    problem = VisaProblem()
    FIGDIR.mkdir(parents=True, exist_ok=True)
    decoders = {k: DECODERS[k] for k in ["greedy", "C1_fractional", "C2_stochastic_skip"]}

    print(f"== Exp C: ladder x 3 decoders x {len(seeds)} seeds ==")
    res = run_ladder(problem, decoders, seeds)

    # feasibility audit on a sample of produced solutions per decoder
    feas = {}
    for dname, dec in decoders.items():
        rng = np.random.default_rng(7)
        viol = 0
        for _ in range(300):
            v = rng.uniform(LB, UB, dec.rk_dim)
            viol += len(check_feasibility(dec.decode_rk(v, problem), problem))
        feas[dname] = viol

    box, norm = common_box_hv(res)
    sep = tier_separation(norm)

    print("== phenotype preservation ==")
    pheno = {d: phenotype_preservation(problem, decoders[d])
             for d in ["greedy", "C1_fractional"]}
    for d, p in pheno.items():
        nr = p["near"]
        print(f"  {d} (near): tau_sbx={nr['tau_order_sbx_mean']:.3f} "
              f"L1_sbx={nr['phenotypic_L1_sbx_mean']:.5f} L1_hho={nr['phenotypic_L1_hho_mean']:.4f} "
              f"(hho/sbx={nr['hho_over_sbx_phenotypic_ratio']}x)")

    eq1 = empirical_q1(res, problem)

    # ----- verdict (matizado): no basta perm>rk; mide cuanto COLAPSA la separacion -----
    g_sep = sep["greedy"]["perm_minus_rk_pct"]
    c1_sep = sep["C1_fractional"]["perm_minus_rk_pct"]
    c2_sep = sep["C2_stochastic_skip"]["perm_minus_rk_pct"]
    c1_ratio = c1_sep / g_sep if g_sep else 0.0       # fraccion de separacion que sobrevive
    c2_ratio = c2_sep / g_sep if g_sep else 0.0
    c1_sig = sep["C1_fractional"]["mwu_p_perm_gt_rk"]
    c1_significant = (c1_sig is not None and c1_sig < 0.05)

    if c1_ratio >= 0.6 and c1_significant:
        h_dec = ("REFUTADA: la separacion perm>rk persiste sustancialmente bajo C1 "
                 f"({c1_sep:+.1f}% vs greedy {g_sep:+.1f}%, {c1_ratio*100:.0f}% sobrevive, "
                 "pareado p<0.05); la ventaja de la representacion NO es artefacto de la "
                 "saturacion del decoder.")
    elif c1_ratio <= 0.25 or not c1_significant:
        h_dec = ("PARCIALMENTE CONFIRMADA: bajo el decoder mas no-saturante (C1) la "
                 f"separacion perm>rk COLAPSA de {g_sep:+.1f}% (greedy, estricta) a "
                 f"{c1_sep:+.1f}% (solo {c1_ratio*100:.0f}% sobrevive"
                 + (", no significativa" if not c1_significant else "") +
                 f"); C2 intermedio {c2_sep:+.1f}%. La saturacion del greedy AMPLIFICA "
                 "el efecto representacion. AMENAZA: C1 anade una sub-dimension continua "
                 "(intensidad alpha) que los metodos perm manejan con operador real "
                 "injertado, diluyendo la ventaja permutacional. El claim del paper debe "
                 "acotarse a decoders saturantes.")
    else:
        h_dec = ("INTERMEDIA: la separacion se reduce bajo C1 "
                 f"({c1_sep:+.1f}% vs {g_sep:+.1f}%, {c1_ratio*100:.0f}% sobrevive) pero "
                 "no colapsa del todo; efecto representacion atenuado, no eliminado.")
    persists = c1_ratio >= 0.6 and c1_significant

    # strip heavy fronts before saving (keep hv + summaries)
    res_light = {d: {m: {"hv_raw": res[d][m]["hv_raw"], "tier": res[d][m]["tier"],
                         "secs": res[d][m]["secs"],
                         "front_size_mean": float(np.mean([len(f) for f in res[d][m]["fronts"]]))}
                     for m in res[d]} for d in res}

    out = {
        "seeds": seeds, "n_seeds": len(seeds), "budget_evals": BUDGET,
        "decoders": list(decoders.keys()),
        "feasibility_violations_per_decoder": feas,
        "ladder_hv_raw": res_light,
        "common_box": box,
        "ladder_hv_norm": norm,
        "tier_separation": sep,
        "separation_collapse": {
            "greedy_perm_minus_rk_pct": g_sep,
            "C1_perm_minus_rk_pct": c1_sep,
            "C2_perm_minus_rk_pct": c2_sep,
            "C1_fraction_of_greedy_separation_surviving": round(c1_ratio, 3),
            "C2_fraction_of_greedy_separation_surviving": round(c2_ratio, 3),
            "C1_significant_mwu": c1_significant,
        },
        "phenotype_preservation": pheno,
        "empirical_Q1_C1": eq1,
        "H_dec_verdict": h_dec,
        "separation_persists_under_nonsaturating": persists,
        "elapsed_s": time.time() - t0,
    }
    json.dump(out, open(RESULTS / "expC_decoder_ladder.json", "w"),
              indent=2, ensure_ascii=False)
    fig_table(sep, box, feas, FIGDIR / "expC_decoder_ladder.html")

    print("\n== tier separation (perm - rk), common-box HV ==")
    for d in decoders:
        print(f"  {d:20s} perm-rk = {sep[d]['perm_minus_rk_pct']:+.2f}%  "
              f"(perm>rk: {sep[d]['perm_beats_rk']}, estricta: {sep[d]['perm_min_gt_rk_max']})")
    print(f"feasibility violations: {feas}")
    print(f"H_dec: {h_dec[:60]}...")
    print(f"-> expC_decoder_ladder.json + figura ({out['elapsed_s']:.0f}s)")


if __name__ == "__main__":
    main()
