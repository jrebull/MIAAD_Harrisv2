# Log de mejoras MICAI 2026

Fecha: 2026-06-01

## Objetivo

Fortalecer el paper MICAI a nivel de codigo, reproducibilidad, validacion algorítmica y narrativa cientifica. Se dejan fuera cambios de alto riesgo para esta version, como reescribir el modelo completo a multi-periodo; quedan como trabajo futuro explicito.

## Cambios de reproducibilidad

- Corregido `backend/tests/test_fifo.py`: el test de FIFO ahora usa los valores canonicos del paper y del firewall:
  - `f1=8.7891`
  - `f2=13.0`
  - `f3=1940`
- Actualizados comentarios stale de seeds en:
  - `backend/rerun_base.py`
  - `backend/discrete_mohho.py`
  - `backend/omnibus_stats.py`
- Actualizado `README.md`, que todavia reportaba el FIFO viejo `7.21, 12.64, 17,540`.
- Agregado `backend/repro/reproduce_fast.py`, verificador pre-envio que ejecuta:
  - unit tests,
  - firewall de claims,
  - conteo de paginas PDF,
  - escaneo de identidad en ZIPs anonimos.

Resultado:

```text
overall_ok: true
pytest: 0
firewall: 0
main_submission.pdf: 27 pp
main_reducida_submission.pdf: 18 pp
anonymous_zip_hits: 0
```

Artefacto: `backend/app/data/results/reproduce_fast.json`.

## Auditoria de equidad alternativa

Agregado `backend/repro/equity_audit.py`.

El script recompone el frente combinado de MOHHO a seeds `1..30` desde las posiciones, decodifica asignaciones y evalua metricas de equidad no optimizadas directamente:

- desviacion estandar de esperas medias por pais,
- Gini de esperas medias por pais,
- Jain index sobre esperas inversas,
- numero de paises servidos.

Resultado principal frente a FIFO:

| Metrica | FIFO | Mejor solucion del frente |
|---|---:|---:|
| `f2_gap` | 13.0 | 2.0 |
| `wait_std` | 3.14 | 0.75 |
| `wait_gini` | 0.79 | 0.17 |
| `jain_inverse_wait` | 0.80 | 0.94 |

Artefacto: `backend/app/data/results/equity_audit.json`.

Uso en paper: se agrego una frase corta para blindar la critica de que la conclusion de equidad depende de una sola metrica (`f2=max-min`).

## Baseline algoritmico adicional

Agregado `backend/perm_spea2.py`.

SPEA2 opera directamente sobre permutaciones con:

- SPEA2 strength fitness,
- densidad por distancia normalizada,
- environmental selection con truncamiento,
- order crossover (OX),
- swap mutation,
- mismo decoder greedy,
- seeds `1..30`.

Resultado:

| Metodo | HV media | Std | CV | Frente combinado | vs random | vs perm-NSGA-II |
|---|---:|---:|---:|---:|---:|---:|
| perm-SPEA2 | 317,135 | 3,814 | 1.20% | 322,037 / 179 sols | `p=4.45e-10` | `p=0.473`, A12=0.446 |

Interpretacion: SPEA2 supera claramente a random restart y queda estadisticamente comparable con permutation-NSGA-II. Esto refuerza la tesis metodologica: cuando los operadores estan acoplados a la representacion, otra familia evolutiva cae en el top tier.

Artefacto: `backend/app/data/results/perm_spea2.json`.

Nota editorial: no se reestructuro la tabla principal para meter SPEA2 como octavo metodo, porque eso arriesga paginas y requiere rehacer figuras. El baseline queda como evidencia suplementaria fuerte.

## Cambios en el manuscrito

Archivos actualizados:

- `MICAI/main_submission.tex`
- `MICAI/main.tex`
- `MICAI/main_reducida_submission.tex`
- `MICAI/main_reducida.tex`

Cambios:

- "real case" -> "calibrated case study".
- "policy dysfunctional" -> "creates measurable inefficiencies in our calibrated instance".
- Aclarado que `P_c=25,620` es un techo cross-preference derivado del limite combinado family-sponsored + employment-based, usado como cap EB-side exogeno en este modelo de un periodo.
- Agregada limitacion/future work: simulacion legal completa cross-preference/spillover.
- Agregada auditoria de equidad alternativa en el texto.
- Data/code availability ahora menciona el fast verifier del suplemento.
- Se removio SPEA2 de future work en las conclusiones porque ya se implemento como baseline suplementario.
- La conclusion se partio en dos parrafos en los 4 `.tex`: primero mecanismo/tesis, luego policy/decision-support/future work. No cambia ningun numero ni claim; reduce densidad de lectura.

PDFs recompilados:

- `MICAI/main_submission.pdf` -> 27 pp.
- `MICAI/main_reducida_submission.pdf` -> 18 pp.

Recomendacion de envio: usar `main_reducida_submission.pdf` por el limite MICAI de 20 paginas sin contactar organizadores.

## ZIPs

Actualizados:

- `MICAI/VisaPredictAI_MICAI_anonymous.zip`
- `MICAI/VisaPredictAI_MICAI_reducida_anonymous.zip`
- `MICAI/VisaPredictAI_MICAI_Overleaf.zip`
- `MICAI/VisaPredictAI_MICAI_reducida.zip`

Escaneo anonimo:

```text
anonymous_zip_hits: 0
```

Nota: durante la actualizacion se creo tambien `MICAI/VisaPredictAI_MICAI.zip` con `main.tex`; no es el paquete historico principal (`VisaPredictAI_MICAI_Overleaf.zip`) y puede ignorarse si se prefiere usar solo los ZIPs ya existentes.

## Comandos ejecutados

```bash
backend/.venv/bin/python backend/repro/equity_audit.py
cd backend && .venv/bin/python perm_spea2.py
backend/.venv/bin/python backend/repro/reproduce_fast.py
cd MICAI && pdflatex -interaction=nonstopmode main_submission.tex
cd MICAI && pdflatex -interaction=nonstopmode main_reducida_submission.tex
```

## Estado final verificado

- Unit tests: pasan.
- Firewall: pasa, incluyendo los nuevos claims de equidad.
- PDFs: compilan.
- Logs LaTeX: sin `Undefined`, sin referencias/citas indefinidas, sin `Overfull`.
- ZIPs anonimos: sin tokens de identidad detectados por el verificador.
