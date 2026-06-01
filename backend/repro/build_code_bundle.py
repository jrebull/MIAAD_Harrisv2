"""Arma _audit_handoff/code_and_results_20260531.zip con CODIGO + JSON + STATUS.md,
para juicio tecnico externo. Excluye Prompts/, .venv, __pycache__, binarios pesados.
Verifica que NO entre ningun path de prompt/KIT antes de cerrar."""
import os, shutil, zipfile

BASE = "/Users/haowei/Documents/MIAAD/SMART/Harris2"
STAGE = os.path.join(BASE, "_audit_handoff", "code_bundle")
if os.path.exists(STAGE):
    shutil.rmtree(STAGE)

SKIP_DIRS = {"__pycache__", ".venv", ".git", "node_modules", "Prompts"}
SKIP_EXT = {".pyc"}


def copy_tree(src_rel, dst_rel):
    src = os.path.join(BASE, src_rel)
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1] in SKIP_EXT:
                continue
            sp = os.path.join(root, f)
            rel = os.path.relpath(sp, src)
            dp = os.path.join(STAGE, dst_rel, rel)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy(sp, dp)
            n += 1
    return n


def copy_files(src_rel, dst_rel, exts):
    src = os.path.join(BASE, src_rel)
    dst = os.path.join(STAGE, dst_rel)
    os.makedirs(dst, exist_ok=True)
    n = 0
    if os.path.isdir(src):
        for f in sorted(os.listdir(src)):
            if os.path.splitext(f)[1] in exts:
                shutil.copy(os.path.join(src, f), os.path.join(dst, f))
                n += 1
    return n


counts = {}
# --- CODE ---
counts["core"] = copy_tree("backend/app/core", "code/app/core")
counts["repro"] = copy_tree("backend/repro", "code/repro")
counts["collapse"] = copy_tree("backend/collapse", "code/collapse")
counts["backend_scripts"] = copy_files("backend", "code", {".py"})
# config/data modules already under app/core; also include requirements if present
for f in ["requirements.txt"]:
    p = os.path.join(BASE, "backend", f)
    if os.path.exists(p):
        shutil.copy(p, os.path.join(STAGE, "code", f))
# --- RESULTS --- (both at top level for browsing AND under code/app/data/results
# so the firewall `python repro/verify_paper.py` runs without flags, as in the repo)
counts["json"] = copy_files("backend/app/data/results", "results", {".json"})
counts["csv"] = copy_files("backend/app/data/results", "results", {".csv"})
copy_files("backend/app/data/results", "code/app/data/results", {".json"})
copy_files("backend/app/data/results", "code/app/data/results", {".csv"})
# --- REPORTS ---
counts["reports"] = copy_files("MICAI/output", "reports", {".md"})
# --- STATUS ---
shutil.copy(os.path.join(BASE, "_audit_handoff", "STATUS.md"),
            os.path.join(STAGE, "STATUS.md"))

# --- ZIP ---
zp = os.path.join(BASE, "_audit_handoff", "code_and_results_20260531.zip")
if os.path.exists(zp):
    os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(STAGE):
        for f in files:
            fp = os.path.join(root, f)
            z.write(fp, os.path.relpath(fp, os.path.join(BASE, "_audit_handoff")))

# --- SAFETY CHECK ---
names = zipfile.ZipFile(zp).namelist()
forbidden = [n for n in names if "prompt" in n.lower() or "kit_" in n.lower()
             or "superprompt" in n.lower() or n.endswith(".pyc")]
total_files = len([n for n in names if not n.endswith("/")])

print("counts:", counts)
print("zip:", os.path.getsize(zp), "bytes |", total_files, "files")
print("forbidden paths inside:", forbidden or "NONE")
