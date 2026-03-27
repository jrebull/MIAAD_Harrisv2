<script setup lang="ts">
import type { SummaryData, GroupsData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

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
</script>

<template>
  <div class="space-y-8">
    <!-- Hero -->
    <section class="text-center py-8">
      <h1 class="text-4xl md:text-5xl font-black tracking-tight">
        <span class="bg-gradient-to-r from-accent-yellow to-accent-green bg-clip-text text-transparent">
          VISA PREDICT AI
        </span>
      </h1>
      <p class="text-gray-400 mt-3 max-w-2xl mx-auto text-lg">
        Optimización multi-objetivo para la asignación de visas EB de EE.UU.
        mediante Harris Hawks Optimization (MOHHO).
      </p>
    </section>

    <!-- KPI Cards -->
    <section v-if="summary && groups" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Total Visas EB" :value="'140,000'" unit="por año fiscal" />
      <KpiCard label="Backlog Total" :value="totalBacklog" unit="peticiones aprobadas" />
      <KpiCard label="Países Analizados" :value="'21'" unit="bloques de países" />
      <KpiCard label="Mayor Espera" :value="maxWait + ' años'" unit="India EB-3" />
    </section>

    <!-- Problem description -->
    <section class="card space-y-4">
      <h2 class="section-title">El Problema</h2>
      <p class="text-gray-400 leading-relaxed">
        Cada año fiscal, EE.UU. otorga <strong class="text-accent-yellow">140,000 visas de empleo</strong>
        (EB) distribuidas en 5 categorías y limitadas por topes por país del 7%.
        El sistema actual (<strong class="text-accent-red">FIFO</strong>) genera esperas de hasta
        <strong class="text-white">13 años</strong> para ciertos países y deja miles de visas sin usar.
      </p>
      <p class="text-gray-400 leading-relaxed">
        MOHHO encuentra un <strong class="text-accent-green">frente de Pareto</strong> con cientos de
        soluciones que mejoran simultáneamente la espera, la equidad entre países y la utilización de visas.
      </p>
    </section>

    <!-- FIFO vs MOHHO comparison -->
    <section v-if="summary" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card border-accent-red/20">
        <h3 class="text-sm font-semibold text-accent-red uppercase tracking-wider mb-3">FIFO (Sistema Actual)</h3>
        <div class="space-y-2 font-mono text-sm">
          <p>f₁ espera: <span class="text-white">{{ summary.baseline.f1.toFixed(3) }}</span> años</p>
          <p>f₂ brecha: <span class="text-white">{{ summary.baseline.f2.toFixed(3) }}</span> años</p>
          <p>f₃ desperdicio: <span class="text-white">{{ formatNumber(summary.baseline.f3) }}</span> visas</p>
        </div>
      </div>
      <div class="card border-accent-green/20">
        <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider mb-3">MOHHO (Mejor Solución)</h3>
        <div class="space-y-2 font-mono text-sm">
          <p>f₁ espera: <span class="text-white">{{ summary.best_f1[0].toFixed(3) }}</span> años
            <span class="text-accent-green text-xs">(mejor)</span>
          </p>
          <p>f₂ brecha: <span class="text-white">{{ summary.best_f2[1].toFixed(3) }}</span> años
            <span class="text-accent-green text-xs">(-{{ ((1 - summary.best_f2[1] / summary.baseline.f2) * 100).toFixed(0) }}%)</span>
          </p>
          <p>f₃ desperdicio: <span class="text-white">{{ formatNumber(summary.best_f3[2]) }}</span> visas
            <span class="text-accent-green text-xs">(cero desperdicio posible)</span>
          </p>
        </div>
      </div>
    </section>

    <!-- Objectives explained -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card">
        <h3 class="text-accent-yellow font-bold mb-2">f₁ — Carga de Espera</h3>
        <p class="text-xs text-gray-400">
          Mide los años de espera ponderados de las personas que NO reciben visa.
          Menor = más humanitario.
        </p>
        <p class="font-mono text-xs text-gray-500 mt-2">f₁(x) = Σ(nᵍ - xᵍ)·wᵍ / Σnᵍ</p>
      </div>
      <div class="card">
        <h3 class="text-accent-green font-bold mb-2">f₂ — Disparidad</h3>
        <p class="text-xs text-gray-400">
          Mide la brecha máxima de espera entre países.
          Menor = más equitativo.
        </p>
        <p class="font-mono text-xs text-gray-500 mt-2">f₂(x) = max|W̄c₁ - W̄c₂|</p>
      </div>
      <div class="card">
        <h3 class="text-accent-blue font-bold mb-2">f₃ — Desperdicio</h3>
        <p class="text-xs text-gray-400">
          Mide las visas que quedan sin usar por la interacción de topes.
          Menor = más eficiente.
        </p>
        <p class="font-mono text-xs text-gray-500 mt-2">f₃(x) = V - Σxᵍ</p>
      </div>
    </section>
  </div>
</template>
