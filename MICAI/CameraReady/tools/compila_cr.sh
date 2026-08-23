#!/usr/bin/env bash
# compila_cr.sh -- compilador reproducible del camera-ready.
# MUTA EL DISCO: reemplaza el PDF y los auxiliares del directorio de trabajo.
# Lee las TRES senales: codigo de salida, lineas '!' del log, y el log en latin-1.
set -u
set -o pipefail
# Sin esta comprobacion, una herramienta ausente o rota no falla: pdffonts devolviendo
# 127 hacia un `grep -c || true` reportaba "0 fuentes Type 3, 0 sin incrustar" y rc=0.
for _t in pdflatex iconv pdfinfo pdffonts; do
  command -v "$_t" >/dev/null 2>&1 || { echo "FALLO: falta la herramienta '$_t'"; exit 4; }
  case "$_t" in
    pdflatex) "$_t" --version  >/dev/null 2>&1 || { echo "FALLO: '$_t' no ejecuta"; exit 4; } ;;
    iconv)    printf 'x' | "$_t" -f latin1 -t utf-8 >/dev/null 2>&1 || { echo "FALLO: '$_t' no ejecuta"; exit 4; } ;;
    *)        "$_t" -v >/dev/null 2>&1 || "$_t" --help >/dev/null 2>&1 || { echo "FALLO: '$_t' no ejecuta"; exit 4; } ;;
  esac
done
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
  PF=$(pdffonts "$JOB.pdf") || { echo "FALLO: pdffonts fallo sobre $JOB.pdf"; exit 4; }
  T3=$(printf '%s\n' "$PF" | tail -n +3 | grep -c 'Type 3' || true)
  EMB=$(printf '%s\n' "$PF" | tail -n +3 | awk 'NF>0 && $(NF-4)!="yes"' | wc -l | tr -d ' ')
  NF_TOT=$(printf '%s\n' "$PF" | tail -n +3 | grep -c . || true)
  echo "  fuentes totales     = $NF_TOT"
  echo "  fuentes Type 3      = $T3"
  echo "  fuentes NO incrust. = $EMB"
fi
# Estas tres condiciones rompen el camera-ready y antes solo se IMPRIMIAN: quien
# leyera el codigo de salida veia 0 con referencias rotas o fuentes sin incrustar.
FALLOS=0
[ "${UNDEF:-0}" -ne 0 ] && { echo "FALLO: $UNDEF referencias o citas indefinidas"; FALLOS=1; }
[ "${T3:-0}"    -ne 0 ] && { echo "FALLO: $T3 fuentes Type 3"; FALLOS=1; }
[ "${EMB:-0}"   -ne 0 ] && { echo "FALLO: $EMB fuentes sin incrustar"; FALLOS=1; }
[ "${BANG:-0}"  -ne 0 ] && { echo "FALLO: $BANG lineas '!' en el log"; FALLOS=1; }
[ "${NF_TOT:-0}" -eq 0 ] && { echo "FALLO: pdffonts no reporto ninguna fuente; no se midio nada"; FALLOS=1; }
[ $rc -eq 0 ] && [ $FALLOS -ne 0 ] && rc=3
exit $rc
