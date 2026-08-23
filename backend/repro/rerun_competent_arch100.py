"""Paso 2+3 de la nota de correccion: re-corre SOLO el metodo competente con
capacidad de archivo 100 y comprueba la invariancia de trayectoria contra 200.

Alcance congelado por NOTA_CORRECCION_ARCHIVO.md. Ningun otro metodo se toca.
Escribe results/competent_arch100.json.
"""
import sys, json, time, hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import _bootstrap; _bootstrap.bootstrap_engine()
from app.core.problem import VisaProblem
from app.core import mohho as M
import competent_mohho as C

R = Path(_bootstrap.results_dir())
SEEDS = list(range(1, 31))
p = VisaProblem()
def ev(h): return M.evaluate_hawk(h, p)[1]
def HV(F): return M.compute_hypervolume([tuple(x) for x in F])

def main():
    t0 = time.time()
    out = {"scope": "visa", "arch_cap_old": 200, "arch_cap_new": 100,
           "seeds": SEEDS, "pop": 50, "gen": 500, "pm": 0.15, "use_sbx": True}
    fp200, fp100, hv200, hv100, fronts100 = [], [], [], [], []
    for s in SEEDS:
        a = C.run_competent_mohho(ev, M.NUM_GROUPS, 3, HV, s, 50, 500,
                                  pm=0.15, use_sbx=True, arch_cap=200, fingerprint=True)
        b = C.run_competent_mohho(ev, M.NUM_GROUPS, 3, HV, s, 50, 500,
                                  pm=0.15, use_sbx=True, arch_cap=100, fingerprint=True)
        fp200.append(a["pop_fingerprint"]); fp100.append(b["pop_fingerprint"])
        hv200.append(a["hv"]); hv100.append(b["hv"])
        fronts100.append([list(map(float, x)) for x in b["front"]])
        print(f"  seed {s:2d}: fp {'IGUAL' if a['pop_fingerprint']==b['pop_fingerprint'] else 'DISTINTO'}"
              f"  |F|200={a['archive']:3d} |F|100={b['archive']:3d}"
              f"  HV {a['hv']:,.0f} -> {b['hv']:,.0f}  ({time.time()-t0:.0f}s)", flush=True)
    same = sum(1 for x, y in zip(fp200, fp100) if x == y)
    out["trajectory_invariance"] = {"seeds_identical": same, "n": len(SEEDS),
                                    "fingerprints_200": fp200, "fingerprints_100": fp100}
    out["hv_per_seed_arch200"] = hv200
    out["hv_per_seed_arch100"] = hv100
    out["front_sizes_arch100"] = [len(f) for f in fronts100]
    out["fronts_arch100"] = fronts100
    out["hv_mean_arch200"] = float(np.mean(hv200))
    out["hv_mean_arch100"] = float(np.mean(hv100))
    out["elapsed_s"] = time.time() - t0
    (R / "competent_arch100.json").write_text(json.dumps(out))
    print(f"\nINVARIANCIA DE TRAYECTORIA: {same}/{len(SEEDS)} semillas con huella identica")
    print(f"HV medio  archivo 200: {np.mean(hv200):,.1f}")
    print(f"HV medio  archivo 100: {np.mean(hv100):,.1f}   ({(np.mean(hv100)/np.mean(hv200)-1)*100:+.3f} %)")
    print(f"|F| medio archivo 100: {np.mean([len(f) for f in fronts100]):.2f}")
    if same != len(SEEDS):
        print("\n*** TRAYECTORIAS DISTINTAS -> PARAR E INVESTIGAR ***"); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
