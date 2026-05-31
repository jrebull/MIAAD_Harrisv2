# Reporte v5 — Order-Preservation tau (con matiz honesto)

> Todo numero desde `app/data/results/*.json` (seed=1). Ladder v5 a 30 seeds.

## 1. Resumen ejecutivo

- **El MO-HHO competente LE GANA a random restart** en el visa: 316,347 vs 310,214 (+1.98%, Wilcoxon pareado p=5.7e-04, 30 seeds). El MOHHO INGENUO pierde (302,756, naive_beats_random=False).
- **Por tanto 'the decoder does the work / random beats the swarm' es artefacto del swarm ingenuo roto.** Un swarm competente (HHO + non-dominated sorting + mutacion) supera al muestreo ciego.
- **Pero la tesis precisa NO es una correlacion HV-tau** (es debil: Spearman rho=-0.21, p=0.69, n=6). Los datos soportan una **regla de DOS condiciones**: un metodo gana al muestreo ciego sii (1) su operador cambia el orden decodificado (NO near-identity, tau lejos de +1) Y (2) su seleccion preserva diversidad (NDS/descomposicion/archivo, NO aceptacion dominance-gated). Reportado tal cual, sin adornar.
- **Validacion del competente:** config adoptada {'pm': 0.15, 'use_sbx': True}, sana en ZDT1/ZDT2/DTLZ2 (min 91% del frente verdadero; ZDT2 pasa de 20% a ~99%).

## 2. Ladder v5 (30 seeds, 25,000 evals) + tau por metodo

| Metodo | HV medio | CV | comb HV | tier | tau | gana a random |
|---|---|---|---|---|---|---|
| nsga2_realcoded | 293,367 | 2.38% | 316,060 | random_key | +0.990 | no |
| naive_mohho | 302,756 | 2.36% | 320,984 | random_key | -0.154 | no |
| competent_mohho | 316,347 | 2.11% | 321,800 | random_key | -0.331 | SI |
| random_restart | 310,214 | 0.88% | 317,673 | random_key | n/a | — |
| perm_nsga2 | 318,151 | 0.58% | 321,935 | permutation | +0.284 | SI |
| perm_moead | 314,846 | 1.71% | 320,969 | permutation | +0.284 | SI |
| discrete_mohho | 316,792 | 0.71% | 321,408 | permutation | +0.284 | SI |

random restart HV = 310,214. Figura central: `Figures/v5/hv_vs_tau.html`.

**Regla de dos condiciones (explica los 7 metodos):** A method beats blind random restart iff (1) its operator changes the decoded order (NOT near-identity, tau far from +1) AND (2) its selection preserves population diversity (NDS / decomposition / crowded archive, NOT dominance-gated acceptance).

- NSGA-II: FAILS (1): tau=0.99 near-identity -> loses
- MOHHO ingenuo: FAILS (2): gated acceptance freezes the population -> loses
- MO-HHO competente: satisfies BOTH (low-tau HHO offspring + NDS) -> first real-coded swarm to beat random
- metodos perm: satisfy BOTH (order-changing OX/swap + diversity-preserving selection) -> win

## 3. Veredicto sobre la tesis

La afirmacion 'random restart beats the real-coded swarm; the decoder does most of the work' **se cae como tesis general** y debe reescribirse: el muestreo ciego supera a busquedas \emph{near-identity} (NSGA-II SBX, tau=0.99) y al swarm \emph{ingenuo congelado}, pero NO a un swarm competente. La ley defendible es la **regla de dos condiciones** (operador que cambia el orden + seleccion que preserva diversidad), de la cual tau es un componente medible pero no suficiente por si solo. La dominacion de FIFO, el decoder, Taguchi, el factorial y las 4 estructuras quedan intactos.

**Riesgo residual:** con n=6 metodos la correlacion HV-tau escalar carece de potencia; la evidencia fuerte es el contraste cualitativo competente-vs-ingenuo (misma familia, mismo tau bajo, distinta seleccion -> distinto resultado).

---
_Generado por `repro/build_v5_outputs.py` desde results/*.json._
