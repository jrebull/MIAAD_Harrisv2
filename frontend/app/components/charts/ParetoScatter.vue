<script setup lang="ts">
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  points: Array<{ f1: number; f2: number; f3: number; visas_used: number }>
  baseline?: { f1: number; f2: number; f3: number; visas_used: number } | null
  projection?: 'f1f2' | 'f1f3' | 'f2f3'
}>()

const emit = defineEmits<{
  (e: 'select', point: { f1: number; f2: number; f3: number }): void
}>()

const option = computed<EChartsOption>(() => {
  const proj = props.projection || 'f1f2'
  const xKey = proj === 'f2f3' ? 'f2' : 'f1'
  const yKey = proj === 'f1f2' ? 'f2' : 'f3'
  const xLabel = xKey === 'f1' ? 'f₁ — Carga de espera (años)' : 'f₂ — Disparidad (años)'
  const yLabel = yKey === 'f2' ? 'f₂ — Disparidad (años)' : 'f₃ — Visas desperdiciadas'

  const data = props.points.map(p => [
    p[xKey as keyof typeof p],
    p[yKey as keyof typeof p],
    p.visas_used,
    p.f1, p.f2, p.f3,
  ])

  const series: any[] = [
    {
      name: 'Frente de Pareto',
      type: 'scatter',
      data,
      symbolSize: 8,
      itemStyle: { color: CHART_COLORS.primary, opacity: 0.7, borderColor: '#fff', borderWidth: 0.5 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: CHART_COLORS.primary } },
    },
  ]

  if (props.baseline) {
    series.push({
      name: 'FIFO (Baseline)',
      type: 'effectScatter',
      data: [[
        props.baseline[xKey as keyof typeof props.baseline],
        props.baseline[yKey as keyof typeof props.baseline],
        props.baseline.visas_used,
        props.baseline.f1, props.baseline.f2, props.baseline.f3,
      ]],
      symbolSize: 18,
      itemStyle: { color: CHART_COLORS.red },
      rippleEffect: { brushType: 'stroke', scale: 3 },
    })
  }

  return {
    ...baseChartOption,
    title: {
      text: `Frente de Pareto: ${xKey} vs ${yKey}`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 12 },
      formatter: (p: any) => {
        const d = p.data
        return `f₁: ${d[3].toFixed(3)}<br>f₂: ${d[4].toFixed(3)}<br>f₃: ${d[5].toLocaleString()}<br>Visas: ${d[2].toLocaleString()}`
      },
    },
    legend: { show: true, top: 8, right: 16, textStyle: { color: CHART_COLORS.textMuted, fontSize: 11 } },
    xAxis: {
      name: xLabel,
      nameLocation: 'center',
      nameGap: 32,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
      axisLabel: { color: CHART_COLORS.textMuted },
    },
    yAxis: {
      name: yLabel,
      nameLocation: 'center',
      nameGap: 50,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
      axisLabel: { color: CHART_COLORS.textMuted },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0 },
      { type: 'inside', yAxisIndex: 0 },
    ],
    series,
  }
})

function handleClick(params: any) {
  if (params.data) {
    emit('select', { f1: params.data[3], f2: params.data[4], f3: params.data[5] })
  }
}
</script>

<template>
  <VChart
    :option="option"
    autoresize
    class="w-full h-[500px]"
    @click="handleClick"
  />
</template>
