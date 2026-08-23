#!/usr/bin/env bash
# compila_cr.sh -- compilador reproducible del camera-ready.
# MUTA EL DISCO: reemplaza el PDF y los auxiliares del directorio de trabajo.
# Lee las TRES senales: codigo de salida, lineas '!' del log, y el log en latin-1.
set -u
SRC="${1:?uso: compila_cr.sh <dir-src> [jobname]}"
JOB="${2:-main_cr}"
export SOURCE_DATE_EPOCH=1787356800   # 2026-08-22T00:00:00Z UTC, fijo -> PDF reproducible
export FORCE_SOURCE_DATE=1
cd "$SRC" || exit 2
rc=0
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "$JOB.tex" >/dev/null 2>&1
  rc=$?
  [ $rc -ne 0 ] && { echo "FALLO en pasada $pass (rc=$rc)"; break; }
done
echo "rc=$rc"
# el .log de pdfTeX viene en latin-1
BANG=$(iconv -f latin1 -t utf-8 "$JOB.log" 2>/dev/null | grep -c '^!' || true)
UNDEF=$(iconv -f latin1 -t utf-8 "$JOB.log" 2>/dev/null | grep -ci 'undefined \(citation\|reference\)\|LaTeX Warning: Reference' || true)
echo "lineas '!'          = $BANG"
echo "refs/citas indef.   = $UNDEF"
iconv -f latin1 -t utf-8 "$JOB.log" 2>/dev/null | grep -a 'Overfull\|Underfull' | sed 's/^/  warn: /'
if [ -f "$JOB.pdf" ]; then
  pdfinfo "$JOB.pdf" | grep -E '^Pages|^Page size' | sed 's/^/  /'
  T3=$(pdffonts "$JOB.pdf" | tail -n +3 | grep -c 'Type 3' || true)
  EMB=$(pdffonts "$JOB.pdf" | tail -n +3 | awk 'NF>0 && $(NF-4)!="yes"' | wc -l | tr -d ' ')
  NF_TOT=$(pdffonts "$JOB.pdf" | tail -n +3 | grep -c . || true)
  echo "  fuentes totales     = $NF_TOT"
  echo "  fuentes Type 3      = $T3"
  echo "  fuentes NO incrust. = $EMB"
fi
exit $rc
