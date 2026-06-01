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

- `MICAI/main_submission.pdf` -> 27 pp (en este punto; luego el pase de titulo lo lleva a 28 pp).
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

## Pase editorial final: titulo y narrativa MOHHO

Motivo: reducir el riesgo de que un revisor lea el titulo como clickbait y corregir la tension narrativa donde Discrete-MOHHO parecia venderse como heroe principal aunque permutation-NSGA-II es el metodo marginalmente mas fuerte.

Archivos actualizados:

- `MICAI/main_submission.tex`
- `MICAI/main.tex`
- `MICAI/main_reducida_submission.tex`
- `MICAI/main_reducida.tex`

Cambios:

- Titulo cambiado de una formulacion centrada en el gancho "blind sampling beats tuned NSGA-II" a:
  `A Two-Condition Diagnostic for Decoder-Based Multi-Objective Search: When Blind Sampling Beats Tuned NSGA-II`.
- Running title cambiado a:
  `Two-Condition Diagnostic for Decoder-Based Search`.
- Discrete-MOHHO se reencuadro como mecanismo de validacion: demuestra que una arquitectura swarm entra al top tier cuando la representacion y los operadores estan acoplados.
- permutation-NSGA-II queda explicitamente reconocido como el metodo marginalmente mas fuerte y estable dentro de los metodos matched.
- En el factorial operador-arquitectura, Discrete-MOHHO se mantiene como evidencia de robustez por operadores, no como claim de superioridad global.

Efecto esperado para revision: el paper vende primero la contribucion metodologica general (diagnostico de dos condiciones) y deja el gancho NSGA-II como subtitulo/resultado, reduciendo riesgo de rechazo por sobreventa.

Efecto en paginas: el titulo mas largo empujo `main_submission.pdf` de 27 a 28 pp. Ningun numero ni claim cambio (firewall 0/72, inventario .tex 0 tokens).

Invariante de paginas actualizado: **28 / 28 / 18 / 18** (main / main_submission / main_reducida / main_reducida_submission), A4 real (595.276x841.89 pt), 0 undefined, 0 overfull, 0 citas/refs indefinidas. El envio a MICAI sigue siendo la reducida (18 pp), bajo el limite de 20; la full anonima (28 pp) ya excede ese limite y no es enviable tal cual. Los 4 `Feasibility-*.pdf` se refrescaron a 28/28/18/18. (Luego los ORCID camera-ready llevan `main_reducida` a 19 pp; ver seccion final.)

## ORCID camera-ready y repo de reproducibilidad anonimo

Repo de reproducibilidad curado y saneado (codigo + datos, 0 identidad), subido a un repo privado de GitHub y anonimizado en:
`https://anonymous.4open.science/r/decoder-moo-reproducibility/`

Cambios en los `.tex`:
- Versiones de ENVIO (`main_submission`, `main_reducida_submission`): en "Data and Code Availability" se cambio "(repository withheld for double-blind review)" por el enlace anonimo de 4open. Siguen sin ORCID ni nombres.
- Versiones NO anonimas / camera-ready (`main`, `main_reducida`): se agregaron los ORCID al bloque de autores via `\orcidID{}`:
  - Javier Augusto Rebull Saucedo — 0009-0008-2089-5274
  - Yazmin Ivonne Flores Martinez — 0009-0002-6848-1608
  - Raul Gibran Porras Alaniz — 0000-0002-6772-5351

Efecto en paginas: los superindices ORCID hacen wrap en el bloque de autores y llevan `main_reducida` (no-anon) de 18 a 19 pp. El ENVIO (`main_reducida_submission`) sigue en 18 pp. **Invariante: 28 / 28 / 19 / 18.**

Gate de anonimato (verificado): las versiones de envio tienen 0 ORCID/nombres y sostienen la URL anonima; firewall 0/72; `reproduce_fast` overall_ok=true con anonymous_zip_hits=0 tras regenerar los 4 ZIP. Feasibility-*.pdf refrescados a 28/28/19/18.

## Titulo final y recorte de bibliografia

- Titulo cambiado a "When Blind Sampling Beats Tuned NSGA-II: A Two-Condition Diagnostic with a Calibrated Visa Allocation Case Study" (recupera el caso, que el titulo anterior puramente metodologico habia perdido). Saltos con `\texorpdfstring{\\}{ }`.
- Para devolver `main_reducida` (camera-ready) de 19 a 18 pp: se opto por NO tocar la bibliografia (se conservan todas las URLs y DOIs) y en su lugar se quito la frase de recap de robustez de la **conclusion** de ambas reducidas (three-axis: non-saturating decoders / reference-point sweeps / MILP). Ese analisis sigue completo en el cuerpo (Results/Generalization), asi que no se pierde ningun claim. La full conserva la frase.

**Invariante restaurado: 28 / 28 / 18 / 18.** A4, 0 undefined/overfull, Token-not-allowed 0; firewall 0/72; `reproduce_fast` overall_ok=true, anonymous_zip_hits=0. Feasibility-*.pdf y los 4 ZIP refrescados.

## Auditoria de gramatica

Pase de gramatica/puntuacion/ingles americano (respetando convenciones LNCS: em-dashes en incisos, en-dashes en rangos, coma de Oxford). La prosa estaba muy limpia; se corrigieron solo dos cosas reales en los 4 .tex:
- Caption del ladder: oracion que arrancaba en minuscula tras punto, "permutation-NSGA-II" -> "Permutation-NSGA-II".
- Frase duplicada verbatim en la seccion del ladder (artefacto del reencuadre de Discrete-MOHHO): "Discrete-MOHHO is therefore not the overall champion but a mechanism check...". Aparecia 2 veces; se quito la segunda (parrafo "empirical regularity"), conservando la primera. No se pierde ningun claim.

Efecto: `main_submission` baja 28->27 pp (la frase estaba cerca de un borde). Invariante: **28 / 27 / 18 / 18**. A4, 0 undefined/overfull, Token-not-allowed 0; firewall 0/72; reproduce_fast overall_ok=true, anonymous_zip_hits=0.
