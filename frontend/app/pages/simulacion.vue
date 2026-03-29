<script setup lang="ts">
import type { AllocationData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { state, start, stop, seekTo, progress } = useSimulation()
const { fetchCustomAllocation } = useOptimizer()

const popSize = ref(30)
const maxIter = ref(100)
const seed = ref(42)
const scrubIdx = ref(0)
const scrubbing = ref(false)

// Allocation for selected iteration
const simAllocation = ref<AllocationData | null>(null)
const allocLoading = ref(false)
const categories = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

// Live fitness values from the current Pareto front leader
const leaderF1 = computed(() => state.value.paretoFront[0]?.f1 ?? 0)
const leaderF2 = computed(() => state.value.paretoFront[0]?.f2 ?? 0)
const leaderF3 = computed(() => state.value.paretoFront[0]?.f3 ?? 0)

// Best (min) of each objective across the entire Pareto front
const bestF1 = computed(() => {
  const pf = state.value.paretoFront
  return pf.length ? Math.min(...pf.map(p => p.f1)) : 0
})
const bestF2 = computed(() => {
  const pf = state.value.paretoFront
  return pf.length ? Math.min(...pf.map(p => p.f2)) : 0
})
const bestF3 = computed(() => {
  const pf = state.value.paretoFront
  return pf.length ? Math.min(...pf.map(p => p.f3)) : 0
})
const visasUsed = computed(() => 140000 - leaderF3.value)

function handleStart() {
  scrubbing.value = false
  simAllocation.value = null
  start(popSize.value, maxIter.value, seed.value)
}

function handleScrub(e: Event) {
  const val = parseInt((e.target as HTMLInputElement).value)
  scrubIdx.value = val
  seekTo(val)
}

function toggleScrub() {
  scrubbing.value = !scrubbing.value
  if (scrubbing.value && state.value.history.length > 0) {
    scrubIdx.value = state.value.history.length - 1
  }
}

// Fetch allocation for the best solution in the current Pareto front
async function loadAllocation() {
  if (!state.value.paretoFront.length) return
  // Use the first Pareto solution (leader / best balanced)
  const best = state.value.paretoFront[0]
  allocLoading.value = true
  try {
    simAllocation.value = await fetchCustomAllocation(best.f1, best.f2, best.f3)
  } catch (e) {
    console.error('Failed to fetch custom allocation:', e)
  } finally {
    allocLoading.value = false
  }
}

// Keep scrubber at end while running
watch(() => state.value.history.length, (len) => {
  if (!scrubbing.value) {
    scrubIdx.value = len - 1
  }
})

// Auto-fetch allocation when simulation completes
watch(() => state.value.completed, (done) => {
  if (done) loadAllocation()
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Simulación en Vivo</h1>

    <!-- Controls -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="text-xs text-gray-500 uppercase flex items-center gap-1.5">
            <Icon name="hawk" :size="13" /> Población
          </label>
          <input
            v-model.number="popSize"
            type="range" min="10" max="80" step="5"
            class="w-full"
            :disabled="state.running"
          >
          <p class="text-xs text-gray-400 font-mono text-center">{{ popSize }} halcones</p>
        </div>
        <div>
          <label class="text-xs text-gray-500 uppercase">Iteraciones</label>
          <input
            v-model.number="maxIter"
            type="range" min="20" max="300" step="10"
            class="w-full"
            :disabled="state.running"
          >
          <p class="text-xs text-gray-400 font-mono text-center">{{ maxIter }}</p>
        </div>
        <div>
          <label class="text-xs text-gray-500 uppercase">Semilla</label>
          <input
            v-model.number="seed"
            type="number" min="0"
            class="w-full bg-dark-bg2 border border-dark-border rounded-lg px-3 py-1.5 text-sm text-white font-mono"
            :disabled="state.running"
          >
        </div>
        <div>
          <button
            v-if="!state.running"
            class="btn-primary w-full flex items-center justify-center gap-2"
            @click="handleStart"
          >
            <Icon name="hawk" :size="16" /> {{ state.completed ? 'Re-ejecutar' : 'Iniciar Simulaci\u00f3n' }}
          </button>
          <button
            v-else
            class="btn-secondary w-full border-accent-red/40 text-accent-red"
            @click="stop"
          >
            Detener
          </button>
        </div>
      </div>

      <!-- Progress bar -->
      <div v-if="state.running || state.iteration > 0" class="mt-4">
        <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span>Iteración {{ state.iteration }} / {{ state.maxIter }}</span>
          <span>{{ progress }}%</span>
        </div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-primary to-accent-green rounded-full transition-all duration-300"
            :style="{ width: progress + '%' }"
          />
        </div>
      </div>

      <!-- Scrubber control (after completion) -->
      <div v-if="!state.running && state.history.length > 1" class="mt-4 pt-3 border-t border-dark-border">
        <div class="flex items-center gap-3">
          <button
            class="text-xs px-3 py-1 rounded-md transition-colors"
            :class="scrubbing ? 'bg-accent-yellow/20 text-accent-yellow' : 'bg-dark-bg2 text-gray-400 hover:text-white'"
            @click="toggleScrub"
          >
            {{ scrubbing ? 'Reproduciendo' : 'Explorar paso a paso' }}
          </button>
          <input
            v-if="scrubbing"
            type="range"
            :min="0"
            :max="state.history.length - 1"
            :value="scrubIdx"
            class="flex-1"
            @input="handleScrub"
          >
          <span v-if="scrubbing" class="text-xs text-gray-400 font-mono whitespace-nowrap">
            Iter {{ state.history[scrubIdx]?.iteration || 0 }} / {{ state.maxIter }}
            — HV: {{ state.history[scrubIdx]?.hv.toLocaleString() || 0 }}
            — {{ state.history[scrubIdx]?.paretoFront.length || 0 }} soluciones
          </span>
          <button
            v-if="scrubbing"
            class="text-xs px-3 py-1 rounded-md bg-primary/20 text-primary-300 hover:bg-primary/30 transition-colors"
            :disabled="allocLoading"
            @click="loadAllocation"
          >
            {{ allocLoading ? 'Calculando...' : 'Ver Asignaci\u00f3n' }}
          </button>
        </div>
      </div>
    </div>

    <!-- KPI during simulation -->
    <section v-if="state.iteration > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Iteración" :value="state.iteration" :unit="'de ' + state.maxIter" />
      <KpiCard label="Soluciones Pareto" :value="state.archiveSize" color="text-accent-green" />
      <KpiCard label="Hipervolumen" :value="state.hv.toLocaleString()" color="text-accent-yellow" />
      <KpiCard
        label="Fase"
        :value="progress < 30 ? 'Exploraci\u00f3n' : progress < 70 ? 'Transici\u00f3n' : 'Asedio'"
        :color="progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-accent-yellow' : 'text-accent-red'"
      />
    </section>

    <!-- Live fitness objectives (f1, f2, f3) -->
    <div v-if="state.iteration > 0" class="card">
      <h3 class="text-xs text-gray-500 uppercase mb-3">Objetivos en tiempo real — Solución Líder (presa)</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- f1 -->
        <div class="bg-dark-bg2 rounded-lg p-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-gray-400">f₁ — Carga de espera</span>
            <span class="text-lg font-bold font-mono text-accent-yellow">{{ leaderF1.toFixed(4) }}</span>
          </div>
          <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div class="h-full bg-accent-yellow/60 rounded-full transition-all duration-500"
              :style="{ width: Math.min(100, leaderF1 > 0 ? Math.max(5, (1 - leaderF1 / 10) * 100) : 0) + '%' }" />
          </div>
          <p class="text-[10px] text-gray-500 mt-1.5">
            ∑ w<sub>i</sub> · max(0, d<sub>i</sub> − x<sub>i</sub>) / D — espera ponderada normalizada.
            <span class="text-accent-yellow">Mejor en frente: {{ bestF1.toFixed(4) }}</span>
          </p>
        </div>
        <!-- f2 -->
        <div class="bg-dark-bg2 rounded-lg p-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-gray-400">f₂ — Disparidad entre países</span>
            <span class="text-lg font-bold font-mono text-accent-green">{{ leaderF2.toFixed(4) }}</span>
          </div>
          <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div class="h-full bg-accent-green/60 rounded-full transition-all duration-500"
              :style="{ width: Math.min(100, leaderF2 > 0 ? Math.max(5, (1 - leaderF2 / 20) * 100) : 0) + '%' }" />
          </div>
          <p class="text-[10px] text-gray-500 mt-1.5">
            max(ratio<sub>i</sub>) − min(ratio<sub>i</sub>) donde ratio = x<sub>i</sub>/d<sub>i</sub> — brecha máx-mín de cobertura.
            <span class="text-accent-green">Mejor en frente: {{ bestF2.toFixed(4) }}</span>
          </p>
        </div>
        <!-- f3 -->
        <div class="bg-dark-bg2 rounded-lg p-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-gray-400">f₃ — Visas desperdiciadas</span>
            <span class="text-lg font-bold font-mono text-accent-red">{{ formatNumber(leaderF3) }}</span>
          </div>
          <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div class="h-full bg-accent-red/60 rounded-full transition-all duration-500"
              :style="{ width: Math.min(100, Math.max(5, (1 - leaderF3 / 140000) * 100)) + '%' }" />
          </div>
          <p class="text-[10px] text-gray-500 mt-1.5">
            V − ∑ x<sub>i</sub> = {{ formatNumber(leaderF3) }} sin usar de 140,000.
            <span class="text-primary-300">Usadas: {{ formatNumber(visasUsed) }} ({{ (visasUsed / 140000 * 100).toFixed(1) }}%)</span>
          </p>
        </div>
      </div>
      <!-- Hypervolume explanation -->
      <div class="mt-3 pt-3 border-t border-dark-border">
        <details class="group">
          <summary class="text-xs text-gray-500 cursor-pointer hover:text-gray-300 transition-colors">
            ¿Cómo se calcula el hipervolumen <strong class="text-accent-yellow font-mono">{{ state.hv.toLocaleString() }}</strong>?
          </summary>
          <div class="mt-2 text-[11px] text-gray-400 leading-relaxed space-y-1.5">
            <p>
              El <strong class="text-white">hipervolumen (HV)</strong> mide el volumen del espacio objetivo dominado por el frente de Pareto,
              relativo a un <strong class="text-gray-300">punto de referencia</strong> r = (r₁, r₂, r₃).
            </p>
            <p>
              Para cada solución Pareto p<sub>k</sub> = (f₁, f₂, f₃), se calcula el "cajón" entre
              p<sub>k</sub> y r. El HV es la <strong class="text-accent-yellow">unión de todos esos cajones</strong> en el espacio 3D,
              eliminando solapamientos.
            </p>
            <p class="font-mono text-gray-500">
              HV = volumen( ∪<sub>k</sub> [f₁<sup>k</sup>, r₁] × [f₂<sup>k</sup>, r₂] × [f₃<sup>k</sup>, r₃] )
            </p>
            <p>
              A mayor HV, mejor calidad del frente: las soluciones están más cerca del origen (menores objetivos)
              y más distribuidas. Con <strong class="text-accent-green">{{ state.archiveSize }} soluciones</strong> no dominadas,
              cada una contribuye un "cajón" al hipervolumen total.
            </p>
          </div>
        </details>
      </div>
    </div>

    <!-- Phase explanation -->
    <div v-if="state.iteration > 0" class="card py-3">
      <div class="flex items-start gap-3">
        <div
          class="w-3 h-3 mt-0.5 rounded-full flex-shrink-0 shadow-lg animate-pulse"
          :class="state.completed
            ? 'bg-emerald-400 shadow-emerald-400/50'
            : progress < 30
              ? 'bg-blue-400 shadow-blue-400/50'
              : progress < 70
                ? 'bg-yellow-400 shadow-yellow-400/50'
                : 'bg-orange-400 shadow-orange-400/50'"
        />
        <div>
          <h3
            class="text-sm font-bold"
            :class="state.completed
              ? 'text-emerald-400'
              : progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-accent-yellow' : 'text-accent-red'"
          >
            {{ state.completed ? 'Optimizaci\u00f3n Completada' : progress < 30 ? 'Fase 1 \u2014 Exploraci\u00f3n' : progress < 70 ? 'Fase 2 \u2014 Transici\u00f3n' : 'Fase 3 \u2014 Asedio' }}
            <span class="text-xs font-normal text-gray-500 ml-2">E(t) = {{ state.completed ? '0.00' : (2 * (1 - progress / 100)).toFixed(2) }}</span>
          </h3>
          <p class="text-xs text-gray-400 mt-1 leading-relaxed">
            <template v-if="state.completed">
              Los halcones capturaron al conejo. Se encontraron <strong class="text-emerald-300">{{ state.archiveSize }} soluciones Pareto</strong> no dominadas.
              El hipervolumen final de <strong class="text-accent-yellow">{{ state.hv.toLocaleString() }}</strong> mide la calidad del frente.
              Puedes explorar cada iteración con el control de abajo o ver la asignación de visas resultante.
            </template>
            <template v-else-if="progress < 30">
              Los halcones se dispersan por el espacio de búsqueda (105 dimensiones, una por grupo país-categoría).
              La energía E(t) es alta — cada halcón explora libremente, evaluúa combinaciones de asignación y
              descubre regiones prometedoras del frente de Pareto. El conejo (solución líder) se mueve rápidamente.
            </template>
            <template v-else-if="progress < 70">
              La energía E(t) decrece. Los halcones equilibran exploración y explotación —
              algunos se acercan al conejo mientras otros siguen explorando nuevas regiones.
              El frente de Pareto se define y el hipervolumen crece de forma constante.
              Se aplican saltos de Lévy para escapar de óptimos locales.
            </template>
            <template v-else>
              Energía E(t) baja — los halcones ejecutan la estrategia de <strong class="text-orange-300">asedio cooperativo</strong>:
              rodean al conejo (solución líder) en formación y refinan las soluciones cercanas.
              Movimientos súbitos de Lévy permiten últimos escapes.
              El frente de Pareto converge a su forma final optimizando f₁, f₂ y f₃ simultáneamente.
            </template>
          </p>
        </div>
      </div>
    </div>

    <!-- Hawk Hunt animation -->
    <ClientOnly>
      <div class="card p-0 overflow-hidden">
        <HawkHunt
          :pareto-front="state.paretoFront"
          :iteration="state.iteration"
          :max-iter="state.maxIter"
          :running="state.running"
          :completed="state.completed"
          :pop-size="popSize"
        />
      </div>
    </ClientOnly>

    <!-- Live data charts -->
    <ClientOnly>
      <div v-if="state.iteration > 0" class="card">
        <SimulationLive
          :pareto-front="state.paretoFront"
          :hv-history="state.hvHistory"
          :iteration="state.iteration"
          :max-iter="state.maxIter"
        />
      </div>
    </ClientOnly>

    <!-- ===== ALLOCATION TABLE (after simulation / on scrub) ===== -->
    <template v-if="simAllocation">
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-bold text-white">
            Asignación de Visas — Solución Líder
          </h2>
          <div class="flex items-center gap-4 text-xs font-mono">
            <span class="text-accent-yellow">f₁ = {{ simAllocation.fitness.f1.toFixed(2) }}</span>
            <span class="text-accent-green">f₂ = {{ simAllocation.fitness.f2.toFixed(2) }}</span>
            <span class="text-accent-red">f₃ = {{ simAllocation.fitness.f3.toLocaleString() }}</span>
            <span class="text-primary-300">{{ simAllocation.visas_used.toLocaleString() }} visas ({{ simAllocation.utilization }}%)</span>
          </div>
        </div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden mb-4">
          <div
            class="h-full bg-gradient-to-r from-primary to-accent-green rounded-full"
            :style="{ width: simAllocation.utilization + '%' }"
          />
        </div>
      </div>

      <!-- Heatmap -->
      <ClientOnly>
        <div class="card">
          <ImpactHeatmap
            :countries="simAllocation.rows.map(r => r.flag + ' ' + r.country)"
            :categories="categories"
            :matrix="simAllocation.matrix"
            title="Asignación: Solución Líder del Frente Pareto"
          />
        </div>
      </ClientOnly>

      <!-- Data table -->
      <details class="card" open>
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
          Tabla de asignación por país
        </summary>
        <div class="mt-4">
          <DataTable
            :headers="['Pa\u00eds', ...categories, 'Total']"
            :rows="simAllocation.rows.map(r => [
              r.flag + ' ' + r.country,
              ...categories.map(c => formatNumber(r.categories[c] || 0)),
              formatNumber(r.total)
            ])"
          />
        </div>
      </details>
    </template>

    <!-- Visual guide: what you see in the simulation -->
    <details v-if="state.iteration > 0" class="card">
      <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors font-medium">
        Guía visual — ¿Qué representa cada elemento de la simulación?
      </summary>
      <div class="mt-4 space-y-4 text-xs text-gray-400 leading-relaxed">
        <!-- Hawks -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full bg-blue-400 flex-shrink-0 shadow-[0_0_6px_rgba(80,160,255,0.8)]" />
          <div>
            <h4 class="text-white font-bold text-sm">Halcones (agentes de búsqueda)</h4>
            <p>
              Cada halcón es una <strong class="text-blue-300">solución candidata</strong> — un vector de 105 valores
              (uno por grupo país-categoría) que define una asignación de visas.
              Su posición en pantalla corresponde a los valores f₁ y f₂ de esa solución normalizados al canvas.
              El color indica su fase actual:
              <span class="text-blue-400">azul</span> = exploración,
              <span class="text-yellow-400">amarillo</span> = transición,
              <span class="text-orange-400">naranja</span> = asedio.
            </p>
          </div>
        </div>
        <!-- Rabbit -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full bg-pink-500 flex-shrink-0 shadow-[0_0_6px_rgba(255,51,102,0.8)]" />
          <div>
            <h4 class="text-white font-bold text-sm">Presa / Conejo (solución líder)</h4>
            <p>
              El conejo rosa es la <strong class="text-pink-300">primera solución no dominada</strong> del archivo Pareto en cada iteración.
              Se mueve porque el archivo cambia con cada iteración: entran nuevas soluciones mejores y salen las dominadas.
              En la fase de exploración se mueve rápido (muchos cambios en el frente); en el asedio se estabiliza conforme
              el frente converge. El movimiento suave es interpolación visual — en cada frame avanza 4% hacia su nueva posición.
            </p>
          </div>
        </div>
        <!-- Pareto front -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full bg-blue-600 flex-shrink-0 shadow-[0_0_6px_rgba(0,100,255,0.8)]" />
          <div>
            <h4 class="text-white font-bold text-sm">Frente de Pareto (línea azul + puntos)</h4>
            <p>
              La línea azul conecta las <strong class="text-blue-300">soluciones no dominadas</strong> del archivo.
              Cada punto es una asignación de visas diferente donde ninguna otra solución es mejor en los tres objetivos
              simultáneamente. El frente se expande y refina con cada iteración — su forma final define el conjunto
              de opciones óptimas entre las cuales elegir (humanitario, equilibrio, equidad, etc.).
            </p>
          </div>
        </div>
        <!-- Phases -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full bg-gradient-to-r from-blue-400 via-yellow-400 to-orange-400 flex-shrink-0" />
          <div>
            <h4 class="text-white font-bold text-sm">Fases del algoritmo</h4>
            <div class="space-y-1 mt-1">
              <p>
                <strong class="text-blue-400">Exploración</strong> (E(t) &gt; 1.4):
                Los halcones se dispersan ampliamente por el espacio 105-dimensional. Cada uno evalúa una asignación aleatoria
                y descubre regiones prometedoras. Alta diversidad, baja precisión.
              </p>
              <p>
                <strong class="text-yellow-400">Transición</strong> (0.6 &lt; E(t) &lt; 1.4):
                Los halcones equilibran explorar lo desconocido y explotar lo prometedor.
                Saltos de Lévy permiten escapar de óptimos locales. El frente de Pareto se define.
              </p>
              <p>
                <strong class="text-orange-400">Asedio</strong> (E(t) &lt; 0.6):
                Los halcones rodean al conejo en formación (anillos concéntricos visibles en pantalla).
                Refinan las soluciones cercanas a la líder. El frente converge a su forma final.
              </p>
            </div>
          </div>
        </div>
        <!-- Formation rings -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full border border-dashed border-orange-400/50 flex-shrink-0" />
          <div>
            <h4 class="text-white font-bold text-sm">Anillos de formación</h4>
            <p>
              Los círculos punteados que aparecen en el asedio representan los anillos de órbita:
              cada halcón se asigna a un anillo según su índice, con una posición angular única.
              Esto garantiza que todos los halcones sean visibles individualmente mientras realizan el asedio cooperativo.
            </p>
          </div>
        </div>
        <!-- Sparks -->
        <div class="flex items-start gap-3">
          <span class="w-3 h-3 mt-0.5 rounded-full bg-yellow-500 flex-shrink-0 shadow-[0_0_6px_rgba(255,180,0,0.8)]" />
          <div>
            <h4 class="text-white font-bold text-sm">Chispas y efectos</h4>
            <p>
              Las chispas naranjas durante el asedio indican <strong class="text-orange-300">interacción activa</strong>
              entre halcones y presa — el algoritmo está refinando soluciones cercanas al líder.
              Las chispas multicolor al finalizar son la <strong class="text-emerald-300">celebración</strong> —
              los halcones capturaron al conejo y se encontró el frente óptimo.
            </p>
          </div>
        </div>
      </div>
    </details>

    <!-- Instructions when idle -->
    <div v-if="state.iteration === 0 && !state.running" class="card text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary/20 to-accent-yellow/20 flex items-center justify-center">
        <Icon name="hawk" :size="32" class="text-accent-yellow" />
      </div>
      <h3 class="text-lg font-bold text-white mb-2">Listo para simular</h3>
      <p class="text-sm text-gray-400 max-w-lg mx-auto leading-relaxed">
        Configura los parámetros y presiona <strong class="text-white">"Iniciar Simulación"</strong> para observar
        el algoritmo MOHHO optimizando en tiempo real. Los halcones de Harris convergerán
        sobre el conejo (solución líder) mientras construyen el frente de Pareto.
      </p>
      <p class="text-xs text-gray-500 mt-3">Al terminar, verás la tabla completa de asignación de visas y podrás explorar cada iteración.</p>
    </div>
  </div>
</template>
