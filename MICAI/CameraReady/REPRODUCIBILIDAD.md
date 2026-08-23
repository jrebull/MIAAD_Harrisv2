# Reproducibilidad del camera-ready — MICAI 2026, paper #38

Manifiesto de entorno para reproducir el PDF y sus cifras. `backend/requirements.txt` es
el manifiesto de Python del repositorio completo; este documento añade lo que aquél no
puede expresar: **versiones concretas probadas** y **dependencias de sistema**.

## Artefactos de referencia

| Qué | Identidad |
|---|---|
| Commit del camera-ready | el que contiene este fichero, etiquetado `micai-cameraready-r1` |
| Tag citado en Data Availability | `micai-cameraready-r1` |
| PDF | `MICAI/CameraReady/src/main_cr.pdf` — sha256 `ceeacee775611f89a415d46f7d595296f8627115d317f192c44ca9867f599452` |
| Paquete de envío | `MICAI/CameraReady/038_r1.zip` — su sha256 va en el sello |
| Sello | `MICAI/CameraReady/038_r1_SHA256.txt`; el del paquete anterior se conserva en `038_SHA256.txt` |

## Dependencias de sistema

No son instalables con `pip` y **ningún gate las declara**; sin ellas el proceso falla o,
peor, se salta controles.

| Requisito | Para qué | Versión probada |
|---|---|---|
| **TeX Live** (`pdflatex`) | compilar el `.tex`; `tools/compila_cr.sh` fuerza `SOURCE_DATE_EPOCH` para que el PDF sea reproducible | pdfTeX 3.141592653-2.6-1.40.27 (TeX Live 2025) |
| **Poppler** (`pdftotext`, `pdfinfo`, `pdffonts`) | `cr_firewall.py` extrae el texto del PDF; `compila_cr.sh` cuenta páginas, fuentes Type 3 y no incrustadas | 26.04.0 |

`llncs.cls` **no** se toma de TeX Live: viaja en `src/` y dentro del ZIP de envío, para que la
compilación no dependa de qué versión de la clase tenga instalada quien reproduzca.

**CBC no aparece como requisito de sistema aparte.** En el entorno probado, `pulp` 3.3.2
trae su propio binario CBC en `pulp/solverdir/cbc/osx/i64/cbc` y `PULP_CBC_CMD().available()`
devuelve esa ruta, de modo que declarar `pulp` bastó para el control MILP. Es lo observado
en macOS con esa versión, **no una garantía para cualquier plataforma o versión de PuLP**:
si en tu sistema `available()` no devuelve ruta, instala CBC por separado.

## Dependencias de Python

Declaradas en `backend/requirements.txt`. Las cinco que importan para el camera-ready:

| Paquete | Quién la usa | Si falta |
|---|---|---|
| `numpy`, `scipy` | toda la derivación estadística; `cr_derive.py`, `verify_paper.py` | no corre nada |
| `matplotlib` | los cuatro generadores de figuras | no se regenera ninguna figura |
| `pdfplumber` | control de lettering ≥ 6 pt de `cr_firewall.py` | **el gate falla en cerrado** y dice que falta la librería; no se salta el control en silencio |
| `pulp` | `collapse/experiments/exact_front_f1f3_milp.py`, el MILP exacto $(f_1,f_3)$ reportado en §3 y §5.2 | no se puede re-derivar ese control |

## Entornos en los que se validó

Se validó bajo **dos** intérpretes distintos. Ambos dieron los cuatro gates en verde y el
PDF byte a byte idéntico. **El control MILP no entra en esa doble validación**: `pulp` solo
estuvo presente en el entorno A, así que el MILP exacto $(f_1,f_3)$ se ejercitó únicamente
ahí. La columna B lo refleja con un guion.

| | Entorno A (`backend/.venv`) | Entorno B (validación desde checkout limpio) |
|---|---|---|
| Python | 3.14.2 | 3.12 |
| numpy | 2.4.3 | 2.0.0 |
| scipy | 1.17.1 | 1.14.1 |
| matplotlib | 3.10.9 | 3.10.0 |
| pdfplumber | 0.11.10 | 0.11.10 |
| pulp | 3.3.2 | — |

Las cotas de `requirements.txt` son mínimos, no anclajes. Si necesitas reproducir bit a
bit una cifra que dependa de un generador aleatorio de NumPy, fija las versiones de la
columna que corresponda: el rango 2.0 – 2.4 se comportó igual aquí, pero eso es una
observación sobre estas dos, no una garantía sobre todas.

## Cómo reproducir

```bash
git clone https://github.com/jrebull/MIAAD_Harrisv2
cd MIAAD_Harrisv2 && git checkout micai-cameraready-r1
python3 -m venv backend/.venv && source backend/.venv/bin/activate
pip install -r backend/requirements.txt
# Versiones del entorno A, el unico donde las tres coexistieron y se ejercitaron
# juntas. requirements.txt ya las declara en r1; el pin fija la terna probada.
pip install "matplotlib==3.10.9" "pdfplumber==0.11.10" "pulp==3.3.2"

# 1. compilar (reproducible: SOURCE_DATE_EPOCH fijo)
bash MICAI/CameraReady/tools/compila_cr.sh MICAI/CameraReady/src main_cr

# 2. los cuatro gates, desde backend/
cd backend
python3 repro/verify_paper.py                     # 190 cifras contra instantáneas
python3 repro/cr_firewall.py --pdf ../MICAI/CameraReady/src/main_cr.pdf \
                             --figdir ../MICAI/CameraReady/src/figures
python3 repro/cr_gate_derived.py --derived app/data/results/cr_derived.json
python3 repro/cr_gate_freshness.py --src ../MICAI/CameraReady/src \
                                   --compile ../MICAI/CameraReady/tools/compila_cr.sh
```

Los cuatro devuelven **0** al pasar. Léelos por su código de salida: una tubería como
`gate.py | tail` devuelve el de `tail`, que siempre vale 0.

**Sobre `cr_gate_freshness` en un checkout recién clonado**: compara mtimes para detectar
un PDF rancio, y en un clon todos los mtimes son el del clon, así que ahí no significan
nada y hay que normalizarlos. La señal válida en ese contexto es la otra que el gate
comprueba: que el PDF coincida byte a byte con una recompilación limpia.

## Alcance conocido de este manifiesto

- `micai-cameraready-r1` **sí** declara las tres. El tag anterior, `micai-cameraready`
  (`6cf9cd5`), no las declaraba; se conserva intacto como versión histórica, con su propio
  sello, y quien reproduzca desde él debe instalarlas a mano. La receta de arriba las
  instala de todos modos, así que funciona con cualquiera de los dos.
- Las cifras no se re-ejecutan desde cero: se re-derivan de instantáneas gobernadas en
  `backend/app/data/results/`. Reproducir el artículo significa reproducir esa derivación,
  no volver a correr 30 semillas × 9 métodos.
- Para tres métodos, el re-scoring histórico procede de frentes retenidos y no de una
  instantánea corriente establecida. El artículo lo declara en Data Availability.
