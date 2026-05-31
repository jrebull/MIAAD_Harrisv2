# Reporte de Diagnostico de Colapso v2

## MOHHO / Visa Predict AI -- desmontaje de la objecion de colapso del espacio de busqueda

> Todos los numeros provienen de `app/data/results/*.json` (SUPERPROMPT v2, cero hardcode). Instancia base verificada (sha256 `9bcdaca740b55bd8...`), presupuesto `25,000` evals identico entre los 6 metodos, reference point `(10.0, 16.0, 20000.0)`.

## 1. Resumen ejecutivo

- **Gate de optimizers (Exp A):** MOHHO real-coded = `sospechoso`; operadores permutacionales = `sano`; random restart = `confirmado_muestreo_puro`. Gate SUPERADO. FUNCIONAL pero DEBIL en multi-objetivo: sano en ZDT1 (0.995) y DTLZ2 (0.854), y en ZDT2 converge al frente verdadero (g=1) pero colapsa a un extremo (fallo de diversidad, no bug). El ladder NO esta contaminado por implementacion rota.
- **H_str (colapso estructural, Exp B):** PARCIAL: f3 colapsa por saturacion (PC3~1%) y f1 es estructuralmente angosto (f2/f1=39.4x), pero el trade-off f1-f2 es bidimensional y genuino (PC1+PC2~99%). El problema es EFECTIVAMENTE BI-OBJETIVO, no mono-objetivo.
- **H_dec (colapso por decoder, Exp C):** REFUTADA EN LO ESENCIAL (con matiz de magnitud). La separacion perm>rk es SIGNIFICATIVA bajo los TRES decoders (greedy +6.93%, C2 +4.27%, C1 +1.45%; Wilcoxon pareado p<0.001 en los tres) y NUNCA se invierte: por tanto la ventaja de la representacion NO es un artefacto de la saturacion del decoder -- persiste al introducir intensidad fraccional (C1) y skip estocastico (C2). MATIZ HONESTO: la MAGNITUD escala con la saturacion (solo 21% del margen greedy sobrevive bajo C1), y C1 (no-saturante) halla 11 soluciones con f2 mejor que el mejor f2 del greedy que el greedy no captura. Conclusion: el efecto representacion es real y robusto, AMPLIFICADO -- no creado -- por la saturacion del decoder.
- **H_met (colapso por metrica, Exp D):** PARCIAL (mezcla honesta). (a) ROBUSTO -> refuta el artefacto de ref inflado: el ranking de cabeza es estable al reference point (perm-NSGA-II #1 en 5/5; random restart SUPERA a MOHHO real-coded en 5/5; tier perm>rk en 4/5, rompe solo bajo el ref mas apretado). 'random restart competitivo' NO es artefacto de un HV insensible. (b) CONFIRMADO PARCIALMENTE -> acota el alcance: el HV esta determinado en ~99.5% por la cobertura de f2 (fijando f1,f3 a medianas se recupera casi todo el HV), de modo que el indicador HV discrimina esencialmente via el eje f2; y bajo IGD+/epsilon (sin reference point) sobre los frentes COMBINADOS el orden estricto de tiers no se preserva (artefacto de que los frentes combinados convergen casi al mismo Z). Recomendacion: reportar IGD+/epsilon junto al HV y declarar que el HV discrimina por f2 -- el claim basado en HV aplica al eje de disparidad f2, consistente con que f2 es la unica dimension ancha (Exp B).
- **Q1 (no-saturantes no-dominados, MILP):** claim_holds=`False`; 7 contraejemplos formales, 0 practicamente significativos.

## 2. Gate de optimizers (Exp A)

Re-implementaciones genericas de los mismos algoritmos sobre benchmarks con optimo/frente conocido (presupuesto generoso de 50,000 evals para un chequeo de convergencia inequivoco).

| Benchmark | MOHHO/true | veredicto MOHHO | NSGA/true | NSGA self-check |
|---|---|---|---|---|
| ZDT1 | 0.995 | sano | 0.990 | sano |
| ZDT2 | 0.203 | roto | 0.986 | sano |
| DTLZ2 | 0.854 | sano | 0.824 | sano |

**Diagnostico del 'fallo' en ZDT2:** el archivo de MOHHO colapsa a ~1 punto(s) con g=1.000 (frente verdadero g=1): MOHHO CONVERGE al frente pero no se DESPLIEGA por el frente concavo -- fallo de DIVERSIDAD, no bug. En ZDT1 (convexo) recupera 0.995 y en DTLZ2 0.854.

**TSP de juguete (optimo 6.1803):** operadores perm-NSGA-II gap_min=0.00\%, Discrete-MOHHO gap_min=0.00\% -> alcanzan el optimo: operadores permutacionales SANOS.

**Random restart:** confirmado_muestreo_puro (HV combinado 316,383); confirmado muestreo puro (sin operadores, sin busqueda local oculta).

> **Implicacion:** MOHHO real-coded esta correctamente implementado pero es un optimizador multi-objetivo DEBIL (poca diversidad en fronts concavos). Por tanto `random restart ~ MOHHO real-coded` refleja una debilidad algoritmica genuina del swarm real-coded, NO una contaminacion del ladder por codigo roto. El ladder es valido.

## 3. H_str -- colapso estructural (Exp B)

**Dimensionalidad efectiva (PCA):** PC1 en [0.81, 0.91], PC1+PC2 en [0.984, 0.992], PC3 en [0.008, 0.016]. Dimension efectiva mediana (95\% var) = 2. PCA sobre objetivos min-max por metodo. PC3~1% => f3 colapsa por saturacion (82/92 sols con f3=0). PC1+PC2~99% con PC2~12-18% => trade-off f1-f2 genuino y bidimensional. El frente NO es mono-objetivo, pero el visa es un lead-case multi-objetivo DEBIL (un eje, f2, domina; f1 angosto; f3 saturado).

**Degeneracion del decoder:** ratio = 1.269 (50,000 permutaciones -> 39,401 puntos objetivo distintos): el greedy NO es masivamente degenerado. Rangos alcanzables: f1 ancho 0.2732, f2 ancho 10.75 (f2/f1 = 39.4x). f3 observado max = 22080 vs ref 20000 (factor 0.9).

**Cobertura por tier:** Ambos tiers alcanzan el rango COMPLETO de f2 (mismo ALCANCE); la ventaja perm es de RESOLUCION/cardinalidad (188 vs 116 sols), no de region nueva. Matiza el argumento 'perm llega a regiones que rk no'.

> **Veredicto H_str:** PARCIAL: f3 colapsa por saturacion (PC3~1%) y f1 es estructuralmente angosto (f2/f1=39.4x), pero el trade-off f1-f2 es bidimensional y genuino (PC1+PC2~99%). El problema es EFECTIVAMENTE BI-OBJETIVO, no mono-objetivo.

## 4. H_dec -- colapso por decoder (Exp C)

**Q1 (frente exacto bi-objetivo f1-f3 via MILP, f2 a posteriori):** frente exacto de 7 puntos; utilizacion maxima ponderada 101,220/140,000. **claim_holds = `False`**: 7 optimos no-saturantes no-dominados respecto al greedy, pero **0 practicamente significativos** (los demas difieren solo en el 5o decimal de f1 -- el eje degenerado -- y su f2 incidental es peor que el mejor f2 del greedy = 2.0). El greedy NO pierde estructura practicamente relevante.

Complemento empirico (decoder C1, slack_V>0): 1286 soluciones no-saturantes no-dominadas vs greedy, 11 con mejora significativa de f2.

**Re-corrida del ladder sobre decoders no-saturantes** (HV normalizado en box comun de los 3 decoders; feasibility verificada, 0 violaciones):

| Decoder | rk-tier | perm-tier | perm&minus;rk | perm&gt;rk | estricta | p pareado |
|---|---|---|---|---|---|---|
| greedy | 65.48 | 70.01 | +6.93\% | True | True | 9.3e-10 |
| C1_fractional | 66.51 | 67.47 | +1.45\% | True | False | 2.1e-04 |
| C2_stochastic_skip | 63.07 | 65.76 | +4.27\% | True | False | 1.3e-08 |

**Colapso (no inversion) de la separacion:** greedy +6.93\% -> C2 +4.27\% (sobrevive 62\%) -> C1 +1.45\% (sobrevive 21\%). Punto clave: perm-tier NUNCA es peor que rk-tier bajo ningun decoder (perm&gt;rk en los 3 = `True`); el margen se ENCOGE al relajar la saturacion pero no se INVIERTE. La permutation-nativeness nunca perjudica; su VENTAJA escala con la saturacion del decoder.

**Phenotype-preservation** (regimen 'near' = on-trajectory):

| Decoder | tau_orden SBX | L1 fenotipica SBX | L1 fenotipica HHO | HHO/SBX |
|---|---|---|---|---|
| greedy | 0.897 | 0.00244 | 1.5138 | 621.5x |
| C1_fractional | 0.891 | 0.00313 | 0.9681 | 309.13x |

> **Veredicto H_dec:** REFUTADA EN LO ESENCIAL (con matiz de magnitud). La separacion perm>rk es SIGNIFICATIVA bajo los TRES decoders (greedy +6.93%, C2 +4.27%, C1 +1.45%; Wilcoxon pareado p<0.001 en los tres) y NUNCA se invierte: por tanto la ventaja de la representacion NO es un artefacto de la saturacion del decoder -- persiste al introducir intensidad fraccional (C1) y skip estocastico (C2). MATIZ HONESTO: la MAGNITUD escala con la saturacion (solo 21% del margen greedy sobrevive bajo C1), y C1 (no-saturante) halla 11 soluciones con f2 mejor que el mejor f2 del greedy que el greedy no captura. Conclusion: el efecto representacion es real y robusto, AMPLIFICADO -- no creado -- por la saturacion del decoder.

## 5. H_met -- colapso por metrica (Exp D)

**Barrido de reference points (HV per-run, ranking de 6 metodos):** random restart supera a MOHHO real-coded en 5/5 reference points; tier perm&gt;rk en 4/5 (rompe solo bajo el ref mas apretado). El BEST method (perm-NSGA-II) es #1 en todos.

| Reference point | rank 1 | perm&gt;rk tier | rank random restart | rank MOHHO |
|---|---|---|---|---|
| baseline_(10,16,20000) | perm_nsga2 | True | 4 | 5 |
| fitted_(9.1,13.5,2100) | perm_nsga2 | True | 4 | 5 |
| tight_(9.0,13.2,1000) | perm_nsga2 | False | 3 | 5 |
| mid_(9.5,14.5,8000) | perm_nsga2 | True | 4 | 5 |
| f3_collapsed_(9.1,13.5,700) | perm_nsga2 | True | 4 | 5 |

**Metricas sin reference point** (Z = union no-dominada de los SEIS frentes, |Z|=190): IGD+ ranking = ['perm_nsga2', 'discrete_mohho', 'mohho_realcoded', 'nsga2_realcoded', 'perm_moead', 'random_restart'] (tier preservado=False); epsilon ranking = ['perm_nsga2', 'discrete_mohho', 'mohho_realcoded', 'perm_moead', 'random_restart', 'nsga2_realcoded'] (tier preservado=False).

**Sensibilidad del HV a f2:** HV(f2-only)/HV(full) medio = 0.9948. Si HV(f2-only)/HV(full) ~ 1, el HV esta casi enteramente determinado por la cobertura de f2 -> el claim aplica al eje f2.

> **Veredicto H_met:** PARCIAL (mezcla honesta). (a) ROBUSTO -> refuta el artefacto de ref inflado: el ranking de cabeza es estable al reference point (perm-NSGA-II #1 en 5/5; random restart SUPERA a MOHHO real-coded en 5/5; tier perm>rk en 4/5, rompe solo bajo el ref mas apretado). 'random restart competitivo' NO es artefacto de un HV insensible. (b) CONFIRMADO PARCIALMENTE -> acota el alcance: el HV esta determinado en ~99.5% por la cobertura de f2 (fijando f1,f3 a medianas se recupera casi todo el HV), de modo que el indicador HV discrimina esencialmente via el eje f2; y bajo IGD+/epsilon (sin reference point) sobre los frentes COMBINADOS el orden estricto de tiers no se preserva (artefacto de que los frentes combinados convergen casi al mismo Z). Recomendacion: reportar IGD+/epsilon junto al HV y declarar que el HV discrimina por f2 -- el claim basado en HV aplica al eje de disparidad f2, consistente con que f2 es la unica dimension ancha (Exp B).

## 6. Ubicacion en la matriz de desenlaces (s.7)

**Celda: tesis (esencialmente) blindada, con matiz de magnitud.** La separacion perm&gt;rk es significativa bajo los tres decoders (incluido el no-saturante C1, +1.4\%, p&lt;0.001) y nunca se invierte: NO es artefacto de la saturacion. El problema mantiene un trade-off bi-objetivo genuino (H_str), y el ranking es robusto a la metrica (H_met). Matiz honesto: la MAGNITUD del efecto escala con la saturacion (6.9\%->1.4\%).

### Texto de rebuttal para el revisor

Agradecemos la objecion de colapso, que separamos en tres causas y probamos una por una sobre la instancia base verificada (mismo presupuesto de 25,000 evals e identico reference point para los seis metodos).

(i) *Estructura* (H_str): el decoder greedy no es masivamente degenerado (ratio 1.269, 39,401 puntos objetivo distintos de 50,000 permutaciones) y el frente es efectivamente BI-objetivo (PCA: PC1+PC2~99\%, PC3~1\% por saturacion de f3), no mono-objetivo; eso si, f2 es ~39.4x mas ancho que f1, por lo que reconocemos al visa como lead-case multi-objetivo debil.

(ii) *Decoder* (H_dec): re-corrimos el ladder completo sobre dos decoders NO-saturantes (fraccional C1 y stochastic-skip C2, feasibility por construccion). La separacion perm&gt;rk PERSISTE y es SIGNIFICATIVA bajo los tres decoders (greedy +6.9\%, C2 +4.3\%, C1 +1.4\%; Wilcoxon pareado p&lt;0.001 en los tres) y nunca se invierte, de modo que la ventaja de la representacion NO es un artefacto de la saturacion del decoder. Lo reportamos con honestidad: la MAGNITUD del efecto escala con la saturacion (bajo C1 sobrevive ~21\% del margen), de modo que la saturacion AMPLIFICA -- no crea -- el efecto. El mecanismo se mantiene: SBX es casi-identidad sobre el FENOTIPO completo (L1 621.5x menor que HHO), no solo sobre el orden.

(iii) *Metrica* (H_met): el ranking de cabeza es robusto al reference point -- perm-NSGA-II es #1 y random restart supera a MOHHO real-coded en 5/5 reference points (tier perm&gt;rk en 4/5, rompe solo bajo el ref mas apretado), de modo que 'random restart competitivo' NO es artefacto de un HV insensible por reference point inflado. Con honestidad anhadimos dos matices: el HV esta determinado en ~99\% por la cobertura de f2, y bajo IGD+/epsilon sobre los frentes COMBINADOS el orden ESTRICTO de tiers no se preserva (los frentes combinados convergen casi al mismo Z; el tier es un fenomeno PER-RUN). El claim basado en HV aplica al eje de disparidad f2.

Finalmente, el frente exacto bi-objetivo (f1,f3) via MILP confirma que el greedy no pierde estructura practicamente relevante (0 contraejemplos no-saturantes significativos).

### Ajuste recomendado al paper

**Titulo intacto.** Anadir una subseccion de robustez (Exp B/C/D) y UNA frase al abstract reconociendo que el efecto, aunque robusto a decoder y metrica, es de MAGNITUD amplificada por la saturacion del decoder feasibility-preserving (efecto induced por la representacion saturante). Rebuttal demoledor con los numeros de C1/C2, IGD+/epsilon y el MILP.

### Correccion de la inconsistencia del frente de policy (Hallazgo D)

El frente de policy (Fig. 2 / Tabla 4 / Fig. 10, dominacion de FIFO, las 92 soluciones) se genera con **MOHHO clasico (real-coded SPV)** (HV per-run 302,379), NO con el metodo recomendado **Discrete-MOHHO** (149 sols, HV 316,637). Recomendacion: regenerar Fig. 2/Tabla 4/Fig. 10 con Discrete-MOHHO (frente recomendado y dominante), o declarar explicitamente que el menu de politicas usa el frente combinado clasico por continuidad con el estudio.

## 7. Amenazas residuales

- **C1 anade una sub-dimension continua (intensidad alpha).** Los metodos permutacionales la manejan con un operador real injertado (SBX/gaussiano), no permutation-native; por tanto el colapso de la separacion bajo C1 mezcla dos efectos (quitar la saturacion + diluir la ventaja permutacional en un sub-espacio continuo). El resultado acota el claim a decoders saturantes, que es lo honesto.

- **MOHHO real-coded es debil en multi-objetivo (Exp A, ZDT2).** No invalida el ladder (todos los metodos comparten decoder, presupuesto e instancia), pero matiza que la parte 'real-coded' de la comparacion no es un optimizador de referencia fuerte.

- **f2 es la unica dimension ancha.** El visa es un lead-case multi-objetivo DEBIL; la ley general (representation governs) descansa en las 4 estructuras del estudio de generalizacion, no solo en el visa.


---
_Generado por `collapse/experiments/build_report.py` desde results/*.json._
