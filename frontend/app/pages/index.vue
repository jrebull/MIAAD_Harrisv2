<script setup lang="ts">
import type { SummaryData, GroupsData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

// Inline composable: animated count-up with easeOutExpo
function useCountUp(target: Ref<number | null>, duration = 2000) {
  const current = ref(0)
  let animationId: number | null = null

  function easeOutExpo(t: number): number {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
  }

  watch(target, (newVal) => {
    if (newVal === null || newVal === undefined) return
    if (animationId !== null) cancelAnimationFrame(animationId)

    const startVal = current.value
    const delta = newVal - startVal
    const startTime = performance.now()

    function step(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const easedProgress = easeOutExpo(progress)
      current.value = Math.round(startVal + delta * easedProgress)

      if (progress < 1) {
        animationId = requestAnimationFrame(step)
      } else {
        current.value = newVal!
        animationId = null
      }
    }

    animationId = requestAnimationFrame(step)
  }, { immediate: true })

  onUnmounted(() => {
    if (animationId !== null) cancelAnimationFrame(animationId)
  })

  return current
}

const { fetchSummary, fetchGroups } = useOptimizer()

const summary = ref<SummaryData | null>(null)
const groups = ref<GroupsData | null>(null)

onMounted(async () => {
  const [s, g] = await Promise.all([fetchSummary(), fetchGroups()])
  summary.value = s
  groups.value = g
})

const totalBacklog = computed(() => groups.value ? formatNumber(groups.value.total_demand) : '...')
const maxWait = computed(() => {
  if (!groups.value) return '...'
  return Math.max(...groups.value.groups.map(g => g.w))
})

const fifoWaste = computed(() => {
  if (!summary.value) return 0
  return Math.round(summary.value.baseline.f3)
})

const mohhoImprovement = computed(() => {
  if (!summary.value) return { f1: '0', f2: '0', waste: '0' }
  const b = summary.value.baseline
  return {
    f1: ((1 - summary.value.best_f1[0] / b.f1) * 100).toFixed(1),
    f2: ((1 - summary.value.best_f2[1] / b.f2) * 100).toFixed(1),
    waste: formatNumber(Math.round(b.f3 - summary.value.best_f3[2])),
  }
})

// --- Animated KPI targets ---
const kpiVisas = computed(() => (summary.value && groups.value) ? 140000 : null)
const kpiBacklog = computed(() => groups.value ? groups.value.total_demand : null)
const kpiCountries = computed(() => (summary.value && groups.value) ? 21 : null)
const kpiMaxWait = computed(() => {
  if (!groups.value) return null
  return Math.max(...groups.value.groups.map(g => g.w))
})

const animVisas = useCountUp(kpiVisas, 2000)
const animBacklog = useCountUp(kpiBacklog, 2000)
const animCountries = useCountUp(kpiCountries, 1500)
const animMaxWait = useCountUp(kpiMaxWait, 1800)

// --- Animated Experimental Config targets ---
const expNumRuns = computed(() => summary.value ? summary.value.num_runs : null)
const expPopSize = computed(() => summary.value ? summary.value.pop_size : null)
const expMaxIter = computed(() => summary.value ? summary.value.max_iter : null)
const expParetoSize = computed(() => summary.value ? summary.value.combined_pareto_size : null)

const animNumRuns = useCountUp(expNumRuns, 1500)
const animPopSize = useCountUp(expPopSize, 1800)
const animMaxIter = useCountUp(expMaxIter, 2000)
const animParetoSize = useCountUp(expParetoSize, 2200)
</script>

<template>
  <div class="space-y-10">

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- CINEMATIC HERO                                        -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="relative overflow-hidden rounded-2xl -mx-2 md:-mx-4">
      <!-- Layered animated background -->
      <div class="absolute inset-0 bg-gradient-to-br from-[#001a4d] via-dark-bg1 to-[#001a2e]" />
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/12 rounded-full blur-[150px] animate-pulse" style="animation-duration:5s" />
      <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-600/8 rounded-full blur-[120px] animate-pulse" style="animation-duration:7s" />
      <div class="absolute top-1/4 right-1/4 w-[300px] h-[300px] bg-accent-yellow/5 rounded-full blur-[100px] animate-pulse" style="animation-duration:4s" />
      <!-- Orbital rings -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full border border-primary/[0.04] animate-spin" style="animation-duration:80s" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[420px] h-[420px] rounded-full border border-emerald-500/[0.04] animate-spin" style="animation-duration:55s;animation-direction:reverse" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[250px] h-[250px] rounded-full border border-accent-yellow/[0.04] animate-spin" style="animation-duration:35s" />
      <!-- Grid pattern overlay -->
      <div class="absolute inset-0 opacity-[0.03]" style="background-image: radial-gradient(circle, rgba(255,255,255,0.3) 1px, transparent 1px); background-size: 40px 40px;" />

      <div class="relative px-6 py-16 md:py-24 text-center space-y-8">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 bg-primary/15 border border-primary/25 rounded-full px-5 py-2 backdrop-blur-sm">
          <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)] animate-pulse" />
          <span class="text-primary-300 text-[10px] font-bold uppercase tracking-[0.25em]">Multi-Objective Harris Hawks Optimization</span>
        </div>

        <!-- Title -->
        <div class="space-y-3">
          <h1 class="text-5xl md:text-7xl font-black tracking-tight leading-[1.05]">
            <span class="bg-gradient-to-r from-accent-yellow via-accent-green to-primary-300 bg-clip-text text-transparent">
              VISA PREDICT AI
            </span>
          </h1>
          <p class="text-gray-400 max-w-2xl mx-auto text-base md:text-lg leading-relaxed">
            Optimización inteligente para la asignación de
            <span class="text-white font-semibold">140,000 visas de empleo</span> de Estados Unidos.
            Tres objetivos. Cero compromisos innecesarios.
          </p>
        </div>

        <!-- Hero KPI strip -->
        <div class="flex flex-wrap justify-center gap-8 pt-4">
          <div class="text-center group">
            <p class="text-4xl md:text-5xl font-black font-mono text-accent-yellow transition-transform group-hover:scale-110">140K</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Visas / Año</p>
          </div>
          <div class="w-px h-16 bg-gradient-to-b from-transparent via-gray-700 to-transparent hidden md:block" />
          <div class="text-center group">
            <p class="text-4xl md:text-5xl font-black font-mono text-white transition-transform group-hover:scale-110">21<span class="text-xl text-gray-500">×</span>5</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Países × Categorías</p>
          </div>
          <div class="w-px h-16 bg-gradient-to-b from-transparent via-gray-700 to-transparent hidden md:block" />
          <div class="text-center group">
            <p class="text-4xl md:text-5xl font-black font-mono text-accent-red transition-transform group-hover:scale-110">13</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Años de Espera Max</p>
          </div>
          <div class="w-px h-16 bg-gradient-to-b from-transparent via-gray-700 to-transparent hidden md:block" />
          <div class="text-center group">
            <p class="text-4xl md:text-5xl font-black font-mono text-accent-green transition-transform group-hover:scale-110">406</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Soluciones Pareto</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- THE CRISIS — Emotional data-driven storytelling       -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="relative overflow-hidden rounded-2xl">
      <div class="absolute inset-0 bg-gradient-to-r from-accent-red/8 via-transparent to-accent-red/5" />
      <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-accent-red via-accent-red/60 to-transparent rounded-r" />
      <div class="relative p-6 md:p-8 space-y-6">
        <div>
          <p class="text-[10px] text-accent-red font-bold uppercase tracking-[0.2em] mb-2">El Problema</p>
          <h2 class="text-2xl md:text-3xl font-black text-white leading-tight">
            Un sistema roto que deja<br>
            <span class="text-accent-red">miles de visas sin usar</span>
            cada año
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <p class="text-sm text-gray-400 leading-relaxed">
              Cada año fiscal, EE.UU. otorga <strong class="text-white">140,000 visas de empleo</strong>
              (EB-1 a EB-5) limitadas por un tope de <strong class="text-white">7% por país</strong>.
              El sistema actual <strong class="text-accent-red">FIFO</strong> (First In, First Out)
              asigna por orden de llegada sin considerar eficiencia ni equidad.
            </p>
            <p class="text-sm text-gray-400 leading-relaxed">
              El resultado: familias de India esperan <strong class="text-white">más de una década</strong>,
              mientras miles de visas quedan vacías porque los topes impiden reasignarlas.
              <strong class="text-accent-red">{{ fifoWaste > 0 ? formatNumber(fifoWaste) : '...' }} visas desperdiciadas</strong>
              cada año bajo FIFO.
            </p>
          </div>

          <!-- Crisis stats -->
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-dark-bg1/80 rounded-xl p-4 border border-accent-red/15 text-center">
              <p class="text-3xl font-black text-accent-red font-mono">{{ animMaxWait }}</p>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Años de espera máx.</p>
              <p class="text-[9px] text-gray-600 mt-0.5">India EB-3</p>
            </div>
            <div class="bg-dark-bg1/80 rounded-xl p-4 border border-accent-yellow/15 text-center">
              <p class="text-3xl font-black text-accent-yellow font-mono">{{ formatNumber(animBacklog) }}</p>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Backlog total</p>
              <p class="text-[9px] text-gray-600 mt-0.5">Peticiones aprobadas</p>
            </div>
            <div class="bg-dark-bg1/80 rounded-xl p-4 border border-white/10 text-center">
              <p class="text-3xl font-black text-white font-mono">{{ animCountries }}</p>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Países</p>
              <p class="text-[9px] text-gray-600 mt-0.5">En competencia</p>
            </div>
            <div class="bg-dark-bg1/80 rounded-xl p-4 border border-accent-red/15 text-center">
              <p class="text-3xl font-black text-accent-red font-mono">{{ fifoWaste > 0 ? formatNumber(fifoWaste) : '...' }}</p>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Visas perdidas</p>
              <p class="text-[9px] text-gray-600 mt-0.5">Bajo FIFO</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- THREE OBJECTIVES — The trilemma                        -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="space-y-4">
      <div class="text-center space-y-1">
        <p class="text-[10px] text-primary-300 font-bold uppercase tracking-[0.2em]">El Trilema</p>
        <h2 class="text-xl md:text-2xl font-black text-white">Tres Objetivos en Conflicto</h2>
        <p class="text-xs text-gray-500 max-w-lg mx-auto">Mejorar uno inevitablemente empeora otro. No existe una solución perfecta — solo compromisos óptimos.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- f1 -->
        <div class="card group relative overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(250,204,21,0.08)]">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-yellow to-accent-yellow/0" />
          <div class="absolute top-4 right-4 text-5xl font-black text-accent-yellow/[0.06] select-none">f₁</div>
          <div class="relative">
            <div class="w-12 h-12 rounded-xl bg-accent-yellow/10 border border-accent-yellow/20 flex items-center justify-center mb-4">
              <span class="text-accent-yellow text-xl font-black">f₁</span>
            </div>
            <h3 class="text-accent-yellow font-bold text-lg mb-2">Carga de Espera</h3>
            <p class="text-xs text-gray-400 leading-relaxed mb-3">
              Suma ponderada de años de espera de las personas que NO reciben visa. Los que llevan más tiempo pesan más.
            </p>
            <div class="bg-dark-bg1 rounded-lg p-3 space-y-1">
              <p class="font-mono text-[11px] text-white">f₁(x) = Σ(nᵍ - xᵍ)·wᵍ / Σnᵍ</p>
              <p class="text-[10px] text-accent-yellow font-semibold">Minimizar = más humanitario</p>
            </div>
          </div>
        </div>

        <!-- f2 -->
        <div class="card group relative overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(0,229,160,0.08)]">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-green to-accent-green/0" />
          <div class="absolute top-4 right-4 text-5xl font-black text-accent-green/[0.06] select-none">f₂</div>
          <div class="relative">
            <div class="w-12 h-12 rounded-xl bg-accent-green/10 border border-accent-green/20 flex items-center justify-center mb-4">
              <span class="text-accent-green text-xl font-black">f₂</span>
            </div>
            <h3 class="text-accent-green font-bold text-lg mb-2">Disparidad</h3>
            <p class="text-xs text-gray-400 leading-relaxed mb-3">
              Brecha máxima de espera entre cualquier par de países. Captura la inequidad del sistema.
            </p>
            <div class="bg-dark-bg1 rounded-lg p-3 space-y-1">
              <p class="font-mono text-[11px] text-white">f₂(x) = max|W̄c₁ - W̄c₂|</p>
              <p class="text-[10px] text-accent-green font-semibold">Minimizar = más equitativo</p>
            </div>
          </div>
        </div>

        <!-- f3 -->
        <div class="card group relative overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(96,165,250,0.08)]">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-300 to-primary-300/0" />
          <div class="absolute top-4 right-4 text-5xl font-black text-primary-300/[0.06] select-none">f₃</div>
          <div class="relative">
            <div class="w-12 h-12 rounded-xl bg-primary-300/10 border border-primary-300/20 flex items-center justify-center mb-4">
              <span class="text-primary-300 text-xl font-black">f₃</span>
            </div>
            <h3 class="text-primary-300 font-bold text-lg mb-2">Desperdicio</h3>
            <p class="text-xs text-gray-400 leading-relaxed mb-3">
              Visas que quedan sin usar por la interacción de topes legales. Cada visa vacía es una oportunidad perdida.
            </p>
            <div class="bg-dark-bg1 rounded-lg p-3 space-y-1">
              <p class="font-mono text-[11px] text-white">f₃(x) = V - Σxᵍ</p>
              <p class="text-[10px] text-primary-300 font-semibold">Minimizar = máxima eficiencia</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- FIFO vs MOHHO — Side-by-side battle                   -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section v-if="summary" class="space-y-4">
      <div class="text-center space-y-1">
        <p class="text-[10px] text-emerald-400 font-bold uppercase tracking-[0.2em]">La Solución</p>
        <h2 class="text-xl md:text-2xl font-black text-white">FIFO vs MOHHO</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- FIFO -->
        <div class="relative overflow-hidden rounded-xl border border-accent-red/20 bg-gradient-to-br from-accent-red/[0.04] to-transparent p-6">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-accent-red/50 rounded-r" />
          <div class="absolute top-4 right-4">
            <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-accent-red/15 text-accent-red border border-accent-red/20">SISTEMA ACTUAL</span>
          </div>
          <h3 class="text-lg font-black text-accent-red mb-6">FIFO</h3>
          <div class="space-y-4 font-mono text-sm">
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₁ Carga de Espera</p>
              <p class="text-2xl font-black text-white">{{ summary.baseline.f1.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">años</span></p>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₂ Disparidad</p>
              <p class="text-2xl font-black text-white">{{ summary.baseline.f2.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">años</span></p>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₃ Desperdicio</p>
              <p class="text-2xl font-black text-accent-red">{{ formatNumber(Math.round(summary.baseline.f3)) }} <span class="text-xs text-gray-500 font-normal">visas</span></p>
            </div>
          </div>
        </div>

        <!-- MOHHO -->
        <div class="relative overflow-hidden rounded-xl border border-accent-green/20 bg-gradient-to-br from-accent-green/[0.04] to-transparent p-6">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-accent-green/50 rounded-r" />
          <div class="absolute top-4 right-4">
            <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-accent-green/15 text-accent-green border border-accent-green/20">OPTIMIZADO</span>
          </div>
          <h3 class="text-lg font-black text-accent-green mb-6">MOHHO</h3>
          <div class="space-y-4 font-mono text-sm">
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₁ Carga de Espera</p>
              <div class="flex items-baseline gap-2">
                <p class="text-2xl font-black text-white">{{ summary.best_f1[0].toFixed(3) }}</p>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent-green/15 text-accent-green">-{{ mohhoImprovement.f1 }}%</span>
              </div>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₂ Disparidad</p>
              <div class="flex items-baseline gap-2">
                <p class="text-2xl font-black text-white">{{ summary.best_f2[1].toFixed(3) }}</p>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent-green/15 text-accent-green">-{{ mohhoImprovement.f2 }}%</span>
              </div>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">f₃ Desperdicio</p>
              <div class="flex items-baseline gap-2">
                <p class="text-2xl font-black text-accent-green">{{ formatNumber(Math.round(summary.best_f3[2])) }}</p>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent-green/15 text-accent-green">-{{ mohhoImprovement.waste }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Improvement summary bar -->
      <div class="bg-gradient-to-r from-accent-green/10 via-accent-green/5 to-transparent rounded-xl border border-accent-green/15 p-4 flex flex-wrap items-center justify-center gap-6">
        <p class="text-xs text-gray-400">MOHHO supera a FIFO en <strong class="text-white">todos los objetivos</strong>:</p>
        <div class="flex gap-4 text-center">
          <div>
            <p class="text-lg font-black text-accent-green">-{{ mohhoImprovement.f1 }}%</p>
            <p class="text-[9px] text-gray-500 uppercase">Espera</p>
          </div>
          <div>
            <p class="text-lg font-black text-accent-green">-{{ mohhoImprovement.f2 }}%</p>
            <p class="text-[9px] text-gray-500 uppercase">Disparidad</p>
          </div>
          <div>
            <p class="text-lg font-black text-accent-green">-{{ mohhoImprovement.waste }}</p>
            <p class="text-[9px] text-gray-500 uppercase">Visas salvadas</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- EXPERIMENTAL CONFIG — Impressive stats                -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section v-if="summary" class="card relative overflow-hidden">
      <div class="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div class="relative">
        <div class="text-center mb-6">
          <p class="text-[10px] text-primary-300 font-bold uppercase tracking-[0.2em] mb-1">Validación Estadística</p>
          <h2 class="text-xl font-black text-white">Configuración Experimental</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-dark-bg1 rounded-xl p-5 text-center border border-white/5 transition-all hover:border-primary/20 hover:shadow-[0_0_20px_rgba(0,60,166,0.08)]">
            <p class="text-3xl font-black font-mono text-white">{{ animNumRuns }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Corridas</p>
            <p class="text-[9px] text-gray-600 mt-0.5">Semillas 42–71</p>
          </div>
          <div class="bg-dark-bg1 rounded-xl p-5 text-center border border-white/5 transition-all hover:border-accent-yellow/20 hover:shadow-[0_0_20px_rgba(250,204,21,0.08)]">
            <p class="text-3xl font-black font-mono text-white">{{ animPopSize }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Halcones</p>
            <p class="text-[9px] text-gray-600 mt-0.5">Agentes por corrida</p>
          </div>
          <div class="bg-dark-bg1 rounded-xl p-5 text-center border border-white/5 transition-all hover:border-accent-green/20 hover:shadow-[0_0_20px_rgba(0,229,160,0.08)]">
            <p class="text-3xl font-black font-mono text-white">{{ formatNumber(animMaxIter) }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Iteraciones</p>
            <p class="text-[9px] text-gray-600 mt-0.5">Por corrida</p>
          </div>
          <div class="bg-dark-bg1 rounded-xl p-5 text-center border border-accent-green/15 transition-all hover:border-accent-green/30 hover:shadow-[0_0_20px_rgba(0,229,160,0.1)]">
            <p class="text-3xl font-black font-mono text-accent-green">{{ formatNumber(animParetoSize) }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Soluciones Pareto</p>
            <p class="text-[9px] text-gray-600 mt-0.5">No-dominadas</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- EB VISA TYPES — Visual cards                          -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="space-y-4">
      <div class="text-center space-y-1">
        <p class="text-[10px] text-accent-yellow font-bold uppercase tracking-[0.2em]">Categorías</p>
        <h2 class="text-xl font-black text-white">Las 5 Visas de Empleo</h2>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="rounded-xl border border-accent-yellow/20 bg-accent-yellow/[0.03] p-4 relative overflow-hidden transition-all hover:border-accent-yellow/40 hover:bg-accent-yellow/[0.06]">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-accent-yellow" />
          <p class="text-accent-yellow font-mono font-black text-lg">EB-1</p>
          <p class="text-[10px] text-accent-yellow/60 uppercase tracking-wider font-bold mt-0.5">Extraordinarios</p>
          <p class="text-[10px] text-gray-500 leading-relaxed mt-2">Nobel, CEOs, investigadores, atletas de renombre internacional.</p>
        </div>
        <div class="rounded-xl border border-accent-green/20 bg-accent-green/[0.03] p-4 relative overflow-hidden transition-all hover:border-accent-green/40 hover:bg-accent-green/[0.06]">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-accent-green" />
          <p class="text-accent-green font-mono font-black text-lg">EB-2</p>
          <p class="text-[10px] text-accent-green/60 uppercase tracking-wider font-bold mt-0.5">Grado Avanzado</p>
          <p class="text-[10px] text-gray-500 leading-relaxed mt-2">Maestría, doctorado, habilidad excepcional en ciencias o arte.</p>
        </div>
        <div class="rounded-xl border border-primary-300/20 bg-primary-300/[0.03] p-4 relative overflow-hidden transition-all hover:border-primary-300/40 hover:bg-primary-300/[0.06]">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-primary-300" />
          <p class="text-primary-300 font-mono font-black text-lg">EB-3</p>
          <p class="text-[10px] text-primary-300/60 uppercase tracking-wider font-bold mt-0.5">Calificados</p>
          <p class="text-[10px] text-gray-500 leading-relaxed mt-2">Profesionales con licenciatura, trabajadores con 2+ años de experiencia.</p>
        </div>
        <div class="rounded-xl border border-purple-400/20 bg-purple-400/[0.03] p-4 relative overflow-hidden transition-all hover:border-purple-400/40 hover:bg-purple-400/[0.06]">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-purple-400" />
          <p class="text-purple-400 font-mono font-black text-lg">EB-4</p>
          <p class="text-[10px] text-purple-400/60 uppercase tracking-wider font-bold mt-0.5">Especiales</p>
          <p class="text-[10px] text-gray-500 leading-relaxed mt-2">Trabajadores religiosos, traductores militares, empleados intl.</p>
        </div>
        <div class="rounded-xl border border-accent-red/20 bg-accent-red/[0.03] p-4 relative overflow-hidden transition-all hover:border-accent-red/40 hover:bg-accent-red/[0.06]">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-accent-red" />
          <p class="text-accent-red font-mono font-black text-lg">EB-5</p>
          <p class="text-[10px] text-accent-red/60 uppercase tracking-wider font-bold mt-0.5">Inversionistas</p>
          <p class="text-[10px] text-gray-500 leading-relaxed mt-2">Inversión mínima $1.05M creando 10+ empleos en EE.UU.</p>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- GLOSSARY — Collapsible                                -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="card">
      <h2 class="text-lg font-bold text-white mb-2">Glosario de Términos</h2>
      <p class="text-xs text-gray-500 mb-5">Referencia completa de la terminología técnica empleada en este sistema.</p>

      <!-- Conceptos del Algoritmo -->
      <details class="mb-4 group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-green tracking-wide">Conceptos del Algoritmo</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">MOHHO <span class="text-gray-600 font-normal">(Multi-Objective Harris Hawks Optimization)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Metaheurística poblacional inspirada en la <strong class="text-white">caza cooperativa de los halcones Harris</strong>. Los halcones (soluciones candidatas) persiguen un conejo (mejor solución) alternando fases de exploración y explotación. La variante multi-objetivo mantiene un archivo de soluciones no-dominadas.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Frente de Pareto</span>
            <p class="text-xs text-gray-400 leading-relaxed">Conjunto de soluciones <strong class="text-white">no-dominadas</strong>: ninguna es estrictamente mejor que otra en todos los objetivos simultáneamente. Representa la frontera eficiente del espacio de decisión.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Dominancia de Pareto</span>
            <p class="text-xs text-gray-400 leading-relaxed">Una solución <strong class="text-white">A domina a B</strong> (A ≻ B) si y solo si A es mejor o igual en todos los objetivos y estrictamente mejor en al menos uno.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Hipervolumen (HV)</span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Volumen del espacio objetivo</strong> cubierto por el frente de Pareto. Mayor HV = mejor convergencia y diversidad.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Knee point <span class="text-gray-600 font-normal">(punto rodilla)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Solución con el <strong class="text-white">mejor balance entre objetivos</strong>. Máxima distancia perpendicular a la línea entre extremos del frente.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">SPV <span class="text-gray-600 font-normal">(Smallest Position Value)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Convierte un <strong class="text-white">vector continuo [0,1]¹⁰⁵</strong> en permutación para definir la prioridad de asignación.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Energía de escape (E)</span>
            <p class="text-xs text-gray-400 leading-relaxed">Parámetro que <strong class="text-white">decrece linealmente de 2 a 0</strong>. |E| ≥ 1 → exploración; |E| < 1 → explotación intensiva.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Vuelo de Lévy</span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Caminata aleatoria</strong> con saltos largos ocasionales para escapar de óptimos locales.</p>
          </div>
        </div>
      </details>

      <!-- Conceptos del Problema de Visas -->
      <details class="mb-4 group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-blue tracking-wide">Conceptos del Problema de Visas</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">FIFO <span class="text-gray-600 font-normal">(First In, First Out)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Sistema actual de asignación por <strong class="text-white">orden de llegada</strong>. No optimiza equidad ni eficiencia.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Per-country cap <span class="text-gray-600 font-normal">(tope por país)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Límite de <strong class="text-white">7% del total anual</strong> (25,620 visas) por país. Genera esperas extremas para India y China.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Spillover <span class="text-gray-600 font-normal">(cascada)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Visas no usadas de EB-4/5 se reasignan: <strong class="text-white">EB-4/5 → EB-1 → EB-2 → EB-3</strong>.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Backlog <span class="text-gray-600 font-normal">(acumulación)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Peticiones aprobadas esperando visa.</strong> India EB-3 tiene backlog de 10+ años.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Visa Bulletin</span>
            <p class="text-xs text-gray-400 leading-relaxed">Publicación mensual del <strong class="text-white">Departamento de Estado</strong> con fechas de prioridad actuales por categoría y país.</p>
          </div>
        </div>
      </details>

      <!-- Estadística -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-red tracking-wide">Estadística y Métricas</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">σ <span class="text-gray-600 font-normal">(desviación estándar)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Dispersión de resultados respecto a la media. Menor σ = más reproducible.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">CV <span class="text-gray-600 font-normal">(coeficiente de variación)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">σ/μ × 100</strong>. CV < 5% indica alta consistencia del algoritmo.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">IQR <span class="text-gray-600 font-normal">(rango intercuartílico)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Q3 - Q1: rango que contiene el <strong class="text-white">50% central</strong> de los datos. Robusto ante outliers.</p>
          </div>
        </div>
      </details>
    </section>
  </div>
</template>
