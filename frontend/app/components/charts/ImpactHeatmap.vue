<script setup lang="ts">
import VChart from 'vue-echarts'
import { CHART_COLORS, baseChartOption, type EChartsOption } from '~/composables/useEcharts'

const props = defineProps<{
  countries: string[]
  categories: string[]
  matrix: number[][]
  title?: string
}>()

const option = computed<EChartsOption>(() => {
  const data: [number, number, number][] = []
  let maxVal = 0

  for (let i = 0; i < props.countries.length; i++) {
    for (let j = 0; j < props.categories.length; j++) {
      const val = props.matrix[i]?.[j] || 0
      data.push([j, i, val])
      if (val > maxVal) maxVal = val
    }
  }

  return {
    ...baseChartOption,
    title: {
      text: props.title || 'Asignación de Visas',
      textStyle: { color: CHART_COLORS.text, fontSize: 14 },
      left: 'center',
    },
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(10,10,26,0.9)',
      borderColor: CHART_COLORS.primary,
      textStyle: { color: CHART_COLORS.text, fontSize: 11 },
      formatter: (p: any) => {
        const [j, i, val] = p.data
        return `${props.countries[i]} × ${props.categories[j]}<br><b>${val.toLocaleString()}</b> visas`
      },
    },
    grid: { left: 120, right: 80, top: 48, bottom: 32 },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 11 },
      splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0.02)', 'transparent'] } },
    },
    yAxis: {
      type: 'category',
      data: props.countries,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      textStyle: { color: CHART_COLORS.textMuted },
      inRange: { color: ['#0d1b2a', '#003CA6', '#FFD600', '#FF3366'] },
    },
    series: [{
      type: 'heatmap',
      data,
      label: {
        show: true,
        color: '#fff',
        fontSize: 8,
        formatter: (p: any) => {
          const v = p.data[2]
          return v > 0 ? v.toLocaleString() : ''
        },
      },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,60,166,0.5)' } },
    }],
  }
})
</script>

<template>
  <VChart :option="option" autoresize class="w-full h-[600px]" />
</template>
