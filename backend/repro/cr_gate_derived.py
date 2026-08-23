"""Gate del derivado. Falla con codigo != 0."""
import sys, json, argparse
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--derived", required=True)
a = ap.parse_args(); d = json.loads(Path(a.derived).read_text()); f = []
o = d["omnibus"]["ladder9"]["primary"]
if not o["test"].startswith("Kruskal-Wallis"): f.append("omnibus primario no es Kruskal-Wallis")
if abs(o["H"] - 149.81) > 0.05: f.append(f"KW H alterado: {o['H']}")
i = d["interaction_2x2"]
if "Wilcoxon" not in i["primary"]["test"]: f.append("interaccion: la primaria no es Wilcoxon bloqueado")
if abs(i["primary"]["p"] - 7.979e-4) > 1e-5: f.append(f"interaccion p alterada: {i['primary']['p']}")
if "retired" not in i: f.append("no se declara que los p invalidos fueron retirados")
for k in ("unpaired_primary", "seed_label_sensitivity"):
    if k not in d["holm"]: f.append(f"falta la familia Holm {k}")
    elif not d["holm"][k]["all_survive"]: f.append(f"Holm {k}: alguna no sobrevive")
OBSOLETE = ("paired_wilcoxon_p_perm_gt_rk", "C1_paired_significant")

def walk_keys(o, path=""):
    """Toda clave del derivado, excluyendo el CONTENIDO textual de las listas
    obsolete_keys_removed (que legitimamente nombra las claves retiradas)."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "obsolete_keys_removed":
                continue                      # su contenido es declarativo, no dato
            yield path + "/" + k
            yield from walk_keys(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_keys(v, f"{path}[{i}]")

for kp in walk_keys(d):
    leaf = kp.rsplit("/", 1)[-1]
    if leaf in OBSOLETE:
        f.append(f"clave obsoleta presente en {kp}")
for blk in ("expC_reanalysis", "factorial_2x2_reanalysis"):
    if blk not in d: f.append(f"falta el bloque {blk}")
rem = d.get("expC_reanalysis", {}).get("obsolete_keys_removed", [])
for bad in OBSOLETE:
    if bad not in rem: f.append(f"no se declara retirada la clave {bad}")
sf = d["interaction_2x2"]["sensitivity"]["blocked_sign_flip"]
for k in ("n_perm", "seed", "exceedances", "correction", "mcse", "ci95"):
    if k not in sf: f.append(f"sign-flip sin {k}")
if sf.get("n_perm", 0) < 1_000_000: f.append(f"sign-flip con solo {sf.get('n_perm')} permutaciones")
vs = d["omnibus"]["structures"].get("visa", {})
if abs(vs.get("H", 0) - 134.28) < 1e-6: f.append("el H de visa sigue copiado de omnibus_stats (134.28)")
if "derived_from" not in vs: f.append("el omnibus de visa no declara derivacion")
z = d["z9_provenance"]
if z["Z9_current"]["size"] == z["Z9_historical"]["size"]: f.append("Z9 actual e historico conflacionados")
p = d["_provenance"]
# El manifiesto no basta con EXISTIR: se recalculan los hashes contra los
# archivos vivos. Un manifiesto que solo se comprueba a si mismo no prueba nada.
import hashlib
sys.path.insert(0, str(Path(__file__).parent)); import _bootstrap
RES = Path(_bootstrap.results_dir())
for fname, want in (p.get("inputs_sha256") or {}).items():
    fp = RES / fname
    if not fp.exists():
        f.append(f"entrada declarada inexistente: {fname}")
    elif hashlib.sha256(fp.read_bytes()).hexdigest() != want:
        f.append(f"entrada MUTADA respecto al manifiesto: {fname}")
scr = Path(__file__).parent / "cr_derive.py"
if p.get("script_sha256") != hashlib.sha256(scr.read_bytes()).hexdigest():
    f.append("el sha256 del derivador no coincide con cr_derive.py en disco")
if p.get("schema_version") != "cr-derived/1.0":
    f.append(f"schema_version inesperado: {p.get('schema_version')}")
for k in ("script", "script_sha256", "schema_version", "inputs_sha256", "config", "no_optimizers_executed"):
    if k not in p: f.append(f"procedencia incompleta: falta {k}")
if not p.get("no_optimizers_executed"): f.append("se declara que se ejecutaron optimizadores")
for x in f: print("  FALLO:", x)
print(f"  n_fallos = {len(f)}")
sys.exit(1 if f else 0)
