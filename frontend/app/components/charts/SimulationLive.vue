<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  hvHistory: number[]
  iteration: number
  maxIter: number
}>()

function axisPad(vals: number[], pad = 0.08) {
  if (!vals.length) return { min: 0, max: 1 }
  const mn = Math.min(...vals), mx = Math.max(...vals)
  const r = mx - mn || 1
  return { min: mn - r * pad, max: mx + r * pad }
}

const paretoOption = computed<EChartsOption>(() => {
  const data = props.paretoFront.map(p => [p.f1, p.f2, p.f3])
  const pct = props.maxIter > 0 ? Math.round(props.iteration / props.maxIter * 100) : 0

  const xB = axisPad(data.map(d => d[0]))
  const yB = axisPad(data.map(d => d[1]))

  return {
    ...baseChartOption,
    title: {
      text: `Pareto en vivo \u2014 Iter ${props.iteration}/${props.maxIter} (${pct}%)`,
      subtext: `${data.length} soluciones no-dominadas`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      subtextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      left: 'center',
    },
    xAxis: {
      name: 'f\u2081 espera',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      min: xB.min,
      max: xB.max,
    },
    yAxis: {
      name: 'f\u2082 disparidad',
      nameLocation: 'center',
      nameGap: 45,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      min: yB.min,
      max: yB.max,
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      formatter: (p: any) => `<span style="opacity:0.5">f\u2081:</span> <b>${p.data[0].toFixed(4)}</b><br><span style="opacity:0.5">f\u2082:</span> <b>${p.data[1].toFixed(4)}</b><br><span style="opacity:0.5">f\u2083:</span> <b>${Math.round(p.data[2]).toLocaleString()}</b>`,
    },
    series: [{
      type: 'scatter',
      data,
      symbolSize: 10,
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 1,
          colorStops: [
            { offset: 0, color: '#60a5fa' },
            { offset: 1, color: CHART_COLORS.green },
          ],
        },
        borderColor: 'rgba(255,255,255,0.2)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: { shadowBlur: 12, shadowColor: 'rgba(96,165,250,0.6)', borderColor: '#fff' },
      },
      animationDuration: 200,
    }],
  }
})

const hvOption = computed<EChartsOption>(() => ({
  ...baseChartOption,
  title: {
    text: 'Hipervolumen',
    subtext: props.hvHistory.length ? `Actual: ${props.hvHistory[props.hvHistory.length - 1].toLocaleString()}` : '',
    textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
    subtextStyle: { color: CHART_COLORS.green, fontSize: 12, fontWeight: 700 },
    left: 'center',
  },
  xAxis: {
    type: 'category',
    name: 'Iteraci\u00f3n',
    nameLocation: 'center',
    nameGap: 28,
    nameTextStyle: { color: CHART_COLORS.textMuted },
    data: props.hvHistory.map((_, i) => i),
    axisLabel: { color: CHART_COLORS.textMuted, interval: Math.max(1, Math.floor(props.hvHistory.length / 8)) },
    axisLine: { lineStyle: { color: CHART_COLORS.grid } },
  },
  yAxis: {
    type: 'value',
    name: 'HV',
    nameTextStyle: { color: CHART_COLORS.textMuted },
    axisLabel: { color: CHART_COLORS.textMuted },
    splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
  },
  tooltip: {
    ...baseTooltip,
    trigger: 'axis',
  },
  series: [{
    type: 'line',
    data: props.hvHistory,
    smooth: true,
    lineStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: CHART_COLORS.primary },
          { offset: 1, color: CHART_COLORS.green },
        ],
      },
      width: 2.5,
    },
    itemStyle: { color: CHART_COLORS.green },
    symbol: 'none',
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(0,229,160,0.2)' },
          { offset: 1, color: 'rgba(0,229,160,0)' },
        ],
      },
    },
    animationDuration: 200,
  }],
}))
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <VChart :option="paretoOption" autoresize class="w-full h-[420px]" />
    <VChart :option="hvOption" autoresize class="w-full h-[420px]" />
  </div>
</template>
