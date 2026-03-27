<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  countries: string[]
  categories: string[]
  matrix: number[][]
  title?: string
}>()

const catColors = [
  { from: '#003CA6', to: '#1a6fd4' },
  { from: '#FFD600', to: '#ffb300' },
  { from: '#00E5A0', to: '#00b880' },
  { from: '#FF3366', to: '#cc1a4a' },
  { from: '#60a5fa', to: '#3b82f6' },
]

const option = computed<EChartsOption>(() => {
  const series = props.categories.map((cat, j) => ({
    name: cat,
    type: 'bar' as const,
    stack: 'total',
    data: props.countries.map((_, i) => props.matrix[i]?.[j] || 0),
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: catColors[j].from },
          { offset: 1, color: catColors[j].to },
        ],
      },
      borderRadius: j === props.categories.length - 1 ? [0, 2, 2, 0] : [0, 0, 0, 0],
    },
    emphasis: { focus: 'series' as const },
    animationDuration: 800,
    animationEasing: 'cubicOut',
    animationDelay: (idx: number) => idx * 40,
  }))

  return {
    ...baseChartOption,
    title: {
      text: props.title || 'Asignaci\u00f3n por Pa\u00eds',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const items = Array.isArray(params) ? params : [params]
        if (!items.length) return ''
        const country = items[0].name
        let total = 0
        const rows = items.map((p: any) => {
          total += p.value || 0
          return `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${catColors[p.seriesIndex]?.from};margin-right:6px"></span>${p.seriesName}: <b>${(p.value || 0).toLocaleString()}</b>`
        }).join('<br>')
        return `<b>${country}</b><br>${rows}<br><span style="opacity:0.6;margin-top:4px;display:inline-block">Total:</span> <b style="color:${CHART_COLORS.green}">${total.toLocaleString()}</b>`
      },
    },
    legend: {
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      itemStyle: { borderWidth: 0 },
    },
    grid: { left: 120, right: 16, top: 56, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => v.toLocaleString() },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
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
