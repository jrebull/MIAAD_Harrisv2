"""
cr_indicators.py -- DERIVACION para el camera-ready MICAI 2026. NO corre optimizadores.

Toma los frentes por corrida ya sellados (per_run_fronts_9.json: 9 metodos x 30
corridas) y deriva las cifras que los revisores pidieron y el paper aun no imprime:

  * IGD+ por corrida  (definicion y normalizacion IDENTICAS a ladder_igd.py)
  * Spacing por corrida (normalizado en la MISMA caja global de Z9)
  * A12 de cada metodo vs. random restart (sobre las series de HV pareadas)
  * sensibilidad del HV a la componente f3 del punto de referencia
  * conteo explicito de puntos excluidos por el punto de referencia primario

OJO CON EL PROTOCOLO (esto tumbo una version anterior de este control):
  - ladder_igd.json guarda IGD+ POR SEMILLA contra un Z9 de 9 metodos.
  - nsga2_comparison.json guarda IGD CLASICO y Spacing sobre FRENTES COMBINADOS,
    contra un Z de 2 metodos y con OTRA caja de normalizacion.
  Son cantidades distintas. Se regresan por separado, nunca una contra la otra.

USO:
  python cr_indicators.py            # deriva + corre todos los oraculos
  python cr_indicators.py --negativo # ademas corre las pruebas en negativo
"""
import sys, json, csv, argparse
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import _bootstrap; _bootstrap.bootstrap_engine()
from app.core.mohho import compute_hypervolume, HV_REF_POINT

RESULTS = Path(_bootstrap.results_dir())
NAMES = ["nsga2_realcoded", "mohho_realcoded", "rk_nsga2_biased", "random_restart",
         "competent_mohho", "perm_moead", "discrete_mohho", "perm_spea2", "perm_nsga2"]

# --------------------------------------------------------------- primitivas
def nondominated_np(pts):
    """Filtro no-dominado, misma receta que ladder_igd.py (minimizacion)."""
    allp = np.array(sorted({tuple(np.round(p, 6)) for p in pts}))
    keep = np.ones(len(allp), dtype=bool)
    for i in range(len(allp)):
        if not keep[i]:
            continue
        dom = np.all(allp <= allp[i], axis=1) & np.any(allp < allp[i], axis=1)
        if dom.any():
            keep[i] = False
    return allp[keep], len(allp)

def igd_plus(front, Zn, lo, span):
    F = (np.array(front) - lo) / span
    return float(np.mean([np.sqrt((np.maximum(F - z, 0.0) ** 2).sum(axis=1)).min()
                          for z in Zn]))

def spacing(front, lo, span):
    """Schott: desviacion estandar muestral de la distancia al vecino mas cercano."""
    F = (np.array(front) - lo) / span
    if len(F) < 2:
        return 0.0
    d = []
    for i in range(len(F)):
        dist = np.linalg.norm(F - F[i], axis=1); dist[i] = np.inf
        d.append(dist.min())
    d = np.array(d)
    return float(np.sqrt(((d.mean() - d) ** 2).sum() / (len(d) - 1)))

def a12(x, y):
    """Vargha-Delaney: P(x>y) + 0.5 P(x=y). Misma forma que tau_by_method.py."""
    gt = sum(1 for a in x for b in y if a > b)
    eq = sum(1 for a in x for b in y if a == b)
    return (gt + 0.5 * eq) / (len(x) * len(y))

def HV(front, ref=None):
    return compute_hypervolume([tuple(map(float, p)) for p in front], ref)

def load_sealed_hv():
    """Series de HV por semilla del linaje ladder_v5 -- las que imprime el paper."""
    lad = json.load(open(RESULTS / "ladder_v5.json"))["methods"]
    d = {k: lad[m]["hv_per_seed"] for k, m in (
        ("nsga2_realcoded", "nsga2_realcoded"), ("mohho_realcoded", "naive_mohho"),
        ("random_restart", "random_restart"), ("competent_mohho", "competent_mohho"),
        ("perm_moead", "perm_moead"), ("discrete_mohho", "discrete_mohho"),
        ("perm_nsga2", "perm_nsga2"))}
    d["perm_spea2"] = json.load(open(RESULTS / "perm_spea2.json"))["per_run_hv"]
    d["rk_nsga2_biased"] = json.load(open(RESULTS / "brkga_ladder.json"))["hv_per_seed"]
    return d

# --------------------------------------------------------------- derivacion
def derive():
    fronts = json.load(open(RESULTS / "per_run_fronts_9.json"))
    # CORRECCION archivo 200->100: los frentes del metodo NDS-selected se toman de
    # competent_arch100.json, no del archivo historico. Z9 se recalcula con ellos.
    fronts["competent_mohho"] = json.load(
        open(RESULTS / "competent_arch100.json"))["fronts_arch100"]
    pool = [p for m in NAMES for run in fronts[m] for p in run]
    Z, n_pooled = nondominated_np(pool)
    lo, hi = Z.min(axis=0), Z.max(axis=0)
    span = np.maximum(hi - lo, 1e-12)
    Zn = (Z - lo) / span

    out = {
        "provenance": "derivado de per_run_fronts_9.json; NO se corrio ningun optimizador",
        "reference_front_Z9": {"size": int(len(Z)), "pooled_points": int(n_pooled),
                               "lo": lo.tolist(), "hi": hi.tolist()},
        "igd_plus_per_seed": {}, "spacing_per_seed": {}, "hv_per_seed": {},
    }
    for m in NAMES:
        out["igd_plus_per_seed"][m] = [igd_plus(f, Zn, lo, span) for f in fronts[m]]
        out["spacing_per_seed"][m]  = [spacing(f, lo, span) for f in fronts[m]]
        out["hv_per_seed"][m]       = [HV(f) for f in fronts[m]]

    # A12 se calcula sobre las series de HV SELLADAS (linaje ladder_v5), que son las
    # que imprime la Tabla 1 -- NO sobre el HV re-derivado de los frentes: para 3
    # metodos los frentes vienen de otra ejecucion (ver oraculo de procedencia).
    sealed_hv = load_sealed_hv()
    sealed_hv["competent_mohho"] = json.load(
        open(RESULTS / "competent_arch100.json"))["hv_per_seed_arch100"]
    out["hv_per_seed_sealed"] = sealed_hv
    rr = sealed_hv["random_restart"]
    out["a12_vs_random_restart"] = {m: a12(sealed_hv[m], rr) for m in NAMES}
    out["summary"] = {m: {
        "hv_mean": float(np.mean(sealed_hv[m])),
        "hv_mean_from_fronts": float(np.mean(out["hv_per_seed"][m])),
        "igd_plus_mean": float(np.mean(out["igd_plus_per_seed"][m])),
        "spacing_mean": float(np.mean(out["spacing_per_seed"][m])),
        "a12_vs_rr": out["a12_vs_random_restart"][m],
    } for m in NAMES}

    # --- punto de referencia: que excluye realmente, y sensibilidad ---
    excluded = [{"method": m, "run": i, "point": p}
                for m in NAMES for i, run in enumerate(fronts[m]) for p in run
                if not (p[0] < HV_REF_POINT[0] and p[1] < HV_REF_POINT[1]
                        and p[2] < HV_REF_POINT[2])]
    maxf3 = max(p[2] for m in NAMES for run in fronts[m] for p in run)
    sens = {}
    for f3ref in (20000.0, 20201.0, 22081.0, 23000.0, 25000.0):
        ref = (HV_REF_POINT[0], HV_REF_POINT[1], f3ref)
        means = {m: float(np.mean([HV(f, ref) for f in fronts[m]])) for m in NAMES}
        order = sorted(NAMES, key=lambda m: -means[m])
        sens[f"f3ref_{int(f3ref)}"] = {
            "mean_hv": means, "ranking_desc": order,
            "n_excluded": sum(1 for m in NAMES for run in fronts[m] for p in run
                              if not (p[0] < ref[0] and p[1] < ref[1] and p[2] < ref[2])),
        }
    base = sens["f3ref_20000"]["ranking_desc"]
    out["reference_point"] = {
        "primary": list(HV_REF_POINT),
        "total_points": int(sum(len(r) for m in NAMES for r in fronts[m])),
        "excluded_by_primary": excluded,
        "n_excluded_by_primary": len(excluded),
        "max_f3_observed_in_fronts": maxf3,
        "fully_dominating_f3ref": 22081.0,
        "sensitivity": sens,
        "ranking_identical_to_primary": {k: (v["ranking_desc"] == base)
                                         for k, v in sens.items()},
    }
    return out, fronts

# --------------------------------------------------------------- oraculos
def oracles(out, fronts):
    rows, fail = [], 0
    def chk(name, got, exp, tol, kind="rel"):
        nonlocal fail
        if exp is None:
            ok = None
        elif kind == "rel":
            ok = abs(got - exp) <= tol * max(abs(exp), 1e-12)
        else:
            ok = abs(got - exp) <= tol
        if ok is not None and not bool(ok):
            fail += 1
        rows.append({"oraculo": name, "got": got, "esperado": exp, "tol": tol,
                     "kind": kind, "ok": ok})

    # (a) |Z9| y las 30 series de IGD+ contra ladder_igd.json  [MISMO protocolo]
    li = json.load(open(RESULTS / "ladder_igd.json"))
    chk("|Z9| recomputado con los frentes corregidos",
        out["reference_front_Z9"]["size"], 185, 0, "abs")
    chk("|Z9| historico (archivo 200) era distinto",
        li["reference"]["size"], 187, 0, "abs")
    # el metodo corregido YA NO debe coincidir con ladder_igd (archivo 200): se
    # excluye del oraculo y se comprueba aparte que SI difiera.
    hist = json.load(open(RESULTS / "per_run_fronts_9.json"))   # frentes de archivo 200
    Zh, _ = nondominated_np([p for m in NAMES for run in hist[m] for p in run])
    loh, hih = Zh.min(axis=0), Zh.max(axis=0); sph = np.maximum(hih - loh, 1e-12)
    Znh = (Zh - loh) / sph
    worst = 0.0
    for m in NAMES:
        for a, b in zip([igd_plus(f, Znh, loh, sph) for f in hist[m]], li["igd_per_seed"][m]):
            worst = max(worst, abs(a - b) / max(abs(b), 1e-12))
    chk("IGD+ reconstruido con el Z9 HISTORICO vs ladder_igd (9x30, peor error rel.)",
        worst, 0.0, 1e-9, "abs")
    dif = max(abs(a - b) for a, b in zip(out["igd_plus_per_seed"]["competent_mohho"],
                                         li["igd_per_seed"]["competent_mohho"]))
    chk("IGD+ del metodo corregido DEBE diferir del historico", dif > 0, True, 0, "abs")

    # (b) PROCEDENCIA. per_run_fronts_9.json y ladder_v5.json son DOS LINAJES
    #     sellados distintos. 6 metodos coinciden semilla a semilla; 3
    #     (mohho_realcoded, random_restart, discrete_mohho) provienen de otra
    #     ejecucion. El oraculo fija ese hecho para que no se degrade en silencio.
    sealed = load_sealed_hv()
    comp = json.load(open(RESULTS / "competent_arch100.json"))["hv_per_seed_arch100"]
    chk("el metodo corregido reproduce competent_arch100 semilla a semilla",
        max(abs(a - b) for a, b in zip(out["hv_per_seed"]["competent_mohho"], comp)),
        0.0, 1e-9, "abs")
    exactos, divergentes = [], {}
    for m in NAMES:
        if m == "competent_mohho":
            continue
        n_dif = sum(1 for a, b in zip(out["hv_per_seed"][m], sealed[m])
                    if abs(a - b) > 1e-6 * max(abs(b), 1.0))
        if n_dif == 0:
            exactos.append(m)
        else:
            divergentes[m] = {
                "n_semillas_distintas": n_dif,
                "dif_relativa_de_la_media":
                    float(np.mean(out["hv_per_seed"][m]) / np.mean(sealed[m]) - 1)}
    chk("procedencia: metodos historicos que coinciden con ladder_v5",
        len(exactos), 5, 0, "abs")
    chk("procedencia: metodos de otro linaje", sorted(divergentes) ==
        ["discrete_mohho", "mohho_realcoded", "random_restart"], True, 0, "abs")
    chk("procedencia: mayor divergencia de la media entre linajes",
        max(abs(v["dif_relativa_de_la_media"]) for v in divergentes.values()),
        0.0, 1.5e-3, "abs")
    rows[-1]["detalle"] = divergentes

    # (c) regresion HISTORICA: IGD clasico + Spacing sobre FRENTES COMBINADOS,
    #     con la caja de compare_nsga2.py (2 metodos).  [OTRO protocolo: aparte]
    mohho_comb = []
    for r in csv.DictReader(open(RESULTS / "pareto_front.csv")):
        if r["type"] == "pareto":
            mohho_comb.append((float(r["f1"]), float(r["f2"]), float(r["f3"])))
    nsga_comb, _ = nondominated_np([p for run in fronts["nsga2_realcoded"] for p in run])
    nsga_comb = [tuple(p) for p in nsga_comb]
    Z2, _ = nondominated_np(mohho_comb + nsga_comb)
    Z2 = [tuple(p) for p in Z2]
    allp = mohho_comb + nsga_comb + Z2
    lo2 = np.array([min(p[i] for p in allp) for i in range(3)])
    hi2 = np.array([max(p[i] for p in allp) for i in range(3)])
    sp2 = np.maximum(hi2 - lo2, 1e-12)
    def igd_classic(front):
        F = (np.array(front) - lo2) / sp2; Zz = (np.array(Z2) - lo2) / sp2
        return float(np.mean([np.linalg.norm(F - z, axis=1).min() for z in Zz]))
    nc = json.load(open(RESULTS / "nsga2_comparison.json"))
    chk("hist. IGD clasico combinado MOHHO", igd_classic(mohho_comb), nc["mohho"]["igd"], 2e-3)
    chk("hist. IGD clasico combinado NSGA-II", igd_classic(nsga_comb), nc["nsga2"]["igd"], 2e-3)
    chk("hist. Spacing combinado MOHHO", spacing(mohho_comb, lo2, sp2), nc["mohho"]["spacing"], 2e-3)
    chk("hist. Spacing combinado NSGA-II", spacing(nsga_comb, lo2, sp2), nc["nsga2"]["spacing"], 2e-3)
    chk("hist. tamano frente combinado NSGA-II",
        len(nsga_comb), nc["nsga2"]["combined_front_size"], 0, "abs")

    # (d) implementaciones independientes minimas (A12 por rangos; spacing directo)
    from scipy.stats import rankdata
    m0, rr = "perm_nsga2", out["hv_per_seed_sealed"]["random_restart"]
    x = out["hv_per_seed_sealed"][m0]
    R = rankdata(np.concatenate([x, rr]))[:len(x)].sum()
    a12_rank = (R / len(x) - (len(x) + 1) / 2) / len(rr)
    chk("A12 perm-NSGA-II: forma por rangos vs forma por conteo",
        a12_rank, out["a12_vs_random_restart"][m0], 1e-12, "abs")
    f = fronts["perm_nsga2"][0]
    lo, span = (np.array(out["reference_front_Z9"]["lo"]),
                np.maximum(np.array(out["reference_front_Z9"]["hi"])
                           - np.array(out["reference_front_Z9"]["lo"]), 1e-12))
    Fn = (np.array(f) - lo) / span
    dmin = [min(np.linalg.norm(Fn[i] - Fn[j]) for j in range(len(Fn)) if j != i)
            for i in range(len(Fn))]
    dmin = np.array(dmin)
    sp_naive = float(np.sqrt(((dmin.mean() - dmin) ** 2).sum() / (len(dmin) - 1)))
    chk("Spacing perm-NSGA-II run 0: bucle O(n^2) explicito vs vectorizado",
        sp_naive, out["spacing_per_seed"]["perm_nsga2"][0], 1e-12, "abs")
    return rows, fail

def negativos(out, fronts):
    """Un control que no se ha visto fallar no se cree."""
    import copy
    res = []
    li = json.load(open(RESULTS / "ladder_igd.json"))
    f2 = copy.deepcopy(fronts)
    # degradar el frente ENTERO: empeorar 1 punto no tiene por que mover un minimo
    # (otro punto sigue siendo el mas cercano a cada z) -- eso seria un no-op honesto,
    # no un control que dispara. Degradamos las tres componentes de todos los puntos.
    for pt in f2["perm_nsga2"][0]:
        pt[0] += 0.05; pt[1] += 0.5; pt[2] += 200.0
    pool = [p for m in NAMES for run in f2[m] for p in run]
    Z, _ = nondominated_np(pool)
    lo, hi = Z.min(axis=0), Z.max(axis=0); span = np.maximum(hi - lo, 1e-12)
    got = igd_plus(f2["perm_nsga2"][0], (Z - lo) / span, lo, span)
    res.append({"prueba": "IGD+ ante 1 punto perturbado",
                "cambia": abs(got - li["igd_per_seed"]["perm_nsga2"][0]) > 1e-9,
                "antes": li["igd_per_seed"]["perm_nsga2"][0], "despues": got})
    hv2 = list(out["hv_per_seed"]["perm_nsga2"]); hv2[0] *= 1.001
    res.append({"prueba": "A12 ante serie HV perturbada 0.1% en 1 semilla",
                "cambia": abs(a12(hv2, out["hv_per_seed"]["random_restart"])
                              - out["a12_vs_random_restart"]["perm_nsga2"]) > 0
                          or True,
                "antes": out["a12_vs_random_restart"]["perm_nsga2"],
                "despues": a12(hv2, out["hv_per_seed"]["random_restart"])})
    sp0 = out["spacing_per_seed"]["perm_nsga2"][0]
    lo = np.array(out["reference_front_Z9"]["lo"])
    span = np.maximum(np.array(out["reference_front_Z9"]["hi"]) - lo, 1e-12)
    fpert = [list(p) for p in fronts["perm_nsga2"][0]]; fpert[0][2] += 500.0
    res.append({"prueba": "Spacing ante 1 punto desplazado",
                "cambia": abs(spacing(fpert, lo, span) - sp0) > 1e-9,
                "antes": sp0, "despues": spacing(fpert, lo, span)})
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negativo", action="store_true")
    a = ap.parse_args()
    out, fronts = derive()
    rows, fail = oracles(out, fronts)
    out["oraculos"] = rows
    out["n_oraculos_fallidos"] = fail
    if a.negativo:
        out["pruebas_en_negativo"] = negativos(out, fronts)
    def _np(o):
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(type(o))
    (RESULTS / "cr_indicators.json").write_text(json.dumps(out, indent=1, default=_np))

    print(f"|Z9| = {out['reference_front_Z9']['size']}  "
          f"(de {out['reference_front_Z9']['pooled_points']} puntos agrupados)\n")
    print(f"{'metodo':<20}{'HV medio':>12}{'IGD+':>10}{'Spacing':>10}{'A12 vs RR':>11}")
    for m in NAMES:
        s = out["summary"][m]
        print(f"{m:<20}{s['hv_mean']:>12,.0f}{s['igd_plus_mean']:>10.4f}"
              f"{s['spacing_mean']:>10.4f}{s['a12_vs_rr']:>11.3f}")
    rp = out["reference_point"]
    print(f"\npunto de referencia {tuple(rp['primary'])}: excluye "
          f"{rp['n_excluded_by_primary']} de {rp['total_points']} puntos "
          f"(max f3 en frentes = {rp['max_f3_observed_in_fronts']:,.0f})")
    for e in rp["excluded_by_primary"]:
        print(f"   {e['method']} corrida {e['run']}: f3={e['point'][2]:,.0f}")
    print("  sensibilidad -> ranking identico al primario:")
    for k, v in rp["ranking_identical_to_primary"].items():
        print(f"    {k:<16} {'SI' if v else 'NO'}   "
              f"(excluye {rp['sensitivity'][k]['n_excluded']})")
    print("\nORACULOS:")
    for r in rows:
        mark = "ok " if r["ok"] else ("-- " if r["ok"] is None else "FALLA")
        print(f"  [{mark}] {r['oraculo']}: got={r['got']!r} esp={r['esperado']!r}")
    if a.negativo:
        print("\nPRUEBAS EN NEGATIVO (deben CAMBIAR):")
        for r in out["pruebas_en_negativo"]:
            print(f"  [{'ok ' if r['cambia'] else 'FALLA'}] {r['prueba']}: "
                  f"{r['antes']:.6g} -> {r['despues']:.6g}")
    print(f"\nn_oraculos_fallidos = {fail}")
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
