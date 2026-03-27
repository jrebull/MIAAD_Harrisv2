<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

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
  const xLabel = xKey === 'f1' ? 'f\u2081 \u2014 Carga de espera (a\u00f1os)' : 'f\u2082 \u2014 Disparidad (a\u00f1os)'
  const yLabel = yKey === 'f2' ? 'f\u2082 \u2014 Disparidad (a\u00f1os)' : 'f\u2083 \u2014 Visas desperdiciadas'

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
      symbolSize: 9,
      itemStyle: {
        color: {
          type: 'radial',
          x: 0.5, y: 0.5, r: 0.5,
          colorStops: [
            { offset: 0, color: CHART_COLORS.primaryLight },
            { offset: 1, color: CHART_COLORS.primary },
          ],
        },
        opacity: 0.85,
        borderColor: 'rgba(255,255,255,0.15)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 16,
          shadowColor: 'rgba(0,60,166,0.6)',
          borderColor: '#fff',
          borderWidth: 2,
        },
        scale: 1.8,
      },
      animationDelay: (idx: number) => idx * 3,
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
      symbolSize: 20,
      itemStyle: { color: CHART_COLORS.red, shadowBlur: 12, shadowColor: CHART_COLORS.red },
      rippleEffect: { brushType: 'stroke', scale: 4, period: 3 },
    })
  }

  return {
    ...baseChartOption,
    title: {
      text: `Frente de Pareto \u2014 ${xKey === 'f1' ? 'f\u2081' : 'f\u2082'} vs ${yKey === 'f2' ? 'f\u2082' : 'f\u2083'}`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      formatter: (p: any) => {
        const d = p.data
        const label = p.seriesName === 'FIFO (Baseline)' ? '<span style="color:#FF3366;font-weight:700">FIFO Baseline</span><br>' : ''
        return `${label}<span style="opacity:0.6">f\u2081:</span> <b>${d[3].toFixed(4)}</b> a\u00f1os<br><span style="opacity:0.6">f\u2082:</span> <b>${d[4].toFixed(4)}</b> a\u00f1os<br><span style="opacity:0.6">f\u2083:</span> <b>${d[5].toLocaleString()}</b><br><span style="opacity:0.6">Visas:</span> <span style="color:${CHART_COLORS.green}">${d[2].toLocaleString()}</span>`
      },
    },
    legend: {
      show: true,
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      itemStyle: { borderWidth: 0 },
    },
    xAxis: {
      name: xLabel,
      nameLocation: 'center',
      nameGap: 32,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      axisLabel: { color: CHART_COLORS.textMuted },
    },
    yAxis: {
      name: yLabel,
      nameLocation: 'center',
      nameGap: 55,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
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
