#!/usr/bin/env python3
"""Compara un PDF candidato contra el snapshot del baseline, pagina por pagina.

SOLO LECTURA: no escribe nada fuera de un directorio temporal propio.

Usa DOS senales, porque una sola miente:
  - texto extraido  -> ve cambios de prosa, no ve un cambio puramente grafico
  - raster por pagina -> ve el cambio grafico, y confirma que el texto no reflujo
Distingue: cambio TEXTUAL, cambio VISUAL, o solo METADATOS del PDF.
"""
import subprocess, sys, tempfile, hashlib, pathlib, argparse

def sh(*a):
    return subprocess.run(a, capture_output=True)

def pages(pdf):
    out = sh("pdfinfo", pdf).stdout.decode("utf8", "replace")
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0

def md5(p):
    return hashlib.md5(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidato")
    ap.add_argument("--baseline-dir", required=True)
    a = ap.parse_args()
    B = pathlib.Path(a.baseline_dir)
    nb = len(list((B / "txt").glob("*.txt")))
    nc = pages(a.candidato)
    print(f"paginas: baseline={nb}  candidato={nc}", end="")
    print("   <-- CAMBIO DE PAGINACION" if nb != nc else "")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="diffpag_"))
    (tmp / "txt").mkdir(); (tmp / "png").mkdir()
    for p in range(1, nc + 1):
        sh("pdftotext", "-f", str(p), "-l", str(p), "-layout",
           a.candidato, str(tmp / "txt" / f"p{p:02d}.txt"))
    sh("pdftoppm", "-r", "100", "-png", a.candidato, str(tmp / "png" / "p"))
    tchg, vchg, same = [], [], []
    for p in range(1, min(nb, nc) + 1):
        bt, ct = B / "txt" / f"p{p:02d}.txt", tmp / "txt" / f"p{p:02d}.txt"
        bp = B / "png" / f"p-{p:02d}.png"
        if not bp.exists():
            bp = B / "png" / f"p-{p}.png"
        cp = tmp / "png" / f"p-{p:02d}.png"
        if not cp.exists():
            cp = tmp / "png" / f"p-{p}.png"
        dt = (not bt.exists() or not ct.exists()) or md5(bt) != md5(ct)
        dv = (not bp.exists() or not cp.exists()) or md5(bp) != md5(cp)
        if dt:   tchg.append(p)
        elif dv: vchg.append(p)
        else:    same.append(p)
    print(f"  texto cambiado : {tchg if tchg else 'ninguna'}")
    print(f"  solo visual    : {vchg if vchg else 'ninguna'}")
    print(f"  sin cambio     : {len(same)} paginas")
    if nb != nc:
        print(f"  paginas nuevas/perdidas: {abs(nb-nc)}")
    print(f"\n(raster del candidato en {tmp})")

if __name__ == "__main__":
    main()
