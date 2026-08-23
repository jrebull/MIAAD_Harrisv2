"""
verify_paper.py — FIREWALL DE REPRODUCIBILIDAD. Cruza cada numero declarado en el
paper contra results/*.json y FALLA si hay discrepancia > tolerancia.

Operacionaliza el principio "cero hardcode": si un numero del .tex no se puede
trazar a un JSON regenerado, es un FALLO.

USO:
  python verify_paper.py [--tex DIR] [--results DIR]
- CLAIMS: registro semilla con numeros VERIFICADOS contra el codigo (extiendelo
  con el resto de cifras del paper).
- tex_number_inventory(): lista todos los tokens numericos del .tex para cablearlos.

NOTA: los paper_value de abajo provienen del PDF MICAI. Ajusta/expande segun el
.tex real. n_mismatch>0 => hay cifras sin respaldo o stale.
"""
import os, re, json, argparse
from pathlib import Path
import _bootstrap

# ---------- navegacion de JSON: "a.b[0].c" ----------
def jget(obj, path):
    cur = obj
    for tok in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if tok.startswith("[") and tok.endswith("]"):
            cur = cur[int(tok[1:-1])]
        else:
            cur = cur[tok]
    return cur

# ---------- REGISTRO SEMILLA (extender) ----------
# kind: "rel" (tolerancia relativa) | "abs" (absoluta) | "exact"
CLAIMS = [
    # name, paper_value, json_file, json_path, tol, kind
    ("degeneration_ratio", 1.27, "expB_structural_collapse.json",
     "B2_decoder_degeneration.degeneration_ratio", 0.02, "abs"),
    ("distinct_objective_points", 39401, "expB_structural_collapse.json",
     "B2_decoder_degeneration.n_distinct_objective_points", 50, "abs"),
    ("pca_pc1_plus_pc2_mohho", 0.99, "expB_structural_collapse.json",
     "B1_effective_dimensionality.mohho_realcoded.pc1_plus_pc2", 0.01, "abs"),
    ("f1_vs_f2_range_ratio", 39.4, "expB_structural_collapse.json",
     "B2_decoder_degeneration.f1_vs_f2_range_ratio", 0.5, "abs"),
    ("decoder_margin_greedy_pct", 6.93, "expC_decoder_ladder.json",
     "separation_collapse.greedy_perm_minus_rk_pct", 0.1, "abs"),
    ("decoder_margin_C1_pct", 1.45, "expC_decoder_ladder.json",
     "separation_collapse.C1_perm_minus_rk_pct", 0.1, "abs"),
    ("decoder_margin_C2_pct", 4.27, "expC_decoder_ladder.json",
     "separation_collapse.C2_perm_minus_rk_pct", 0.1, "abs"),
    # ---- ladder per-run HV (Tabla 5/7), repo UNIFICADO a seeds 1-30 ----
    # MOHHO y NSGA: nsga2_comparison.json (estudio principal regenerado a 1-30).
    # random/Discrete/perm-*: ladder_v5.json (ya a 1-30).
    ("hv_mohho_mean", 302756, "nsga2_comparison.json", "mohho.hv_mean", 0.005, "rel"),
    ("hv_nsga2_mean", 293367, "nsga2_comparison.json", "nsga2.hv_mean", 0.005, "rel"),
    ("hv_random_restart", 310214, "ladder_v5.json", "methods.random_restart.hv_mean", 0.005, "rel"),
    ("hv_discrete_mohho", 316792, "ladder_v5.json", "methods.discrete_mohho.hv_mean", 0.005, "rel"),
    ("hv_perm_nsga2", 318151, "ladder_v5.json", "methods.perm_nsga2.hv_mean", 0.005, "rel"),
    ("hv_perm_moead", 314846, "ladder_v5.json", "methods.perm_moead.hv_mean", 0.005, "rel"),
    ("combined_hv_discrete", 321408, "ladder_v5.json", "methods.discrete_mohho.combined_front_hv", 0.005, "rel"),
    ("combined_hv_perm_nsga2", 321935, "ladder_v5.json", "methods.perm_nsga2.combined_front_hv", 0.005, "rel"),
    ("combined_size_discrete", 137, "ladder_v5.json", "methods.discrete_mohho.combined_front_size", 0, "exact"),
    ("mohho_igd_1to30", 0.0212, "nsga2_comparison.json", "mohho.igd", 0.002, "abs"),
    ("nsga_igd_1to30", 0.0071, "nsga2_comparison.json", "nsga2.igd", 0.002, "abs"),
    ("mohho_cv_1to30", 2.36, "ladder_v5.json", "methods.naive_mohho.cv_pct", 0.05, "abs"),
    ("discrete_cv_1to30", 0.71, "ladder_v5.json", "methods.discrete_mohho.cv_pct", 0.05, "abs"),
    ("perm_nsga_cv_1to30", 0.58, "ladder_v5.json", "methods.perm_nsga2.cv_pct", 0.05, "abs"),
    ("canonical_levy_fematched_1to30", 309180, "control_canonical_hho.json",
     "fe_matched.hv_mean", 0.01, "rel"),
    # ---- omnibus / mechanism ----
    ("tau_sbx", 0.99, "operator_order.json",
     "operators.SBX crossover (GA).mean_tau", 0.01, "abs"),
    # ---- FIFO baseline + extremes (Tabla 4) ----
    ("fifo_f1", 8.7891, "summary.json", "baseline.f1", 0.001, "abs"),
    ("fifo_f2", 13.0, "summary.json", "baseline.f2", 0.01, "abs"),
    ("fifo_f3", 1940, "summary.json", "baseline.f3", 1, "abs"),
    ("combined_pareto_size", 104, "summary.json", "combined_pareto_size", 0, "exact"),
    ("min_f1_sol_f1", 8.7884, "summary.json", "best_f1.[0]", 0.001, "abs"),
    ("min_f1_sol_f3", 680, "summary.json", "best_f1.[2]", 1, "abs"),
    ("min_f2_sol_f2", 2.0, "summary.json", "best_f2.[1]", 0.01, "abs"),
    # ---- Taguchi ----
    ("taguchi_grand_mean_sn", 109.46, "taguchi.json", "grand_mean_sn", 0.01, "abs"),
    # ---- policy of Fig.10 (f2 recomputed) ----
    ("policy_f2_years", 7.59, "policy_impact.json", "f2", 0.01, "abs"),
    ("equity_wait_std_fifo", 3.14, "equity_audit.json",
     "front_ranges.wait_std.fifo", 0.02, "abs"),
    ("equity_wait_std_front_best", 0.75, "equity_audit.json",
     "front_ranges.wait_std.min", 0.02, "abs"),
    ("equity_gini_fifo", 0.79, "equity_audit.json",
     "front_ranges.wait_gini.fifo", 0.02, "abs"),
    ("equity_gini_front_best", 0.17, "equity_audit.json",
     "front_ranges.wait_gini.min", 0.02, "abs"),
    ("equity_jain_fifo", 0.80, "equity_audit.json",
     "front_ranges.jain_inverse_wait.fifo", 0.02, "abs"),
    ("equity_jain_front_best", 0.94, "equity_audit.json",
     "front_ranges.jain_inverse_wait.max", 0.02, "abs"),
    # ---- Friedman ranks (Tabla 8, visa column) ----
    ("rank_perm_nsga2_visa", 1.60, "omnibus_visa_paired.json", "avg_rank.perm-NSGA-II", 0.01, "abs"),
    ("rank_discrete_visa", 2.23, "omnibus_visa_paired.json", "avg_rank.Discrete-MOHHO", 0.01, "abs"),
    ("rank_perm_moead_visa", 2.53, "omnibus_visa_paired.json", "avg_rank.perm-MOEA/D", 0.01, "abs"),
    ("rank_random_visa", 4.20, "omnibus_visa_paired.json", "avg_rank.Random restart", 0.01, "abs"),
    ("rank_mohho_visa", 4.67, "omnibus_visa_paired.json", "avg_rank.MOHHO", 0.01, "abs"),
    ("rank_nsga2_visa", 5.77, "omnibus_visa_paired.json", "avg_rank.NSGA-II", 0.01, "abs"),
    # ---- v5: competent MO-HHO + order-preservation ----
    ("competent_vs_random_pct", 2.0, "ladder_v5.json",
     "key_finding.competent_beats_random_pct", 0.6, "abs"),
    ("competent_beats_random", True, "ladder_v5.json",
     "key_finding.competent_beats_random", 0, "exact"),
    ("naive_beats_random", False, "ladder_v5.json",
     "key_finding.naive_beats_random", 0, "exact"),
    ("competent_zdt2_validation", 0.99, "competent_mohho_validation.json",
     "configs.[3].per_benchmark.ZDT2.hv_over_true", 0.03, "abs"),
    ("tau_nsga2", 0.99, "tau_by_method.json", "methods.nsga2_realcoded.tau_mean", 0.02, "abs"),
    ("hv_tau_spearman_rho", -0.21, "hv_vs_tau.json", "spearman_hv_vs_tau.rho", 0.05, "abs"),
    ("hv_tau_correlation_weak", True, "hv_vs_tau.json", "correlation_is_weak", 0, "exact"),
    # ---- v6: controlled 2x2 (two conditions, sec:twoconditions) ----
    ("c2x2_order_nds_hv", 315730, "factorial_2x2_conditions.json",
     "cells.order_nds.hv_mean", 0.01, "rel"),
    ("c2x2_order_gated_hv", 304126, "factorial_2x2_conditions.json",
     "cells.order_gated.hv_mean", 0.01, "rel"),
    ("c2x2_near_nds_hv", 305892, "factorial_2x2_conditions.json",
     "cells.near_nds.hv_mean", 0.01, "rel"),
    ("c2x2_near_gated_hv", 304760, "factorial_2x2_conditions.json",
     "cells.near_gated.hv_mean", 0.01, "rel"),
    ("c2x2_random_hv", 310214, "factorial_2x2_conditions.json",
     "random_restart.hv_mean", 0.01, "rel"),
    ("c2x2_order_nds_vs_random_pct", 1.78, "factorial_2x2_conditions.json",
     "cells.order_nds.vs_random_pct", 0.2, "abs"),
    ("c2x2_order_nds_A12", 0.791, "factorial_2x2_conditions.json",
     "cells.order_nds.A12_vs_random", 0.02, "abs"),
    ("c2x2_only_order_nds_wins", True, "factorial_2x2_conditions.json",
     "only_order_nds_wins", 0, "exact"),
    ("c2x2_interaction_significant", True, "factorial_2x2_conditions.json",
     "anova.interaction_significant", 0, "exact"),
    ("c2x2_wilcoxon_order_nds_p", 0.0014, "factorial_2x2_paired.json",
     "cells.order_nds.wilcoxon_p_vs_random", 0.05, "rel"),
    ("c2x2_perm_interaction_p", 0.0002, "factorial_2x2_paired.json",
     "interaction.p_permutation", 0.05, "rel"),
    ("c2x2_paired_rerun_mean", 315730, "factorial_2x2_paired.json",
     "cells.order_nds.hv_mean", 0.01, "rel"),
    # ---- v6 FASE 2: competent across 4 structures (structures_v6.json) ----
    ("struct_competent_knapsack_pos", 1, "structures_v6.json",
     "placement.knapsack.competent_position_of_7", 0, "exact"),
    ("struct_competent_knapsack_rank", 1.13, "structures_v6.json",
     "placement.knapsack.competent_avg_rank", 0.05, "abs"),
    ("struct_competent_knapsack_perm_best", False, "structures_v6.json",
     "placement.knapsack.perm_native_still_best", 0, "exact"),
    ("struct_competent_visa_pos", 2, "structures_v6.json",
     "placement.visa.competent_position_of_7", 0, "exact"),
    ("struct_competent_tsp_pos", 5, "structures_v6.json",
     "placement.TSP.competent_position_of_7", 0, "exact"),
    ("struct_competent_flowshop_pos", 2, "structures_v6.json",
     "placement.flow-shop.competent_position_of_7", 0, "exact"),
    # ---- 2026-06-10: predictive test BRKGA-style (brkga_ladder/brkga_full) ----
    ("brkga_tau_xover", 0.63, "brkga_ladder.json",
     "operator_tau.biased_uniform_xover.mean_tau", 0.01, "abs"),
    ("brkga_hv_mean", 309970, "brkga_ladder.json", "hv_mean", 60, "abs"),
    ("brkga_hv_std", 9790, "brkga_ladder.json", "hv_std", 30, "abs"),
    ("brkga_cv_pct", 3.16, "brkga_ladder.json", "cv_pct", 0.02, "abs"),
    ("brkga_combined_hv", 325465, "brkga_ladder.json", "combined_front_hv", 60, "abs"),
    ("brkga_combined_sols", 157, "brkga_ladder.json", "combined_front_size", 0, "exact"),
    ("brkga_vs_random_a12", 0.47, "brkga_ladder.json", "paired[0].a12", 0.01, "abs"),
    ("brkga_vs_realcoded_diff_pct", 5.7, "brkga_ladder.json",
     "paired[2].mean_diff_pct", 0.1, "abs"),
    ("brkga_full_hv_mean", 309928, "brkga_full.json", "hv_mean", 60, "abs"),
    # ---- 2026-06-10: perm-SPEA2 al ladder (perm_spea2.json) ----
    ("spea2_hv_mean", 317135, "perm_spea2.json", "hv_mean", 60, "abs"),
    ("spea2_hv_std", 3814, "perm_spea2.json", "hv_std", 30, "abs"),
    ("spea2_cv_pct", 1.20, "perm_spea2.json", "cv_pct", 0.02, "abs"),
    ("spea2_combined_hv", 322037, "perm_spea2.json", "combined_front_hv", 60, "abs"),
    ("spea2_combined_sols", 179, "perm_spea2.json", "combined_front_size", 0, "exact"),
    ("spea2_vs_perm_nsga_p", 0.47, "perm_spea2.json",
     "vs_perm_nsga_p_two_sided", 0.01, "abs"),
    ("spea2_vs_perm_nsga_a12", 0.45, "perm_spea2.json", "vs_perm_nsga_A12", 0.01, "abs"),
    # ---- 2026-06-10: tau por estructura (tau_structures.json) ----
    ("tau_struct_knapsack_sbx", 0.99, "tau_structures.json",
     "structures.knapsack.sbx_family_mean", 0.01, "abs"),
    ("tau_struct_tsp_sbx", 0.99, "tau_structures.json",
     "structures.tsp.sbx_family_mean", 0.01, "abs"),
    ("tau_struct_flowshop_sbx", 0.99, "tau_structures.json",
     "structures.flowshop.sbx_family_mean", 0.01, "abs"),
    ("tau_struct_knapsack_hho_near0", 0.0, "tau_structures.json",
     "structures.knapsack.hho_family_mean", 0.15, "abs"),
    # ---- 2026-06-10: headroom sweep ampliado a n=15 (headroom_sweep_n15.json) ----
    ("headroom_n15_rho", -0.78, "headroom_sweep_n15.json", "spearman_rho", 0.01, "abs"),
    ("headroom_n15_perm_p", 0.001, "headroom_sweep_n15.json", "perm_p_two_sided", 0.0005, "abs"),
    ("headroom_n15_last_frac", 0.85, "headroom_sweep_n15.json", "fracs[14]", 0, "exact"),
    ("headroom_n15_seeds", 10, "headroom_sweep_n15.json", "seeds", 0, "exact"),
    # ---- 2026-06-10: validacion prospectiva registrada mo-SCP (prospective_scp.json) ----
    ("scp_random_hv", 0.259, "prospective_scp.json", "hv_mean.random_restart", 0.001, "abs"),
    ("scp_nsga_rc_hv", 0.286, "prospective_scp.json", "hv_mean.nsga2_realcoded", 0.001, "abs"),
    ("scp_rk_biased_hv", 0.415, "prospective_scp.json", "hv_mean.rk_nsga2_biased", 0.001, "abs"),
    ("scp_perm_nsga_hv", 0.357, "prospective_scp.json", "hv_mean.perm_nsga2", 0.001, "abs"),
    ("scp_competent_hv", 0.386, "prospective_scp.json", "hv_mean.competent_mohho", 0.001, "abs"),
    ("scp_P1_holds", False, "prospective_scp.json", "verdict.P1.holds", 0, "exact"),
    ("scp_P2_holds", False, "prospective_scp.json", "verdict.P2.holds", 0, "exact"),
    ("scp_P3_holds", True, "prospective_scp.json", "verdict.P3.holds", 0, "exact"),
    ("scp_P4_holds", True, "prospective_scp.json", "verdict.P4.holds", 0, "exact"),
    ("scp_rk_biased_gap_pct", 59.9, "prospective_scp.json",
     "verdict.P2.gap_vs_random_pct", 0.5, "abs"),
    ("scp_P3_p", 9.3e-10, "prospective_scp.json", "verdict.P3.p_one_sided", 1e-10, "abs"),
    ("scp_P1_p_above", 1.3e-8, "prospective_scp.json",
     "verdict.P1.p_above_random_one_sided", 5e-9, "abs"),
    # ---- 2026-06-10 ronda 3: endurecimiento estadistico (stats_round3.json) ----
    ("r3_friedman9_chi2", 133.8, "stats_round3.json", "friedman_9methods.chi2", 0.2, "abs"),
    ("r3_friedman9_cd", 2.19, "stats_round3.json", "friedman_9methods.nemenyi_cd_005", 0.01, "abs"),
    ("r3_rank_perm_nsga2", 2.97, "stats_round3.json",
     "friedman_9methods.mean_ranks.perm_nsga2", 0.01, "abs"),
    ("r3_rank_nsga2_rc", 8.77, "stats_round3.json",
     "friedman_9methods.mean_ranks.nsga2_realcoded", 0.01, "abs"),
    ("r3_rank_rk_biased", 4.57, "stats_round3.json",
     "friedman_9methods.mean_ranks.rk_nsga2_biased", 0.01, "abs"),
    ("r3_rank_random", 6.47, "stats_round3.json",
     "friedman_9methods.mean_ranks.random_restart", 0.01, "abs"),
    ("r3_mohho_vs_nsga2_paired", 4.4e-6, "stats_round3.json",
     "mohho_vs_nsga2.paired_wilcoxon_two_sided", 2e-7, "abs"),
    ("r3_holm_all_survive", True, "stats_round3.json",
     "holm_family.all_headline_survive", 0, "exact"),
    ("r3_sign_test", 0.03125, "stats_round3.json", "sign_test_5of5_one_sided", 1e-5, "abs"),
    # ---- 2026-06-10: barrido rho_e registrado (rho_sweep.json) ----
    ("rho_visa_spearman_hv", 0.145, "rho_sweep.json",
     "structures.visa.spearman_tau_hv", 0.01, "abs"),
    ("rho_knapsack_spearman_hv", 0.236, "rho_sweep.json",
     "structures.knapsack.spearman_tau_hv", 0.01, "abs"),
    ("rho_flowshop_spearman_hv", 0.482, "rho_sweep.json",
     "structures.flowshop.spearman_tau_hv", 0.01, "abs"),
    ("rho_visa_igd_spearman", 0.80, "rho_sweep.json",
     "structures.visa.spearman_tau_igd", 0.01, "abs"),
    ("rho_knapsack_igd_spearman", 0.964, "rho_sweep.json",
     "structures.knapsack.spearman_tau_igd", 0.01, "abs"),
    ("rho_tsp_igd_spearman", 1.0, "rho_sweep.json",
     "structures.tsp.spearman_tau_igd", 0.001, "abs"),
    ("rho_visa_above_all", False, "rho_sweep.json",
     "structures.visa.above_random_at_all_levels", 0, "exact"),
    ("rho_tsp_above_all", True, "rho_sweep.json",
     "structures.tsp.above_random_at_all_levels", 0, "exact"),
    ("rho_flowshop_above_all", True, "rho_sweep.json",
     "structures.flowshop.above_random_at_all_levels", 0, "exact"),
    ("rho_scp_above_all", True, "rho_sweep.json",
     "structures.scp.above_random_at_all_levels", 0, "exact"),
    ("rho_R1_visa_fails", False, "rho_sweep.json", "verdict.R1_visa.holds", 0, "exact"),
    ("rho_R3_fails", False, "rho_sweep.json", "verdict.R3_igd_agrees.holds", 0, "exact"),
    ("rho_knapsack_hv_level0", 0.31, "rho_sweep.json",
     "structures.knapsack.hv_mean_levels[0]", 0.005, "abs"),
    # ---- 2026-06-10 Paquete A: GRASP control, IGD+/eps per-run, slope CI ----
    ("grasp_hv_mean", 298531, "grasp_control.json", "hv_mean", 60, "abs"),
    ("grasp_vs_random_diff_pct", -3.77, "grasp_control.json",
     "paired[0].mean_diff_pct", 0.05, "abs"),
    ("igd9_rankcorr_hv_igd", 0.82, "ladder_igd.json",
     "rank_correlation_hv_vs_igd", 0.01, "abs"),
    ("igd9_rankcorr_hv_eps", 0.85, "ladder_igd.json",
     "rank_correlation_hv_vs_eps", 0.01, "abs"),
    ("igd9_friedman_igd_chi2", 176.5, "ladder_igd.json", "friedman.igd_plus[0]", 0.2, "abs"),
    ("igd9_friedman_eps_chi2", 169.3, "ladder_igd.json", "friedman.eps[0]", 0.2, "abs"),
    ("igd9_spea2_igd_rank", 1.10, "ladder_igd.json",
     "mean_ranks_igd_plus.perm_spea2", 0.02, "abs"),
    ("igd9_moead_igd_rank", 7.23, "ladder_igd.json",
     "mean_ranks_igd_plus.perm_moead", 0.02, "abs"),
    ("slope_visa_ci_lo", -0.151, "rho_slope_ci.json",
     "structures.visa.slope_pct_per_0p1_tau_ci95[0]", 0.02, "abs"),
    ("slope_visa_ci_hi", 0.212, "rho_slope_ci.json",
     "structures.visa.slope_pct_per_0p1_tau_ci95[1]", 0.02, "abs"),
    # ---- 2026-06-10 elevacion final: tuning L9, ablacion E, PLS, indice s ----
    ("l9_visa_confirm", 308082, "nsga2_l9.json", "visa.confirmation_mean", 60, "abs"),
    ("l9_visa_diff_pct", -0.69, "nsga2_l9.json", "visa.diff_vs_random_pct", 0.05, "abs"),
    ("l9_knap_diff_pct", 46.07, "nsga2_l9.json", "knapsack.diff_vs_random_pct", 0.2, "abs"),
    ("l9_knap_p_two", 1.86e-9, "nsga2_l9.json", "knapsack.p_vs_random_two_sided", 5e-10, "abs"),
    ("l9_best_eta", 2.0, "nsga2_l9.json", "visa.best_config.eta_c", 0, "exact"),
    ("l9_best_pm_mult", 5.0, "nsga2_l9.json", "visa.best_config.pm_mult", 0, "exact"),
    ("eabl_diff_pct", 0.01, "discrete_e_ablation.json", "diff_pct", 0.02, "abs"),
    ("eabl_p", 0.87, "discrete_e_ablation.json", "p_two_sided_vs_scheduled", 0.01, "abs"),
    ("pls_hv_mean", 303979, "pls_control.json", "hv_mean", 60, "abs"),
    ("pls_vs_random_diff", -2.01, "pls_control.json", "vs_random.diff_pct", 0.05, "abs"),
    ("sat_visa", 0.994, "sat_index.json", "index.visa.s", 0.005, "abs"),
    ("sat_knapsack", 0.998, "sat_index.json", "index.knapsack.s", 0.005, "abs"),
    ("sat_tsp", 0.0, "sat_index.json", "index.tsp.s", 0, "exact"),
    # ---- CAMERA-READY MICAI 2026: cifras nuevas impresas en el .tex ----
    # punto de referencia del HV (respuesta a Reviewer #1)
    ("cr_refpoint_total_points", 15273, "cr_indicators.json",
     "reference_point.total_points", 0, "abs"),
    ("cr_refpoint_n_excluded", 3, "cr_indicators.json",
     "reference_point.n_excluded_by_primary", 0, "abs"),
    ("cr_refpoint_max_f3", 20200.0, "cr_indicators.json",
     "reference_point.max_f3_observed_in_fronts", 0.5, "abs"),
    # frentes de referencia declarados en 4.4
    ("cr_Z9_size", 185, "cr_indicators.json", "reference_front_Z9.size", 0, "abs"),
    ("cr_Z2_size", 126, "nsga2_comparison.json", "reference_front_size", 0, "abs"),
    # Spacing e IGD clasicos MOHHO-NSGA-II (protocolo compartido), impresos en 4.3
    ("cr_spacing_mohho", 0.011, "nsga2_comparison.json", "mohho.spacing", 0.0005, "abs"),
    ("cr_spacing_nsga2", 0.046, "nsga2_comparison.json", "nsga2.spacing", 0.0005, "abs"),
    ("cr_igd_mohho", 0.021, "nsga2_comparison.json", "mohho.igd", 0.0005, "abs"),
    ("cr_igd_nsga2", 0.007, "nsga2_comparison.json", "nsga2.igd", 0.0005, "abs"),
    # columna A12 de la Tabla 1 (9 metodos, linaje sellado ladder_v5)
    ("cr_a12_nsga2", 0.03, "cr_indicators.json",
     "a12_vs_random_restart.nsga2_realcoded", 0.005, "abs"),
    ("cr_a12_mohho", 0.25, "cr_indicators.json",
     "a12_vs_random_restart.mohho_realcoded", 0.005, "abs"),
    ("cr_a12_rk_nsga2", 0.47, "cr_indicators.json",
     "a12_vs_random_restart.rk_nsga2_biased", 0.005, "abs"),
    ("cr_a12_competent", 0.79, "cr_indicators.json",
     "a12_vs_random_restart.competent_mohho", 0.005, "abs"),
    ("cr_a12_perm_moead", 0.86, "cr_indicators.json",
     "a12_vs_random_restart.perm_moead", 0.005, "abs"),
    ("cr_a12_discrete", 0.97, "cr_indicators.json",
     "a12_vs_random_restart.discrete_mohho", 0.005, "abs"),
    ("cr_a12_perm_spea2", 0.96, "cr_indicators.json",
     "a12_vs_random_restart.perm_spea2", 0.005, "abs"),
    ("cr_a12_perm_nsga2", 1.00, "cr_indicators.json",
     "a12_vs_random_restart.perm_nsga2", 0.005, "abs"),
    # ---- correccion archivo 200->100 y jerarquia estadistica ----
    ("cr_nds_hv_mean", 316345.0, "competent_arch100.json", "hv_mean_arch100", 2.0, "abs"),
    ("cr_nds_trajectory_invariance", 30, "competent_arch100.json",
     "trajectory_invariance.seeds_identical", 0, "abs"),
    ("cr_kw_omnibus_H", 149.8, "cr_derived.json", "omnibus.ladder9.primary.H", 0.1, "abs"),
    ("cr_mwu_nds_vs_random", 5.87e-05, "cr_derived.json",
     "holm.unpaired_primary.results.nds_vs_random.p", 0.02, "rel"),
    ("cr_wilcoxon_sensitivity_nds", 5.66e-04, "cr_derived.json",
     "holm.seed_label_sensitivity.results.nds_vs_random.p", 0.02, "rel"),
    ("cr_holm_family_size", 12, "cr_derived.json", "holm.unpaired_primary.m", 0, "abs"),
    # ---- 2x2 reanalizado: paquetes, interaccion bloqueada, presupuesto real ----
    ("cr2x2_interaction_wilcoxon", 7.9789758e-04, "cr_derived.json",
     "interaction_2x2.primary.p", 1e-3, "rel"),
    ("cr2x2_signflip", 6.029994e-04, "cr_derived.json",
     "interaction_2x2.sensitivity.blocked_sign_flip.p", 1e-3, "rel"),
    ("cr2x2_hv_order_nds", 315730.4, "factorial_2x2_reanalysis_cr.json",
     "cells.order_nds.hv_mean", 0.5, "abs"),
    ("cr2x2_hv_near_nds", 305892.3, "factorial_2x2_reanalysis_cr.json",
     "cells.near_nds.hv_mean", 0.5, "abs"),
    ("cr2x2_hv_order_gated", 304126.0, "factorial_2x2_reanalysis_cr.json",
     "cells.order_gated.hv_mean", 0.5, "abs"),
    ("cr2x2_hv_near_gated", 304760.0, "factorial_2x2_reanalysis_cr.json",
     "cells.near_gated.hv_mean", 0.5, "abs"),
    ("cr2x2_moved_order_gated", 0.0087, "factorial_2x2_reanalysis_cr.json",
     "cells.order_gated.moved_fraction_mean", 1e-5, "abs"),
    ("cr2x2_moved_near_gated", 0.0175, "factorial_2x2_reanalysis_cr.json",
     "cells.near_gated.moved_fraction_mean", 1e-5, "abs"),
    ("cr2x2_total_evals", 25050, "factorial_2x2_reanalysis_cr.json",
     "budget.total_evals", 0, "abs"),
    ("cr2x2_pm_order", 0.15, "factorial_2x2_reanalysis_cr.json",
     "cells.order_nds.pm", 1e-9, "abs"),
    ("cr2x2_pm_near", 0.00952381, "factorial_2x2_reanalysis_cr.json",
     "cells.near_nds.pm", 1e-6, "abs"),
    # ---- N1: el enjambre gated gana en knapsack (rompe la mitad C2 fuera del visa)
    ("cr_knapsack_gated_hv", 0.216608, "second_problem.json",
     "methods.MOHHO (real-coded).hv_mean", 1e-5, "abs"),
    ("cr_knapsack_random_hv", 0.198307, "second_problem.json",
     "methods.Random restart.hv_mean", 1e-5, "abs"),
    # ---- equidad: la asignacion unica de minima f2
    ("cr_equity_std", 0.752, "equity_audit.json",
     "best_by_metric.f2_gap.fairness.wait_std", 5e-4, "abs"),
    ("cr_equity_gini", 0.2295, "equity_audit.json",
     "best_by_metric.f2_gap.fairness.wait_gini", 5e-4, "abs"),
    ("cr_equity_jain", 0.9360, "equity_audit.json",
     "best_by_metric.f2_gap.fairness.jain_inverse_wait", 5e-4, "abs"),
    ("cr_equity_served", 21, "equity_audit.json",
     "best_by_metric.f2_gap.fairness.served_countries", 0, "abs"),
]


def check(results_dir):
    rows = []; n_mismatch = 0
    for name, pv, jf, jp, tol, kind in CLAIMS:
        fp = Path(results_dir) / jf
        if not fp.exists():
            rows.append({"name": name, "status": "JSON_MISSING", "file": jf,
                         "paper": pv, "json": None}); n_mismatch += 1; continue
        try:
            jv = jget(json.loads(fp.read_text()), jp)
        except Exception as e:
            rows.append({"name": name, "status": "PATH_ERROR", "file": jf,
                         "path": jp, "err": str(e), "paper": pv}); n_mismatch += 1; continue
        if kind == "exact":
            ok = (jv == pv)
        elif kind == "abs":
            ok = abs(float(jv) - float(pv)) <= tol
        else:
            ok = abs(float(jv) - float(pv)) <= tol * abs(float(pv))
        if not ok: n_mismatch += 1
        rows.append({"name": name, "status": "OK" if ok else "MISMATCH",
                     "paper": pv, "json": jv, "delta": (float(jv) - float(pv))
                     if isinstance(jv, (int, float)) else None})
    return rows, n_mismatch


def tex_number_inventory(tex_dir):
    inv = []
    p = Path(tex_dir)
    if not p.exists():
        return inv
    for tex in p.rglob("*.tex"):
        for ln, line in enumerate(tex.read_text(errors="ignore").splitlines(), 1):
            for m in re.finditer(r"(?<![\\A-Za-z])\d[\d,]*\.?\d*", line):
                tok = m.group(0)
                if len(tok.replace(",", "").replace(".", "")) >= 3:
                    inv.append({"file": tex.name, "line": ln, "token": tok,
                                "context": line.strip()[:120]})
    return inv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=_bootstrap.results_dir())
    ap.add_argument("--tex", default=None,
                    help="dir del paper LaTeX (MICAI/) para inventario de numeros")
    a = ap.parse_args()
    rows, n_mismatch = check(a.results)
    inv = tex_number_inventory(a.tex) if a.tex else []
    out = {"n_claims_checked": len(rows), "n_mismatch": n_mismatch,
           "rows": rows, "tex_inventory_count": len(inv),
           "tex_inventory_sample": inv[:40]}
    Path(a.results, "_verify_paper.json").write_text(json.dumps(out, indent=2))
    for r in rows:
        print(f"  [{r['status']:12s}] {r['name']}: paper={r.get('paper')} json={r.get('json')}")
    print(f"\nn_mismatch = {n_mismatch} (de {len(rows)} claims cableados). "
          f"Inventario .tex: {len(inv)} tokens. -> _verify_paper.json")
    if n_mismatch:
        print("FALLO: hay cifras del paper sin respaldo o stale. Corrige el PAPER, no el JSON.")
    return 1 if n_mismatch else 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
