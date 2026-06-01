"""Build the reviewer handoff zip from the FINAL committed state (a4f3b1c).
Excludes anything under Prompts/. Writes to _audit_handoff/ (gitignored)."""
import os, shutil, zipfile, json
base = "/Users/haowei/Documents/MIAAD/SMART/Harris2"
stage = os.path.join(base, "_audit_handoff", "bundle_v6")
if os.path.exists(stage): shutil.rmtree(stage)
for d in ["results", "reports", "figures", "repro", "paper"]:
    os.makedirs(os.path.join(stage, d))

nj = nr = nf = ns = 0
rd = os.path.join(base, "backend/app/data/results")
for f in sorted(os.listdir(rd)):
    if f.endswith(".json"):
        shutil.copy(os.path.join(rd, f), os.path.join(stage, "results", f)); nj += 1
od = os.path.join(base, "MICAI/output")
for f in sorted(os.listdir(od)):
    if f.endswith(".md"):
        shutil.copy(os.path.join(od, f), os.path.join(stage, "reports", f)); nr += 1
for sub in ["v4", "v5", "v6", "collapse"]:
    src = os.path.join(base, "MICAI/figures", sub)
    if os.path.isdir(src):
        dst = os.path.join(stage, "figures", sub); os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f)); nf += 1
mp = os.path.join(base, "MICAI/figures/mechanism_2x2.pdf")
if os.path.exists(mp): shutil.copy(mp, os.path.join(stage, "figures", "mechanism_2x2.pdf")); nf += 1
rp = os.path.join(base, "backend/repro")
for f in sorted(os.listdir(rp)):
    if f.endswith(".py"):
        shutil.copy(os.path.join(rp, f), os.path.join(stage, "repro", f)); ns += 1
for src, dst in [("MICAI/Feasibility-Preserving_MOHHO_MICAI_reducida_anonymous.pdf", "submission_reducida_anonymous_18pp.pdf"),
                 ("MICAI/Feasibility-Preserving_MOHHO_MICAI_anonymous.pdf", "full_anonymous_27pp.pdf")]:
    s = os.path.join(base, src)
    if os.path.exists(s): shutil.copy(s, os.path.join(stage, "paper", dst))

fac = json.load(open(os.path.join(rd, "factorial_2x2_conditions.json")))
sv = json.load(open(os.path.join(rd, "structures_v6.json")))
vp = json.load(open(os.path.join(rd, "_verify_paper.json")))
on = fac["cells"]["order_nds"]; kn = sv["placement"]["knapsack"]
manifest = f"""AUDIT HANDOFF v6 (FINAL, commit a4f3b1c) - Visa Predict AI / MOHHO (MICAI)
==========================================================================
TESIS (v6 unificada): NON-DEGENERATE SEARCH governs decoder-based MO optimization
--- not the encoding, not the metaheuristic family. A method beats blind sampling
iff (1) its operator changes the decoded order AND (2) its selection preserves
diversity. The two conditions are SYNERGISTIC (significant interaction).

KEY EVIDENCE:
- 2x2 (factorial_2x2_conditions.json): only (order-change ^ NDS) beats random
  ({on['hv_mean']:,.0f} vs {fac['random_restart']['hv_mean']:,.0f}, p={on['mwu_p_greater_random']:.1e}); interaction
  eta2={fac['anova']['eta2_interaction_AxB']:.3f}, p={fac['anova']['p_interaction']:.1e} (significant -> synergistic).
- 4 structures (structures_v6.json, 30 seeds, 7 methods): the competent RANDOM-KEY
  MO-HHO WINS the knapsack (rank {kn['competent_avg_rank']:.2f}, pos {kn['competent_position_of_7']}/7, above every
  permutation-native method) -> a random-key method can be the single best, so the
  encoding is not the divider. visa 2/7, flow-shop 2/7, TSP 5/7.
- FIREWALL (_verify_paper.json): n_mismatch={vp['n_mismatch']} over {vp['n_claims_checked']} wired figures.
  Reproduce: cd backend && python repro/verify_paper.py

CONTENTS: results/ {nj} JSON  |  reports/ {nr} md  |  figures/ {nf}  |  repro/ {ns} py
          |  paper/ submission (18pp) + full (27pp) compiled PDFs

NOTE: Table 8 (tab:structures) remains the published 6-method comparison; the
competent method's cross-structure placement is reported in §6.6 prose + this bundle
(structures_v6.json), not by recomputing the table. The 2x2 robustness on
knapsack/flow-shop is declared future work.
NO prompt/KIT files are included.
"""
open(os.path.join(stage, "MANIFEST.txt"), "w").write(manifest)

zp = os.path.join(base, "_audit_handoff", "audit_handoff_20260531_v6.zip")
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(stage):
        for f in files:
            fp = os.path.join(root, f)
            z.write(fp, os.path.relpath(fp, os.path.join(base, "_audit_handoff")))
# safety: confirm no prompt paths inside
bad = [n for n in zipfile.ZipFile(zp).namelist() if "prompt" in n.lower() or "kit_" in n.lower()]
print(f"zip: {os.path.getsize(zp)} bytes | results={nj} reports={nr} figures={nf} repro={ns}")
print("forbidden paths inside:", bad or "NONE")
