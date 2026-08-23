#!/usr/bin/env python3
"""sanea_cr.py -- produce la copia del .tex que viaja al maquetador.

Quita SOLO notas internas de proceso: historia de versiones, bases congeladas,
la variante de doble ciego y los recordatorios de tramite. CONSERVA los
comentarios tecnicos que explican por que el preambulo hace lo que hace (la
trampa de A4, el silenciado del warning de \\vec, los separadores de seccion y
los comentarios estructurales de las figuras TikZ), porque esos viajan al
maquetador y le sirven.

Que el saneo es inocuo NO se argumenta: se demuestra compilando la copia y
exigiendo que el PDF salga identico byte a byte al canonico.
"""
import re, sys, pathlib

BLOQUES_FUERA = [
    # cabecera con historia interna, bases congeladas e instrucciones de doble ciego
    (r"^%{20,}\n(?:%.*\n)+?%{20,}\n", "cabecera interna + doble ciego"),
]
LINEAS_FUERA = [
    (r"^% Tag del repositorio citado.*$", "nota de proceso del tag"),
    (r"^% El tag se crea SOBRE el commit.*$", "nota de proceso del tag"),
    (r"^% fuente publicada se cite a si misma\.$", "nota de proceso del tag"),
    (r"^% >>> CAMERA-READY.*$", "marca de variante"),
    (r"^% >>> REVIEW.*$", "marca de variante"),
    (r"^% \\author\{Anonymous.*$", "bloque anonimo"),
    (r"^% \\authorrunning\{Anonymous\}.*$", "bloque anonimo"),
    (r"^% \\institute\{Institution withheld.*$", "bloque anonimo"),
]

def sanea(txt):
    quitado = []
    for pat, why in BLOQUES_FUERA:
        m = re.search(pat, txt, re.M)
        if m:
            quitado.append((why, len(m.group(0).splitlines())))
            txt = txt[:m.start()] + txt[m.end():]
    out = []
    for ln in txt.splitlines(True):
        drop = next((why for pat, why in LINEAS_FUERA if re.match(pat, ln)), None)
        if drop:
            quitado.append((drop, 1))
        else:
            out.append(ln)
    txt = "".join(out)
    txt = re.sub(r"\n{3,}", "\n\n", txt)          # normaliza huecos que deja el saneo
    return txt, quitado

if __name__ == "__main__":
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    t, q = sanea(src.read_text(encoding="utf-8"))
    dst.write_text(t, encoding="utf-8")
    tot = {}
    for why, n in q:
        tot[why] = tot.get(why, 0) + n
    for why, n in sorted(tot.items()):
        print(f"  fuera: {why} ({n} lineas)")
    print(f"  {len(src.read_text(encoding='utf-8').splitlines())} -> "
          f"{len(t.splitlines())} lineas")
    resid = [l for l in t.splitlines()
             if re.search(r">>>|doble ciego|double-blind|FROZEN|TODO|FIXME|Anonymous", l)]
    print(f"  residuos de proceso: {resid or 'ninguno'}")
