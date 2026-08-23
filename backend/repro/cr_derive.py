"""Derivador PURO del camera-ready. Lee SOLO series almacenadas y escribe en un
directorio de salida (por defecto staging). NO ejecuta optimizadores, no toca
artefactos sellados y no parchea nada in-place.

Produce, con procedencia completa (script, hashes de entrada, esquema, config,
commit base):
  * omnibus Kruskal-Wallis (primario) + Friedman seed-label (sensibilidad),
    para la escalera de 9 y para las 4 estructuras;
  * LAS DOS familias Holm -- no pareada y seed-label -- para mostrar que la
    conclusion sobrevive a la dependencia heterogenea;
  * interaccion 2x2 BLOQUEADA: Wilcoxon sobre diferencias-en-diferencias como
    principal y sign-flip bloqueado como sensibilidad (la permutacion anterior
    rompia los bloques por semilla);
  * tier_separation de expC recomputada desde las series, sin la clave obsoleta;
  * procedencia de Z9: actual (185) frente al historico (187).

Uso: python cr_derive.py [--out DIR]
"""
import sys, json, hashlib, argparse, subprocess
from pathlib import Path
import numpy as np
from scipy.stats import kruskal, friedmanchisquare, wilcoxon, mannwhitneyu
sys.path.insert(0, str(Path(__file__).parent))
import _bootstrap; _bootstrap.bootstrap_engine()
R = Path(_bootstrap.results_dir())

# El manifiesto NO se declara a mano: J() registra cada archivo que se abre de
# verdad. Una lista manual mentia en las dos direcciones (sobraba controls.json,
# faltaban omnibus_stats.json y cr_indicators.json).
_READS = {}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def J(f):
    path = R / f
    _READS[f] = sha(path)
    return json.loads(path.read_text())

def provenance():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, cwd=str(R)).stdout.strip()
    except Exception:
        commit = None
    return {"schema_version": "cr-derived/1.0",
            "script": "backend/repro/cr_derive.py",
            "script_sha256": sha(Path(__file__)),
            "base_commit": commit,
            "base_commit_note": ("commit del arbol EN EL MOMENTO DE DERIVAR. Es por "
                                 "construccion un ancestro del commit que contiene este "
                                 "JSON: el fichero no puede registrar el hash del commit "
                                 "que aun no existe cuando se escribe. No se exige "
                                 "igualdad; lo que si se exige es que los sha256 de "
                                 "inputs_sha256 coincidan con los ficheros vivos."),
            "no_optimizers_executed": True,
            "inputs_sha256": dict(sorted(_READS.items())),   # lecturas EFECTIVAS
            "n_inputs_read": len(_READS),
            "config": {"seeds": list(range(1, 31)), "alpha": 0.05}}

def a12(x, y):
    gt = sum(1 for a in x for b in y if a > b); eq = sum(1 for a in x for b in y if a == b)
    return (gt + 0.5 * eq) / (len(x) * len(y))

def series9():
    lad = J("ladder_v5.json")["methods"]
    return {"nsga2_realcoded": lad["nsga2_realcoded"]["hv_per_seed"],
            "mohho_realcoded": lad["naive_mohho"]["hv_per_seed"],
            "rk_nsga2_biased": J("brkga_ladder.json")["hv_per_seed"],
            "random_restart": lad["random_restart"]["hv_per_seed"],
            "nds_selected_mohho": J("competent_arch100.json")["hv_per_seed_arch100"],
            "perm_moead": lad["perm_moead"]["hv_per_seed"],
            "discrete_mohho": lad["discrete_mohho"]["hv_per_seed"],
            "perm_spea2": J("perm_spea2.json")["per_run_hv"],
            "perm_nsga2": lad["perm_nsga2"]["hv_per_seed"]}

# ---------------------------------------------------------------- omnibus
def omnibus():
    S = series9(); v = list(S.values())
    H, pk = kruskal(*v); chi, pf = friedmanchisquare(*v)
    out = {"ladder9": {"primary": {"test": "Kruskal-Wallis (unpaired)", "H": float(H),
                                   "p": float(pk), "k": 9, "n": 30},
                       "sensitivity": {"test": "Friedman (seed-label, descriptive)",
                                       "chi2": float(chi), "p": float(pf)}},
           "structures": {}}
    lad = J("ladder_v5.json")["methods"]
    # Las SEIS series exactas que alimentan la Fig. 5 en el caso visa.
    # Antes se copiaba H=134.28 de omnibus_stats.json y ademas el dict `src` con
    # la clave "visa" se sobrescribia acto seguido: el visa nunca se derivaba.
    visa6 = [lad["nsga2_realcoded"]["hv_per_seed"], lad["random_restart"]["hv_per_seed"],
             lad["naive_mohho"]["hv_per_seed"], lad["discrete_mohho"]["hv_per_seed"],
             lad["perm_moead"]["hv_per_seed"], lad["perm_nsga2"]["hv_per_seed"]]
    ms = J("more_structures.json")
    src = {"visa": visa6,
           "knapsack": [x["per_run_hv"] for x in J("second_problem.json")["methods"].values()],
           "TSP": [x["per_run_hv"] for x in ms["mo-TSP"]["methods"].values()],
           "flow-shop": [x["per_run_hv"] for x in ms["mo-PFSP"]["methods"].values()]}
    for k, sser in src.items():
        H2, p2 = kruskal(*sser)
        out["structures"][k] = {"H": float(H2), "p": float(p2), "k": len(sser), "n": 30,
                                "derived_from": "per-seed series (no value copied)"}
    return out

# ------------------------------------------------------- interaccion 2x2
def interaction_2x2():
    """Diferencias-en-diferencias BLOQUEADAS por semilla.

    La permutacion previa barajaba residuos entre semillas y rompia los bloques.
    Aqui el contraste es d_s = (order_nds - order_gated) - (near_nds - near_gated)
    dentro de cada semilla s, que es exactamente el termino de interaccion.
    Principal: Wilcoxon signed-rank sobre d. Sensibilidad: sign-flip dentro del bloque.
    """
    c = J("factorial_2x2_paired.json")["cells"]
    on = np.array(c["order_nds"]["hv_per_seed"]);  og = np.array(c["order_gated"]["hv_per_seed"])
    nn = np.array(c["near_nds"]["hv_per_seed"]);   ng = np.array(c["near_gated"]["hv_per_seed"])
    d = (on - og) - (nn - ng)
    w = float(wilcoxon(d, alternative="two-sided").pvalue)
    t_stat = float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d))))
    from scipy.stats import t as tdist
    t_p = float(2 * (1 - tdist.cdf(abs(t_stat), len(d) - 1)))
    # 1e6 permutaciones por bloques (memoria), correccion (count+1)/(n+1),
    # con MCSE e IC: con 2e4 habia demasiado pocas excedencias y el p oscilaba.
    SEED, NPERM, BLK = 20260822, 1_000_000, 50_000
    rng = np.random.default_rng(SEED); obs = abs(d.mean()); exc = 0
    for start in range(0, NPERM, BLK):
        n = min(BLK, NPERM - start)
        S = rng.choice([-1.0, 1.0], size=(n, len(d)))
        exc += int((np.abs(S @ d / len(d)) >= obs).sum())
    sf = (exc + 1) / (NPERM + 1)
    mcse = float(np.sqrt(sf * (1 - sf) / NPERM))
    ci = [max(0.0, sf - 1.96 * mcse), sf + 1.96 * mcse]
    return {"contrast": "(order_nds - order_gated) - (near_nds - near_gated), per seed",
            "mean_difference_in_differences": float(d.mean()),
            "primary": {"test": "Wilcoxon signed-rank on blocked differences",
                        "p": w, "n": int(len(d))},
            "sensitivity": {"blocked_t": {"t": t_stat, "p": t_p},
                            "blocked_sign_flip": {"p": sf, "n_perm": NPERM, "seed": SEED,
                                                  "exceedances": exc, "correction": "(count+1)/(n+1)",
                                                  "mcse": mcse, "ci95": ci}},
            "retired": {"anova_F_p": 8.0e-5, "unblocked_permutation_p": 2.0e-4,
                        "why": "la permutacion barajaba residuos entre semillas y rompia los bloques"}}

# ------------------------------------------------------------ familias Holm
def holm(pairs):
    fam = sorted(pairs, key=lambda r: r[1]); m = len(fam); res = {}; ok = True
    for i, (name, p) in enumerate(fam):
        thr = 0.05 / (m - i); s = p <= thr; ok &= s
        res[name] = {"p": float(p), "holm_threshold": thr, "survives": bool(s)}
    return {"m": m, "results": res, "all_survive": bool(ok)}

def holm_families(inter):
    S = series9(); rr = S["random_restart"]
    scp = J("prospective_scp.json")["hv_per_seed"]
    def both(x, y, alt):
        return (float(mannwhitneyu(x, y, alternative=alt).pvalue),
                float(wilcoxon(x, y, alternative=alt).pvalue))
    items = [("perm_nsga2_vs_random", S["perm_nsga2"], rr, "greater"),
             ("nsga2_vs_random", S["nsga2_realcoded"], rr, "less"),
             ("perm_spea2_vs_random", S["perm_spea2"], rr, "greater"),
             ("mohho_vs_random", S["mohho_realcoded"], rr, "less"),
             ("perm_moead_vs_random", S["perm_moead"], rr, "greater"),
             ("nds_vs_random", S["nds_selected_mohho"], rr, "greater"),
             ("mohho_vs_nsga2", S["mohho_realcoded"], S["nsga2_realcoded"], "two-sided"),
             ("discrete_vs_mohho", S["discrete_mohho"], S["mohho_realcoded"], "greater"),
             ("scp_perm_vs_random", scp["perm_nsga2"], scp["random_restart"], "greater"),
             ("scp_nds_vs_random", scp["competent_mohho"], scp["random_restart"], "greater")]
    unp, seed = [], []
    for name, x, y, alt in items:
        m, w = both(x, y, alt); unp.append((name, m)); seed.append((name, w))
    c = J("factorial_2x2_paired.json")["cells"]
    rr2 = J("factorial_2x2_paired.json")["random_hv_per_seed"]
    cell = c["order_nds"]["hv_per_seed"]
    unp.append(("cell2x2_vs_random", float(mannwhitneyu(cell, rr2, alternative="greater").pvalue)))
    seed.append(("cell2x2_vs_random", float(wilcoxon(cell, rr2, alternative="greater").pvalue)))
    unp.append(("interaction_2x2", inter["primary"]["p"]))
    seed.append(("interaction_2x2", inter["primary"]["p"]))
    return {"unpaired_primary": holm(unp), "seed_label_sensitivity": holm(seed),
            "note": "ambas familias se reportan; la conclusion debe sobrevivir a las dos"}

# ---------------------------------------------------------------- expC
def expC():
    d = J("expC_decoder_ladder.json"); norm = d["ladder_hv_norm"]; out = {}
    for dn, methods in norm.items():
        rk = [m for m in methods if methods[m]["tier"] == "random_key"]
        pm = [m for m in methods if methods[m]["tier"] == "permutation"]
        n = len(methods[rk[0]]["hv_norm_per_seed"])
        rs = [float(np.mean([methods[m]["hv_norm_per_seed"][i] for m in rk])) for i in range(n)]
        ps = [float(np.mean([methods[m]["hv_norm_per_seed"][i] for m in pm])) for i in range(n)]
        out[dn] = {"rk_mean": float(np.mean(rs)), "perm_mean": float(np.mean(ps)),
                   "perm_minus_rk_pct": round((np.mean(ps) / np.mean(rs) - 1) * 100, 2),
                   "mwu_p_perm_gt_rk": float(mannwhitneyu(ps, rs, alternative="greater").pvalue),
                   "seedlabel_wilcoxon_p_perm_gt_rk": float(wilcoxon(ps, rs, alternative="greater").pvalue),
                   "perm_gt_rk_seed_fraction": round(float(np.mean([a > b for a, b in zip(ps, rs)])), 3)}
    return {"_derived_from": "expC_decoder_ladder.json (historico, intacto: contiene las series crudas)",
            "tier_separation": out,
            "obsolete_keys_removed": ["paired_wilcoxon_p_perm_gt_rk", "C1_paired_significant"]}

def factorial_reanalysis():
    """Reanalisis del 2x2 SIN ejecutar factorial_2x2.py.

    Series de factorial_2x2_paired.json; los movimientos gated se toman del
    artefacto historico (unica medicion existente); configuracion y presupuesto,
    del codigo ya corregido. El JSON historico se conserva intacto.
    """
    pr = J("factorial_2x2_paired.json"); hist = J("factorial_2x2_conditions.json")
    rr = pr["random_hv_per_seed"]; cells = {}
    for name, c in pr["cells"].items():
        h = hist["cells"][name]; sel = h["selection"]; hv = c["hv_per_seed"]
        measured = sel == "gated"
        cells[name] = {
            "operator": h["operator"], "selection": sel,
            "hv_mean": float(np.mean(hv)), "hv_std_pop": float(np.std(hv)),
            "hv_per_seed": hv,
            "vs_random_pct": round((np.mean(hv) / np.mean(rr) - 1) * 100, 2),
            "mwu_p_greater_random": float(mannwhitneyu(hv, rr, alternative="greater").pvalue),
            "seedlabel_wilcoxon_p": float(wilcoxon(hv, rr, alternative="greater").pvalue),
            "A12_vs_random": a12(hv, rr),
            "movement_measured": measured,
            "moved_fraction_mean": (h["moved_fraction_mean"] if measured else None),
            "movement_note": ("proporcion de descendientes que dominan y reemplazan a su padre"
                              if measured else
                              "no definida bajo (mu+lambda): la siguiente poblacion sale de la union"),
            "pm": 0.15 if h["operator"] == "order" else 1.0 / 105}
    return {"_derived_from": "factorial_2x2_paired.json + movimientos gated de factorial_2x2_conditions.json (historicos, intactos)",
            "budget": {"pop": 50, "gen": 500, "initial_evals": 50,
                       "offspring_evals": 25000, "total_evals": 25050},
            "factor_is_a_package": "las celdas difieren en operador Y en p_m (0.15 vs 1/d): el factor es un paquete, no el operador aislado",
            "random_restart_hv_mean": float(np.mean(rr)), "cells": cells}

# ------------------------------------------------------------ procedencia Z9
def z9():
    return {"Z9_current": {"size": J("cr_indicators.json")["reference_front_Z9"]["size"],
                           "source": "per_run_fronts_9.json + competent_arch100.fronts_arch100",
                           "used_for": "IGD+/spacing per-run reported in the camera-ready"},
            "Z9_historical": {"size": J("ladder_igd.json")["reference"]["size"],
                              "source": "per_run_fronts_9.json con la serie de archivo 200",
                              "used_for": "el re-scoring IGD+/epsilon citado en 5.2"},
            "must_not_be_conflated": True}

def controls_vs_random():
    """MWU de los dos controles contra blind random restart, derivada de las series.

    El articulo declara en la Seccion 4.4 que los contrastes van a DOS COLAS salvo
    aviso, asi que la cifra impresa es la bilateral. Se guarda tambien la unilateral
    para que la relacion 2x quede a la vista y nadie tenga que recalcularla fuera.
    """
    rr = J("ladder_v5.json")["methods"]["random_restart"]["hv_per_seed"]
    out = {}
    for nombre, fichero in (("grasp", "grasp_control.json"), ("pls", "pls_control.json")):
        x = J(fichero)["hv_per_seed"]
        dos = mannwhitneyu(x, rr, alternative="two-sided").pvalue
        una = mannwhitneyu(x, rr, alternative="less").pvalue
        out[nombre] = {"n": [len(x), len(rr)],
                       "hv_mean": float(np.mean(x)),
                       "vs_random_pct": float(100 * (np.mean(x) / np.mean(rr) - 1)),
                       "p_two_sided": float(dos),      # <- la que se imprime
                       "p_one_sided_less": float(una),
                       "A12_vs_random": a12(x, rr),
                       "reported": "two-sided, per the Section 4.4 convention"}
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="staging")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    inter = interaction_2x2()
    expc = expC(); fact = factorial_reanalysis()
    doc = {"omnibus": omnibus(), "interaction_2x2": inter,
           "holm": holm_families(inter), "expC_reanalysis": expc,
           "factorial_2x2_reanalysis": fact, "z9_provenance": z9(),
           "controls_vs_random": controls_vs_random()}
    doc["_provenance"] = provenance()          # ultimo: ya estan todas las lecturas
    (out / "expC_reanalysis_cr.json").write_text(json.dumps(expc, indent=1, sort_keys=True))
    (out / "factorial_2x2_reanalysis_cr.json").write_text(json.dumps(fact, indent=1, sort_keys=True))
    (out / "cr_derived.json").write_text(json.dumps(doc, indent=1, sort_keys=True))
    print(f"  -> {out/'cr_derived.json'}")
    o = doc["omnibus"]["ladder9"]
    print(f"  KW ladder9      H={o['primary']['H']:.2f}  p={o['primary']['p']:.3e}")
    print(f"  Friedman (sens) chi2={o['sensitivity']['chi2']:.2f}  p={o['sensitivity']['p']:.3e}")
    print(f"  interaccion 2x2 Wilcoxon bloqueado p={inter['primary']['p']:.3e}"
          f"  | t bloqueada p={inter['sensitivity']['blocked_t']['p']:.3e}"
          f"  | sign-flip p={inter['sensitivity']['blocked_sign_flip']['p']:.3e}")
    for k, v in doc["holm"].items():
        if isinstance(v, dict) and "all_survive" in v:
            print(f"  Holm {k:<24} m={v['m']}  todas sobreviven: {v['all_survive']}")
    for k, v in doc["expC_reanalysis"]["tier_separation"].items():
        print(f"  expC {k:<20} MWU={v['mwu_p_perm_gt_rk']:.3e}  Wilcoxon={v['seedlabel_wilcoxon_p_perm_gt_rk']:.3e}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
