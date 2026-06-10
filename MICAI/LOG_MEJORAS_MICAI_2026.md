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

## Auditoria de figuras/tablas

Chequeos (dimension LNCS): archivos de figura existen (14 en figures/, via \graphicspath), labels<->refs resuelven sin huerfanos ni duplicados, captions correctos (tablas arriba, figuras abajo), floats [t] (ningun [h]), orden de mencion.

Unico hallazgo, solo en la full: la Tabla del ladder (tab:ladder) se citaba antes que la del factorial (tab:factorial) pero su entorno estaba definido despues -> Tabla 5 citada antes que Tabla 4 (no ascendente). La reducida de envio ya estaba conforme.

Fix: se movio el bloque \begin{table} de tab:ladder a antes del de tab:factorial en main.tex y main_submission.tex, renumerando ladder->Tabla 4 y factorial->Tabla 5 (ascendente segun cita). Sin cambio de paginas (28/27), 0 undefined refs/cites, 0 Overfull; firewall 0/72; reproduce_fast overall_ok=true, anonymous_zip_hits=0. La reducida no se toco.

## Pase mayor 2026-06-10: auditoría ciega multi-eje + mejora considerable

Auditoría: panel de 3 revisores MICAI simulados (ciegos, sobre la reducida de envío)
+ 4 auditores técnicos (semántica, referencias, gramática, tablas/figuras) + re-derivación
ciega de ~200 cifras + anonimato/versiones. Nota "antes": 6.0/6.0/6.5 (~6.2 consolidada).
Triage completo en `output/AUDITORIA_2026-06-10_triage.md`.

### Experimentos nuevos

- **Test predictivo BRKGA** (`backend/brkga_nsga.py`, `brkga_full.py`): rk-NSGA-II con
  crossover uniforme sesgado (τ=0.63) + reset mutation, 30 seeds; y BRKGA canónico
  (elites 20%, mutants 15%). Ambos EMPATAN con random restart (309,970 / 309,928 vs
  310,214; p=0.79). La regla de 2 condiciones se refina: **necesarias pero no
  suficientes**, con gradiente monótono en τ (0.99→293k, 0.92→305k, 0.63→310k,
  ≈0→315.7k) que cruza el nivel de blind sampling en τ≈0.6. Artefactos:
  `brkga_ladder.json`, `brkga_full.json`.
- **Headroom sweep n=5→15** (`backend/headroom_sweep_n15.py`): el "inconclusive"
  (ρ=-0.90, p=0.083) se convierte en refutación con potencia: ρ=-0.775,
  p-permutación=0.0012 — el escalar se mueve OPUESTO a la hipótesis. Artefacto:
  `headroom_sweep_n15.json`.
- **τ por estructura** (`backend/tau_structures.py`): la frase "re-confirmed τ on each
  problem's keys" ahora es trazable (SBX≈0.992, HHO≈-0.12 en d=105/120/100/50).
- **Per-seed del competent en knapsack** (`repro/structures_competent.py` re-corrido con
  persistencia): habilita el 7.º violín de ladder2. Mismos ranks (1.13 knapsack).

### Cambios al manuscrito (4 .tex sincronizados)

- Críticos corregidos: regla "iff" universal re-acotada a selection landscapes y
  graduada (abstract/conclusiones); autocontradicción "never the single best";
  IGD invertido en la reducida (NSGA-II gana IGD 0.0071 vs 0.0212) + cifras stale
  (3.1%→3.2%, 1.3e-5→1.8e-6, 0.82→0.85, 9/30→10/30, iter 138→135); caption de
  fig:gen con ranking invertido; atribución "Çerçi and Dönmez"→Wang et al.
- Ladder ampliado a 9 métodos: + perm-SPEA2 (317,135±3,814, empate con perm-NSGA-II)
  y + rk-NSGA-II biased uniform (test predictivo).
- Reposicionamiento: la regla es ahora un **protocolo diagnóstico a priori** (3 pasos,
  medición barata de τ + chequeo de selección + clasificación de paisaje) en Discussion.
- Literatura añadida: Rothlauf (locality), Raidl & Gottlieb (decoder EAs, knapsack),
  Sörensen (metaphor exposed), Gonçalves & Resende (BRKGA), SPEA2. Bibliografía 25→30.
- Honestidad estadística: p≤0.071 ya no se vende como "outperforms"; η² con criterio
  consistente; "law"→"regularity"; "0.11 of the true front"→0.20 (error de unidades);
  MOEA/D totalmente especificado; IGD declarado como indicador interno del par.
- kusoglu re-alfabetizado (Yüzgeç primer autor, verificado) + URL; visa bulletin
  deep-link a febrero 2026; S/N 109.78→109.77; "dominant factor (T)"→N.

### Figuras (11 regeneradas, fonttype 42 — 0 Type 3)

ladder 9 violines; ladder2 7 violines (competent mejor en knapsack); convergence sin
labels duplicados ni `\,` literal; overlay con marcadores distinguibles en B&W; pareto
3D/2D con viridis truncado + bordes; generalization sin barras recortadas y anotada;
taguchi con estrella; mechanism_2x2 sin título incrustado, labels del paper y HV anotado.

### Entregables y verificación

- ZIPs anónimos renombrados sin marca: `submission_anonymous_full.zip`,
  `submission_anonymous_reducida.zip` (los `VisaPredictAI_*_anonymous.zip` eliminados —
  el nombre de archivo filtraba identidad). No-anónimos: Overleaf y reducida rebuilt.
- Firewall 72→**97 claims, n_mismatch=0**. `reproduce_fast` overall_ok=true
  (pytest 0, firewall 0, anonymous_zip_hits 0).
- **Invariante de páginas nuevo: 30 / 29 / 20 / 19** (main / submission / reducida /
  reducida_submission), A4, 0 undefined, 0 overfull. El envío sigue siendo la
  reducida_submission (19 pp ≤ 20). Abstract 241 palabras (≤250).
- 4 `Feasibility-Preserving_MOHHO_MICAI*.pdf` refrescados.

### Pendiente de verificación manual

- Confirmar en navegador que `https://anonymous.4open.science/r/decoder-moo-reproducibility/`
  resuelve (Cloudflare bloquea la verificación CLI) y que el snapshot 4open refleja el
  código nuevo (brkga, headroom n15, tau_structures).

### Re-panel "después" y micro-pase final (mismo día)

Re-panel ciego sobre la reducida mejorada: R1 6.0 (borderline), R2 6.5 (weak accept),
R3 6.5 (weak accept) — consolidado ~6.3 vs ~6.2 "antes". Lectura honesta: la nota
numérica casi no se mueve (los revisores simulados siempre encuentran la siguiente
objeción), pero TODOS los críticos de la ronda 1 desaparecieron; las objeciones nuevas
son de segundo orden salvo una unánime y repetida en ambas rondas: **el título
"Tuned NSGA-II" se lee como strawman** (el "tuned" viene del Taguchi de N/T compartidos,
no de un tuning propio de NSGA-II, y el propio campeón del paper ES un NSGA-II).
Cambiar el título es decisión del autor — pendiente.

Micro-pase aplicado tras el re-panel: "replicate"→"directionally consistent" en
conclusiones (p≤0.071 no soporta "replicate"); caveat de heterogeneidad del gradiente
de τ (4 operadores distintos, no una perilla continua); "Discrete-MOHHO we introduce"
reposicionado como mechanism check (existen HHO discretos mono-objetivo); literatura
del dominio añadida (Bansak et al., Science 2018, bib 30→31); future work con
validación prospectiva registrada. Reducidas re-condensadas (prueba compacta,
adaptación MO de HHO compacta) para sostener el invariante.

**Invariante final: 30 / 30 / 19 / 19**, A4, 0 undefined, 0 overfull, abstract 241
palabras, firewall 97/97, reproduce_fast overall_ok, anonymous_zip_hits 0.

## Salto final 2026-06-10 (parte 2): re-título + validación prospectiva registrada

### Título nuevo (decisión del autor, siguiendo al panel unánime)

`A Two-Condition Diagnostic for Decoder-Based Multi-Objective Search: When Blind
Sampling Beats a Mismatched NSGA-II` — la tesis primero, el gancho después, y
"Mismatched" en lugar de "Tuned" (que era inexacto: el Taguchi afinó N/T compartidos,
no a NSGA-II). El cuerpo se limpió en consecuencia ("tuned"→"standard"/"mismatched"
donde refería a NSGA-II; los usos legítimos de Taguchi quedan).

### Validación prospectiva REGISTRADA en un 5.º problema (mo-SCP)

Registro de 4 predicciones commiteado ANTES de correr (211f9c1 precede al commit de
resultados — esa es la evidencia de prospectividad). Problema: set covering
tri-objetivo (150 elementos, 120 conjuntos, 3 vectores de costo), etiquetado
"selection landscape" por su estructura de subconjuntos.

Veredicto (30 seeds × 5 métodos, mismo presupuesto):
- **P3 y P4 SOSTENIDAS** (las que dependen solo de las 2 condiciones): perm-NSGA-II
  0.357 y competent 0.386 vs random 0.259, p=9.3e-10, A12=1.0 ambas.
- **P1 y P2 FALSIFICADAS** (las que dependían de la etiqueta de paisaje): SBX-NSGA-II
  +10% SOBRE random (p=1.3e-8) y rk-biased es EL MEJOR método (0.415, +60%, encima
  incluso de perm-NSGA-II p=9.3e-10).

Lectura integrada al paper (tal cual salió, sin maquillar): el núcleo de 2 condiciones
predice prospectivamente (el mejor método en las 5 estructuras cumple ambas; los
métodos de renovación de orden vencen a blind sampling en las 5); la etiqueta
superficie subset/sequencing NO predice (mo-SCP no satura presupuesto compartido →
se comporta como sequencing; el gradiente monótono en τ es además instance-specific).
El paso 3 del protocolo se reescribió como "baseline check" (medir la fuerza de blind
sampling, no clasificar por estructura) y el determinante operativo queda como
hipótesis registrada: saturación de presupuesto del decoder (consistente con la
anticorrelación del headroom).

### Estado verificado

- Invariante: **31 / 31 / 20 / 20** pp (la reducida queda EXACTAMENTE en el límite
  MICAI de 20 sin contactar organizadores), A4, 0 undefined, 0 overfull.
- Abstract 247 palabras. Firewall **109/109 n_mismatch=0** (+12 claims prospectivos).
- reproduce_fast overall_ok=true, anonymous_zip_hits=0. 4 ZIPs + 4 Feasibility-*.pdf
  refrescados.
- 4open verificado por el autor en navegador. ⚠️ Subir al snapshot el código nuevo:
  prospective_scp.py (+ registración y resultados JSON) además de brkga/headroom/tau.

## Ronda 3 del panel ciego + endurecimiento estadístico (2026-06-10, cierre)

Panel sobre la versión definitiva (título nuevo + test prospectivo): R1 6.0, R2 6.5,
R3 6.5 (~6.3). Las peticiones grandes restantes son de escala proyecto (tuning
per-método con irace, índice de saturación computable, ablación de E en
Discrete-MOHHO) — documentadas aquí como material de rebuttal, no ejecutadas.

Fixes integrados de la ronda 3 (stats_round3.json, +9 claims al firewall):
- **Omnibus sobre los 9 métodos** (antes 6, exclusión que R2 llamó selectiva):
  Friedman χ²=133.8, p=4.6e-25, CD=2.19; ranks: perm-NSGA-II 2.97 > competent 3.10 >
  SPEA2 3.53 > Discrete 3.93 > MOEA/D 4.33 > rk-biased 4.57 (dentro del CD de
  random 6.47) > naive MOHHO 7.33 > NSGA-II rc 8.77 — el orden que la cuenta de
  2 condiciones predice.
- **Wilcoxon pareado** para la comparación cabecera (seeds comunes): MOHHO vs
  NSGA-II p=4.4e-6 dos colas (reemplaza al Mann–Whitney no pareado unilateral).
- **Holm sobre la familia de 12 tests cabecera: TODOS sobreviven** (mayor p
  superviviente 5.7e-4).
- **Sign test exacto** para las 5 instancias perturbadas direccionalmente
  consistentes: p=2⁻⁵=0.031 (la "robustez" deja de ser anecdótica).
- Honestidad: "monotonically" condicionado a la instancia líder (mo-SCP lo
  invierte); asimetría del test prospectivo declarada (la mitad confirmada tenía
  menor riesgo de falsación); ρ=−0.78 marcado descriptivo (niveles anidados).
- Citas nuevas (bib 31→35): Aranha et al. 2022 (metaphor call-for-action),
  Tasgetiren et al. 2007 (nombre SPV), Gezici & Livatyali 2022 (HHO discreto,
  faltaba la cita), Malan & Engelbrecht 2013 (posicionamiento vs fitness-landscape
  analysis). Todas verificadas vía Crossref.
- Reducida: figura Taguchi removida (tabla y prosa intactas; R1 la llamó vestigial
  en ambas rondas) para compensar páginas.

**Estado final: 31/31/20/20 pp** A4, 0 undefined/overfull, abstract 249 palabras,
firewall **118/118**, reproduce_fast ok, anonymous_zip_hits 0, 4 ZIPs + 4
Feasibility-*.pdf refrescados.

## Auditoría total de la versión definitiva (2026-06-10, cierre final)

5 auditores en paralelo (números/figuras-tablas/referencias/idioma/semántica) sobre la
versión con título nuevo + prospectivo + ronda 3.

- **Números: LIMPIO** — ~270 cifras (118 firewall + ~155 re-derivadas) reproducibles
  desde los artefactos, 0 mismatches duros, full↔reducida numéricamente idénticas.
  3 observaciones de redacción corregidas: "not individually significant"→"significant
  on only two of the five" (instancias 1 y 3 SÍ son significativas, p=0.0023/0.0018);
  márgenes de decoders etiquetados (4.3% stochastic-skip, 1.4% fractional — el orden
  paralelo estaba traspuesto); 0.039→0.038 dB.
- **Referencias**: bansak tenía 7 autores listados → 6 + et al. (regla LNCS); errata
  "problems" tras \cite{gezici}; los 35 items en orden alfabético correcto, DOIs de
  los 10 nuevos verificados contra Crossref/DataCite, 0 huérfanos en ambas versiones.
- **Figuras/tablas**: 3 menores corregidos (forward-cite de tab:nsga en §4.4, caption
  ladder2 "real-coded methods"→"GA", negritas de empates en tab:nsga). 9 violines =
  9 filas verificado visualmente; 0 Type 3; 0 refs rotas tras quitar la fig Taguchi
  de la reducida.
- **Idioma**: 1 mayor (sujeto equivocado en conclusiones: el que empata es el método,
  no el test) + 12 menores aplicados (comma splice y antecedente del abstract,
  set-covering con guion, paralelismos, "profits"→"benefits", terminología η_c).
- **Semántica**: 1 crítico corregido — el párrafo prospectivo decía "the protocol's
  step 3 labels..." cuando el Step 3 reescrito ya NO clasifica por estructura
  (ahora: "as originally formulated" + puntero a la reformulación); mayores: la
  contribución (v) aún decía "only on selection landscapes" (→ budget saturation) y
  no mencionaba el test prospectivo (añadido); "three matched paradigms" stale (son
  4; el factorial usa 3 arquitecturas, ahora nombradas); claim de necesidad acotado
  "(within the critical difference)" — el naive MOHHO en knapsack queda nominalmente
  arriba de random (3.93 vs 5.23) pero dentro del CD; "entire six-method ladder" →
  "six-method core"; matiz 4/5 reference points restaurado en la reducida.

**Estado final: 31/31/20/20 pp**, A4, 0 undefined/overfull, abstract 245 palabras,
firewall **118/118**, reproduce_fast ok, anonymous_zip_hits 0, ZIPs + Feasibility
refrescados.

## Barrido ρ_e registrado: dosis-respuesta limpio (2026-06-10, "subir el nivel")

La palanca #1 de la ronda 3 (R2): un solo operador con perilla continua de disrupción
(ρ_e del biased uniform crossover, 11 niveles, τ∈[0.42,1.0]), selección NDS fija,
**las 5 estructuras × 30 seeds** (~1,650 corridas, 2.6 h), HV + IGD⁺ per-run contra
el pool del propio barrido. Predicciones registradas y PUSHEADAS antes de correr
(commit 4b9bf2f).

Veredicto (rho_sweep.json, +13 claims al firewall → **131/131**):
- **R1 (visa/knapsack: monotonía + cruce) FALSIFICADA**: el HV es PLANO en τ en las
  5 estructuras (Spearman 0.15–0.48, ninguno significativo; visa oscila 98–100% de
  random sin tendencia; flowshop clavado en 103.2%). **El "gradiente monótono" de 4
  puntos era un contraste de FAMILIAS, no una dosis-respuesta — τ es bandera, no
  perilla.** Exactamente lo que R2 sospechaba, demostrado por nuestro propio test.
- **R2 (TSP/flowshop/SCP encima de random en todos los niveles) SOSTENIDA 3/3.**
- **R3 (IGD⁺ concuerda con HV) FALSIFICADA-como-formulada, informativamente**: el
  IGD⁺ SÍ degrada con τ→1 en visa/knapsack/TSP (ρ=0.80/0.96/1.00) mientras el HV no
  ve nada — el efecto dosis residual existe pero solo es visible a una métrica de
  cobertura, invisible al HV f₂-dominado.
- **Hallazgo bonus**: en los DOS problemas de subconjuntos la familia biased-uniform
  supera al MEJOR método del ladder en todos los niveles (knapsack ~0.31 vs 0.27 del
  competent) — la hipótesis de saturación de presupuesto acota dónde colapsa SBX,
  no lo que logra una familia bien acoplada.

Integración: párrafo del gradiente reescrito en las 4 versiones (el "cruce en τ≈0.6"
eliminado — no existe como curva); figura nueva fig:rho (2 paneles, solo full);
abstract y conclusiones ahora dicen "registered prospective tests" (plural) y "el
tipo de renovación, no la cantidad de disrupción, lleva el efecto"; protocolo: "τ es
bandera, no perilla". Abstract 247 palabras.

**Invariante: 32/32/20/20 pp**, A4, 0 undefined/overfull, firewall 131/131,
reproduce_fast ok, ZIPs + Feasibility refrescados.

## Ronda 4 del panel ciego (2026-06-10, sobre la versión con los 3 tests registrados)

R1 6.0 / R2 6.5 / R3 6.5 — **meseta en ~6.3 por cuarta ronda consecutiva** (el panel
adversarial encuentra la siguiente objeción más profunda en cada ronda). Elogios
consistentes: "protocolo de los más disciplinados que he visto", "fairness de verdad,
no retórica", "eso es ciencia", "práctica ejemplar" (tests registrados con fallos
reportados).

Objeciones nuevas (material de rebuttal / mejoras futuras):
- R2: sign test n=5 es "significativo por construcción" (presentar §6.5 como
  descriptivo); "flat in τ" = aceptar H0 sin TOST/IC de pendiente; los claims
  cabecera deberían sobrevivir per-run bajo IGD⁺/ε para los 9 métodos; familia de
  Holm autoseleccionada; el "registro" es commit propio, no prerregistro externo.
- R3: falta literatura GRASP/semi-greedy (el random restart a través de decoder
  greedy saturante ES una construcción semi-aleatoria multistart) y la mitad de
  *heuristic bias* de Raidl & Gottlieb; "six hard constraints" infladas (R4-R6
  triviales por construcción); naive-MOHHO dominance-gated no corresponde a
  ninguna variante publicada; falta baseline con búsqueda local.
- R1: re-titular alrededor del estudio de falsación; degradar visa a testbed
  en todo el texto.

## Paquete A: blindaje final post-ronda-4 (2026-06-10)

Las tres palancas ejecutables de la ronda 4, ejecutadas:

1. **Re-scoring per-run reference-free de los 9 métodos** (`backend/ladder_igd.py` →
   `ladder_igd.json`; los 3 métodos sin frentes persistidos se re-corrieron con sanity
   check de HV contra los valores canónicos — 0 mismatches): contra el frente común
   |Z₉|=187, **el ladder sobrevive fuera del HV**: correlaciones de ranks HV↔IGD⁺=0.82
   y HV↔ε=0.85 (Friedman χ²=176.5/169.3); los 4 métodos de ambas-condiciones ocupan el
   top-4 bajo los TRES indicadores (SPEA2 el mejor bajo ambos reference-free); los 2
   real-coded degenerados al fondo; única dislocación: perm-MOEA/D (rank 7.2 bajo IGD⁺,
   cobertura pobre del frente combinado). Era "el cambio único" de R2 (→7.5-8).
2. **"Flat in τ" acotado** (`backend/rho_slope_ci.py` → `rho_slope_ci.json`): bootstrap
   CI 95% de la pendiente — |efecto dosis| ≤ ~1 punto porcentual de blind sampling por
   0.1τ en las 5 estructuras (visa [−0.15,+0.21]). El H₀-aceptado se volvió cota.
3. **Control GRASP semi-greedy** (`backend/grasp_control.py` → `grasp_control.json`):
   RCL sobre w_g, α~U(0,1) por construcción, mismo presupuesto/archivo. Resultado:
   **298,531 = −3.8% BAJO random uniforme** (p=1.9e-9) — la fuerza del blind sampling
   no es greediness a nivel de orden: el heuristic bias del decoder (Raidl & Gottlieb,
   mitad que faltaba citar) beneficia a toda construcción, y sesgar el orden hacia un
   objetivo cuesta diversidad de frente. Ancla el resultado en la literatura GRASP
   (Feo & Resende, bib 36→37... 36) en vez de dejarlo como sorpresa.

Matices honestos: §6.5 reformulado como robustez DESCRIPTIVA (el sign test n=5 se
retiró del texto — R2 tenía razón: "significativo por construcción"); "six constraints"
aclarado (3 budgets vinculantes; R4-R6 automáticas por construcción); procedencia del
naive-MOHHO declarada (greedy del HHO mono-objetivo elevado a dominancia; las variantes
publicadas no especifican ese gate — caracteriza la elección de diseño, no a aquellas).

Para caber: la reducida soltó el par de figuras Pareto 3D/2D (la dominación de FIFO
queda numérica en tab:extremes; el ladder — la tesis — se conserva; la full mantiene
todo). **Invariante: 33/33/20/20 pp**, abstract 248, firewall **143/143**,
reproduce_fast ok, 0 overfull/undefined.
