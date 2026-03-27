<script setup lang="ts">
import type { ParetoData, SummaryData, ParetoPoint } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchPareto, fetchSummary } = useOptimizer()

const pareto = ref<ParetoData | null>(null)
const summary = ref<SummaryData | null>(null)
const projection = ref<'f1f2' | 'f1f3' | 'f2f3'>('f1f2')
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
    <div class="flex items-center justify-between">
      <h1 class="section-title">Frente de Pareto</h1>
      <div class="flex gap-2">
        <button
          v-for="p in (['f1f2', 'f1f3', 'f2f3'] as const)"
          :key="p"
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
          :class="projection === p ? 'bg-primary text-white' : 'bg-dark-card text-gray-400 hover:text-white'"
          @click="projection = p"
        >
          {{ p === 'f1f2' ? 'f₁ vs f₂' : p === 'f1f3' ? 'f₁ vs f₃' : 'f₂ vs f₃' }}
        </button>
      </div>
    </div>

    <div v-if="pareto" class="card">
      <ParetoScatter
        :points="pareto.points"
        :baseline="pareto.baseline"
        :projection="projection"
        @select="handleSelect"
      />
    </div>

    <!-- KPI row -->
    <section v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Soluciones Pareto" :value="summary.combined_pareto_size" />
      <KpiCard label="HV Medio" :value="formatNumber(Math.round(summary.hv_stats.mean))" :unit="'± ' + formatNumber(Math.round(summary.hv_stats.std))" />
      <KpiCard label="Mejor f₂" :value="summary.best_f2[1].toFixed(2)" unit="años disparidad" />
      <KpiCard label="Mejor f₃" :value="formatNumber(summary.best_f3[2])" unit="visas desperdiciadas" />
    </section>

    <!-- Selected point detail -->
    <div v-if="selectedPoint" class="card border-primary/30">
      <h3 class="text-sm font-semibold text-primary-300 uppercase tracking-wider mb-2">Punto Seleccionado</h3>
      <div class="flex gap-6 font-mono text-sm">
        <p>f₁: <span class="text-white">{{ selectedPoint.f1.toFixed(4) }}</span></p>
        <p>f₂: <span class="text-white">{{ selectedPoint.f2.toFixed(4) }}</span></p>
        <p>f₃: <span class="text-white">{{ formatNumber(selectedPoint.f3) }}</span></p>
        <p>Visas: <span class="text-accent-green">{{ formatNumber(140000 - selectedPoint.f3) }}</span></p>
      </div>
    </div>
  </div>
</template>
