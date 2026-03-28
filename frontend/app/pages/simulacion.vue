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
    <h1 class="section-title">Simulaci&oacute;n en Vivo</h1>

    <!-- Controls -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="text-xs text-gray-500 uppercase flex items-center gap-1.5">
            <Icon name="hawk" :size="13" /> Poblaci&oacute;n
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
          <span>Iteraci&oacute;n {{ state.iteration }} / {{ state.maxIter }}</span>
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
            &mdash; HV: {{ state.history[scrubIdx]?.hv.toLocaleString() || 0 }}
            &mdash; {{ state.history[scrubIdx]?.paretoFront.length || 0 }} soluciones
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
      <KpiCard label="Iteraci&oacute;n" :value="state.iteration" :unit="'de ' + state.maxIter" />
      <KpiCard label="Soluciones Pareto" :value="state.archiveSize" color="text-accent-green" />
      <KpiCard label="Hipervolumen" :value="state.hv.toLocaleString()" color="text-accent-yellow" />
      <KpiCard
        label="Fase"
        :value="progress < 30 ? 'Exploraci\u00f3n' : progress < 70 ? 'Transici\u00f3n' : 'Asedio'"
        :color="progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-accent-yellow' : 'text-accent-red'"
      />
    </section>

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
              Puedes explorar cada iteraci&oacute;n con el control de abajo o ver la asignaci&oacute;n de visas resultante.
            </template>
            <template v-else-if="progress < 30">
              Los halcones se dispersan por el espacio de b&uacute;squeda (105 dimensiones, una por grupo pa&iacute;s-categor&iacute;a).
              La energ&iacute;a E(t) es alta &mdash; cada halc&oacute;n explora libremente, evalu&uacute;a combinaciones de asignaci&oacute;n y
              descubre regiones prometedoras del frente de Pareto. El conejo (soluci&oacute;n l&iacute;der) se mueve r&aacute;pidamente.
            </template>
            <template v-else-if="progress < 70">
              La energ&iacute;a E(t) decrece. Los halcones equilibran exploraci&oacute;n y explotaci&oacute;n &mdash;
              algunos se acercan al conejo mientras otros siguen explorando nuevas regiones.
              El frente de Pareto se define y el hipervolumen crece de forma constante.
              Se aplican saltos de L&eacute;vy para escapar de &oacute;ptimos locales.
            </template>
            <template v-else>
              Energ&iacute;a E(t) baja &mdash; los halcones ejecutan la estrategia de <strong class="text-orange-300">asedio cooperativo</strong>:
              rodean al conejo (soluci&oacute;n l&iacute;der) en formaci&oacute;n y refinan las soluciones cercanas.
              Movimientos s&uacute;bitos de L&eacute;vy permiten &uacute;ltimos escapes.
              El frente de Pareto converge a su forma final optimizando f&sub1;, f&sub2; y f&sub3; simult&aacute;neamente.
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
            Asignaci&oacute;n de Visas &mdash; Soluci&oacute;n L&iacute;der
          </h2>
          <div class="flex items-center gap-4 text-xs font-mono">
            <span class="text-accent-yellow">f&sub1; = {{ simAllocation.fitness.f1.toFixed(2) }}</span>
            <span class="text-accent-green">f&sub2; = {{ simAllocation.fitness.f2.toFixed(2) }}</span>
            <span class="text-accent-red">f&sub3; = {{ simAllocation.fitness.f3.toLocaleString() }}</span>
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
            title="Asignaci\u00f3n: Soluci\u00f3n L\u00edder del Frente Pareto"
          />
        </div>
      </ClientOnly>

      <!-- Data table -->
      <details class="card" open>
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
          Tabla de asignaci&oacute;n por pa&iacute;s
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

    <!-- Instructions when idle -->
    <div v-if="state.iteration === 0 && !state.running" class="card text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary/20 to-accent-yellow/20 flex items-center justify-center">
        <Icon name="hawk" :size="32" class="text-accent-yellow" />
      </div>
      <h3 class="text-lg font-bold text-white mb-2">Listo para simular</h3>
      <p class="text-sm text-gray-400 max-w-lg mx-auto leading-relaxed">
        Configura los par&aacute;metros y presiona <strong class="text-white">&ldquo;Iniciar Simulaci&oacute;n&rdquo;</strong> para observar
        el algoritmo MOHHO optimizando en tiempo real. Los halcones de Harris converger&aacute;n
        sobre el conejo (soluci&oacute;n l&iacute;der) mientras construyen el frente de Pareto.
      </p>
      <p class="text-xs text-gray-500 mt-3">Al terminar, ver&aacute;s la tabla completa de asignaci&oacute;n de visas y podr&aacute;s explorar cada iteraci&oacute;n.</p>
    </div>
  </div>
</template>
