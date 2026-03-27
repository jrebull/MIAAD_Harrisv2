<script setup lang="ts">
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'
import type { ConvergenceData, RunsHVData, SummaryData, ParetoRunData, RunHV } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchConvergence, fetchRunsHV, fetchSummary, fetchParetoRun } = useOptimizer()

const convergence = ref<ConvergenceData | null>(null)
const runsHV = ref<RunsHVData | null>(null)
const summary = ref<SummaryData | null>(null)
const selectedRunIdx = ref<number | null>(null)
const selectedRunData = ref<ParetoRunData | null>(null)

onMounted(async () => {
  const [c, r, s] = await Promise.all([fetchConvergence(), fetchRunsHV(), fetchSummary()])
  convergence.value = c
  runsHV.value = r
  summary.value = s
})

async function loadRun(runIdx: number) {
  selectedRunIdx.value = runIdx
  selectedRunData.value = await fetchParetoRun(runIdx)
}

// Find 95% convergence iteration
const convergence95 = computed(() => {
  if (!convergence.value) return null
  const hvFinal = convergence.value.hv_mean[convergence.value.hv_mean.length - 1]
  const threshold = hvFinal * 0.95
  const idx = convergence.value.hv_mean.findIndex((h: number) => h >= threshold)
  return idx >= 0 ? idx : null
})

const hvBarsOption = computed<EChartsOption>(() => {
  if (!runsHV.value) return {}
  const runs = [...runsHV.value.runs].sort((a: RunHV, b: RunHV) => b.hv_final - a.hv_final)
  return {
    ...baseChartOption,
    title: {
      text: 'Hipervolumen Final por Corrida',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text },
    },
    xAxis: {
      type: 'category',
      data: runs.map((r: RunHV) => `#${r.run}`),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    series: [{
      type: 'bar',
      data: runs.map((r: RunHV, i: number) => ({
        value: Math.round(r.hv_final),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: CHART_COLORS.primary },
              { offset: 1, color: CHART_COLORS.green },
            ],
          },
          opacity: 0.5 + 0.5 * (1 - i / runs.length),
        },
      })),
    }],
  }
})

const paretoSizeOption = computed<EChartsOption>(() => {
  if (!runsHV.value) return {}
  const runs = runsHV.value.runs
  return {
    ...baseChartOption,
    title: {
      text: 'Soluciones Pareto por Corrida',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    xAxis: {
      type: 'category',
      data: runs.map((r: RunHV) => `#${r.run}`),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    series: [{
      type: 'bar',
      data: runs.map((r: RunHV) => r.num_pareto),
      itemStyle: { color: CHART_COLORS.yellow, opacity: 0.7 },
    }],
  }
})

const runParetoOption = computed<EChartsOption>(() => {
  if (!selectedRunData.value) return {}
  const pts = selectedRunData.value.points
  return {
    ...baseChartOption,
    title: {
      text: `Pareto Corrida #${selectedRunData.value.run} (${pts.length} soluciones, HV=${formatNumber(Math.round(selectedRunData.value.hv_final))})`,
      textStyle: { color: CHART_COLORS.text, fontSize: 13 },
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 11 },
      formatter: (p: any) => `f₁: ${p.value[0].toFixed(4)}<br>f₂: ${p.value[1].toFixed(4)}`,
    },
    xAxis: {
      type: 'value',
      name: 'f₁ espera',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'value',
      name: 'f₂ disparidad',
      nameLocation: 'center',
      nameGap: 50,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    series: [{
      type: 'scatter',
      data: pts.map(p => [p.f1, p.f2]),
      symbolSize: 8,
      itemStyle: { color: CHART_COLORS.green, opacity: 0.8 },
    }],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Convergencia</h1>

    <!-- KPI -->
    <section v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard
        label="HV Final Medio"
        :value="formatNumber(Math.round(summary.hv_stats.mean))"
        :unit="'± ' + formatNumber(Math.round(summary.hv_stats.std))"
      />
      <KpiCard label="Mejor Corrida" :value="formatNumber(Math.round(summary.hv_stats.max))" />
      <KpiCard
        label="Mejora vs Inicio"
        :value="convergence ? ((convergence.hv_mean[convergence.hv_mean.length - 1] / convergence.hv_mean[0] - 1) * 100).toFixed(1) + '%' : '...'"
      />
      <KpiCard label="95% Convergencia" :value="convergence95 !== null ? 'Iter ' + convergence95 : '...'" />
    </section>

    <!-- Main convergence chart -->
    <ClientOnly>
      <div v-if="convergence" class="card">
        <ConvergenceLine
          :iterations="convergence.iterations"
          :hv-mean="convergence.hv_mean"
          :hv-std="convergence.hv_std"
        />
      </div>
    </ClientOnly>

    <!-- Per-run charts -->
    <ClientOnly>
      <div v-if="runsHV" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="card">
          <VChart :option="hvBarsOption" autoresize class="w-full h-[400px]" />
        </div>
        <div class="card">
          <VChart :option="paretoSizeOption" autoresize class="w-full h-[400px]" />
        </div>
      </div>
    </ClientOnly>

    <!-- Per-run Pareto front explorer -->
    <div v-if="runsHV" class="card space-y-4">
      <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider">Explorar Pareto por Corrida</h3>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="r in runsHV.runs"
          :key="r.run"
          class="px-2.5 py-1 text-xs font-mono rounded-md transition-colors"
          :class="selectedRunIdx === r.run ? 'bg-primary text-white' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
          @click="loadRun(r.run)"
        >
          #{{ r.run }}
        </button>
      </div>
      <ClientOnly>
        <div v-if="selectedRunData" class="mt-2">
          <VChart :option="runParetoOption" autoresize class="w-full h-[400px]" />
        </div>
      </ClientOnly>
    </div>
  </div>
</template>
