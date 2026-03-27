<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'
import type { ImpactData, ImpactRow } from '~/composables/useOptimizer'
import { formatNumber, formatDelta } from '~/utils/formatters'

const { scenario } = useScenario()
const { fetchImpact } = useOptimizer()

const impact = ref<ImpactData | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  impact.value = await fetchImpact()
  loading.value = false
}

onMounted(load)
watch(scenario, load)

const deltaOption = computed<EChartsOption>(() => {
  if (!impact.value) return {}
  const rows = impact.value.rows
  return {
    ...baseChartOption,
    title: {
      text: `Cambio vs FIFO — ${scenario.value}`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const r = rows[p.dataIndex]
        const arrow = r.delta >= 0 ? '\u25b2' : '\u25bc'
        const color = r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red
        return `<b>${r.flag} ${r.country}</b><br><span style="opacity:0.6">Delta:</span> <span style="color:${color};font-weight:700">${arrow} ${formatDelta(r.delta)}</span> visas`
      },
    },
    grid: { left: 120, right: 50, top: 48, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map((r: ImpactRow) => r.flag + ' ' + r.country),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    series: [{
      type: 'bar',
      data: rows.map((r: ImpactRow) => ({
        value: r.delta,
        itemStyle: {
          color: {
            type: 'linear',
            x: r.delta >= 0 ? 0 : 1, y: 0,
            x2: r.delta >= 0 ? 1 : 0, y2: 0,
            colorStops: [
              { offset: 0, color: r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red },
              { offset: 1, color: r.delta >= 0 ? 'rgba(0,229,160,0.3)' : 'rgba(255,51,102,0.3)' },
            ],
          },
          borderRadius: r.delta >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
        },
      })),
      label: {
        show: true,
        position: 'right',
        color: CHART_COLORS.textMuted,
        fontSize: 9,
        formatter: (p: any) => formatDelta(p.value),
      },
      animationDuration: 800,
      animationDelay: (idx: number) => idx * 40,
    }],
  }
})

const comparisonOption = computed<EChartsOption>(() => {
  if (!impact.value) return {}
  const rows = impact.value.rows
  return {
    ...baseChartOption,
    title: {
      text: 'Visas: FIFO vs Escenario',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.04)' } },
    },
    legend: { top: 8, right: 16, textStyle: { color: CHART_COLORS.textMuted }, itemStyle: { borderWidth: 0 } },
    grid: { left: 120, right: 16, top: 56, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map((r: ImpactRow) => r.flag + ' ' + r.country),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    series: [
      {
        name: 'FIFO',
        type: 'bar',
        data: rows.map((r: ImpactRow) => r.fifo_visas),
        itemStyle: { color: CHART_COLORS.red, opacity: 0.5, borderRadius: [0, 2, 2, 0] },
      },
      {
        name: scenario.value,
        type: 'bar',
        data: rows.map((r: ImpactRow) => r.scenario_visas),
        itemStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: CHART_COLORS.primary },
              { offset: 1, color: CHART_COLORS.primaryLight },
            ],
          },
          borderRadius: [0, 2, 2, 0],
        },
      },
    ],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Impacto por País</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else-if="impact">
      <ClientOnly>
        <div class="card">
          <VChart :option="comparisonOption" autoresize class="w-full h-[600px]" />
        </div>
        <div class="card">
          <VChart :option="deltaOption" autoresize class="w-full h-[600px]" />
        </div>
      </ClientOnly>

      <!-- Impact table -->
      <details class="card">
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white">Ver tabla completa</summary>
        <div class="mt-4">
          <DataTable
            :headers="['País', 'FIFO', 'Escenario', 'Delta', 'Espera máx.']"
            :rows="impact.rows.map((r: ImpactRow) => [
              r.flag + ' ' + r.country,
              formatNumber(r.fifo_visas),
              formatNumber(r.scenario_visas),
              formatDelta(r.delta),
              r.max_wait + ' años',
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
