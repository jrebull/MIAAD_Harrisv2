"""
SUPERPROMPT v2 - Orquestador del diagnostico de colapso (nombre de entregable del
prompt). El programa se dividio en modulos granulares; este wrapper los corre en el
orden del gate-sequence (A -> B -> Q1 -> C -> D -> reporte) y deja todos los JSON en
app/data/results/. Re-ejecuta TODO de cero (cuidado: el ladder de C tarda ~40 min).

Ejecutar desde backend/:  python3 -m collapse.experiments.exp_collapse_diagnosis
"""
import runpy
import sys

STEPS = [
    ("Exp A  - optimizer sanity gate", "collapse.experiments.exp_optimizer_sanity"),
    ("Exp A  - ZDT2 diagnosis",        "collapse.experiments.expA_zdt2_diagnosis"),
    ("Regen  - combined fronts",       "collapse.experiments.dump_fronts"),
    ("Exp B  - structural collapse",   "collapse.experiments.exp_structural_collapse"),
    ("Q1     - exact MILP front f1-f3", "collapse.experiments.exact_front_f1f3_milp"),
    ("Exp C  - decoder ladder",        "collapse.experiments.exp_decoder_ladder"),
    ("Exp C  - patch verdict",         "collapse.experiments.patch_expC_verdict"),
    ("Exp D  - metric robustness",     "collapse.experiments.exp_metric_robustness"),
    ("Report - build REPORTE",         "collapse.experiments.build_report"),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for title, mod in STEPS:
        if only and only not in mod:
            continue
        print(f"\n{'='*70}\n{title}  [{mod}]\n{'='*70}")
        runpy.run_module(mod, run_name="__main__")


if __name__ == "__main__":
    main()
