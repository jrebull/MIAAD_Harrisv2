# Auditoría ciega multi-eje — 2026-06-10 (triage)

Base: commit 36e97b0, 4 versiones 28/27/18/18 pp, firewall 0/72.
Panel ciego sobre `main_reducida_submission.tex` (lo que se envía). 8 auditores en paralelo:
3 revisores MICAI simulados + semántica + referencias + gramática + tablas/figuras + números + anonimato.

## Nota "antes" (panel ciego, calificando duro)

| Revisor | Nota | Recomendación |
|---|---|---|
| R1 pro-novedad | 6.0 | borderline |
| R2 estadístico | 6.0 | borderline → weak accept con revisión mayor del framing |
| R3 metaheurísticas | 6.5 | weak accept condicionado |
| **Consolidada** | **~6.2** | borderline/weak accept — por debajo del ~7.0 estimado |

Convergencia de los 3: (1) el "diagnóstico" no es ejecutable a priori; (2) falta BRKGA
como baseline (citado 2×, nunca corrido); (3) la regla "iff" universalizada en el
abstract está refutada por la propia Tabla de estructuras en paisajes de secuenciación.

## CRÍTICOS (todos se corrigen)

| # | Hallazgo | Fuente | Fix |
|---|---|---|---|
| C1 | Abstract/conclusiones universalizan la regla de 2 condiciones; Tabla de estructuras refuta el "only if" en TSP/flow-shop (τ=0.99 vence a random) | R2-D1, T1-2/3/17 | Re-scope: regla condicionada a selection landscapes + refinamiento dosis-respuesta (BRKGA) |
| C2 | Autocontradicción "never the single best … the single best optimizer there" (knapsack); la reducida perdió el calificador "naive" y se autocontradice | T1-1/5, T3-6 | Reescribir la oración; restaurar calificador en reducida |
| C3 | Reducida: claim de IGD **invertido** (NSGA-II gana IGD 0.0071 vs 0.0212) + cifras stale (3.1%/1.3e-5/0.82 → canónico 3.2%/1.8e-6/0.85) | T1-4/6, T3-1, N1 | Corregir a valores canónicos verificados |
| C4 | Caption fig:gen afirma ranking invertido ("MOHHO > random restart"); los datos dicen random ≥ MOHHO en 5/5; y menciona FIFO que no está en la figura | T1-9, T4-1, N1-1 | Reescribir caption |
| C5 | Texto full atribuye `cerci` a "Çerçi and Dönmez"; el bibitem es Wang et al. (2022) | T2-1 | ✅ APLICADO (→ Wang et al.) |

## MAYORES (selección, todos programados)

- M1 10/30 vs 9/30 seeds (full correcta) · M2 iter 135 vs 138 (135 canónico) · M3 "dominant factor (T)" → N es dominante
- M4 "All conclusions hold across five perturbed instances" excede lo corrido (solo FIFO/MOHHO/NSGA-II/random) → acotar
- M5 "outperforms … p≤0.071" vendido como confirmación (R1, R2, T1) → redacción honesta
- M6/M7 "law" vs "not a law"; doble sentido de "representation–operator match"; tesis intro vs abstract → unificar en regla de 2 condiciones acotada
- M8 kusoglu: orden de autores invertido (Yüzgeç 1.º, verificado contra la revista) ✅ APLICADO (+URL, re-alfabetizado); deep-link visa bulletin ✅
- M9 figuras ladder/ladder2 muestran 6 métodos; la tesis vigente es de 7 (+ nuevos) → regenerar
- M10–M14 figuras: convergence (labels duplicados, `\,` literal), mechanism_2x2 (caption≠figura, labels de código, título incrustado), nsga2_overlay (indistinguible en B&W), pareto3d/2d (amarillo viridis invisible en B&W, fuentes ~5pt), generalization (barras recortadas) → regenerar con fonttype 42 (Type 3 → TrueType, M-global)
- M15 ZIPs anónimos con "VisaPredictAI" en el nombre de archivo → renombrar
- M16 "0.11 of the true front" es HV absoluto, la fracción es 0.20 → corregir
- M17 Literatura faltante: Rothlauf (representations), Raidl & Gottlieb (locality/heritability en decoder-EAs para knapsack), Sörensen (metaphor exposed) — el paper la redescubre sin citarla → añadir y reposicionar
- M18 MOEA/D infraespecificado (T vecindad, δ, n_r, #pesos) → reportar desde código
- M19 Frente de referencia Z del IGD solo con 2 métodos → aclarar que IGD es solo para ese par (el ladder usa HV)
- M20 Doble estándar η² (5.5–13.4% "second-order" vs 9.8% "synergistic") → criterio consistente
- M21 Taguchi: "dominant factor" + claim (iii) a medias → reframe del propósito (punto de operación común a todo el ladder, evita confound de tuning) y suavizar
- M22 "re-confirmed τ on each problem's keys" sin artefacto → generar JSON con τ por estructura

## Experimentos nuevos (resultados)

1. **BRKGA (2 configuraciones, 30 seeds, mismo presupuesto)**: biased uniform crossover
   τ=0.631 + NDS → **empata con random restart** (309,970 y 309,928 vs 310,214; p=0.79);
   +5.7% sobre real-coded; −2.6% bajo el tier de permutación. Con los puntos existentes
   (τ=0.99→293k, 0.92→~305k, 0.63→310k, ~0→316–318k) la regla se refina:
   **las 2 condiciones son necesarias pero NO suficientes; dosis-respuesta en τ;
   superar al muestreo ciego exigió renovación casi total del orden (τ≈0)**.
   Responde la pregunta de rebuttal #1 de R1/R3 y el umbral operacional de R2.
2. **Headroom sweep n=5→15** (corriendo): convierte el "ρ=−0.90, p=0.083, inconclusive"
   en resultado con potencia o null honesto.
3. **perm-SPEA2** (ya corrido 1-jun): entra al ladder como 4.ª familia matched.

## Plan de mejora (Fase 3, en orden)

1. Fixes C1–C4 + mayores de texto en los 4 .tex (cuerpos sincronizados).
2. Reposicionamiento: regla → protocolo diagnóstico accionable con umbrales empíricos de τ.
3. Integración BRKGA (tabla ladder + párrafo de test predictivo) + SPEA2 + headroom n=15.
4. Literatura (Rothlauf, Raidl & Gottlieb, Sörensen) + MOEA/D params + abstract/contribuciones reescritos.
5. Regenerar las 11 figuras (fonttype 42, B&W-safe, 7+ métodos en ladder).
6. Firewall: claims nuevos; gate de páginas (reducida ≤19); panel "después"; ZIPs+PDFs; commits.
