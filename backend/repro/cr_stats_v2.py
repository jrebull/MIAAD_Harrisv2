"""Re-analitica estadistica del camera-ready, con jerarquia explicita de pruebas.

REGLAS (una prueba PRIMARIA por afirmacion):
  * Contrastes exploratorios entre algoritmos (visa): Mann-Whitney U es PRIMARIA.
    Compartir etiqueta de semilla no acopla dos representaciones. El Wilcoxon por
    etiqueta de semilla se reporta como SENSIBILIDAD.
  * mo-SCP: el Wilcoxon pareado es PREREGISTRADO y se conserva como primario --
    una prueba registrada no se sustituye retrospectivamente. MWU va de sensibilidad.
  * 2x2: las cuatro celdas comparten inicializacion por construccion
    (factorial_2x2.py sortea P antes de ramificar operador/seleccion), asi que el
    bloqueo es real: Wilcoxon pareado primario + sign-flip como confirmacion.
  * Holm sobre la familia enumerada de 12, con el p PRIMARIO de cada afirmacion.

NO ejecuta optimizadores: solo lee series por semilla ya selladas.
Salida: results/cr_stats_v2.json
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon, mannwhitneyu
sys.path.insert(0, str(Path(__file__).parent))
import _bootstrap; _bootstrap.bootstrap_engine()
R = Path(_bootstrap.results_dir())
J = lambda f: json.load(open(R / f))

def a12(x, y):
    gt = sum(1 for a in x for b in y if a > b); eq = sum(1 for a in x for b in y if a == b)
    return (gt + 0.5 * eq) / (len(x) * len(y))

def pair(x, y, alt="greater", primary="mwu"):
    """Devuelve primaria y sensibilidad segun la regla, sin elegir por resultado."""
    w = float(wilcoxon(x, y, alternative=alt).pvalue)
    m = float(mannwhitneyu(x, y, alternative=alt).pvalue)
    return {"p_primary": m if primary == "mwu" else w,
            "primary_test": "Mann-Whitney U (unpaired)" if primary == "mwu" else "Wilcoxon signed-rank (paired)",
            "p_sensitivity": w if primary == "mwu" else m,
            "sensitivity_test": "Wilcoxon signed-rank (seed-label)" if primary == "mwu" else "Mann-Whitney U (unpaired)",
            "alternative": alt, "a12": a12(x, y)}

def sign_flip(x, y, n=20000, seed=12345):
    """Confirmacion del contraste bloqueado del 2x2: permuta el SIGNO de cada
    diferencia dentro de su bloque (semilla), que es el intercambio valido."""
    d = np.asarray(x) - np.asarray(y); obs = d.mean()
    rng = np.random.default_rng(seed)
    S = rng.choice([-1.0, 1.0], size=(n, len(d)))
    return float(((S * d).mean(axis=1) >= obs).mean())

def main():
    lad = J("ladder_v5.json")["methods"]
    rr = lad["random_restart"]["hv_per_seed"]
    comp = J("competent_arch100.json")["hv_per_seed_arch100"]
    out = {"rules": __doc__.split("REGLAS")[1].split("NO ejecuta")[0].strip(), "visa": {}}

    V = out["visa"]
    V["competent_vs_random"]   = pair(comp, rr, "greater")
    V["mohho_vs_nsga2"]        = pair(lad["naive_mohho"]["hv_per_seed"], lad["nsga2_realcoded"]["hv_per_seed"], "two-sided")
    V["discrete_vs_mohho"]     = pair(lad["discrete_mohho"]["hv_per_seed"], lad["naive_mohho"]["hv_per_seed"], "greater")
    V["perm_nsga2_vs_random"]  = pair(lad["perm_nsga2"]["hv_per_seed"], rr, "greater")
    V["perm_moead_vs_random"]  = pair(lad["perm_moead"]["hv_per_seed"], rr, "greater")
    V["perm_spea2_vs_random"]  = pair(J("perm_spea2.json")["per_run_hv"], rr, "greater")
    V["nsga2_vs_random"]       = pair(lad["nsga2_realcoded"]["hv_per_seed"], rr, "less")
    V["mohho_vs_random"]       = pair(lad["naive_mohho"]["hv_per_seed"], rr, "less")
    V["rk_nsga2_vs_random"]    = pair(J("brkga_ladder.json")["hv_per_seed"], rr, "two-sided")
    V["spea2_vs_perm_nsga2"]   = pair(J("perm_spea2.json")["per_run_hv"], lad["perm_nsga2"]["hv_per_seed"], "two-sided")
    for k, f in (("grasp_vs_random", "grasp_control.json"), ("pls_vs_random", "pls_control.json")):
        try: V[k] = pair(J(f)["hv_per_seed"], rr, "less")
        except Exception as e: V[k] = {"error": str(e)}
    V["nsga2_l9_vs_random"] = pair(J("nsga2_l9.json")["visa"]["confirmation_hv_per_seed"], rr, "two-sided")

    # --- 2x2: bloqueo REAL (inicializacion compartida) ---
    f2 = J("factorial_2x2_paired.json")
    cells = f2["cells"]; rr2 = f2["random_hv_per_seed"]
    out["factorial_2x2"] = {"note": "cells share the initial population per seed by construction; blocking is real"}
    for name, c in cells.items():
        alt = "greater" if c["wilcoxon_alt"] == "greater" else "two-sided"
        d = pair(c["hv_per_seed"], rr2, alt, primary="wilcoxon")
        d["sign_flip_p"] = sign_flip(c["hv_per_seed"], rr2)
        out["factorial_2x2"][name] = d
    out["factorial_2x2"]["interaction_permutation_p"] = f2["interaction"]["p_permutation"]

    # --- mo-SCP: preregistrado, Wilcoxon pareado PRIMARIO ---
    scp = J("prospective_scp.json"); hs = scp["hv_per_seed"]
    out["mo_scp"] = {"note": "preregistered paired Wilcoxon retained as primary; MWU as sensitivity"}
    for k, a in (("perm_nsga2_vs_random", "perm_nsga2"), ("competent_vs_random", "competent_mohho")):
        out["mo_scp"][k] = pair(hs[a], hs["random_restart"], "greater", primary="wilcoxon")

    # --- Holm sobre la familia enumerada de 12, con el p PRIMARIO ---
    fam = [("perm_nsga2_vs_random", V["perm_nsga2_vs_random"]["p_primary"]),
           ("nsga2_vs_random", V["nsga2_vs_random"]["p_primary"]),
           ("perm_spea2_vs_random", V["perm_spea2_vs_random"]["p_primary"]),
           ("mohho_vs_random", V["mohho_vs_random"]["p_primary"]),
           ("perm_moead_vs_random", V["perm_moead_vs_random"]["p_primary"]),
           ("competent_vs_random", V["competent_vs_random"]["p_primary"]),
           ("mohho_vs_nsga2", V["mohho_vs_nsga2"]["p_primary"]),
           ("discrete_vs_mohho", V["discrete_vs_mohho"]["p_primary"]),
           ("cell2x2_vs_random", out["factorial_2x2"]["order_nds"]["p_primary"]),
           ("interaction_2x2", out["factorial_2x2"]["interaction_permutation_p"]),
           ("scp_perm_vs_random", out["mo_scp"]["perm_nsga2_vs_random"]["p_primary"]),
           ("scp_competent_vs_random", out["mo_scp"]["competent_vs_random"]["p_primary"])]
    fam.sort(key=lambda r: r[1]); m = len(fam); res = {}; all_ok = True
    for i, (name, p) in enumerate(fam):
        thr = 0.05 / (m - i); ok = p <= thr; all_ok &= ok
        res[name] = {"p_primary": p, "holm_threshold": thr, "survives": bool(ok)}
    out["holm_family"] = {"m": m, "results": res, "all_survive": bool(all_ok),
                          "recomputed": "every p is the PRIMARY test for its claim; no hardcoded literals"}
    (R / "cr_stats_v2.json").write_text(json.dumps(out, indent=1))

    print(f"{'contraste':<26}{'primaria':>12}{'prueba':>12}{'sensib.':>12}{'A12':>7}")
    for k, v in V.items():
        if "error" in v: print(f"  {k:<24} ERROR {v['error'][:40]}"); continue
        print(f"{k:<26}{v['p_primary']:>12.2e}{'MWU':>12}{v['p_sensitivity']:>12.2e}{v['a12']:>7.3f}")
    print(f"\n2x2 (bloqueo real, Wilcoxon primario):")
    for k in ("order_nds","order_gated","near_nds","near_gated"):
        v=out["factorial_2x2"][k]
        print(f"  {k:<14} wilcoxon={v['p_primary']:.2e}  sign-flip={v['sign_flip_p']:.2e}  mwu={v['p_sensitivity']:.2e}")
    print(f"\nmo-SCP (preregistrado, Wilcoxon primario):")
    for k in ("perm_nsga2_vs_random","competent_vs_random"):
        v=out["mo_scp"][k]; print(f"  {k:<24} wilcoxon={v['p_primary']:.2e}  mwu={v['p_sensitivity']:.2e}  A12={v['a12']:.3f}")
    print(f"\nHolm m={m}: {'TODAS sobreviven' if all_ok else 'ALGUNA NO sobrevive'}")
    for name,(p) in sorted(res.items(), key=lambda r:r[1]['p_primary']):
        print(f"  {'OK ' if p['survives'] else 'NO '} {name:<26} p={p['p_primary']:.2e}  umbral={p['holm_threshold']:.2e}")
    return 0
main()
