<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  hvHistory: number[]
  iteration: number
  maxIter: number
}>()

const paretoOption = computed<EChartsOption>(() => {
  const data = props.paretoFront.map(p => [p.f1, p.f2, p.f3])
  const pct = props.maxIter > 0 ? Math.round(props.iteration / props.maxIter * 100) : 0

  return {
    ...baseChartOption,
    title: {
      text: `Pareto en vivo \u2014 Iter ${props.iteration}/${props.maxIter} (${pct}%)`,
      textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
      left: 'center',
    },
    xAxis: {
      name: 'f\u2081 espera',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      name: 'f\u2082 disparidad',
      nameLocation: 'center',
      nameGap: 45,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      formatter: (p: any) => `<span style="opacity:0.6">f\u2081:</span> <b>${p.data[0].toFixed(4)}</b><br><span style="opacity:0.6">f\u2082:</span> <b>${p.data[1].toFixed(4)}</b><br><span style="opacity:0.6">f\u2083:</span> <b>${p.data[2].toLocaleString()}</b>`,
    },
    series: [{
      type: 'scatter',
      data,
      symbolSize: 10,
      itemStyle: {
        color: {
          type: 'radial', x: 0.5, y: 0.5, r: 0.5,
          colorStops: [
            { offset: 0, color: CHART_COLORS.primaryLight },
            { offset: 1, color: CHART_COLORS.primary },
          ],
        },
        borderColor: 'rgba(255,255,255,0.2)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: { shadowBlur: 12, shadowColor: CHART_COLORS.primary, borderColor: '#fff' },
      },
      animationDuration: 200,
    }],
  }
})

const hvOption = computed<EChartsOption>(() => ({
  ...baseChartOption,
  title: {
    text: 'Hipervolumen',
    textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
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
    formatter: (params: any) => {
      const p = Array.isArray(params) ? params[0] : params
      return `<span style="opacity:0.6">Iter:</span> <b>${p.name}</b><br><span style="opacity:0.6">HV:</span> <b>${p.value.toLocaleString()}</b>`
    },
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
          { offset: 0, color: 'rgba(0,229,160,0.15)' },
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
    <VChart :option="paretoOption" autoresize class="w-full h-[400px]" />
    <VChart :option="hvOption" autoresize class="w-full h-[400px]" />
  </div>
</template>
