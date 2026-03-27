# Visa Predict AI v2.0

**Multi-Objective Harris Hawks Optimization (MOHHO) for US Employment-Based Visa Allocation**

> Tesis de Maestría en Ingeniería de Análisis y Aprendizaje de Datos (MIAAD) — UACJ 2026

## Descripción

Este sistema aplica el algoritmo **MOHHO** (Multi-Objective Harris Hawks Optimization) para optimizar la asignación de **140,000 visas EB** anuales de EE.UU. entre 21 países y 5 categorías de empleo, buscando simultáneamente:

| Objetivo | Fórmula | Meta |
|----------|---------|------|
| **f₁** — Carga de Espera | `Σ(nᵍ - xᵍ)·wᵍ / Σnᵍ` | Minimizar años de espera ponderados |
| **f₂** — Disparidad | `max \|W̄c₁ - W̄c���\|` | Minimizar brecha entre países |
| **f₃** — Desperdicio | `V - Σxᵍ` | Minimizar visas sin usar |

El sistema genera un **frente de Pareto** con cientos de soluciones que mejoran sustancialmente sobre el sistema FIFO actual.

## Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic v2, NumPy, SciPy |
| Frontend | Nuxt 4 (Vue 3 + TypeScript), Tailwind CSS |
| Visualización | Apache ECharts vía vue-echarts |
| Comunicación | REST API + WebSocket (simulación en vivo) |
| Infraestructura | Docker Compose |

## Inicio Rápido

### Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs interactiva: http://localhost:8000/docs

### Frontend (Nuxt 4)

```bash
cd frontend
npm install
npm run dev
```

Aplicación: http://localhost:3000

### Docker (ambos servicios)

```bash
docker compose up --build
```

## Arquitectura

```
Harris2/
├── backend/
│   ├── app/
│   │   ├── core/           # Algoritmo MOHHO
│   │   │   ├── config.py   # Parámetros del problema (V=140000, P_C=25620, etc.)
│   │   │   ├── data.py     # Datos de demanda (21 países × 5 categorías)
│   │   │   ├── problem.py  # VisaProblem: f₁, f₂, f₃
│   │   │   ├── decoder.py  # SPV + decodificador greedy
│   │   │   ├── hho.py      # 6 operadores Harris Hawks
│   │   │   ├── mohho.py    # MOHHO: archivo Pareto, crowding distance, HV
│   │   │   ├── fifo.py     # Línea base FIFO
│   │   │   └── models.py   # Esquemas Pydantic
│   │   ├── api/            # Endpoints REST + WebSocket
│   │   │   ├── scenarios.py    # /api/scenarios, /api/summary, /api/groups, /api/allocation, /api/impact
│   │   │   ├── pareto.py       # /api/pareto, /api/pareto/run/{idx}
│   │   │   ├── convergence.py  # /api/convergence, /api/convergence/runs
│   │   │   ├── optimize.py     # POST /api/optimize
│   │   │   └── ws.py           # WS /ws/simulation
│   │   ├── data/results/   # Resultados pre-computados (30 corridas)
│   │   └── main.py         # App FastAPI con CORS + lifespan
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── pages/          # 8 páginas: inicio, modelo, pareto, asignación, impacto, convergencia, simulación, datos
│   │   ├── components/     # charts/ (ECharts) + ui/ (layout)
│   │   ├── composables/    # useApi, useScenario, useOptimizer, useSimulation, useEcharts
│   │   ├── utils/          # formatters.ts
│   │   └── layouts/        # default.vue (navbar + sidebar + footer)
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Páginas del Dashboard

| Página | Ruta | Descripción |
|--------|------|-------------|
| Inicio | `/` | KPIs, descripción del problema, FIFO vs MOHHO |
| Modelo | `/modelo` | Formulación matemática (página estática) |
| Pareto | `/pareto` | Frente de Pareto con proyecciones f₁/f₂/f₃ |
| Asignación | `/asignacion` | Heatmap + barras apiladas por país/categoría |
| Impacto | `/impacto` | Comparación delta vs FIFO por país |
| Convergencia | `/convergencia` | Curva HV, barras por corrida, explorador de Pareto individual |
| Simulación | `/simulacion` | MOHHO en vivo vía WebSocket |
| Datos | `/datos` | Tabla de 105 grupos con procedencia de datos |

## 5 Escenarios

| Escenario | Estrategia |
|-----------|-----------|
| Humanitario | Minimiza f₁ (espera ponderada) |
| Equilibrio | Punto de rodilla del frente de Pareto |
| Equidad | Minimiza f₂ (brecha entre países) |
| Máx. Utilización | Minimiza f₃ (visas desperdiciadas) |
| FIFO | Sistema actual (línea base) |

## Resultados Clave

- **30 corridas** × 500 iteraciones, población 50, archivo 100
- **406 soluciones Pareto** combinadas
- FIFO: f₁=7.21, f₂=12.64, f₃=17,540
- Mejor f₁: reducción significativa de espera ponderada
- Mejor f₃: **cero desperdicio** de visas posible

## Fuentes de Datos

- **USCIS FY2025 Q2** — Peticiones I-140/I-360/I-526 aprobadas en espera
- **Visa Bulletin Abril 2026** — Fechas de acción final (Dept. of State)
- **DHS Yearbook FY2023** — Cuotas de inmigración por país
- **INA Sección 203(b)** — Reglas de spillover: EB-4/5 → EB-1 → EB-2 → EB-3

## Equipo

**MIAAD × UACJ 2026** — Yazmín Flores, Javier Rebull
