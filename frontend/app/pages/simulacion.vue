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

// FIFO baseline (verified)
const FIFO = { f1: 7.2138, f2: 12.6377, f3: 17540 }

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

// Energy of escape E(t)
const energy = computed(() => {
  if (state.value.maxIter === 0) return 2
  return 2 * (1 - state.value.iteration / state.value.maxIter)
})

// Improvement deltas vs FIFO
const deltaF1pct = computed(() => bestF1.value > 0 ? ((FIFO.f1 - bestF1.value) / FIFO.f1 * 100) : 0)
const deltaF2pct = computed(() => bestF2.value > 0 ? ((FIFO.f2 - bestF2.value) / FIFO.f2 * 100) : 0)
const deltaF3pct = computed(() => bestF3.value > 0 ? ((FIFO.f3 - bestF3.value) / FIFO.f3 * 100) : 0)

// HV velocity (last 5 iterations)
const hvVelocity = computed(() => {
  const h = state.value.hvHistory
  if (h.length < 2) return 0
  const w = Math.min(5, h.length - 1)
  return (h[h.length - 1] - h[h.length - 1 - w]) / w
})

// f1/f2/f3 best per iteration (for convergence chart)
const f1History = computed(() =>
  state.value.history.map(s => s.paretoFront.length ? Math.min(...s.paretoFront.map(p => p.f1)) : FIFO.f1)
)
const f2History = computed(() =>
  state.value.history.map(s => s.paretoFront.length ? Math.min(...s.paretoFront.map(p => p.f2)) : FIFO.f2)
)
const f3History = computed(() =>
  state.value.history.map(s => s.paretoFront.length ? Math.min(...s.paretoFront.map(p => p.f3)) : FIFO.f3)
)

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

// ═══════════════════════════════════════════════
// MISSION CONTROL LOG
// ═══════════════════════════════════════════════
interface LogEntry {
  time: number
  text: string
  type: 'info' | 'phase' | 'milestone' | 'improve'
}

const eventLog = ref<LogEntry[]>([])
const logContainerRef = ref<HTMLElement | null>(null)
let simStartTime = 0
let lastPhase = ''
let lastArchiveSize = 0
let logBestF1 = Infinity
let logBestF2 = Infinity
let logBestF3 = Infinity
let allBetterLogged = false

function formatElapsed(ms: number) {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  const sec = s % 60
  const frac = Math.floor((ms % 1000) / 100)
  return m > 0 ? `${m}:${String(sec).padStart(2, '0')}.${frac}` : `${String(sec).padStart(2, '0')}.${frac}`
}

function logEvent(text: string, type: LogEntry['type'] = 'info') {
  const elapsed = Date.now() - simStartTime
  eventLog.value.push({ time: elapsed, text, type })
  if (eventLog.value.length > 80) eventLog.value.shift()
}

// Initialize log on simulation start
watch(() => state.value.running, (r) => {
  if (r) {
    eventLog.value = []
    simStartTime = Date.now()
    lastPhase = ''; lastArchiveSize = 0
    logBestF1 = Infinity; logBestF2 = Infinity; logBestF3 = Infinity
    allBetterLogged = false
    logEvent('Simulaci\u00f3n MOHHO iniciada', 'phase')
    logEvent(`Poblaci\u00f3n: ${popSize.value} halcones \u00b7 ${maxIter.value} iter \u00b7 semilla: ${seed.value}`, 'info')
  }
})

// Track live events
watch(() => state.value.iteration, (iter) => {
  if (!state.value.running || iter <= 0) return

  const pf = state.value.paretoFront
  const archSize = state.value.archiveSize
  const p = state.value.maxIter > 0 ? iter / state.value.maxIter : 0
  const phase = p < 0.3 ? 'Exploraci\u00f3n' : p < 0.65 ? 'Transici\u00f3n' : 'Asedio'

  // Phase transitions
  if (phase !== lastPhase && lastPhase !== '') {
    const E = (2 * (1 - p)).toFixed(2)
    logEvent(`FASE \u2192 ${phase} \u2014 E(t) = ${E}`, 'phase')
  }
  lastPhase = phase

  // Archive milestones
  if (archSize >= 25 && lastArchiveSize < 25) logEvent(`${archSize} soluciones Pareto en archivo`, 'milestone')
  if (archSize >= 50 && lastArchiveSize < 50) logEvent(`${archSize} soluciones no dominadas`, 'milestone')
  if (archSize >= 100 && lastArchiveSize < 100) logEvent(`Archivo masivo: ${archSize} soluciones Pareto`, 'milestone')
  lastArchiveSize = archSize

  // Objective improvements (log significant jumps >3%)
  if (pf.length) {
    const bf1 = Math.min(...pf.map((s: any) => s.f1))
    const bf2 = Math.min(...pf.map((s: any) => s.f2))
    const bf3 = Math.min(...pf.map((s: any) => s.f3))

    if (bf1 < logBestF1 * 0.97 && bf1 < FIFO.f1) {
      const imp = ((FIFO.f1 - bf1) / FIFO.f1 * 100).toFixed(1)
      logEvent(`f\u2081 mejor\u00f3 ${imp}% vs FIFO \u2192 ${bf1.toFixed(4)}`, 'improve')
      logBestF1 = bf1
    }
    if (bf2 < logBestF2 * 0.97 && bf2 < FIFO.f2) {
      const imp = ((FIFO.f2 - bf2) / FIFO.f2 * 100).toFixed(1)
      logEvent(`f\u2082 mejor\u00f3 ${imp}% vs FIFO \u2192 ${bf2.toFixed(4)}`, 'improve')
      logBestF2 = bf2
    }
    if (bf3 < logBestF3 * 0.97 && bf3 < FIFO.f3) {
      const imp = ((FIFO.f3 - bf3) / FIFO.f3 * 100).toFixed(1)
      logEvent(`f\u2083 mejor\u00f3 ${imp}% vs FIFO \u2192 ${Math.round(bf3).toLocaleString()}`, 'improve')
      logBestF3 = bf3
    }

    if (!allBetterLogged && bf1 < FIFO.f1 && bf2 < FIFO.f2 && bf3 < FIFO.f3) {
      allBetterLogged = true
      logEvent('MOHHO supera a FIFO en los 3 objetivos simult\u00e1neamente', 'milestone')
    }
  }

  // Periodic status
  if (iter % 20 === 0) {
    logEvent(`iter ${iter}/${state.value.maxIter} \u2014 ${archSize} Pareto \u2014 HV: ${state.value.hv.toLocaleString()}`, 'info')
  }
})

// Log completion
watch(() => state.value.completed, (done) => {
  if (!done) return
  logEvent('OPTIMIZACI\u00d3N COMPLETADA', 'phase')
  logEvent(`Resultado: ${state.value.archiveSize} soluciones \u2014 HV: ${state.value.hv.toLocaleString()}`, 'milestone')
  if (bestF1.value < FIFO.f1) logEvent(`f\u2081 final: ${bestF1.value.toFixed(4)} (\u2193${deltaF1pct.value.toFixed(1)}% vs FIFO)`, 'improve')
  if (bestF2.value < FIFO.f2) logEvent(`f\u2082 final: ${bestF2.value.toFixed(4)} (\u2193${deltaF2pct.value.toFixed(1)}% vs FIFO)`, 'improve')
  if (bestF3.value < FIFO.f3) logEvent(`f\u2083 final: ${Math.round(bestF3.value).toLocaleString()} (\u2193${deltaF3pct.value.toFixed(1)}% vs FIFO)`, 'improve')
  logEvent(`Visas utilizadas: ${formatNumber(visasUsed.value)}/140,000 (${(visasUsed.value / 140000 * 100).toFixed(1)}%)`, 'info')
})

// Auto-scroll log to bottom
watch(() => eventLog.value.length, () => {
  nextTick(() => {
    if (logContainerRef.value) logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
  })
})

// Visa savings counter
const visasSaved = computed(() => {
  if (!state.value.paretoFront.length) return 0
  return Math.max(0, Math.round(FIFO.f3 - bestF3.value))
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

    <!-- ═══════════════════════════════════════════════ -->
    <!-- MISSION DASHBOARD: Energy + Phase + Speed     -->
    <!-- ═══════════════════════════════════════════════ -->
    <section v-if="state.iteration > 0" class="card p-0 overflow-hidden">
      <!-- Top gradient bar -->
      <div class="h-1 w-full" :class="state.completed ? 'bg-gradient-to-r from-emerald-500 via-green-400 to-emerald-500' : progress < 30 ? 'bg-gradient-to-r from-blue-600 via-blue-400 to-blue-600' : progress < 70 ? 'bg-gradient-to-r from-yellow-600 via-yellow-400 to-yellow-600' : 'bg-gradient-to-r from-red-600 via-orange-400 to-red-600'" />

      <div class="grid grid-cols-1 lg:grid-cols-[auto_1fr_auto] gap-0 divide-y lg:divide-y-0 lg:divide-x divide-dark-border">
        <!-- Energy gauge -->
        <div class="flex flex-col items-center justify-center p-5 min-w-[180px]">
          <div class="relative w-28 h-14 overflow-hidden">
            <!-- Arc background -->
            <div class="absolute inset-0 w-28 h-28 rounded-full border-[6px] border-white/5" style="clip-path: inset(0 0 50% 0);" />
            <!-- Arc filled -->
            <div
              class="absolute inset-0 w-28 h-28 rounded-full border-[6px] transition-all duration-700"
              :class="state.completed ? 'border-emerald-400' : progress < 30 ? 'border-blue-400' : progress < 70 ? 'border-yellow-400' : 'border-orange-400'"
              :style="{ clipPath: `inset(0 ${Math.max(0, (1 - energy / 2)) * 50}% 50% 0)` }"
            />
            <!-- Needle -->
            <div class="absolute bottom-0 left-1/2 -translate-x-1/2 origin-bottom transition-transform duration-700"
              :style="{ transform: `translateX(-50%) rotate(${(1 - energy / 2) * 180 - 90}deg)`, width: '2px', height: '48px', background: 'white' }"
            />
            <!-- Center value -->
            <div class="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
              <p class="text-xl font-bold font-mono"
                :class="state.completed ? 'text-emerald-400' : progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-yellow-400' : 'text-orange-400'">
                {{ state.completed ? '0.00' : energy.toFixed(2) }}
              </p>
            </div>
          </div>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-2">Energía E(t)</p>
          <p class="text-xs font-bold mt-1"
            :class="state.completed ? 'text-emerald-400' : progress < 30 ? 'text-blue-400' : progress < 70 ? 'text-yellow-400' : 'text-orange-400'">
            {{ state.completed ? 'Completado' : progress < 30 ? 'Exploración' : progress < 70 ? 'Transición' : 'Asedio' }}
          </p>
        </div>

        <!-- Central: Phase description + KPIs -->
        <div class="p-4 space-y-3">
          <p class="text-xs text-gray-400 leading-relaxed">
            <template v-if="state.completed">
              Los halcones capturaron al conejo. Se encontraron <strong class="text-emerald-300">{{ state.archiveSize }} soluciones Pareto</strong> no dominadas con un hipervolumen de <strong class="text-accent-yellow">{{ state.hv.toLocaleString() }}</strong>.
            </template>
            <template v-else-if="progress < 30">
              Los halcones se dispersan por el espacio de búsqueda [0,1]<sup>105</sup>.
              Energía alta: cada halcón explora libremente usando <strong class="text-blue-300">OP1/OP2</strong>, descubriendo regiones prometedoras.
            </template>
            <template v-else-if="progress < 70">
              Equilibrio entre exploración y explotación. Algunos halcones se acercan al conejo (<strong class="text-yellow-300">OP3/OP4</strong>),
              otros usan <strong class="text-yellow-300">vuelos de Lévy</strong> para escapar de óptimos locales.
            </template>
            <template v-else>
              Asedio cooperativo: los halcones rodean al conejo con <strong class="text-orange-300">OP4/OP6</strong>.
              Perturbaciones de Lévy permiten últimas mejoras. El frente converge.
            </template>
          </p>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-dark-bg2 rounded-lg p-2.5 text-center">
              <p class="text-lg font-bold text-white font-mono">{{ state.iteration }}<span class="text-gray-500 text-xs">/{{ state.maxIter }}</span></p>
              <p class="text-[10px] text-gray-500 uppercase">Iteración</p>
            </div>
            <div class="bg-dark-bg2 rounded-lg p-2.5 text-center">
              <p class="text-lg font-bold text-accent-green font-mono">{{ state.archiveSize }}</p>
              <p class="text-[10px] text-gray-500 uppercase">Pareto</p>
            </div>
            <div class="bg-dark-bg2 rounded-lg p-2.5 text-center">
              <p class="text-lg font-bold text-accent-yellow font-mono">{{ state.hv.toLocaleString() }}</p>
              <p class="text-[10px] text-gray-500 uppercase">Hipervolumen</p>
            </div>
            <div class="bg-dark-bg2 rounded-lg p-2.5 text-center">
              <p class="text-lg font-bold font-mono" :class="hvVelocity > 0 ? 'text-accent-green' : 'text-gray-500'">
                {{ hvVelocity > 0 ? '+' + hvVelocity.toFixed(0) : '—' }}
              </p>
              <p class="text-[10px] text-gray-500 uppercase">ΔHV/iter</p>
            </div>
          </div>
        </div>

        <!-- Right: Progress ring -->
        <div class="flex flex-col items-center justify-center p-5 min-w-[140px]">
          <div class="relative w-20 h-20">
            <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
              <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="2.5" />
              <circle cx="18" cy="18" r="15.5" fill="none"
                :stroke="state.completed ? '#34d399' : progress < 30 ? '#60a5fa' : progress < 70 ? '#facc15' : '#fb923c'"
                stroke-width="2.5" stroke-linecap="round"
                :stroke-dasharray="`${progress * 0.974} 100`"
                class="transition-all duration-500"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-xl font-bold font-mono text-white">{{ progress }}%</span>
            </div>
          </div>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-2">Progreso</p>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════ -->
    <!-- OBJECTIVE RACE BARS: f1, f2, f3 vs FIFO        -->
    <!-- ═══════════════════════════════════════════════ -->
    <section v-if="state.iteration > 0" class="card space-y-4">
      <h3 class="text-xs text-gray-500 uppercase tracking-wider">Objetivos en Tiempo Real vs Línea Base FIFO</h3>

      <!-- f1 -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">f₁ — Carga de espera</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-500 font-mono">FIFO: {{ FIFO.f1.toFixed(2) }}</span>
            <span class="text-lg font-bold font-mono text-accent-yellow">{{ bestF1.toFixed(4) }}</span>
            <span v-if="deltaF1pct > 0" class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-accent-green/15 text-accent-green">-{{ deltaF1pct.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="relative h-5 bg-white/5 rounded-full overflow-hidden">
          <!-- MOHHO bar -->
          <div class="absolute inset-y-0 left-0 bg-gradient-to-r from-accent-yellow/80 to-accent-yellow/40 rounded-full transition-all duration-500"
            :style="{ width: Math.min(100, Math.max(3, bestF1 / 10 * 100)) + '%' }" />
          <!-- FIFO marker -->
          <div class="absolute inset-y-0 w-0.5 bg-accent-red transition-all duration-300"
            :style="{ left: (FIFO.f1 / 10 * 100) + '%' }" />
          <div class="absolute top-0 text-[9px] text-accent-red font-mono transition-all duration-300"
            :style="{ left: (FIFO.f1 / 10 * 100 + 1) + '%' }">FIFO</div>
        </div>
      </div>

      <!-- f2 -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">f₂ — Disparidad entre países</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-500 font-mono">FIFO: {{ FIFO.f2.toFixed(2) }}</span>
            <span class="text-lg font-bold font-mono text-accent-green">{{ bestF2.toFixed(4) }}</span>
            <span v-if="deltaF2pct > 0" class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-accent-green/15 text-accent-green">-{{ deltaF2pct.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="relative h-5 bg-white/5 rounded-full overflow-hidden">
          <div class="absolute inset-y-0 left-0 bg-gradient-to-r from-accent-green/80 to-accent-green/40 rounded-full transition-all duration-500"
            :style="{ width: Math.min(100, Math.max(3, bestF2 / 16 * 100)) + '%' }" />
          <div class="absolute inset-y-0 w-0.5 bg-accent-red transition-all duration-300"
            :style="{ left: (FIFO.f2 / 16 * 100) + '%' }" />
          <div class="absolute top-0 text-[9px] text-accent-red font-mono transition-all duration-300"
            :style="{ left: (FIFO.f2 / 16 * 100 + 1) + '%' }">FIFO</div>
        </div>
      </div>

      <!-- f3 -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">f₃ — Visas desperdiciadas</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-500 font-mono">FIFO: {{ formatNumber(FIFO.f3) }}</span>
            <span class="text-lg font-bold font-mono text-primary-300">{{ formatNumber(bestF3) }}</span>
            <span v-if="deltaF3pct > 0" class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-accent-green/15 text-accent-green">-{{ deltaF3pct.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="relative h-5 bg-white/5 rounded-full overflow-hidden">
          <div class="absolute inset-y-0 left-0 bg-gradient-to-r from-primary/80 to-primary/40 rounded-full transition-all duration-500"
            :style="{ width: Math.min(100, Math.max(3, bestF3 / 50000 * 100)) + '%' }" />
          <div class="absolute inset-y-0 w-0.5 bg-accent-red transition-all duration-300"
            :style="{ left: (FIFO.f3 / 50000 * 100) + '%' }" />
          <div class="absolute top-0 text-[9px] text-accent-red font-mono transition-all duration-300"
            :style="{ left: (FIFO.f3 / 50000 * 100 + 1) + '%' }">FIFO</div>
        </div>
      </div>

      <p class="text-[10px] text-gray-500">
        Las barras muestran el mejor valor encontrado en el frente de Pareto. La línea roja marca la referencia FIFO. Menor = mejor en los 3 objetivos.
        <span class="text-primary-300">Utilización: {{ formatNumber(visasUsed) }}/140,000 ({{ (visasUsed / 140000 * 100).toFixed(1) }}%)</span>
      </p>
    </section>

    <!-- ═══════════════════════════════════════════════ -->
    <!-- MISSION CONTROL LOG                           -->
    <!-- ═══════════════════════════════════════════════ -->
    <section v-if="state.iteration > 0 || eventLog.length > 0" class="card p-0 overflow-hidden">
      <div class="flex items-center gap-2 px-4 py-2 border-b border-dark-border">
        <div class="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
        <span class="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Registro de Misión</span>
        <span class="ml-auto text-[10px] text-gray-600 font-mono">{{ eventLog.length }} eventos</span>
      </div>
      <div ref="logContainerRef" class="h-32 overflow-y-auto font-mono text-[11px] p-3 space-y-0.5 bg-black/30 scroll-smooth">
        <div v-for="entry in eventLog" :key="entry.time + entry.text" class="flex gap-2" :class="{
          'text-gray-500': entry.type === 'info',
          'text-yellow-400 font-bold': entry.type === 'phase',
          'text-emerald-400': entry.type === 'milestone',
          'text-blue-400': entry.type === 'improve',
        }">
          <span class="text-gray-600 shrink-0">[{{ formatElapsed(entry.time) }}]</span>
          <span>{{ entry.text }}</span>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════ -->
    <!-- HAWK HUNT — Full width protagonist              -->
    <!-- ═══════════════════════════════════════════════ -->
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

    <!-- ═══════════════════════════════════════════════ -->
    <!-- LIVE CHARTS — Below simulation                  -->
    <!-- ═══════════════════════════════════════════════ -->
    <ClientOnly>
      <div v-if="state.iteration > 0" class="card">
        <SimulationLive
          :pareto-front="state.paretoFront"
          :hv-history="state.hvHistory"
          :iteration="state.iteration"
          :max-iter="state.maxIter"
          :f1-history="f1History"
          :f2-history="f2History"
          :f3-history="f3History"
        />
      </div>
    </ClientOnly>

    <!-- ═══════════════════════════════════════════════ -->
    <!-- EPIC COMPLETION PANEL                          -->
    <!-- ═══════════════════════════════════════════════ -->
    <section v-if="state.completed && state.iteration > 0" class="relative overflow-hidden rounded-2xl">
      <!-- Background glow -->
      <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-primary/5 to-accent-yellow/10" />
      <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl" />
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl" />

      <div class="relative p-6 space-y-6">
        <!-- Header -->
        <div class="text-center space-y-2">
          <div class="inline-flex items-center gap-2 bg-emerald-500/15 border border-emerald-500/30 rounded-full px-4 py-1.5">
            <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span class="text-emerald-300 text-xs font-bold uppercase tracking-widest">Optimización Completada</span>
          </div>
          <h2 class="text-2xl font-bold text-white">MOHHO supera a FIFO en los 3 objetivos</h2>
          <p class="text-sm text-gray-400">{{ state.archiveSize }} soluciones Pareto-óptimas encontradas en {{ state.maxIter }} iteraciones</p>
        </div>

        <!-- MOHHO vs FIFO comparison grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- f1 -->
          <div class="bg-dark-bg1/80 backdrop-blur rounded-xl p-4 border border-accent-yellow/20">
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">f₁ — Carga de Espera</p>
            <div class="flex items-end justify-between mb-3">
              <div>
                <p class="text-[10px] text-gray-500">MOHHO</p>
                <p class="text-2xl font-bold text-accent-yellow font-mono">{{ bestF1.toFixed(2) }}</p>
              </div>
              <div class="text-center px-3">
                <p class="text-xs font-bold" :class="deltaF1pct > 0 ? 'text-accent-green' : 'text-gray-500'">
                  {{ deltaF1pct > 0 ? '↓ ' + deltaF1pct.toFixed(1) + '%' : '—' }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-[10px] text-gray-500">FIFO</p>
                <p class="text-lg text-gray-400 font-mono line-through decoration-accent-red/50">{{ FIFO.f1.toFixed(2) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div class="h-full bg-accent-yellow/60 rounded-full" :style="{ width: (bestF1 / FIFO.f1 * 100) + '%' }" />
            </div>
          </div>

          <!-- f2 -->
          <div class="bg-dark-bg1/80 backdrop-blur rounded-xl p-4 border border-accent-green/20">
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">f₂ — Disparidad</p>
            <div class="flex items-end justify-between mb-3">
              <div>
                <p class="text-[10px] text-gray-500">MOHHO</p>
                <p class="text-2xl font-bold text-accent-green font-mono">{{ bestF2.toFixed(2) }}</p>
              </div>
              <div class="text-center px-3">
                <p class="text-xs font-bold" :class="deltaF2pct > 0 ? 'text-accent-green' : 'text-gray-500'">
                  {{ deltaF2pct > 0 ? '↓ ' + deltaF2pct.toFixed(1) + '%' : '—' }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-[10px] text-gray-500">FIFO</p>
                <p class="text-lg text-gray-400 font-mono line-through decoration-accent-red/50">{{ FIFO.f2.toFixed(2) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div class="h-full bg-accent-green/60 rounded-full" :style="{ width: (bestF2 / FIFO.f2 * 100) + '%' }" />
            </div>
          </div>

          <!-- f3 -->
          <div class="bg-dark-bg1/80 backdrop-blur rounded-xl p-4 border border-primary/20">
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">f₃ — Desperdicio</p>
            <div class="flex items-end justify-between mb-3">
              <div>
                <p class="text-[10px] text-gray-500">MOHHO</p>
                <p class="text-2xl font-bold text-primary-300 font-mono">{{ formatNumber(bestF3) }}</p>
              </div>
              <div class="text-center px-3">
                <p class="text-xs font-bold" :class="deltaF3pct > 0 ? 'text-accent-green' : 'text-gray-500'">
                  {{ deltaF3pct > 0 ? '↓ ' + deltaF3pct.toFixed(1) + '%' : '—' }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-[10px] text-gray-500">FIFO</p>
                <p class="text-lg text-gray-400 font-mono line-through decoration-accent-red/50">{{ formatNumber(FIFO.f3) }}</p>
              </div>
            </div>
            <div class="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div class="h-full bg-primary/60 rounded-full" :style="{ width: Math.max(2, bestF3 / FIFO.f3 * 100) + '%' }" />
            </div>
          </div>
        </div>

        <!-- Bottom stats -->
        <div class="flex flex-wrap items-center justify-center gap-6 text-xs">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-accent-yellow" />
            <span class="text-gray-400">HV final:</span>
            <span class="text-white font-bold font-mono">{{ state.hv.toLocaleString() }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-accent-green" />
            <span class="text-gray-400">Soluciones:</span>
            <span class="text-white font-bold font-mono">{{ state.archiveSize }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-primary" />
            <span class="text-gray-400">Visas usadas:</span>
            <span class="text-white font-bold font-mono">{{ formatNumber(visasUsed) }}/140,000</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-purple-400" />
            <span class="text-gray-400">Evaluaciones:</span>
            <span class="text-white font-bold font-mono">{{ formatNumber(popSize * state.maxIter) }}</span>
          </div>
        </div>
      </div>
    </section>

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
    <div v-if="state.iteration === 0 && !state.running" class="relative overflow-hidden rounded-2xl">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/8 via-transparent to-accent-yellow/8" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />

      <div class="relative text-center py-16 px-6">
        <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary/20 to-accent-yellow/20 border border-primary/20 flex items-center justify-center shadow-[0_0_40px_rgba(0,60,166,0.2)]">
          <Icon name="hawk" :size="40" class="text-accent-yellow" />
        </div>
        <h3 class="text-2xl font-bold text-white mb-3">Simulación MOHHO en Vivo</h3>
        <p class="text-sm text-gray-400 max-w-xl mx-auto leading-relaxed mb-6">
          Observa el algoritmo Multi-Objective Harris Hawks Optimization ejecutándose en tiempo real.
          Verás <strong class="text-blue-300">{{ popSize }} halcones</strong> explorando el espacio de búsqueda de
          <strong class="text-accent-yellow">105 dimensiones</strong>, convergiendo sobre el conejo (solución líder)
          y construyendo un frente de Pareto que optimiza <strong class="text-white">3 objetivos simultáneamente</strong>.
        </p>

        <div class="grid grid-cols-3 gap-4 max-w-md mx-auto mb-8">
          <div class="bg-dark-bg1/50 rounded-lg p-3 border border-blue-500/15">
            <p class="text-blue-400 font-bold text-sm">Fase 1</p>
            <p class="text-[10px] text-gray-500 mt-1">Exploración</p>
            <p class="text-[10px] text-gray-600">E(t) &gt; 1</p>
          </div>
          <div class="bg-dark-bg1/50 rounded-lg p-3 border border-yellow-500/15">
            <p class="text-yellow-400 font-bold text-sm">Fase 2</p>
            <p class="text-[10px] text-gray-500 mt-1">Transición</p>
            <p class="text-[10px] text-gray-600">Lévy flights</p>
          </div>
          <div class="bg-dark-bg1/50 rounded-lg p-3 border border-orange-500/15">
            <p class="text-orange-400 font-bold text-sm">Fase 3</p>
            <p class="text-[10px] text-gray-500 mt-1">Asedio</p>
            <p class="text-[10px] text-gray-600">E(t) → 0</p>
          </div>
        </div>

        <p class="text-xs text-gray-500">
          Configura los parámetros arriba y presiona <strong class="text-white">Iniciar Simulación</strong>.
          Al terminar, verás un análisis comparativo MOHHO vs FIFO y la asignación de visas resultante.
        </p>
      </div>
    </div>
  </div>
</template>
