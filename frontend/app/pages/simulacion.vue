<script setup lang="ts">
const { state, start, stop, seekTo, progress } = useSimulation()

const popSize = ref(30)
const maxIter = ref(100)
const seed = ref(42)
const scrubIdx = ref(0)
const scrubbing = ref(false)

function handleStart() {
  scrubbing.value = false
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

// Keep scrubber at end while running
watch(() => state.value.history.length, (len) => {
  if (!scrubbing.value) {
    scrubIdx.value = len - 1
  }
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
      <div v-if="state.completed && state.history.length > 1" class="mt-4 pt-3 border-t border-dark-border">
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
        :value="progress < 30 ? 'Exploraci\u00f3n' : progress < 70 ? 'Transici\u00f3n' : 'Siege'"
        :color="progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-accent-yellow' : 'text-accent-red'"
      />
    </section>

    <!-- Hawk Hunt animation -->
    <ClientOnly>
      <div class="card p-0 overflow-hidden">
        <HawkHunt
          :pareto-front="state.paretoFront"
          :iteration="state.iteration"
          :max-iter="state.maxIter"
          :running="state.running"
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
      <p class="text-xs text-gray-500 mt-3">Al terminar, podr&aacute;s explorar cada iteraci&oacute;n paso a paso con el scrubber.</p>
      <div class="mt-6 flex justify-center gap-6 text-xs text-gray-500">
        <div class="flex items-center gap-1.5">
          <span class="w-2.5 h-2.5 rounded-full bg-blue-400" /> Exploraci&oacute;n
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-2.5 h-2.5 rounded-full bg-accent-yellow" /> Siege
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-2.5 h-2.5 rounded-full bg-accent-red" /> Presa
        </div>
      </div>
    </div>
  </div>
</template>
