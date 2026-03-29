<script setup lang="ts">
definePageMeta({ prerender: true })

const expandedFile = ref<string | null>(null)

function toggleFile(name: string) {
  expandedFile.value = expandedFile.value === name ? null : name
}
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto">
    <h1 class="section-title">Algoritmo MOHHO</h1>
    <p class="text-sm text-gray-400 -mt-4 leading-relaxed max-w-3xl">
      Multi-Objective Harris Hawks Optimization: arquitectura completa, operadores,
      codificación y conexión entre la teoría y el código Python.
    </p>

    <!-- ============================= -->
    <!-- 1. ARQUITECTURA DEL SISTEMA   -->
    <!-- ============================= -->
    <section class="card space-y-6">
      <h2 class="text-lg font-bold text-white">1. Arquitectura del Sistema</h2>
      <p class="text-sm text-gray-400">
        Tres capas desacopladas que separan presentación, comunicación y lógica algorítmica.
        El flujo de datos es bidireccional: el frontend solicita optimizaciones y recibe resultados en tiempo real.
      </p>

      <div class="relative space-y-4">
        <!-- CAPA 1: FRONTEND -->
        <div class="relative rounded-xl p-px bg-gradient-to-r from-primary/60 via-blue-400/40 to-primary/60">
          <div class="bg-dark-bg2 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-3">
              <div class="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_12px_rgba(0,60,166,0.8)] animate-pulse" />
              <h3 class="text-primary-300 font-bold text-xs uppercase tracking-widest">Capa de Presentación</h3>
              <span class="text-[10px] text-gray-500 ml-auto font-mono bg-primary/10 px-2 py-0.5 rounded">Nuxt 4 &bull; Vue 3 &bull; TypeScript</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div class="bg-primary/5 rounded-lg p-3 border border-primary/15 text-center">
                <p class="text-primary-300 font-bold text-lg">8</p>
                <p class="text-gray-500 text-[10px]">Páginas SPA</p>
              </div>
              <div class="bg-primary/5 rounded-lg p-3 border border-primary/15 text-center">
                <p class="text-primary-300 font-bold text-lg">5</p>
                <p class="text-gray-500 text-[10px]">Composables</p>
              </div>
              <div class="bg-primary/5 rounded-lg p-3 border border-primary/15 text-center">
                <p class="text-primary-300 font-bold text-lg">12</p>
                <p class="text-gray-500 text-[10px]">Charts ECharts</p>
              </div>
              <div class="bg-primary/5 rounded-lg p-3 border border-primary/15 text-center">
                <p class="text-primary-300 font-bold text-lg">1</p>
                <p class="text-gray-500 text-[10px]">Canvas Animado</p>
              </div>
            </div>
          </div>
        </div>

        <!-- CONEXIÓN FRONTEND ↔ API -->
        <div class="flex items-center justify-center gap-6 py-1">
          <div class="flex items-center gap-2">
            <div class="h-px w-12 bg-gradient-to-r from-transparent to-accent-yellow/60" />
            <span class="text-accent-yellow text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-accent-yellow/10 border border-accent-yellow/20">REST &times; 12</span>
            <div class="h-px w-12 bg-gradient-to-l from-transparent to-accent-yellow/60" />
          </div>
          <div class="flex items-center gap-2">
            <div class="h-px w-8 bg-gradient-to-r from-transparent to-accent-green/60 border-dashed" />
            <span class="text-accent-green text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-accent-green/10 border border-accent-green/20">WebSocket</span>
            <div class="h-px w-8 bg-gradient-to-l from-transparent to-accent-green/60 border-dashed" />
          </div>
        </div>

        <!-- CAPA 2: API GATEWAY -->
        <div class="relative rounded-xl p-px bg-gradient-to-r from-accent-green/60 via-emerald-400/40 to-accent-green/60">
          <div class="bg-dark-bg2 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-3">
              <div class="w-2.5 h-2.5 rounded-full bg-accent-green shadow-[0_0_12px_rgba(0,200,100,0.8)] animate-pulse" />
              <h3 class="text-accent-green font-bold text-xs uppercase tracking-widest">Capa de Comunicación</h3>
              <span class="text-[10px] text-gray-500 ml-auto font-mono bg-accent-green/10 px-2 py-0.5 rounded">FastAPI &bull; Python 3.12 &bull; Uvicorn</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div class="bg-dark-bg1 rounded-lg p-2.5 border border-accent-green/15">
                <p class="text-accent-green font-mono font-bold">scenarios.py</p>
                <p class="text-gray-500 text-[10px] mt-1">/allocation, /impact, /summary</p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-2.5 border border-accent-green/15">
                <p class="text-accent-green font-mono font-bold">pareto.py</p>
                <p class="text-gray-500 text-[10px] mt-1">/pareto, /pareto/run/{idx}</p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-2.5 border border-accent-green/15">
                <p class="text-accent-green font-mono font-bold">convergence.py</p>
                <p class="text-gray-500 text-[10px] mt-1">/convergence, /convergence/runs</p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-2.5 border border-accent-green/15">
                <p class="text-accent-green font-mono font-bold">ws.py</p>
                <p class="text-gray-500 text-[10px] mt-1">/ws/simulation (streaming)</p>
              </div>
            </div>
          </div>
        </div>

        <!-- CONEXIÓN API ↔ CORE -->
        <div class="flex items-center justify-center py-1">
          <div class="flex flex-col items-center">
            <div class="w-px h-4 bg-gradient-to-b from-accent-green/40 to-accent-yellow/60" />
            <span class="text-[10px] font-mono text-gray-500 px-2 py-0.5 bg-dark-bg1 rounded border border-dark-border">import app.core</span>
            <div class="w-px h-4 bg-gradient-to-b from-accent-yellow/60 to-accent-red/40" />
          </div>
        </div>

        <!-- CAPA 3: CORE ALGORITHM -->
        <div class="relative rounded-xl p-px bg-gradient-to-r from-accent-yellow/60 via-orange-400/50 to-accent-red/60">
          <div class="bg-dark-bg2 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-3">
              <div class="w-2.5 h-2.5 rounded-full bg-accent-yellow shadow-[0_0_12px_rgba(255,200,0,0.8)] animate-pulse" />
              <h3 class="text-accent-yellow font-bold text-xs uppercase tracking-widest">Motor de Optimización — MOHHO</h3>
              <span class="text-[10px] text-gray-500 ml-auto font-mono bg-accent-yellow/10 px-2 py-0.5 rounded">app/core/ &bull; 7 módulos</span>
            </div>

            <!-- File dependency graph -->
            <div class="bg-black/30 rounded-lg p-4 space-y-3">
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                <div class="bg-accent-yellow/10 rounded-lg p-2 border border-accent-yellow/30 text-center">
                  <p class="text-accent-yellow font-mono text-[11px] font-bold">config.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">Parámetros</p>
                </div>
                <div class="bg-purple-500/10 rounded-lg p-2 border border-purple-500/30 text-center">
                  <p class="text-purple-400 font-mono text-[11px] font-bold">data.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">Demanda</p>
                </div>
                <div class="bg-accent-red/10 rounded-lg p-2 border border-accent-red/30 text-center">
                  <p class="text-accent-red font-mono text-[11px] font-bold">problem.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">f&#8321; f&#8322; f&#8323;</p>
                </div>
                <div class="bg-accent-green/10 rounded-lg p-2 border border-accent-green/30 text-center">
                  <p class="text-accent-green font-mono text-[11px] font-bold">decoder.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">SPV + Greedy</p>
                </div>
                <div class="bg-blue-500/10 rounded-lg p-2 border border-blue-500/30 text-center">
                  <p class="text-blue-400 font-mono text-[11px] font-bold">hho.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">6 Operadores</p>
                </div>
                <div class="bg-orange-500/10 rounded-lg p-2 border border-orange-500/30 text-center">
                  <p class="text-orange-400 font-mono text-[11px] font-bold">mohho.py</p>
                  <p class="text-gray-600 text-[9px] mt-1">Orquestador</p>
                </div>
              </div>

              <!-- Flow arrows -->
              <div class="text-[10px] text-gray-500 text-center font-mono">
                config &rarr; todos &nbsp; | &nbsp;
                data &rarr; problem &nbsp; | &nbsp;
                decoder + hho &rarr; mohho &nbsp; | &nbsp;
                problem &rarr; mohho &nbsp; | &nbsp;
                fifo usa decoder + problem
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/15">
                <p class="text-white font-medium text-xs">Evaluaciones por corrida</p>
                <p class="text-accent-yellow font-bold text-lg font-mono">25,000</p>
                <p class="text-gray-600 text-[10px]">50 halcones &times; 500 iteraciones</p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/15">
                <p class="text-white font-medium text-xs">Dimensión del espacio</p>
                <p class="text-accent-yellow font-bold text-lg font-mono">[0,1]<sup>105</sup></p>
                <p class="text-gray-600 text-[10px]">21 países &times; 5 categorías</p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/15">
                <p class="text-white font-medium text-xs">Resultado final</p>
                <p class="text-accent-green font-bold text-lg font-mono">406</p>
                <p class="text-gray-600 text-[10px]">soluciones Pareto-óptimas</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ====================================== -->
    <!-- 1B. GRAFO DE DEPENDENCIAS .py          -->
    <!-- ====================================== -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">Grafo de Dependencias del Algoritmo</h2>
      <p class="text-sm text-gray-400">
        Flujo de datos entre los 7 módulos Python que implementan la solución completa.
        Las flechas indican la dirección de las llamadas (<code class="text-white">import</code>).
      </p>

      <!-- Visual dependency graph -->
      <div class="bg-dark-bg1 rounded-xl p-6 border border-dark-border overflow-x-auto">
        <div class="min-w-[640px] space-y-6">
          <!-- Row 1: config.py (feeds everything) -->
          <div class="flex justify-center">
            <div class="relative bg-accent-yellow/10 border-2 border-accent-yellow/50 rounded-xl px-6 py-3 shadow-[0_0_20px_rgba(255,200,0,0.15)]">
              <p class="text-accent-yellow font-mono font-bold text-sm">config.py</p>
              <p class="text-gray-500 text-[10px] text-center">V=140k, N=50, T=500, caps</p>
              <div class="absolute -bottom-4 left-1/2 -translate-x-1/2 text-accent-yellow/60 text-sm">&darr;</div>
            </div>
          </div>

          <!-- Dotted "feeds all" line -->
          <div class="flex justify-center">
            <div class="w-3/4 h-px border-t border-dashed border-accent-yellow/30" />
          </div>

          <!-- Row 2: data.py -->
          <div class="flex justify-center">
            <div class="relative bg-purple-500/10 border-2 border-purple-500/40 rounded-xl px-6 py-3 shadow-[0_0_20px_rgba(168,85,247,0.12)]">
              <p class="text-purple-400 font-mono font-bold text-sm">data.py</p>
              <p class="text-gray-500 text-[10px] text-center">21&times;5 datos de demanda, spillover, country caps</p>
              <div class="absolute -bottom-4 left-1/2 -translate-x-1/2 text-purple-400/60 text-sm">&darr;</div>
            </div>
          </div>

          <!-- Row 3: problem.py + decoder.py + hho.py -->
          <div class="grid grid-cols-3 gap-4">
            <div class="bg-accent-red/10 border-2 border-accent-red/40 rounded-xl px-4 py-3 text-center shadow-[0_0_20px_rgba(255,50,50,0.1)]">
              <p class="text-accent-red font-mono font-bold text-sm">problem.py</p>
              <p class="text-gray-500 text-[10px]">VisaProblem</p>
              <p class="text-gray-500 text-[10px]">evaluate() &rarr; f&#8321;, f&#8322;, f&#8323;</p>
            </div>
            <div class="bg-accent-green/10 border-2 border-accent-green/40 rounded-xl px-4 py-3 text-center shadow-[0_0_20px_rgba(0,200,100,0.1)]">
              <p class="text-accent-green font-mono font-bold text-sm">decoder.py</p>
              <p class="text-gray-500 text-[10px]">spv() &rarr; permutación</p>
              <p class="text-gray-500 text-[10px]">decode() &rarr; asignación</p>
            </div>
            <div class="bg-blue-500/10 border-2 border-blue-500/40 rounded-xl px-4 py-3 text-center shadow-[0_0_20px_rgba(59,130,246,0.1)]">
              <p class="text-blue-400 font-mono font-bold text-sm">hho.py</p>
              <p class="text-gray-500 text-[10px]">op1..op6()</p>
              <p class="text-gray-500 text-[10px]">levy_flight(), escape_energy()</p>
            </div>
          </div>

          <!-- Converging arrows -->
          <div class="flex justify-center gap-12 text-gray-500">
            <span class="text-accent-red/60">&searr;</span>
            <span class="text-accent-green/60">&darr;</span>
            <span class="text-blue-400/60">&swarr;</span>
          </div>

          <!-- Row 4: mohho.py (central orchestrator) -->
          <div class="flex justify-center">
            <div class="relative bg-gradient-to-r from-orange-500/15 to-yellow-500/15 border-2 border-orange-400/50 rounded-xl px-8 py-4 shadow-[0_0_30px_rgba(255,150,0,0.2)]">
              <p class="text-orange-400 font-mono font-bold text-base text-center">mohho.py</p>
              <p class="text-gray-400 text-[11px] text-center mt-1">Orquestador principal del MOHHO</p>
              <div class="grid grid-cols-2 gap-3 mt-3 text-[10px]">
                <div class="text-gray-500">
                  <span class="text-orange-400">run_mohho()</span> &mdash; bucle principal
                </div>
                <div class="text-gray-500">
                  <span class="text-orange-400">dominates()</span> &mdash; Pareto
                </div>
                <div class="text-gray-500">
                  <span class="text-orange-400">crowding_distance()</span> &mdash; diversidad
                </div>
                <div class="text-gray-500">
                  <span class="text-orange-400">compute_hypervolume()</span> &mdash; HV 3D
                </div>
                <div class="text-gray-500">
                  <span class="text-orange-400">update_archive()</span> &mdash; archivo
                </div>
                <div class="text-gray-500">
                  <span class="text-orange-400">select_leader()</span> &mdash; presa
                </div>
              </div>
            </div>
          </div>

          <!-- Side branch: fifo.py -->
          <div class="flex justify-end pr-8">
            <div class="bg-gray-500/10 border-2 border-gray-500/30 rounded-xl px-5 py-3 text-center">
              <p class="text-gray-400 font-mono font-bold text-sm">fifo.py</p>
              <p class="text-gray-500 text-[10px]">Línea base (sin optimización)</p>
              <p class="text-gray-600 text-[10px]">Usa: decoder.py + problem.py</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-4 text-[10px]">
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-accent-yellow/30 border border-accent-yellow/50" /><span class="text-gray-400">Configuración</span></div>
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-purple-500/30 border border-purple-500/50" /><span class="text-gray-400">Datos</span></div>
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-accent-red/30 border border-accent-red/50" /><span class="text-gray-400">Evaluación</span></div>
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-accent-green/30 border border-accent-green/50" /><span class="text-gray-400">Decodificación</span></div>
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-blue-500/30 border border-blue-500/50" /><span class="text-gray-400">Operadores HHO</span></div>
        <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded bg-orange-500/30 border border-orange-500/50" /><span class="text-gray-400">Orquestador</span></div>
      </div>
    </section>

    <!-- ============================== -->
    <!-- 2. FLUJO DEL ALGORITMO MOHHO   -->
    <!-- ============================== -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">2. Flujo del Algoritmo MOHHO</h2>
      <p class="text-sm text-gray-400">
        Diagrama del ciclo completo de optimización, desde la inicialización hasta la convergencia del frente de Pareto.
      </p>

      <div class="relative pl-10">
        <!-- Vertical gradient line -->
        <div class="absolute left-[14px] top-2 bottom-2 w-0.5 bg-gradient-to-b from-primary via-accent-yellow to-accent-red rounded-full" />

        <!-- Step 1 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-primary border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
            <p class="text-primary-300 font-bold text-sm mb-1">1. Inicialización</p>
            <p class="text-xs text-gray-400">Generar <strong class="text-white">N</strong> halcones aleatorios en el hipercubo [0,1]<sup>105</sup></p>
            <pre class="mt-2 text-[11px] text-gray-500 font-mono bg-black/30 rounded p-2 overflow-x-auto">population = rng.random((pop_size, 105))   # N vectores continuos
archive = []                                # Archivo Pareto vacío</pre>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-primary border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
            <p class="text-primary-300 font-bold text-sm mb-1">2. Evaluación (por cada halcón)</p>
            <div class="flex flex-wrap items-center gap-2 mt-2 text-xs font-mono">
              <span class="bg-primary/20 text-primary-300 px-2 py-1 rounded">H ∈ [0,1]<sup>105</sup></span>
              <span class="text-gray-500">→</span>
              <span class="bg-accent-yellow/20 text-accent-yellow px-2 py-1 rounded">π = argsort(H)</span>
              <span class="text-gray-500">→</span>
              <span class="bg-accent-green/20 text-accent-green px-2 py-1 rounded">x = greedy(π)</span>
              <span class="text-gray-500">→</span>
              <span class="bg-accent-red/20 text-accent-red px-2 py-1 rounded">F(x) = (f&#8321;, f&#8322;, f&#8323;)</span>
            </div>
            <p class="text-[11px] text-gray-500 mt-2">SPV convierte continuo → permutación; el greedy decoder asigna visas respetando R1–R6.</p>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-green border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
            <p class="text-accent-green font-bold text-sm mb-1">3. Actualizar Archivo Pareto</p>
            <p class="text-xs text-gray-400">
              Insertar soluciones no dominadas. Eliminar las dominadas.
              Si el archivo excede 100 soluciones, podar por <strong class="text-white">crowding distance</strong> mínima.
            </p>
          </div>
        </div>

        <!-- Step 4: Iteration loop -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-yellow border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold text-sm mb-2">4. Bucle Principal (t = 1 … max_iter)</p>
            <p class="text-xs text-gray-400 mb-3">Para cada halcón, seleccionar líder del archivo y calcular energía:</p>
            <div class="bg-black/30 rounded-lg p-3 font-mono text-[11px] text-gray-400 mb-3">
              E(t) = 2 · (1 - t/T) · r&#8320;<span class="text-gray-600"># r&#8320; ∈ [-1,1] aleatorio</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div class="bg-blue-500/10 rounded-lg p-3 border border-blue-500/20">
                <p class="text-blue-400 font-bold mb-1">|E| ≥ 1 → Exploración</p>
                <p class="text-gray-500"><strong>OP1:</strong> Posición aleatoria de la población</p>
                <p class="text-gray-500"><strong>OP2:</strong> Media de la población + presa</p>
              </div>
              <div class="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/20">
                <p class="text-yellow-400 font-bold mb-1">|E| &lt; 1, r ≥ 0.5 → Siege Suave</p>
                <p class="text-gray-500"><strong>OP3:</strong> Siege suave estándar</p>
                <p class="text-gray-500"><strong>OP5:</strong> Siege suave + Lévy</p>
              </div>
              <div class="bg-red-500/10 rounded-lg p-3 border border-red-500/20">
                <p class="text-red-400 font-bold mb-1">|E| &lt; 1, r &lt; 0.5 → Siege Duro</p>
                <p class="text-gray-500"><strong>OP4:</strong> Convergencia agresiva</p>
                <p class="text-gray-500"><strong>OP6:</strong> Siege duro + Lévy</p>
              </div>
            </div>

            <p class="text-[11px] text-gray-500 mt-3">
              Aceptación greedy: si el candidato domina al halcón actual, se reemplaza.
              Luego se actualiza el archivo Pareto y se calcula el hipervolumen 3D.
            </p>
          </div>
        </div>

        <!-- Step 5 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-yellow border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold text-sm mb-1">5. Selección de Líder (Presa)</p>
            <p class="text-xs text-gray-400">
              El "rabbit" (presa) se selecciona del archivo mediante <strong class="text-white">torneo por crowding distance</strong>,
              favoreciendo soluciones en regiones menos densas del frente para mantener diversidad.
            </p>
          </div>
        </div>

        <!-- Step 6 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-green border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
            <p class="text-accent-green font-bold text-sm mb-1">6. Criterio de Parada</p>
            <p class="text-xs text-gray-400">
              Si <code class="text-white">t &lt; max_iter</code> → volver al paso 4.
              Si no, retornar el <strong class="text-accent-green">Frente de Pareto</strong> (archivo completo) y el historial de hipervolumen.
            </p>
          </div>
        </div>

        <!-- Step 7 -->
        <div class="relative">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-red border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-red/20">
            <p class="text-accent-red font-bold text-sm mb-1">7. Post-Procesamiento</p>
            <p class="text-xs text-gray-400">
              Se decodifica cada solución Pareto en una asignación de visas.
              Se seleccionan 5 escenarios (knee point, extremos de cada objetivo, FIFO).
              Se calcula el impacto Δ por país vs. la línea base FIFO.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================ -->
    <!-- 3. PIPELINE DE CODIFICACIÓN -->
    <!-- ================================ -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">3. Pipeline de Codificación: Continuo → Entero</h2>
      <p class="text-sm text-gray-400">
        La codificación indirecta en 3 capas es el puente entre el espacio continuo de MOHHO y el espacio
        discreto del problema de asignación.
      </p>

      <!-- Visual pipeline -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-primary/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-primary/20 text-primary-300 px-2 py-0.5 rounded text-xs font-bold">CAPA 1</span>
            <span class="text-white font-semibold text-sm">Halcón Continuo</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-primary-300">H = [0.32, 0.87, 0.15, 0.64, ...]</p>
            <p class="text-gray-500"># 105 valores ∈ [0, 1]</p>
            <p class="text-gray-500"># cada posición = 1 grupo (país,cat)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            MOHHO evoluciona estos vectores con sus 6 operadores sin modificación.
            El espacio [0,1]<sup>105</sup> es compacto y continuo.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-accent-yellow/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-accent-yellow/20 text-accent-yellow px-2 py-0.5 rounded text-xs font-bold">CAPA 2</span>
            <span class="text-white font-semibold text-sm">SPV → Permutación</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-accent-yellow">π = argsort(H)</p>
            <p class="text-gray-400">H  = [0.32, 0.87, <span class="text-accent-green">0.15</span>, 0.64, ...]</p>
            <p class="text-gray-400">π = [<span class="text-accent-green">2</span>, 0, 3, 1, ...]</p>
            <p class="text-gray-500"># grupo 2 tiene prioridad máxima</p>
          </div>
          <p class="text-[11px] text-gray-500">
            <strong class="text-gray-400">argsort</strong> ordena índices por valor ascendente.
            El grupo con menor valor en H recibe la mayor prioridad de asignación.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-accent-green/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-accent-green/20 text-accent-green px-2 py-0.5 rounded text-xs font-bold">CAPA 3</span>
            <span class="text-white font-semibold text-sm">Decodificador Greedy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-gray-400">for g in π:</p>
            <p class="text-accent-green">x[g] = min(demand[g],</p>
            <p class="text-accent-green">remaining_visas,</p>
            <p class="text-accent-green">country_cap[g],</p>
            <p class="text-accent-green">category_cap[g])</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Asigna visas en orden de prioridad respetando <strong class="text-gray-400">todas las restricciones</strong>
            (R1–R6). Resultado: asignación <em>siempre factible</em>.
          </p>
        </div>
      </div>

      <!-- Detailed SPV explanation -->
      <div class="bg-dark-bg1 rounded-xl p-5 border border-primary/20 space-y-4">
        <h3 class="text-sm font-bold text-primary-300">¿Por qué valores de 0 a 1? ¿Por qué 105 dimensiones?</h3>
        <div class="text-xs text-gray-400 space-y-2 leading-relaxed">
          <p>
            Cada <strong class="text-white">halcón</strong> es un vector de <strong class="text-accent-yellow">105 números reales ∈ [0, 1]</strong>.
            Los 105 valores corresponden a los 105 grupos del problema: <strong class="text-white">21 países × 5 categorías EB</strong>.
          </p>
          <div class="font-mono text-[11px] bg-black/40 rounded p-3 space-y-1.5">
            <p class="text-gray-500"># Ejemplo: un halcón con 105 valores</p>
            <p>
              <span class="text-gray-500">Pos 0</span> <span class="text-primary-300">(China, EB-1)</span> → <span class="text-accent-yellow">0.71</span>
              <span class="text-gray-600 ml-2">← prioridad baja (valor alto)</span>
            </p>
            <p>
              <span class="text-gray-500">Pos 1</span> <span class="text-primary-300">(China, EB-2)</span> → <span class="text-accent-green">0.12</span>
              <span class="text-gray-600 ml-2">← prioridad alta (valor bajo)</span>
            </p>
            <p>
              <span class="text-gray-500">Pos 2</span> <span class="text-primary-300">(China, EB-3)</span> → <span class="text-accent-yellow">0.48</span>
              <span class="text-gray-600 ml-2">← prioridad media</span>
            </p>
            <p class="text-gray-500">... (105 posiciones en total)</p>
            <p>
              <span class="text-gray-500">Pos 104</span> <span class="text-primary-300">(Otros, EB-5)</span> → <span class="text-accent-red">0.95</span>
              <span class="text-gray-600 ml-2">← prioridad muy baja</span>
            </p>
          </div>
          <p>
            Los valores <strong class="text-white">NO representan visas</strong>. Un valor como 0.71 indica la
            <em>prioridad relativa</em> del grupo. Al aplicar <strong class="text-accent-yellow">argsort</strong>,
            los grupos con valores más bajos reciben visas primero:
          </p>
          <div class="font-mono text-[11px] bg-black/40 rounded p-3 space-y-1">
            <p>H = [<span class="text-accent-yellow">0.71</span>, <span class="text-accent-green">0.12</span>, <span class="text-accent-yellow">0.48</span>, <span class="text-accent-red">0.95</span>, ...]</p>
            <p>π = argsort(H) = [<span class="text-accent-green">1</span>, 2, 0, 3, ...]</p>
            <p class="text-gray-500">↓</p>
            <p class="text-white">Grupo 1 (China, EB-2) recibe visas primero → 0.12 es el valor más bajo</p>
            <p class="text-white">Grupo 2 (China, EB-3) recibe visas segundo → 0.48</p>
            <p class="text-white">Grupo 0 (China, EB-1) recibe visas tercero → 0.71</p>
            <p class="text-gray-500">... y así sucesivamente hasta agotar las 140,000 visas</p>
          </div>
          <p>
            <strong class="text-gray-300">¿Por qué [0, 1] y no enteros?</strong> Porque MOHHO es una metaheurística
            <em>continua</em>: sus 6 operadores (exploración, asedio, vuelo de Lévy) mueven los halcones
            en un espacio continuo. SPV es el puente que transforma ese espacio continuo
            en una asignación discreta válida.
          </p>
        </div>
      </div>

      <p class="text-xs text-gray-500 leading-relaxed bg-dark-bg1 rounded-lg p-4">
        <strong class="text-gray-400">Propiedad clave:</strong>
        Vecinos cercanos en [0,1]<sup>105</sup> producen permutaciones similares (pocos intercambios),
        lo que a su vez genera asignaciones similares. Esto preserva la <em>localidad</em> necesaria
        para que la búsqueda heurística sea efectiva: pequeños movimientos del halcón
        → pequeños cambios en prioridad → pequeños ajustes en la asignación.
      </p>
    </section>

    <!-- ================================= -->
    <!-- 4. LOS 6 OPERADORES DE HHO        -->
    <!-- ================================= -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">4. Los 6 Operadores de Harris Hawks</h2>
      <p class="text-sm text-gray-400">
        La energía de escape E(t) = 2(1 - t/T)·r controla la transición entre fases.
        Cada operador modifica la posición del halcón de forma diferente.
      </p>

      <!-- Energy diagram -->
      <div class="bg-dark-bg1 rounded-lg p-4 text-center">
        <div class="flex items-center justify-center gap-4 text-xs font-mono flex-wrap">
          <span class="text-blue-400">|E| = 2.0</span>
          <span class="w-8 h-px bg-blue-400/40" />
          <span class="text-blue-400">Exploración</span>
          <span class="w-8 h-px bg-gray-600" />
          <span class="text-accent-yellow">|E| = 1.0</span>
          <span class="w-8 h-px bg-accent-yellow/40" />
          <span class="text-accent-yellow">Transición</span>
          <span class="w-8 h-px bg-gray-600" />
          <span class="text-accent-red">|E| = 0.0</span>
          <span class="w-8 h-px bg-accent-red/40" />
          <span class="text-accent-red">Siege</span>
        </div>
        <p class="text-[10px] text-gray-600 mt-2">t = 0 → Exploración pura | t = T → Explotación pura</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- OP1 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-blue-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-blue-400/20 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded">OP1</span>
            <span class="text-white font-medium text-sm">Exploración — Aleatoria</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-blue-300">X(t+1) = X_rand - r&#8321; |X_rand - 2r&#8322; X(t)|</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Usa un halcón aleatorio de la población como referencia.
            <strong class="text-gray-400">Condición:</strong> |E| ≥ 1, q ≥ 0.5
          </p>
        </div>

        <!-- OP2 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-blue-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-blue-400/20 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded">OP2</span>
            <span class="text-white font-medium text-sm">Exploración — Media</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-blue-300">X(t+1) = (X_rabbit - X_mean) - r&#8323; (lb + r&#8324; (ub - lb))</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Combina la posición del líder (presa) con la media de toda la población.
            <strong class="text-gray-400">Condición:</strong> |E| ≥ 1, q &lt; 0.5
          </p>
        </div>

        <!-- OP3 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-yellow-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-yellow-400/20 text-yellow-400 text-[10px] font-bold px-2 py-0.5 rounded">OP3</span>
            <span class="text-white font-medium text-sm">Siege Suave</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-yellow-300">X(t+1) = ΔX(t) - E |J·X_rabbit - X(t)|</p>
            <p class="text-gray-500">ΔX = X_rabbit - X(t),  J = 2(1 - r&#8325;)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Acercamiento progresivo. J simula el salto de la presa.
            <strong class="text-gray-400">Condición:</strong> |E| &lt; 1, |E| ≥ 0.5, r ≥ 0.5
          </p>
        </div>

        <!-- OP4 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-red-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-red-400/20 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded">OP4</span>
            <span class="text-white font-medium text-sm">Siege Duro</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-red-300">X(t+1) = X_rabbit - E |ΔX(t)|</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Convergencia agresiva directa hacia la presa.
            <strong class="text-gray-400">Condición:</strong> |E| &lt; 1, |E| &lt; 0.5, r ≥ 0.5
          </p>
        </div>

        <!-- OP5 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-yellow-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-yellow-400/20 text-yellow-400 text-[10px] font-bold px-2 py-0.5 rounded">OP5</span>
            <span class="text-white font-medium text-sm">Siege Suave + Lévy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-yellow-300">Y = X_rabbit - E |J·X_rabbit - X(t)|</p>
            <p class="text-yellow-300">Z = Y + S × Lévy(β=1.5)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Siege suave con perturbación Lévy para escape de óptimos locales.
            Se acepta el mejor entre Y y Z.
            <strong class="text-gray-400">Condición:</strong> |E| ≥ 0.5, r &lt; 0.5
          </p>
        </div>

        <!-- OP6 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-red-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-red-400/20 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded">OP6</span>
            <span class="text-white font-medium text-sm">Siege Duro + Lévy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-red-300">Y = X_rabbit - E |J·X_rabbit - X_mean|</p>
            <p class="text-red-300">Z = Y + S × Lévy(β=1.5)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Siege duro usando la media poblacional. Lévy proporciona saltos largos
            para mayor exploración tardía.
            <strong class="text-gray-400">Condición:</strong> |E| &lt; 0.5, r &lt; 0.5
          </p>
        </div>
      </div>

      <!-- Lévy flight detail -->
      <div class="bg-dark-bg1 rounded-lg p-4 border border-purple-500/20">
        <h3 class="text-purple-400 font-bold text-sm mb-2">Vuelo de Lévy (β = 1.5)</h3>
        <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
          <p class="text-purple-300">σ = (Γ(1+β) · sin(πβ/2) / (Γ((1+β)/2) · β · 2<sup>(β-1)/2</sup>))<sup>1/β</sup></p>
          <p class="text-purple-300">Lévy = u · σ / |v|<sup>1/β</sup>,u,v ~ N(0,1)</p>
        </div>
        <p class="text-[11px] text-gray-500">
          Los vuelos de Lévy generan movimientos con <strong class="text-gray-400">colas pesadas</strong>:
          mayoritariamente pasos cortos con saltos largos ocasionales. Esto permite
          escapar de óptimos locales sin perder la convergencia general.
        </p>
      </div>
    </section>

    <!-- ===================================== -->
    <!-- 5. CONEXIÓN TEORÍA ↔ CÓDIGO -->
    <!-- ===================================== -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">5. Conexión Teoría ↔ Código</h2>
      <p class="text-sm text-gray-400">
        Cada componente teórico del algoritmo tiene su implementación directa en el código.
      </p>

      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-dark-border">
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Concepto Teórico</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Archivo</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Función / Clase</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Descripción</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-border/50">
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Energía de escape E(t)</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">escape_energy()</td>
              <td class="py-2.5 px-3 text-gray-500">E = 2(1 - t/T) · (2r - 1)</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-blue-400 font-medium">OP1: Exploración aleatoria</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op1_exploration_random()</td>
              <td class="py-2.5 px-3 text-gray-500">Referencia: miembro aleatorio</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-blue-400 font-medium">OP2: Exploración media</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op2_exploration_mean()</td>
              <td class="py-2.5 px-3 text-gray-500">Referencia: centroide + presa</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-yellow-400 font-medium">OP3: Siege suave</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op3_soft_siege()</td>
              <td class="py-2.5 px-3 text-gray-500">Persecución gradual</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-red-400 font-medium">OP4: Siege duro</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op4_hard_siege()</td>
              <td class="py-2.5 px-3 text-gray-500">Convergencia directa</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-yellow-400 font-medium">OP5: Siege suave + Lévy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op5_soft_siege_levy()</td>
              <td class="py-2.5 px-3 text-gray-500">Con perturbación Lévy</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-red-400 font-medium">OP6: Siege duro + Lévy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op6_hard_siege_levy()</td>
              <td class="py-2.5 px-3 text-gray-500">Media + Lévy para escape</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-purple-400 font-medium">Vuelo de Lévy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">levy_flight()</td>
              <td class="py-2.5 px-3 text-gray-500">β=1.5, Mantegna's algorithm</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">SPV → Permutación</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">decoder.py</td>
              <td class="py-2.5 px-3 font-mono text-white">spv(hawk)</td>
              <td class="py-2.5 px-3 text-gray-500">argsort estable del vector</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">Decodificador greedy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">decoder.py</td>
              <td class="py-2.5 px-3 font-mono text-white">decode(perm, ...)</td>
              <td class="py-2.5 px-3 text-gray-500">Asignación factible R1–R6</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">Evaluador 3 objetivos</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">problem.py</td>
              <td class="py-2.5 px-3 font-mono text-white">evaluate(allocation)</td>
              <td class="py-2.5 px-3 text-gray-500">f&#8321;, f&#8322;, f&#8323; + visas usadas</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Dominancia Pareto</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">dominates(a, b)</td>
              <td class="py-2.5 px-3 text-gray-500">≤ en todos, &lt; en al menos uno</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Crowding distance</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">crowding_distance()</td>
              <td class="py-2.5 px-3 text-gray-500">NSGA-II para diversidad</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Hipervolumen 3D</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">hypervolume_3d()</td>
              <td class="py-2.5 px-3 text-gray-500">Ref: (10, 16, 50000)</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-red font-medium">Línea base FIFO</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">fifo.py</td>
              <td class="py-2.5 px-3 font-mono text-white">fifo_allocation()</td>
              <td class="py-2.5 px-3 text-gray-500">Orden por fecha de prioridad</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ================================= -->
    <!-- 6. GESTIÓN DEL ARCHIVO PARETO -->
    <!-- ================================= -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">6. Gestión del Archivo Pareto</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
          <h3 class="text-accent-green font-bold text-sm mb-2">Dominancia de Pareto</h3>
          <p class="text-xs text-gray-400 mb-2">
            Una solución <strong class="text-white">a</strong> domina a <strong class="text-white">b</strong> si:
          </p>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2">
            <p class="text-accent-green">a ≤ b en todos los objetivos</p>
            <p class="text-accent-green">a &lt; b en al menos un objetivo</p>
          </div>
          <p class="text-[11px] text-gray-500 mt-2">
            El archivo solo contiene soluciones <strong class="text-gray-400">mutuamente no dominadas</strong>.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
          <h3 class="text-accent-yellow font-bold text-sm mb-2">Crowding Distance (NSGA-II)</h3>
          <p class="text-xs text-gray-400 mb-2">
            Mide el espacio alrededor de cada solución en el frente:
          </p>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2">
            <p class="text-accent-yellow">CD(i) = Σ<sub>m</sub> (f<sub>m</sub>[i+1] - f<sub>m</sub>[i-1]) / (f<sub>m,max</sub> - f<sub>m,min</sub>)</p>
          </div>
          <p class="text-[11px] text-gray-500 mt-2">
            Mayor CD = región menos densa. Se usa para:
            (1) seleccionar líder, (2) podar archivo cuando excede capacidad.
          </p>
        </div>
      </div>

      <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
        <h3 class="text-primary-300 font-bold text-sm mb-2">Hipervolumen 3D</h3>
        <p class="text-xs text-gray-400 mb-2">
          Métrica de calidad del frente de Pareto. Mide el volumen del espacio objetivo
          dominado entre el frente y un punto de referencia.
        </p>
        <div class="font-mono text-[11px] bg-black/30 rounded p-2">
          <p class="text-primary-300">HV = Vol({y ∈ ℜ<sup>3</sup> : ∃ x ∈ PF tal que x ≤ y ≤ ref})</p>
          <p class="text-gray-500">ref = (10.0, 16.0, 50000)   # siempre domina al frente</p>
        </div>
        <p class="text-[11px] text-gray-500 mt-2">
          <strong class="text-gray-400">Mayor HV = mejor frente.</strong>
          Es la única métrica unaria que es Pareto-compatible:
          si el frente A domina completamente al frente B, entonces HV(A) &gt; HV(B).
        </p>
      </div>
    </section>

    <!-- ============================ -->
    <!-- 7. CÓDIGO CLAVE          -->
    <!-- ============================ -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">7. Código Clave</h2>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-yellow">hho.py</strong> — Operador de escape energy + Siege suave
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">escape_energy</span>(t: int, max_t: int, rng) -> float:
    <span class="text-gray-600">"""E(t) decrece de 2 a 0 con ruido."""</span>
    E0 = 2 * rng.random() - 1
    <span class="text-blue-400">return</span> 2 * E0 * (1 - t / max_t)

<span class="text-blue-400">def</span> <span class="text-accent-green">op3_soft_siege</span>(x, x_rabbit, E, J, rng):
    <span class="text-gray-600">"""Siege suave: persecución gradual."""</span>
    delta = x_rabbit - x
    <span class="text-blue-400">return</span> clip_bounds(delta - E * np.abs(J * x_rabbit - x))</pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-green">decoder.py</strong> — SPV + Greedy decoder
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">spv</span>(hawk: np.ndarray) -> np.ndarray:
    <span class="text-gray-600">"""Smallest Position Value: continuo → permutación."""</span>
    <span class="text-blue-400">return</span> np.argsort(hawk, kind=<span class="text-accent-yellow">"stable"</span>)

<span class="text-blue-400">def</span> <span class="text-accent-green">decode</span>(perm, groups, total_visas, country_cap, cat_caps):
    allocation = np.zeros(len(groups), dtype=int)
    remaining = total_visas
    used_country = defaultdict(int)
    used_cat = defaultdict(int)

    <span class="text-blue-400">for</span> idx <span class="text-blue-400">in</span> perm:
        g = groups[idx]
        available = <span class="text-accent-yellow">min</span>(
            g.n,                                  <span class="text-gray-600"># R2: demanda</span>
            remaining,                            <span class="text-gray-600"># R1: presupuesto total</span>
            country_cap - used_country[g.country], <span class="text-gray-600"># R3: tope país</span>
            cat_caps[g.cat] - used_cat[g.cat],     <span class="text-gray-600"># R4: tope categoría</span>
        )
        allocation[idx] = available
        remaining -= available
        used_country[g.country] += available
        used_cat[g.cat] += available

    <span class="text-blue-400">return</span> allocation</pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-primary-300">mohho.py</strong> — Bucle principal + archivo Pareto
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">run_mohho</span>(pop_size, max_iter, seed, callback):
    rng = np.random.default_rng(seed)
    pop = rng.random((pop_size, DIM))         <span class="text-gray-600"># DIM = 105</span>
    archive, archive_fit = [], []

    <span class="text-blue-400">for</span> t <span class="text-blue-400">in</span> range(max_iter):
        x_mean = pop.mean(axis=0)
        rabbit = select_leader(archive, archive_fit, rng)

        <span class="text-blue-400">for</span> i <span class="text-blue-400">in</span> range(pop_size):
            E = escape_energy(t, max_iter, rng)
            r = rng.random()

            <span class="text-blue-400">if</span> abs(E) >= 1:                    <span class="text-gray-600"># Exploración</span>
                candidate = op1(...) <span class="text-blue-400">if</span> r >= 0.5 <span class="text-blue-400">else</span> op2(...)
            <span class="text-blue-400">elif</span> r >= 0.5:                     <span class="text-gray-600"># Siege suave</span>
                candidate = op3(...) <span class="text-blue-400">if</span> abs(E) >= 0.5 <span class="text-blue-400">else</span> op4(...)
            <span class="text-blue-400">else</span>:                              <span class="text-gray-600"># Siege + Lévy</span>
                candidate = op5(...) <span class="text-blue-400">if</span> abs(E) >= 0.5 <span class="text-blue-400">else</span> op6(...)

            fit_cand = evaluate(decode(spv(candidate)))
            <span class="text-blue-400">if</span> dominates(fit_cand, fitness[i]):
                pop[i] = candidate
            update_archive(candidate, fit_cand)

        hv = hypervolume_3d(archive_fit, REF_POINT)
        callback(t, archive, hv)            <span class="text-gray-600"># Stream a frontend</span></pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-red">problem.py</strong> — Funciones objetivo
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">evaluate</span>(alloc, groups):
    total_demand = sum(g.n <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups)

    <span class="text-gray-600"># f1: carga de espera ponderada</span>
    f1 = sum((g.n - alloc[g.idx]) * g.w <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups) / total_demand

    <span class="text-gray-600"># f2: disparidad máxima entre países</span>
    country_waits = {}
    <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups:
        <span class="text-gray-600"># calcular espera promedio ponderada por país</span>
        ...
    f2 = max(country_waits.values()) - min(country_waits.values())

    <span class="text-gray-600"># f3: visas desperdiciadas</span>
    f3 = TOTAL_VISAS - sum(alloc)

    <span class="text-blue-400">return</span> (f1, f2, f3)</pre>
      </details>
    </section>

    <!-- ============================= -->
    <!-- 8. VISOR DE CÓDIGO FUENTE      -->
    <!-- ============================= -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">8. Código Fuente del Algoritmo</h2>
      <p class="text-sm text-gray-400">
        Haz clic en cualquier archivo para ver su código fuente completo, comentado en español.
        Estos 6 archivos implementan la solución MOHHO completa.
      </p>

      <!-- config.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'config' ? 'border-accent-yellow/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-accent-yellow/5 transition-colors" @click="toggleFile('config')">
          <div class="w-8 h-8 rounded-lg bg-accent-yellow/15 flex items-center justify-center flex-shrink-0">
            <span class="text-accent-yellow text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-accent-yellow font-mono font-bold text-sm">config.py</p>
            <p class="text-gray-500 text-[11px]">Parámetros globales: V=140,000 visas, N=50, T=500, caps por país y categoría</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">62 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'config' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'config'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Parámetros de configuración para la optimización MOHHO de visas."""</span>

<span class="text-gray-600"># ── Presupuesto total de visas EB (fuente: INA §203) ──</span>
<span class="text-accent-yellow">V</span>: int = <span class="text-purple-400">140,000</span>          <span class="text-gray-600"># visas EB disponibles por año fiscal</span>
<span class="text-accent-yellow">V_TOTAL</span>: int = <span class="text-purple-400">366,000</span>    <span class="text-gray-600"># demanda total registrada</span>
<span class="text-accent-yellow">P_C</span>: int = <span class="text-purple-400">25,620</span>        <span class="text-gray-600"># tope per-country (7% de 366,000)</span>
<span class="text-accent-yellow">T_ACTUAL</span>: int = <span class="text-purple-400">2026</span>      <span class="text-gray-600"># año fiscal actual</span>

<span class="text-gray-600"># ── Topes base por categoría (antes de spillover) ──</span>
<span class="text-accent-yellow">K_BASE</span>: dict = {
    <span class="text-accent-green">"EB-1"</span>: <span class="text-purple-400">40,040</span>,   <span class="text-gray-600"># 28.6% de 140k — Extraordinarios</span>
    <span class="text-accent-green">"EB-2"</span>: <span class="text-purple-400">40,040</span>,   <span class="text-gray-600"># 28.6% de 140k — Profesionales</span>
    <span class="text-accent-green">"EB-3"</span>: <span class="text-purple-400">40,040</span>,   <span class="text-gray-600"># 28.6% de 140k — Calificados</span>
    <span class="text-accent-green">"EB-4"</span>: <span class="text-purple-400">9,940</span>,    <span class="text-gray-600"># 7.1%  — Especiales (SIV)</span>
    <span class="text-accent-green">"EB-5"</span>: <span class="text-purple-400">9,940</span>,    <span class="text-gray-600"># 7.1%  — Inversores</span>
}

<span class="text-gray-600"># ── Hiperparámetros del algoritmo MOHHO ──</span>
<span class="text-accent-yellow">POPULATION_SIZE</span>: int = <span class="text-purple-400">50</span>    <span class="text-gray-600"># N halcones (agentes de búsqueda)</span>
<span class="text-accent-yellow">MAX_ITERATIONS</span>: int = <span class="text-purple-400">500</span>   <span class="text-gray-600"># T iteraciones por corrida</span>
<span class="text-accent-yellow">NUM_RUNS</span>: int = <span class="text-purple-400">30</span>          <span class="text-gray-600"># corridas independientes (TLC: n≥30)</span>
<span class="text-accent-yellow">ARCHIVE_SIZE</span>: int = <span class="text-purple-400">100</span>    <span class="text-gray-600"># máx. soluciones en archivo Pareto</span>
<span class="text-accent-yellow">SEED_BASE</span>: int = <span class="text-purple-400">42</span>        <span class="text-gray-600"># semilla inicial (42, 43, ..., 71)</span>
<span class="text-accent-yellow">LB</span>: float = <span class="text-purple-400">0.0</span>            <span class="text-gray-600"># límite inferior del hipercubo</span>
<span class="text-accent-yellow">UB</span>: float = <span class="text-purple-400">1.0</span>            <span class="text-gray-600"># límite superior del hipercubo</span>
<span class="text-accent-yellow">BETA_LEVY</span>: float = <span class="text-purple-400">1.5</span>    <span class="text-gray-600"># exponente del vuelo de Lévy</span>

<span class="text-gray-600"># ── Dimensión del problema ──</span>
<span class="text-accent-yellow">NUM_COUNTRIES</span>: int = <span class="text-purple-400">21</span>     <span class="text-gray-600"># bloques de países</span>
<span class="text-accent-yellow">NUM_CATEGORIES</span>: int = <span class="text-purple-400">5</span>    <span class="text-gray-600"># categorías EB-1 a EB-5</span>
<span class="text-accent-yellow">NUM_GROUPS</span>: int = <span class="text-purple-400">105</span>      <span class="text-gray-600"># 21 × 5 = dimensión del halcón</span>

<span class="text-gray-600"># ── Lista de 21 países (orden del Visa Bulletin) ──</span>
<span class="text-accent-yellow">COUNTRIES</span> = [<span class="text-accent-green">"India"</span>, <span class="text-accent-green">"China"</span>, <span class="text-accent-green">"Filipinas"</span>, <span class="text-accent-green">"Mexico"</span>, ...]
<span class="text-accent-yellow">CATEGORIES</span> = [<span class="text-accent-green">"EB-1"</span>, <span class="text-accent-green">"EB-2"</span>, <span class="text-accent-green">"EB-3"</span>, <span class="text-accent-green">"EB-4"</span>, <span class="text-accent-green">"EB-5"</span>]</pre>
        </div>
      </div>

      <!-- problem.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'problem' ? 'border-accent-red/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-accent-red/5 transition-colors" @click="toggleFile('problem')">
          <div class="w-8 h-8 rounded-lg bg-accent-red/15 flex items-center justify-center flex-shrink-0">
            <span class="text-accent-red text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-accent-red font-mono font-bold text-sm">problem.py</p>
            <p class="text-gray-500 text-[11px]">Definición del problema: 3 funciones objetivo f&#8321;, f&#8322;, f&#8323; y la clase VisaProblem</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">44 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'problem' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'problem'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Definición del problema: funciones objetivo f1, f2, f3."""</span>

<span class="text-blue-400">from</span> app.core.config <span class="text-blue-400">import</span> V          <span class="text-gray-600"># presupuesto total</span>
<span class="text-blue-400">from</span> app.core.data <span class="text-blue-400">import</span> build_groups, compute_spillover, compute_country_caps


<span class="text-blue-400">class</span> <span class="text-accent-yellow">VisaProblem</span>:
    <span class="text-gray-600">"""Encapsula los datos del problema y las 3 funciones objetivo."""</span>

    <span class="text-blue-400">def</span> <span class="text-accent-green">__init__</span>(self):
        self.groups = build_groups()              <span class="text-gray-600"># 105 grupos (país, categoría)</span>
        self.category_caps = compute_spillover(self.groups)  <span class="text-gray-600"># topes con cascade</span>
        self.country_caps = compute_country_caps(self.groups) <span class="text-gray-600"># tope per-country</span>
        self.total_visas = V                      <span class="text-gray-600"># 140,000</span>
        self.total_demand = sum(g[<span class="text-accent-green">"n"</span>] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> self.groups)  <span class="text-gray-600"># 366,000</span>

        <span class="text-gray-600"># Índices agrupados por país (para calcular f2 rápidamente)</span>
        self._groups_by_country = {}
        <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> self.groups:
            self._groups_by_country.setdefault(g[<span class="text-accent-green">"country"</span>], []).append(g)

    <span class="text-blue-400">def</span> <span class="text-accent-green">evaluate</span>(self, x) -> tuple[float, float, float]:
        <span class="text-gray-600">"""Evalúa una asignación x y retorna (f1, f2, f3)."""</span>
        <span class="text-blue-400">return</span> self.f1(x), self.f2(x), self.f3(x)

    <span class="text-blue-400">def</span> <span class="text-accent-green">f1</span>(self, x) -> float:
        <span class="text-gray-600">"""f₁: Carga de espera ponderada.</span>
<span class="text-gray-600">        Σ (demanda_no_satisfecha × años_esperando) / demanda_total</span>
<span class="text-gray-600">        Menor = menos gente esperando menos tiempo."""</span>
        numerator = sum((g[<span class="text-accent-green">"n"</span>] - x[g[<span class="text-accent-green">"index"</span>]]) * g[<span class="text-accent-green">"w"</span>] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> self.groups)
        <span class="text-blue-400">return</span> numerator / self.total_demand

    <span class="text-blue-400">def</span> <span class="text-accent-green">f2</span>(self, x) -> float:
        <span class="text-gray-600">"""f₂: Disparidad máxima entre países.</span>
<span class="text-gray-600">        max(espera_país) - min(espera_país)</span>
<span class="text-gray-600">        Menor = más equidad entre todos los países."""</span>
        w_country = {}
        <span class="text-blue-400">for</span> country, gs <span class="text-blue-400">in</span> self._groups_by_country.items():
            total_assigned = sum(x[g[<span class="text-accent-green">"index"</span>]] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> gs)
            <span class="text-blue-400">if</span> total_assigned > 0:
                weighted_wait = sum(x[g[<span class="text-accent-green">"index"</span>]] * g[<span class="text-accent-green">"w"</span>] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> gs)
                w_country[country] = weighted_wait / total_assigned
            <span class="text-blue-400">else</span>:
                w_country[country] = float(self._country_w_max[country])
        <span class="text-blue-400">return</span> max(w_country.values()) - min(w_country.values())

    <span class="text-blue-400">def</span> <span class="text-accent-green">f3</span>(self, x) -> float:
        <span class="text-gray-600">"""f₃: Visas desperdiciadas.</span>
<span class="text-gray-600">        140,000 - Σ visas_asignadas</span>
<span class="text-gray-600">        Menor = mayor utilización del presupuesto."""</span>
        <span class="text-blue-400">return</span> float(self.total_visas - sum(x[g[<span class="text-accent-green">"index"</span>]] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> self.groups))</pre>
        </div>
      </div>

      <!-- decoder.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'decoder' ? 'border-accent-green/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-accent-green/5 transition-colors" @click="toggleFile('decoder')">
          <div class="w-8 h-8 rounded-lg bg-accent-green/15 flex items-center justify-center flex-shrink-0">
            <span class="text-accent-green text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-accent-green font-mono font-bold text-sm">decoder.py</p>
            <p class="text-gray-500 text-[11px]">SPV (Smallest Position Value) y decodificador greedy con restricciones</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">37 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'decoder' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'decoder'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Decodificación SPV y asignador greedy de visas."""</span>

<span class="text-blue-400">import</span> numpy <span class="text-blue-400">as</span> np


<span class="text-blue-400">def</span> <span class="text-accent-green">spv</span>(hawk: np.ndarray) -> list[int]:
    <span class="text-gray-600">"""Smallest Position Value: convierte vector continuo → permutación.</span>
<span class="text-gray-600">    argsort ordena los índices por valor ascendente.</span>
<span class="text-gray-600">    El grupo con menor valor recibe la prioridad más alta."""</span>
    <span class="text-blue-400">return</span> list(np.argsort(hawk, kind=<span class="text-accent-green">"stable"</span>))


<span class="text-blue-400">def</span> <span class="text-accent-green">decode</span>(
    permutation: list[int],    <span class="text-gray-600"># orden de prioridad (de spv)</span>
    groups: list[dict],         <span class="text-gray-600"># 105 grupos con demanda y metadatos</span>
    total_visas: int,           <span class="text-gray-600"># presupuesto = 140,000</span>
    country_caps: dict,         <span class="text-gray-600"># tope per-country = 25,620</span>
    category_caps: dict,        <span class="text-gray-600"># topes por categoría (con spillover)</span>
) -> dict[int, int]:
    <span class="text-gray-600">"""Asignador greedy: recorre grupos en orden de prioridad,</span>
<span class="text-gray-600">    asignando visas hasta agotar el presupuesto o saturar los topes.</span>
<span class="text-gray-600">    SIEMPRE produce una asignación factible (respeta R1–R6)."""</span>
    x = {g[<span class="text-accent-green">"index"</span>]: 0 <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups}   <span class="text-gray-600"># asignación vacía</span>
    v_remaining = total_visas                    <span class="text-gray-600"># visas disponibles</span>
    country_usage = {}                            <span class="text-gray-600"># uso acumulado por país</span>
    category_usage = {}                           <span class="text-gray-600"># uso acumulado por categoría</span>
    group_lookup = {g[<span class="text-accent-green">"index"</span>]: g <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups}

    <span class="text-blue-400">for</span> g_idx <span class="text-blue-400">in</span> permutation:           <span class="text-gray-600"># recorrer en orden de prioridad</span>
        g = group_lookup[g_idx]
        country = g[<span class="text-accent-green">"country"</span>]
        category = g[<span class="text-accent-green">"category"</span>]
        <span class="text-gray-600"># Calcular cuántas visas se pueden asignar a este grupo:</span>
        cap_country = country_caps[country] - country_usage.get(country, 0)
        cap_category = category_caps[category] - category_usage.get(category, 0)
        x_g = <span class="text-accent-yellow">min</span>(
            g[<span class="text-accent-green">"n"</span>],          <span class="text-gray-600"># R2: no exceder la demanda</span>
            v_remaining,      <span class="text-gray-600"># R1: no exceder presupuesto total</span>
            cap_country,      <span class="text-gray-600"># R3: no exceder tope del país</span>
            cap_category,     <span class="text-gray-600"># R4: no exceder tope de categoría</span>
        )
        x[g_idx] = x_g
        v_remaining -= x_g
        country_usage[country] = country_usage.get(country, 0) + x_g
        category_usage[category] = category_usage.get(category, 0) + x_g

    <span class="text-blue-400">return</span> x   <span class="text-gray-600"># asignación factible: 105 enteros</span></pre>
        </div>
      </div>

      <!-- hho.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'hho' ? 'border-blue-400/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-blue-500/5 transition-colors" @click="toggleFile('hho')">
          <div class="w-8 h-8 rounded-lg bg-blue-500/15 flex items-center justify-center flex-shrink-0">
            <span class="text-blue-400 text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-blue-400 font-mono font-bold text-sm">hho.py</p>
            <p class="text-gray-500 text-[11px]">6 operadores de Harris Hawks + vuelo de Lévy + energía de escape</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">69 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'hho' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'hho'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Harris Hawks Optimization — los 6 operadores de caza."""</span>

<span class="text-blue-400">import</span> math, numpy <span class="text-blue-400">as</span> np
<span class="text-blue-400">from</span> app.core.config <span class="text-blue-400">import</span> BETA_LEVY, LB, UB


<span class="text-blue-400">def</span> <span class="text-accent-green">levy_flight</span>(dim: int, rng) -> np.ndarray:
    <span class="text-gray-600">"""Vuelo de Lévy (β=1.5): genera pasos con colas pesadas.</span>
<span class="text-gray-600">    Pasos cortos frecuentes + saltos largos ocasionales.</span>
<span class="text-gray-600">    Permite escapar de óptimos locales."""</span>
    beta = BETA_LEVY
    sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2)
             / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
            ) ** (1 / beta)
    u = rng.normal(0, sigma, size=dim)   <span class="text-gray-600"># numerador</span>
    v = rng.normal(0, 1, size=dim)       <span class="text-gray-600"># denominador</span>
    <span class="text-blue-400">return</span> 0.01 * u / (np.abs(v) ** (1 / beta))


<span class="text-blue-400">def</span> <span class="text-accent-green">clip_bounds</span>(x):
    <span class="text-gray-600">"""Restringe el vector al hipercubo [0, 1]^105."""</span>
    <span class="text-blue-400">return</span> np.clip(x, LB, UB)


<span class="text-blue-400">def</span> <span class="text-accent-green">escape_energy</span>(t: int, max_t: int, rng) -> float:
    <span class="text-gray-600">"""Energía de escape: E(t) = 2·E₀·(1 - t/T).</span>
<span class="text-gray-600">    Decrece de ±2 → 0 a lo largo de las iteraciones.</span>
<span class="text-gray-600">    |E| ≥ 1 → exploración  |  |E| &lt; 1 → explotación"""</span>
    e0 = 2 * rng.random() - 1          <span class="text-gray-600"># E₀ ∈ [-1, 1]</span>
    <span class="text-blue-400">return</span> 2 * e0 * (1 - t / max_t)


<span class="text-gray-600"># ── FASE DE EXPLORACIÓN (|E| ≥ 1) ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">op1_exploration_random</span>(xi, x_rand, rng):
    <span class="text-gray-600">"""OP1: Referencia aleatoria de la población."""</span>
    r1, r2 = rng.random(), rng.random()
    <span class="text-blue-400">return</span> clip_bounds(x_rand - r1 * np.abs(x_rand - 2 * r2 * xi))

<span class="text-blue-400">def</span> <span class="text-accent-green">op2_exploration_mean</span>(xi, x_rabbit, x_mean, rng):
    <span class="text-gray-600">"""OP2: Combina posición del líder (presa) con media poblacional."""</span>
    r3 = rng.random()
    r4 = rng.random(size=xi.shape[0])
    <span class="text-blue-400">return</span> clip_bounds((x_rabbit - x_mean) - r3 * (LB + r4 * (UB - LB)))


<span class="text-gray-600"># ── FASE DE SIEGE (|E| &lt; 1) ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">op3_soft_siege</span>(xi, x_rabbit, energy, rng):
    <span class="text-gray-600">"""OP3: Asedio suave — persecución gradual hacia la presa.</span>
<span class="text-gray-600">    J simula el salto evasivo del conejo."""</span>
    j = 2 * (1 - rng.random())          <span class="text-gray-600"># salto del conejo</span>
    delta_x = x_rabbit - xi             <span class="text-gray-600"># dirección a la presa</span>
    <span class="text-blue-400">return</span> clip_bounds(delta_x - energy * np.abs(j * x_rabbit - xi))

<span class="text-blue-400">def</span> <span class="text-accent-green">op4_hard_siege</span>(xi, x_rabbit, energy, rng):
    <span class="text-gray-600">"""OP4: Asedio duro — convergencia directa y agresiva."""</span>
    delta_x = x_rabbit - xi
    <span class="text-blue-400">return</span> clip_bounds(x_rabbit - energy * np.abs(delta_x))


<span class="text-gray-600"># ── SIEGE + VUELO DE LÉVY ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">op5_soft_siege_levy</span>(xi, x_rabbit, energy, rng):
    <span class="text-gray-600">"""OP5: Siege suave + perturbación Lévy.</span>
<span class="text-gray-600">    Genera candidato Y (siege) y Z (Y + Lévy).</span>
<span class="text-gray-600">    Se acepta el mejor entre Y y Z."""</span>
    j = 2 * (1 - rng.random())
    y = clip_bounds(x_rabbit - energy * np.abs(j * x_rabbit - xi))
    s = rng.random(size=xi.shape[0])
    z = clip_bounds(y + s * levy_flight(xi.shape[0], rng))
    <span class="text-blue-400">return</span> y, z

<span class="text-blue-400">def</span> <span class="text-accent-green">op6_hard_siege_levy</span>(xi, x_rabbit, energy, x_mean, rng):
    <span class="text-gray-600">"""OP6: Siege duro usando media poblacional + Lévy.</span>
<span class="text-gray-600">    Máxima diversificación en etapas tardías."""</span>
    j = 2 * (1 - rng.random())
    y = clip_bounds(x_rabbit - energy * np.abs(j * x_rabbit - x_mean))
    s = rng.random(size=xi.shape[0])
    z = clip_bounds(y + s * levy_flight(xi.shape[0], rng))
    <span class="text-blue-400">return</span> y, z</pre>
        </div>
      </div>

      <!-- mohho.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'mohho' ? 'border-orange-400/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-orange-500/5 transition-colors" @click="toggleFile('mohho')">
          <div class="w-8 h-8 rounded-lg bg-orange-500/15 flex items-center justify-center flex-shrink-0">
            <span class="text-orange-400 text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-orange-400 font-mono font-bold text-sm">mohho.py</p>
            <p class="text-gray-500 text-[11px]">Orquestador MOHHO: bucle principal, archivo Pareto, dominancia, crowding distance, hipervolumen 3D</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">275 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'mohho' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'mohho'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Multi-Objective Harris Hawks Optimization (MOHHO).</span>
<span class="text-gray-600">Archivo principal que orquesta toda la optimización."""</span>

<span class="text-blue-400">import</span> numpy <span class="text-blue-400">as</span> np
<span class="text-blue-400">from</span> app.core.config <span class="text-blue-400">import</span> POPULATION_SIZE, MAX_ITERATIONS, ARCHIVE_SIZE, NUM_GROUPS
<span class="text-blue-400">from</span> app.core.decoder <span class="text-blue-400">import</span> spv, decode
<span class="text-blue-400">from</span> app.core.hho <span class="text-blue-400">import</span> escape_energy, op1..op6
<span class="text-blue-400">from</span> app.core.problem <span class="text-blue-400">import</span> VisaProblem

<span class="text-accent-yellow">HV_REF_POINT</span> = (<span class="text-purple-400">10.0</span>, <span class="text-purple-400">16.0</span>, <span class="text-purple-400">50,000.0</span>)  <span class="text-gray-600"># punto de referencia para HV</span>


<span class="text-gray-600"># ── DOMINANCIA DE PARETO ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">dominates</span>(a, b) -> bool:
    <span class="text-gray-600">"""a domina a b si: a ≤ b en todo, y a &lt; b en al menos uno.</span>
<span class="text-gray-600">    Como los 3 objetivos se minimizan, 'menor es mejor'."""</span>
    <span class="text-blue-400">return</span> (a[0] &lt;= b[0] <span class="text-blue-400">and</span> a[1] &lt;= b[1] <span class="text-blue-400">and</span> a[2] &lt;= b[2]) \
       <span class="text-blue-400">and</span> (a[0] &lt; b[0] <span class="text-blue-400">or</span> a[1] &lt; b[1] <span class="text-blue-400">or</span> a[2] &lt; b[2])


<span class="text-gray-600"># ── CROWDING DISTANCE (NSGA-II) ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">crowding_distance</span>(fitnesses) -> list[float]:
    <span class="text-gray-600">"""Mide el 'espacio' alrededor de cada solución en el frente.</span>
<span class="text-gray-600">    Soluciones en regiones menos densas → mayor CD.</span>
<span class="text-gray-600">    Se usa para: selección de líder y poda del archivo."""</span>
    n = len(fitnesses)
    distances = [0.0] * n
    <span class="text-blue-400">for</span> m <span class="text-blue-400">in</span> range(3):              <span class="text-gray-600"># para cada objetivo</span>
        indices = sorted(range(n), key=<span class="text-blue-400">lambda</span> i: fitnesses[i][m])
        distances[indices[0]] = float(<span class="text-accent-green">"inf"</span>)   <span class="text-gray-600"># extremos → infinito</span>
        distances[indices[-1]] = float(<span class="text-accent-green">"inf"</span>)
        span = fitnesses[indices[-1]][m] - fitnesses[indices[0]][m]
        <span class="text-blue-400">if</span> span == 0: <span class="text-blue-400">continue</span>
        <span class="text-blue-400">for</span> k <span class="text-blue-400">in</span> range(1, n - 1):   <span class="text-gray-600"># puntos intermedios</span>
            diff = fitnesses[indices[k+1]][m] - fitnesses[indices[k-1]][m]
            distances[indices[k]] += diff / span
    <span class="text-blue-400">return</span> distances


<span class="text-gray-600"># ── SELECCIÓN DE LÍDER (PRESA) ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">select_leader</span>(archive_positions, archive_fitnesses, rng):
    <span class="text-gray-600">"""Selecciona la 'presa' (rabbit) del archivo Pareto.</span>
<span class="text-gray-600">    Probabilidad proporcional a crowding distance:</span>
<span class="text-gray-600">    favorece soluciones en regiones poco densas → diversidad."""</span>
    cd = crowding_distance(archive_fitnesses)
    probs = np.array(cd) / sum(cd)
    idx = rng.choice(len(archive_positions), p=probs)
    <span class="text-blue-400">return</span> archive_positions[idx]


<span class="text-gray-600"># ── ACTUALIZACIÓN DEL ARCHIVO ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">update_archive</span>(archive_pos, archive_fit, new_pos, new_fit, max_size):
    <span class="text-gray-600">"""Inserta solución si no es dominada. Elimina las que domina.</span>
<span class="text-gray-600">    Si el archivo excede max_size, poda por menor crowding distance.</span>
<span class="text-gray-600">    Esto mantiene diversidad: elimina en zonas congestionadas."""</span>
    <span class="text-gray-600"># 1. Si alguien en el archivo domina a new → descartarla</span>
    <span class="text-blue-400">for</span> af <span class="text-blue-400">in</span> archive_fit:
        <span class="text-blue-400">if</span> dominates(af, new_fit): <span class="text-blue-400">return</span>
    <span class="text-gray-600"># 2. Eliminar del archivo las que new domina</span>
    dominated = [i <span class="text-blue-400">for</span> i, af <span class="text-blue-400">in</span> enumerate(archive_fit) <span class="text-blue-400">if</span> dominates(new_fit, af)]
    <span class="text-blue-400">for</span> i <span class="text-blue-400">in</span> sorted(dominated, reverse=True):
        archive_pos.pop(i); archive_fit.pop(i)
    <span class="text-gray-600"># 3. Insertar new</span>
    archive_pos.append(new_pos.copy())
    archive_fit.append(new_fit)
    <span class="text-gray-600"># 4. Podar si excede capacidad</span>
    <span class="text-blue-400">if</span> len(archive_pos) > max_size:
        cd = crowding_distance(archive_fit)
        min_cd_idx = min(range(len(cd)), key=<span class="text-blue-400">lambda</span> i: cd[i])
        archive_pos.pop(min_cd_idx); archive_fit.pop(min_cd_idx)


<span class="text-gray-600"># ── BUCLE PRINCIPAL MOHHO ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">run_mohho</span>(problem, seed, pop_size=50, max_iter=500, archive_size=100):
    <span class="text-gray-600">"""Ejecuta una corrida completa del algoritmo MOHHO.</span>
<span class="text-gray-600">    Retorna: (posiciones_archivo, fitness_archivo, historial_HV)"""</span>
    rng = np.random.default_rng(seed)
    population = rng.uniform(0, 1, size=(pop_size, <span class="text-purple-400">105</span>))  <span class="text-gray-600"># halcones</span>

    <span class="text-gray-600"># Evaluar población inicial</span>
    fitnesses = [evaluate_hawk(pop[i], problem) <span class="text-blue-400">for</span> i <span class="text-blue-400">in</span> range(pop_size)]
    archive_pos, archive_fit = [], []

    <span class="text-blue-400">for</span> t <span class="text-blue-400">in</span> range(max_iter):           <span class="text-gray-600"># T = 500 iteraciones</span>
        x_mean = np.mean(population, axis=0)  <span class="text-gray-600"># centroide de la población</span>
        <span class="text-blue-400">for</span> i <span class="text-blue-400">in</span> range(pop_size):        <span class="text-gray-600"># N = 50 halcones</span>
            E = escape_energy(t, max_iter, rng)
            x_rabbit = select_leader(archive_pos, archive_fit, rng)

            <span class="text-blue-400">if</span> abs(E) >= 1:              <span class="text-gray-600"># EXPLORACIÓN</span>
                candidate = op1() <span class="text-blue-400">or</span> op2()
            <span class="text-blue-400">elif</span> rng.random() >= 0.5:    <span class="text-gray-600"># SIEGE (sin Lévy)</span>
                candidate = op3() <span class="text-blue-400">or</span> op4()
            <span class="text-blue-400">else</span>:                        <span class="text-gray-600"># SIEGE + LÉVY</span>
                candidate = op5() <span class="text-blue-400">or</span> op6()

            <span class="text-gray-600"># Aceptación greedy: si domina, reemplazar</span>
            fit_cand = evaluate(decode(spv(candidate)))
            <span class="text-blue-400">if</span> dominates(fit_cand, fitnesses[i]):
                population[i] = candidate
            update_archive(archive_pos, archive_fit, candidate, fit_cand)

        hv = compute_hypervolume(archive_fit)  <span class="text-gray-600"># HV 3D del frente</span>
        hv_history.append(hv)

    <span class="text-blue-400">return</span> archive_pos, archive_fit, hv_history


<span class="text-gray-600"># ── HIPERVOLUMEN 3D ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">compute_hypervolume</span>(fitnesses, ref_point=(10, 16, 50000)):
    <span class="text-gray-600">"""Calcula el volumen 3D dominado entre el frente y ref_point.</span>
<span class="text-gray-600">    Algoritmo: cortes en f₁, para cada corte calcular HV 2D en (f₂, f₃).</span>
<span class="text-gray-600">    Mayor HV = mejor frente de Pareto."""</span>
    pts = sorted(fitnesses, key=<span class="text-blue-400">lambda</span> p: p[0])
    hv = 0.0
    <span class="text-blue-400">for</span> i, (f1, f2, f3) <span class="text-blue-400">in</span> enumerate(pts):
        f1_next = pts[i+1][0] <span class="text-blue-400">if</span> i+1 &lt; len(pts) <span class="text-blue-400">else</span> ref_point[0]
        width = f1_next - f1          <span class="text-gray-600"># ancho de la rebanada en f₁</span>
        slice_2d = [(p[1], p[2]) <span class="text-blue-400">for</span> p <span class="text-blue-400">in</span> pts[:i+1]]
        hv += width * hv_2d(slice_2d) <span class="text-gray-600"># área 2D × ancho</span>
    <span class="text-blue-400">return</span> hv                         <span class="text-gray-600"># ~ 1,800,000</span></pre>
        </div>
      </div>

      <!-- fifo.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'fifo' ? 'border-gray-400/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-500/5 transition-colors" @click="toggleFile('fifo')">
          <div class="w-8 h-8 rounded-lg bg-gray-500/15 flex items-center justify-center flex-shrink-0">
            <span class="text-gray-400 text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-gray-400 font-mono font-bold text-sm">fifo.py</p>
            <p class="text-gray-500 text-[11px]">Línea base FIFO: simula el sistema actual de asignación por fecha de prioridad</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">18 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'fifo' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'fifo'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Línea base FIFO: simula el sistema actual de asignación.</span>
<span class="text-gray-600">Los grupos se ordenan por fecha de prioridad (d).</span>
<span class="text-gray-600">Es el 'adversario' contra el que MOHHO debe mejorar."""</span>

<span class="text-blue-400">from</span> app.core.decoder <span class="text-blue-400">import</span> decode
<span class="text-blue-400">from</span> app.core.problem <span class="text-blue-400">import</span> VisaProblem


<span class="text-blue-400">def</span> <span class="text-accent-green">fifo_permutation</span>(groups) -> list[int]:
    <span class="text-gray-600">"""Ordena los 105 grupos por fecha de prioridad (ascendente).</span>
<span class="text-gray-600">    Los que llevan más tiempo esperando reciben visas primero.</span>
<span class="text-gray-600">    Es la política actual del Visa Bulletin de USCIS."""</span>
    sorted_groups = sorted(groups, key=<span class="text-blue-400">lambda</span> g: (g[<span class="text-accent-green">"d"</span>], g[<span class="text-accent-green">"index"</span>]))
    <span class="text-blue-400">return</span> [g[<span class="text-accent-green">"index"</span>] <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> sorted_groups]


<span class="text-blue-400">def</span> <span class="text-accent-green">run_baseline</span>(problem: VisaProblem):
    <span class="text-gray-600">"""Ejecuta la asignación FIFO y devuelve (asignación, fitness).</span>
<span class="text-gray-600">    Resultado: f₁=7.21, f₂=12.64, f₃=17,540</span>
<span class="text-gray-600">    → MOHHO mejora los 3 objetivos simultáneamente."""</span>
    perm = fifo_permutation(problem.groups)    <span class="text-gray-600"># orden temporal</span>
    alloc = decode(perm, problem.groups,       <span class="text-gray-600"># decodificar</span>
                   problem.total_visas,
                   problem.country_caps,
                   problem.category_caps)
    fitness = problem.evaluate(alloc)           <span class="text-gray-600"># evaluar (f1,f2,f3)</span>
    <span class="text-blue-400">return</span> alloc, fitness</pre>
        </div>
      </div>

      <!-- data.py -->
      <div class="bg-dark-bg1 rounded-lg border overflow-hidden" :class="expandedFile === 'data' ? 'border-purple-400/40' : 'border-dark-border'">
        <button class="w-full flex items-center gap-3 p-4 text-left hover:bg-purple-500/5 transition-colors" @click="toggleFile('data')">
          <div class="w-8 h-8 rounded-lg bg-purple-500/15 flex items-center justify-center flex-shrink-0">
            <span class="text-purple-400 text-xs font-bold">PY</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-purple-400 font-mono font-bold text-sm">data.py</p>
            <p class="text-gray-500 text-[11px]">Datos de demanda para 21 países &times; 5 categorías + cálculo de spillover y country caps</p>
          </div>
          <span class="text-gray-500 text-xs font-mono">253 líneas</span>
          <span class="text-gray-500 text-sm transition-transform" :class="expandedFile === 'data' ? 'rotate-90' : ''">&#9654;</span>
        </button>
        <div v-if="expandedFile === 'data'" class="border-t border-dark-border">
          <pre class="p-4 text-[11px] font-mono leading-relaxed overflow-x-auto text-gray-400"><span class="text-gray-600">"""Datos de demanda de visas para 21 bloques de países × 5 categorías EB.</span>
<span class="text-gray-600">Fuentes: USCIS FY2025 Q2 Approved Petitions</span>
<span class="text-gray-600">         Visa Bulletin April 2026 (Final Action Dates)"""</span>

<span class="text-blue-400">from</span> app.core.config <span class="text-blue-400">import</span> COUNTRIES, CATEGORIES, T_ACTUAL, K_BASE, P_C, V

<span class="text-gray-600"># ── DATOS DE DEMANDA ──</span>
<span class="text-gray-600"># n = personas en lista de espera</span>
<span class="text-gray-600"># d = año de fecha de prioridad (el año en que entraron a la fila)</span>

<span class="text-accent-yellow">VISA_DATA</span> = {
    <span class="text-accent-green">"India"</span>: {
        <span class="text-accent-green">"EB-1"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">18,462</span>,  <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2023</span>},  <span class="text-gray-600"># 3 años esperando</span>
        <span class="text-accent-green">"EB-2"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">331,561</span>, <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2014</span>},  <span class="text-gray-600"># 12 AÑOS — la fila más larga</span>
        <span class="text-accent-green">"EB-3"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">102,683</span>, <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2013</span>},  <span class="text-gray-600"># 13 años esperando</span>
        <span class="text-accent-green">"EB-4"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">4,866</span>,   <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2022</span>},
        <span class="text-accent-green">"EB-5"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">116</span>,     <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2022</span>},
    },
    <span class="text-accent-green">"China"</span>: {
        <span class="text-accent-green">"EB-1"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">11,858</span>,  <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2023</span>},
        <span class="text-accent-green">"EB-2"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">36,172</span>,  <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2021</span>},
        <span class="text-accent-green">"EB-3"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">13,334</span>,  <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2021</span>},
        <span class="text-accent-green">"EB-5"</span>: {<span class="text-accent-green">"n"</span>: <span class="text-purple-400">12,117</span>,  <span class="text-accent-green">"d"</span>: <span class="text-purple-400">2016</span>},  <span class="text-gray-600"># 10 años — inversores</span>
    },
    <span class="text-gray-600">... (21 países en total)</span>
}


<span class="text-gray-600"># ── CONSTRUCCIÓN DE GRUPOS ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">build_groups</span>() -> list[dict]:
    <span class="text-gray-600">"""Construye la lista de 105 grupos (21 países × 5 categorías).</span>
<span class="text-gray-600">    Cada grupo tiene: index, country, category, n (demanda), d (fecha),</span>
<span class="text-gray-600">    w = T_ACTUAL - d (años de espera)."""</span>
    groups = []
    idx = 0
    <span class="text-blue-400">for</span> country <span class="text-blue-400">in</span> COUNTRIES:
        <span class="text-blue-400">for</span> cat <span class="text-blue-400">in</span> CATEGORIES:
            entry = VISA_DATA[country][cat]
            w = T_ACTUAL - entry[<span class="text-accent-green">"d"</span>]    <span class="text-gray-600"># años esperando</span>
            groups.append({<span class="text-accent-green">"index"</span>: idx, <span class="text-accent-green">"country"</span>: country,
                          <span class="text-accent-green">"category"</span>: cat, <span class="text-accent-green">"n"</span>: entry[<span class="text-accent-green">"n"</span>],
                          <span class="text-accent-green">"d"</span>: entry[<span class="text-accent-green">"d"</span>], <span class="text-accent-green">"w"</span>: w})
            idx += 1
    <span class="text-blue-400">return</span> groups          <span class="text-gray-600"># 105 grupos</span>


<span class="text-gray-600"># ── CÁLCULO DE SPILLOVER (CASCADA) ──</span>

<span class="text-blue-400">def</span> <span class="text-accent-green">compute_spillover</span>(groups) -> dict[str, int]:
    <span class="text-gray-600">"""Calcula los topes efectivos por categoría con cascada de spillover:</span>
<span class="text-gray-600">    EB-4/5 sobrante → EB-1 → EB-2 → EB-3</span>
<span class="text-gray-600">    Esto permite reutilizar visas no usadas por categorías pequeñas."""</span>
    s4 = max(0, K_BASE[<span class="text-accent-green">"EB-4"</span>] - demanda_eb4)  <span class="text-gray-600"># sobrante EB-4</span>
    s5 = max(0, K_BASE[<span class="text-accent-green">"EB-5"</span>] - demanda_eb5)  <span class="text-gray-600"># sobrante EB-5</span>
    k1 = K_BASE[<span class="text-accent-green">"EB-1"</span>] + s4 + s5            <span class="text-gray-600"># EB-1 recibe sobrante</span>
    s1 = max(0, k1 - demanda_eb1)              <span class="text-gray-600"># sobrante EB-1</span>
    k2 = K_BASE[<span class="text-accent-green">"EB-2"</span>] + s1                  <span class="text-gray-600"># EB-2 recibe sobrante de EB-1</span>
    s2 = max(0, k2 - demanda_eb2)
    k3 = K_BASE[<span class="text-accent-green">"EB-3"</span>] + s2                  <span class="text-gray-600"># EB-3 recibe sobrante de EB-2</span>
    <span class="text-blue-400">return</span> {<span class="text-accent-green">"EB-1"</span>: k1, <span class="text-accent-green">"EB-2"</span>: k2, <span class="text-accent-green">"EB-3"</span>: k3, <span class="text-accent-green">"EB-4"</span>: K_BASE[<span class="text-accent-green">"EB-4"</span>], <span class="text-accent-green">"EB-5"</span>: K_BASE[<span class="text-accent-green">"EB-5"</span>]}</pre>
        </div>
      </div>

      <!-- Summary stats -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-xs">
          <div>
            <p class="text-primary-300 font-bold text-lg font-mono">7</p>
            <p class="text-gray-500">módulos Python</p>
          </div>
          <div>
            <p class="text-primary-300 font-bold text-lg font-mono">~740</p>
            <p class="text-gray-500">líneas de código</p>
          </div>
          <div>
            <p class="text-primary-300 font-bold text-lg font-mono">28</p>
            <p class="text-gray-500">funciones</p>
          </div>
          <div>
            <p class="text-primary-300 font-bold text-lg font-mono">3</p>
            <p class="text-gray-500">clases</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
