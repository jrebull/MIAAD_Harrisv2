<script setup lang="ts">
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  countries: string[]
  categories: string[]
  matrix: number[][]
  title?: string
}>()

const catColors = ['#003CA6', '#FFD600', '#00E5A0', '#FF3366', '#60a5fa']

const option = computed<EChartsOption>(() => {
  const series = props.categories.map((cat, j) => ({
    name: cat,
    type: 'bar' as const,
    stack: 'total',
    data: props.countries.map((_, i) => props.matrix[i]?.[j] || 0),
    itemStyle: { color: catColors[j] },
    emphasis: { focus: 'series' as const },
    animationDuration: 600,
    animationDelay: (idx: number) => idx * 30,
  }))

  return {
    ...baseChartOption,
    title: {
      text: props.title || 'Asignación por País',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 11 },
    },
    legend: {
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    },
    grid: { left: 120, right: 16, top: 56, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => v.toLocaleString() },
      splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'category',
      data: props.countries,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
      inverse: true,
    },
    series,
  }
})
</script>

<template>
  <VChart :option="option" autoresize class="w-full h-[600px]" />
</template>
