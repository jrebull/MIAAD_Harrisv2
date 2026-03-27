<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

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
      text: props.title || 'Asignaci\u00f3n de Visas',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      position: 'top',
      formatter: (p: any) => {
        const [j, i, val] = p.data
        const pct = maxVal > 0 ? ((val / maxVal) * 100).toFixed(0) : '0'
        return `<b>${props.countries[i]}</b><br><span style="opacity:0.6">${props.categories[j]}:</span> <b style="color:${CHART_COLORS.yellow}">${val.toLocaleString()}</b> visas<br><span style="opacity:0.5;font-size:11px">${pct}% del m\u00e1ximo</span>`
      },
    },
    grid: { left: 120, right: 80, top: 48, bottom: 32 },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 11, fontWeight: 600 },
      splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0.02)', 'transparent'] } },
      axisTick: { show: false },
      position: 'top',
    },
    yAxis: {
      type: 'category',
      data: props.countries,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      itemHeight: 200,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inRange: { color: ['#1a2040', '#1d3a6e', '#1a6fd4', '#4db8ff', '#FFD600', '#FF3366'] },
    },
    series: [{
      type: 'heatmap',
      data,
      label: {
        show: true,
        color: '#fff',
        fontSize: 9,
        fontWeight: 500,
        textShadowBlur: 2,
        textShadowColor: 'rgba(0,0,0,0.5)',
        formatter: (p: any) => {
          const v = p.data[2]
          return v > 0 ? v.toLocaleString() : '0'
        },
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 16,
          shadowColor: 'rgba(0,60,166,0.5)',
          borderColor: '#fff',
          borderWidth: 1,
        },
      },
      itemStyle: {
        borderColor: 'rgba(10,10,26,0.8)',
        borderWidth: 2,
        borderRadius: 3,
      },
    }],
  }
})
</script>

<template>
  <VChart :option="option" autoresize class="w-full h-[600px]" />
</template>
