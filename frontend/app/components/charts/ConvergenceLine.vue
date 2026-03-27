<script setup lang="ts">
import VChart from 'vue-echarts'
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  iterations: number[]
  hvMean: number[]
  hvStd: number[]
}>()

const option = computed<EChartsOption>(() => {
  const upper = props.hvMean.map((m, i) => m + props.hvStd[i])
  const lower = props.hvMean.map((m, i) => m - props.hvStd[i])

  return {
    ...baseChartOption,
    title: {
      text: 'Convergencia del Hipervolumen',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 11 },
    },
    legend: {
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    },
    xAxis: {
      type: 'category',
      data: props.iterations.map(String),
      name: 'Iteración',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: {
        color: CHART_COLORS.textMuted,
        interval: Math.floor(props.iterations.length / 10),
      },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'value',
      name: 'Hipervolumen (3D)',
      nameLocation: 'center',
      nameGap: 70,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0 },
      { type: 'slider', xAxisIndex: 0, height: 20, bottom: 0, borderColor: CHART_COLORS.grid },
    ],
    series: [
      {
        name: '- 1σ',
        type: 'line',
        data: lower,
        lineStyle: { opacity: 0 },
        areaStyle: { opacity: 0 },
        stack: 'band',
        symbol: 'none',
      },
      {
        name: '± 1σ',
        type: 'line',
        data: props.hvMean.map((m, i) => (upper[i] - lower[i])),
        lineStyle: { opacity: 0 },
        areaStyle: { color: CHART_COLORS.primary, opacity: 0.15 },
        stack: 'band',
        symbol: 'none',
      },
      {
        name: 'HV medio',
        type: 'line',
        data: props.hvMean,
        lineStyle: { color: CHART_COLORS.primary, width: 2 },
        itemStyle: { color: CHART_COLORS.primary },
        symbol: 'none',
        smooth: true,
      },
    ],
  }
})
</script>

<template>
  <VChart :option="option" autoresize class="w-full h-[400px]" />
</template>
