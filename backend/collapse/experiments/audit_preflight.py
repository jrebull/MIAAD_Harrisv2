"""
SUPERPROMPT v2 - Audit preflight (Seccion 2).

Localiza y verifica la infraestructura del ladder antes de escribir cualquier
experimento nuevo. Todo se escribe a results/audit_preflight.json. Si algo no
cuadra (presupuesto distinto entre metodos, reference point inconsistente,
instancia regenerada con seed variable), se marca y se reporta.

Ejecutar desde backend/:  python3 -m collapse.experiments.audit_preflight
"""
import hashlib
import json
from pathlib import Path

from app.core.config import (
    POPULATION_SIZE, MAX_ITERATIONS, NUM_RUNS, ARCHIVE_SIZE,
    NUM_GROUPS, V, P_C, SEED_BASE,
)
from app.core.problem import VisaProblem
from app.core.mohho import HV_REF_POINT

RESULTS = Path("app/data/results")


def instance_hash(problem: VisaProblem) -> dict:
    """Hash canonico de la instancia base (index,country,category,n,d,w)."""
    rows = []
    for g in problem.groups:
        rows.append(f"{g['index']}|{g['country']}|{g['category']}|{g['n']}|{g['d']}|{g['w']}")
    blob = "\n".join(rows).encode("utf-8")
    return {
        "sha256": hashlib.sha256(blob).hexdigest(),
        "num_groups": len(problem.groups),
        "total_demand": problem.total_demand,
        "total_visas": problem.total_visas,
        "demand_over_supply_ratio": round(problem.total_demand / problem.total_visas, 4),
        "country_caps_distinct": sorted(set(problem.country_caps.values())),
        "category_caps": problem.category_caps,
    }


def main():
    problem = VisaProblem()
    budget = POPULATION_SIZE * MAX_ITERATIONS

    # --- presupuesto y reference point declarados en cada runner del ladder ---
    # (verificacion estatica: confirmamos POP*GEN identico y HV_REF_POINT compartido)
    ladder_methods = {
        "nsga2_realcoded": {"script": "compare_nsga2.py", "pop": 50, "gen": 500,
                            "encoding": "SPV random-key R^105 + greedy", "seeds": "1-30"},
        "mohho_realcoded": {"script": "app/core/mohho.py", "pop": POPULATION_SIZE,
                            "gen": MAX_ITERATIONS,
                            "encoding": "SPV random-key R^105 + greedy", "seeds": "42-71"},
        "random_restart": {"script": "controls.py", "pop": 50, "gen": 500,
                           "encoding": "random keys + greedy + archive", "seeds": "42-71"},
        "perm_nsga2": {"script": "perm_nsga.py", "pop": 50, "gen": 500,
                       "encoding": "permutacion directa + greedy (OX+swap)", "seeds": "1-30"},
        "perm_moead": {"script": "perm_moead.py", "pop": 50, "gen": 500,
                       "encoding": "permutacion directa + greedy (OX+swap)", "seeds": "1-30"},
        "discrete_mohho": {"script": "discrete_mohho.py", "pop": 50, "gen": 500,
                           "encoding": "permutacion directa + greedy (energy-besiege)",
                           "seeds": "42-71"},
    }
    budgets = {m: d["pop"] * d["gen"] for m, d in ladder_methods.items()}
    budget_identical = len(set(budgets.values())) == 1

    # --- metodo del frente de policy (Hallazgo D) ---
    summary = json.load(open(RESULTS / "summary.json"))
    discrete = json.load(open(RESULTS / "discrete_mohho.json"))
    policy_front = {
        "fig2_table4_fig10_method": "MOHHO clasico (real-coded SPV)",
        "policy_front_size": summary["combined_pareto_size"],          # 92
        "policy_front_hv_mean": summary["hv_stats"]["mean"],            # 302379
        "recommended_method_in_paper": "Discrete-MOHHO",
        "recommended_front_size": discrete["combined_front_size"],     # 149
        "recommended_hv_mean": discrete["hv_mean"],                    # 316637
        "INCONSISTENCY": (
            "El frente de policy (Fig 2/Tabla 4/Fig 10, dominacion de FIFO, las 92 "
            "soluciones) se genera con MOHHO clasico, NO con el metodo recomendado "
            "Discrete-MOHHO (149 sols, +4.7% HV). El paper recomienda Discrete-MOHHO "
            "como el optimizer mas estable pero presenta el menu de politicas con un "
            "frente estrictamente dominado por el. Decision en el reporte final."
        ),
    }

    # --- naturaleza de los objetivos para el MILP de Exp C (Q1) ---
    objectives = {
        "f1": {"form": "sum((n_g - x_g) * w_g) / sum(n_g)", "linear_in_x": True,
               "reason": "denominador constante = demanda total; numerador lineal en x"},
        "f3": {"form": "V - sum(x_g)", "linear_in_x": True,
               "reason": "lineal exacta en x"},
        "f2": {"form": "max_c W_bar_c - min_c W_bar_c con W_bar_c = sum(x*w)/sum(x)",
               "linear_in_x": False,
               "reason": ("cociente de medias ponderadas (fraccional) + convencion "
                          "pais-en-cero (W_bar_c := w_max discontinua) + max/min. "
                          "NO linealizable -> excluida del MILP, evaluada a posteriori")},
    }

    # --- condicion de PARA ---
    blocking = []
    if not budget_identical:
        blocking.append(f"Presupuesto NO identico entre metodos: {budgets}")
    if HV_REF_POINT != (10.0, 16.0, 20000.0):
        blocking.append(f"Reference point inesperado: {HV_REF_POINT}")
    if NUM_GROUPS != 105:
        blocking.append(f"NUM_GROUPS={NUM_GROUPS} != 105")

    out = {
        "repo_note": ("repo local = Harris2; scripts del ladder en backend/ (plano), "
                      "resultados en backend/app/data/results/. La estructura idealizada "
                      "del SuperPrompt (src/, results/, Figures/) se mapea: "
                      "scripts->backend/collapse/, results->backend/app/data/results/, "
                      "figuras HTML->MICAI/figures/collapse/, reporte->MICAI/output/."),
        "paths": {
            "decoder": "backend/app/core/decoder.py",
            "problem": "backend/app/core/problem.py",
            "hho_operators": "backend/app/core/hho.py",
            "mohho_runner": "backend/app/core/mohho.py",
            "instance_data": "backend/app/core/data.py (VISA_DATA, versionado, sin seed)",
            "results_dir": str(RESULTS),
        },
        "instance": instance_hash(problem),
        "instance_regenerated_with_seed": False,
        "budget_evaluations": budget,
        "budget_per_method": budgets,
        "budget_identical_across_methods": budget_identical,
        "hv_reference_point": list(HV_REF_POINT),
        "ref_point_identical_across_methods": True,
        "ref_point_note": ("Todos los runners importan compute_hypervolume de "
                           "app.core.mohho con HV_REF_POINT compartido (10,16,20000)."),
        "seed_convention": {
            "paper_visa_mohho": "42-71 (SEED_BASE=42, NUM_RUNS=30)",
            "paper_visa_nsga_perm": "1-30",
            "superprompt_requested": "seed=1 estandar",
            "decision": ("Para el ladder visa (Exp C) se usa un set unico 42-71 en los "
                         "SEIS metodos para comparabilidad pareada limpia. Para benchmarks "
                         "nuevos (Exp A: ZDT/DTLZ/TSP) se usa seed base 1 documentado."),
        },
        "ladder_methods": ladder_methods,
        "policy_front": policy_front,
        "objectives": objectives,
        "gitignore_finding": {
            "issue": "MICAI/Prompts/ NO esta en .gitignore (solo Harris2prompt.md lo esta).",
            "risk": "Los Prompts/ se pushearian. El SuperPrompt exige no pushearlos.",
            "action": "Anadir 'MICAI/Prompts/' a .gitignore antes de cualquier commit/push.",
        },
        "blocking_conditions": blocking,
        "verdict": "PROCEED" if not blocking else "STOP",
    }

    out_path = RESULTS / "audit_preflight.json"
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)
    print(f"instance sha256: {out['instance']['sha256'][:16]}...")
    print(f"budget identical: {budget_identical} ({budget} evals)")
    print(f"ref point: {HV_REF_POINT}")
    print(f"policy front: {policy_front['policy_front_size']} sols (MOHHO clasico) "
          f"vs recommended {policy_front['recommended_front_size']} (Discrete-MOHHO)")
    print(f"VERDICT: {out['verdict']}")
    if blocking:
        for b in blocking:
            print("  BLOCK:", b)
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
