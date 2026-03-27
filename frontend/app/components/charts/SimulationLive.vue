<script setup lang="ts">
import VChart from 'vue-echarts'
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  hvHistory: number[]
  iteration: number
  maxIter: number
}>()

const paretoOption = computed<EChartsOption>(() => {
  const data = props.paretoFront.map(p => [p.f1, p.f2, p.f3])

  return {
    ...baseChartOption,
    title: {
      text: `Pareto en vivo — Iteración ${props.iteration}/${props.maxIter}`,
      textStyle: { color: CHART_COLORS.text, fontSize: 13 },
      left: 'center',
    },
    xAxis: {
      name: 'f₁',
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      name: 'f₂',
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 11 },
      formatter: (p: any) => `f₁: ${p.data[0].toFixed(3)}<br>f₂: ${p.data[1].toFixed(3)}<br>f₃: ${p.data[2].toLocaleString()}`,
    },
    series: [{
      type: 'scatter',
      data,
      symbolSize: 10,
      itemStyle: { color: CHART_COLORS.primary, borderColor: '#fff', borderWidth: 1 },
      animationDuration: 200,
    }],
  }
})

const hvOption = computed<EChartsOption>(() => ({
  ...baseChartOption,
  title: {
    text: 'Hipervolumen',
    textStyle: { color: CHART_COLORS.text, fontSize: 13 },
    left: 'center',
  },
  xAxis: {
    type: 'category',
    data: props.hvHistory.map((_, i) => i),
    axisLabel: { color: CHART_COLORS.textMuted, interval: Math.max(1, Math.floor(props.hvHistory.length / 8)) },
    axisLine: { lineStyle: { color: CHART_COLORS.grid } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: CHART_COLORS.textMuted },
    splitLine: { lineStyle: { color: CHART_COLORS.grid } },
  },
  series: [{
    type: 'line',
    data: props.hvHistory,
    smooth: true,
    lineStyle: { color: CHART_COLORS.green, width: 2 },
    itemStyle: { color: CHART_COLORS.green },
    symbol: 'none',
    areaStyle: { color: CHART_COLORS.green, opacity: 0.1 },
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
