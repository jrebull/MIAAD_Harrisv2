<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

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
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params : [params]
        const meanSeries = p.find((s: any) => s.seriesName === 'HV medio')
        if (!meanSeries) return ''
        const idx = meanSeries.dataIndex
        const mean = props.hvMean[idx]
        const std = props.hvStd[idx]
        return `<span style="opacity:0.6">Iteraci\u00f3n</span> <b>${props.iterations[idx]}</b><br><span style="opacity:0.6">HV medio:</span> <b>${mean.toLocaleString('es-MX', { maximumFractionDigits: 0 })}</b><br><span style="opacity:0.6">\u00b11\u03c3:</span> ${std.toLocaleString('es-MX', { maximumFractionDigits: 0 })}`
      },
    },
    legend: {
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    },
    xAxis: {
      type: 'category',
      data: props.iterations.map(String),
      name: 'Iteraci\u00f3n',
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
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0 },
      { type: 'slider', xAxisIndex: 0, height: 20, bottom: 0, borderColor: CHART_COLORS.grid,
        fillerColor: 'rgba(0,60,166,0.15)', handleStyle: { color: CHART_COLORS.primary } },
    ],
    series: [
      {
        name: '- 1\u03c3',
        type: 'line',
        data: lower,
        lineStyle: { opacity: 0 },
        areaStyle: { opacity: 0 },
        stack: 'band',
        symbol: 'none',
      },
      {
        name: '\u00b1 1\u03c3',
        type: 'line',
        data: props.hvMean.map((m, i) => (upper[i] - lower[i])),
        lineStyle: { opacity: 0 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0,60,166,0.25)' },
              { offset: 1, color: 'rgba(0,60,166,0.02)' },
            ],
          },
        },
        stack: 'band',
        symbol: 'none',
      },
      {
        name: 'HV medio',
        type: 'line',
        data: props.hvMean,
        lineStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: CHART_COLORS.primary },
              { offset: 1, color: CHART_COLORS.green },
            ],
          },
          width: 2.5,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0,60,166,0.12)' },
              { offset: 1, color: 'rgba(0,60,166,0)' },
            ],
          },
        },
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
