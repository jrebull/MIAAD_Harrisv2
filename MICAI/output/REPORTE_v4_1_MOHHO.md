# Reporte v4.1 — Reparar/escopar el MOHHO y reconciliar el paper

> Todo numero proviene de `app/data/results/*.json` regenerado (cero hardcode). Diagnosticos con seed=1.

## 1. Resumen ejecutivo

- **Decision: SCOPING honesto** (no reparacion). Ninguna de las 7 variantes de reparacion (R1 reflexion / R2 eps-archivo / R3 damping y combinaciones) sanea ZDT2: todas quedan en 20.2% del frente verdadero (`mohho_repair_selection.json`, any_sane=False). El colapso es una patologia de operadores en frentes concavos, no de la aceptacion.
- **El ranking sobrevive intacto:** no se re-corrio el ladder (la reparacion no procede), asi que las cifras del ladder (Tablas 5/7) se mantienen y siguen verificadas. random restart > MOHHO > NSGA-II y Discrete-MOHHO +4.7% sobre MOHHO clasico estan intactos.
- **Mecanismo reconciliado:** la propuesta HHO salta (tau~0) pero la trayectoria realizada esta CONGELADA bajo el gate (0.58% de hawks se mueven/iter, vs 96% del canonico); el archivo se alimenta de propuestas rechazadas. Texto del paper (pag.14) corregido.
- **Firewall:** `n_mismatch = 0` sobre 35 cifras cableadas (HVs del ladder, omnibus, tau, FIFO, extremos, Taguchi, politica f2, ranks). `python repro/reproduce_all.py` es el script publico de reproduccion.

## 2. Diagnostico (verificado contra el motor)

### 2.1 Aceptacion + reparacion (ZDT1/ZDT2/DTLZ2)

| benchmark | canonical | gated (codigo) | pareto-improving | NSGA-II ref |
|---|---|---|---|---|
| ZDT1 | 99.5% | 99.5% | 99.5% | 99% |
| ZDT2 | 20.2% | 20.2% | 20.2% | 99% |
| DTLZ2 | 86.3% | 87.4% | 87.9% | 89% |

ZDT2 colapsa en las tres (20.2% del verdadero, archivo=1). Reparaciones probadas (HV/true, min sobre los 3):
| variante | ZDT1 | ZDT2 | DTLZ2 | min | sana |
|---|---|---|---|---|---|
| baseline(clip) | 99.5% | 20.2% | 61.7% | 20.2% | False |
| R1 | 99.1% | 20.2% | 27.1% | 20.2% | False |
| R2 | 98.0% | 20.2% | 81.4% | 20.2% | False |
| R3 | 87.3% | 20.2% | 13.2% | 13.2% | False |
| R1+R2 | 97.9% | 20.2% | 44.3% | 20.2% | False |
| R1+R3 | 61.2% | 20.2% | 29.0% | 20.2% | False |
| R1+R2+R3 | 79.1% | 20.2% | 44.9% | 20.2% | False |

Ver `Figures/v4/acceptance_repair.html`, `zdt2_collapse.html`.

### 2.2 Congelamiento en el visa

gated (codigo actual): 0.58% movidos/iter, desplazamiento medio 0.0177, HV 302,756. canonical: 96% movidos, HV 296,767. random restart HV 310,214. Ver `Figures/v4/mohho_freeze.html`.

## 3. Texto LaTeX corregido (insertado en el paper)

**Mecanismo (pag.14, reemplaza 'the swarm genuinely traverses'):** la propuesta HHO salta; el gate la rechaza (~0.6% se mueve); el archivo se alimenta de las propuestas rechazadas, por eso muestrea mas que SBX casi-identico. **MOHHO real-coded declarado como baseline DEBIL** que colapsa en frentes concavos (ZDT2 HV 0.11). La tesis no depende de que sea un swarm fuerte.

**§4.2 (saturante):** corregido --- el MILP halla no-saturantes no-dominados pero ninguno mejora un objetivo de forma practica; el subconjunto saturante no pierde nada relevante (alineado con expC_Q1 y §6.4).

**Framing bi-objetivo:** suavizado a 'near-mono-objective' (PC1 solo 0.81--0.91, segundo eje genuino pero angosto).

**f2 de la politica (Fig.10):** recomputada desde la solucion real = 7.5902 anios (`policy_impact.json`), figura y caption corregidos.

**Seeds:** nota de reproducibilidad (diagnosticos seed=1; comparaciones de 30 corridas con bloques de seed fijos en el codigo).

## 4. Veredicto sobre la tesis

La tesis **se sostiene y se fortalece**: 'representation governs, not metaheuristic'. El MOHHO real-coded debil (colapso en ZDT2 + congelamiento) es CONSISTENTE con la tesis --- los metodos real-coded pierden frente a los permutacionales. El scoping convierte una debilidad oculta en una limitacion declarada y auditable. Ranking, +4.7% de Discrete-MOHHO, y omnibus (chi2=112.6) intactos. Riesgo residual: el MOHHO sigue siendo un swarm debil en MO, ahora declarado explicitamente.

---
_Generado por `repro/build_v4_report.py` desde results/*.json._
