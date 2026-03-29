<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  points: Array<{ f1: number; f2: number; f3: number; visas_used: number }>
  baseline?: { f1: number; f2: number; f3: number; visas_used: number } | null
  projection?: 'f1f2' | 'f1f3' | 'f2f3'
}>()

const emit = defineEmits<{
  (e: 'select', point: { f1: number; f2: number; f3: number; visas_used: number }): void
}>()

function axisPadding(vals: number[], pad = 0.08) {
  const mn = Math.min(...vals), mx = Math.max(...vals)
  const range = mx - mn || 1
  return { min: mn - range * pad, max: mx + range * pad }
}

const option = computed<EChartsOption>(() => {
  const proj = props.projection || 'f1f2'
  const xKey = proj === 'f2f3' ? 'f2' : 'f1'
  const yKey = proj === 'f1f2' ? 'f2' : 'f3'
  const xLabel = xKey === 'f1' ? 'f\u2081 \u2014 Carga de espera (a\u00f1os)' : 'f\u2082 \u2014 Disparidad (a\u00f1os)'
  const yLabel = yKey === 'f2' ? 'f\u2082 \u2014 Disparidad (a\u00f1os)' : 'f\u2083 \u2014 Visas desperdiciadas'

  // Collect all values for axis bounds (including baseline)
  const allPoints = [...props.points]
  if (props.baseline) allPoints.push(props.baseline as any)
  const xVals = allPoints.map(p => p[xKey as keyof typeof p] as number)
  const yVals = allPoints.map(p => p[yKey as keyof typeof p] as number)
  const xBounds = axisPadding(xVals, 0.06)
  const yBounds = axisPadding(yVals, 0.06)

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
      symbolSize: (val: number[]) => {
        // Size by visa utilization
        const u = val[2] / 140000
        return 6 + u * 10
      },
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 1,
          colorStops: [
            { offset: 0, color: '#60a5fa' },
            { offset: 0.5, color: CHART_COLORS.primary },
            { offset: 1, color: CHART_COLORS.green },
          ],
        },
        opacity: 0.9,
        borderColor: 'rgba(255,255,255,0.25)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(96,165,250,0.7)',
          borderColor: '#fff',
          borderWidth: 2,
        },
        scale: 1.6,
      },
      animationDelay: (idx: number) => idx * 4,
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
      symbolSize: 22,
      itemStyle: { color: CHART_COLORS.red, shadowBlur: 16, shadowColor: CHART_COLORS.red },
      rippleEffect: { brushType: 'stroke', scale: 4, period: 3 },
      zlevel: 1,
    })
  }

  return {
    ...baseChartOption,
    grid: { left: 75, right: 25, top: 50, bottom: 62 },
    title: {
      text: `Frente de Pareto — ${xKey === 'f1' ? 'f₁' : 'f₂'} vs ${yKey === 'f2' ? 'f₂' : 'f₃'} (${props.points.length} soluciones)`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      confine: true,
      formatter: (p: any) => {
        const d = p.data
        const label = p.seriesName === 'FIFO (Baseline)' ? '<span style="color:#FF3366;font-weight:700;font-size:13px">FIFO Baseline</span><br>' : ''
        return `${label}<span style="opacity:0.5">f₁:</span> <b>${d[3].toFixed(4)}</b> años<br><span style="opacity:0.5">f₂:</span> <b>${d[4].toFixed(4)}</b> años<br><span style="opacity:0.5">f₃:</span> <b>${Math.round(d[5]).toLocaleString()}</b> desperdicio<br><span style="opacity:0.5">Visas:</span> <span style="color:${CHART_COLORS.green};font-weight:700">${d[2].toLocaleString()}</span>`
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
      nameGap: 36,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      min: xBounds.min,
      max: xBounds.max,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => yKey === 'f3' && xKey === 'f1' ? v.toFixed(2) : v.toFixed(1) },
    },
    yAxis: {
      name: yLabel,
      nameLocation: 'center',
      nameGap: 58,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      min: yBounds.min,
      max: yBounds.max,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => yKey === 'f3' ? Math.round(v).toLocaleString() : v.toFixed(1) },
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
    emit('select', { f1: params.data[3], f2: params.data[4], f3: params.data[5], visas_used: params.data[2] })
  }
}
</script>

<template>
  <VChart
    :option="option"
    autoresize
    class="w-full h-[550px]"
    @click="handleClick"
  />
</template>
