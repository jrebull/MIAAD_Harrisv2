<script setup lang="ts">
import type { ParetoData, SummaryData, ParetoPoint } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchPareto, fetchSummary } = useOptimizer()

const pareto = ref<ParetoData | null>(null)
const summary = ref<SummaryData | null>(null)
const projection = ref<'f1f2' | 'f1f3' | 'f2f3' | '3d'>('f1f2')
const selectedPoint = ref<ParetoPoint | null>(null)

onMounted(async () => {
  const [p, s] = await Promise.all([fetchPareto(), fetchSummary()])
  pareto.value = p
  summary.value = s
})

function handleSelect(point: ParetoPoint) {
  selectedPoint.value = point
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h1 class="section-title">Frente de Pareto</h1>
      <div class="flex gap-2">
        <button
          v-for="p in (['f1f2', 'f1f3', 'f2f3', '3d'] as const)"
          :key="p"
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200"
          :class="projection === p
            ? 'bg-primary text-white shadow-md shadow-primary/25'
            : 'bg-dark-card text-gray-400 hover:text-white hover:bg-white/5'"
          @click="projection = p"
        >
          {{ p === 'f1f2' ? 'f\u2081 vs f\u2082' : p === 'f1f3' ? 'f\u2081 vs f\u2083' : p === 'f2f3' ? 'f\u2082 vs f\u2083' : '3D' }}
        </button>
      </div>
    </div>

    <!-- 2D scatter -->
    <ClientOnly>
      <div v-if="pareto && projection !== '3d'" class="card">
        <ParetoScatter
          :points="pareto.points"
          :baseline="pareto.baseline"
          :projection="projection"
          @select="handleSelect"
        />
      </div>
    </ClientOnly>

    <!-- 3D scatter -->
    <ClientOnly>
      <div v-if="pareto && projection === '3d'" class="card">
        <Pareto3D
          :points="pareto.points"
          :baseline="pareto.baseline"
        />
        <p class="text-center text-[10px] text-gray-600 mt-2">Arrastra para rotar, scroll para zoom</p>
      </div>
    </ClientOnly>

    <!-- KPI row -->
    <section v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Soluciones Pareto" :value="summary.combined_pareto_size" />
      <KpiCard label="HV Medio" :value="formatNumber(Math.round(summary.hv_stats.mean))" :unit="'\u00b1 ' + formatNumber(Math.round(summary.hv_stats.std))" />
      <KpiCard label="Mejor f\u2082" :value="summary.best_f2[1].toFixed(2)" unit="a\u00f1os disparidad" />
      <KpiCard label="Mejor f\u2083" :value="formatNumber(Math.round(summary.best_f3[2]))" unit="visas desperdiciadas" />
    </section>

    <!-- Selected point detail -->
    <div v-if="selectedPoint" class="card border-primary/30">
      <h3 class="text-sm font-semibold text-primary-300 uppercase tracking-wider mb-3">Punto Seleccionado</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-[10px] text-gray-500 uppercase">f\u2081 espera</p>
          <p class="font-mono text-lg font-bold text-accent-yellow">{{ selectedPoint.f1.toFixed(4) }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-500 uppercase">f\u2082 disparidad</p>
          <p class="font-mono text-lg font-bold text-accent-green">{{ selectedPoint.f2.toFixed(4) }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-500 uppercase">f\u2083 desperdicio</p>
          <p class="font-mono text-lg font-bold text-accent-blue">{{ formatNumber(Math.round(selectedPoint.f3)) }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-500 uppercase">Visas asignadas</p>
          <p class="font-mono text-lg font-bold text-white">{{ formatNumber(selectedPoint.visas_used) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
