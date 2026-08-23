"""Gate de CUSTODIA: el PDF canonico no puede ser anterior a sus fuentes ni
distinto de lo que producen. mtime es fragil, asi que la prueba fuerte es
recompilar en un temporal y exigir igualdad byte a byte.

Sin esto, los demas gates certifican un PDF viejo con fuentes nuevas -- que es
exactamente lo que ocurrio.
"""
import sys, subprocess, shutil, tempfile, hashlib, argparse
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True); ap.add_argument("--compile", required=True)
a = ap.parse_args(); S = Path(a.src); f = []
pdf, tex = S / "main_cr.pdf", S / "main_cr.tex"
if not pdf.exists(): f.append("no hay PDF canonico")
else:
    src_mt = max([tex.stat().st_mtime] + [p.stat().st_mtime for p in (S / "figures").glob("*.pdf")]
                 + [(S / "llncs.cls").stat().st_mtime])
    if pdf.stat().st_mtime < src_mt:
        f.append("el PDF canonico es ANTERIOR a alguna de sus fuentes")
    tmp = Path(tempfile.mkdtemp(prefix="fresh_")); (tmp / "figures").mkdir()
    shutil.copy(tex, tmp); shutil.copy(S / "llncs.cls", tmp)
    for g in (S / "figures").glob("*.pdf"): shutil.copy(g, tmp / "figures")
    subprocess.run([a.compile, str(tmp), "main_cr"], capture_output=True)
    h = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if not (tmp / "main_cr.pdf").exists(): f.append("la recompilacion no produjo PDF")
    elif h(tmp / "main_cr.pdf") != h(pdf):
        f.append("el PDF canonico NO es lo que producen sus fuentes actuales")
    log = S / "main_cr.log"
    if log.exists() and log.stat().st_mtime < tex.stat().st_mtime:
        f.append("el .log es anterior al .tex: sus metricas no son del artefacto actual")
for x in f: print("  FALLO:", x)
print(f"  n_fallos = {len(f)}")
sys.exit(1 if f else 0)
