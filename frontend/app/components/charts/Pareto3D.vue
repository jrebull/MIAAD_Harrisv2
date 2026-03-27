<script setup lang="ts">
import { CHART_COLORS, baseTooltip } from '~/composables/useEcharts'
import 'echarts-gl'

const props = defineProps<{
  points: Array<{ f1: number; f2: number; f3: number; visas_used: number }>
  baseline?: { f1: number; f2: number; f3: number; visas_used: number } | null
}>()

const option = computed(() => {
  const data = props.points.map(p => [p.f1, p.f2, p.f3, p.visas_used])
  const f1s = props.points.map(p => p.f1)
  const f2s = props.points.map(p => p.f2)
  const f3s = props.points.map(p => p.f3)

  const series: any[] = [
    {
      name: 'Frente de Pareto',
      type: 'scatter3D',
      data,
      symbolSize: 6,
      itemStyle: {
        color: (params: any) => {
          const t = (params.dataIndex / (data.length || 1))
          const r = Math.round(96 + t * (0 - 96))
          const g = Math.round(165 + t * (229 - 165))
          const b = Math.round(250 + t * (160 - 250))
          return `rgb(${r},${g},${b})`
        },
        opacity: 0.9,
        borderWidth: 0.5,
        borderColor: 'rgba(255,255,255,0.2)',
      },
      emphasis: {
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
      },
    },
  ]

  if (props.baseline) {
    series.push({
      name: 'FIFO',
      type: 'scatter3D',
      data: [[props.baseline.f1, props.baseline.f2, props.baseline.f3, props.baseline.visas_used]],
      symbolSize: 18,
      itemStyle: { color: CHART_COLORS.red, opacity: 1 },
    })
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...baseTooltip,
      formatter: (p: any) => {
        const d = p.data
        const isBaseline = p.seriesName === 'FIFO'
        const label = isBaseline ? '<span style="color:#FF3366;font-weight:700">FIFO</span><br>' : ''
        return `${label}f\u2081: <b>${d[0].toFixed(4)}</b><br>f\u2082: <b>${d[1].toFixed(4)}</b><br>f\u2083: <b>${Math.round(d[2]).toLocaleString()}</b><br>Visas: <span style="color:${CHART_COLORS.green}">${d[3].toLocaleString()}</span>`
      },
    },
    legend: {
      show: true,
      top: 8,
      right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
    },
    grid3D: {
      boxWidth: 100,
      boxHeight: 80,
      boxDepth: 100,
      viewControl: {
        projection: 'perspective',
        distance: 220,
        alpha: 20,
        beta: 40,
        autoRotate: true,
        autoRotateSpeed: 4,
        rotateSensitivity: 2,
        zoomSensitivity: 1.5,
      },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
      axisPointer: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      environment: 'transparent',
      light: {
        main: { intensity: 0.6, shadow: false },
        ambient: { intensity: 0.4 },
      },
    },
    xAxis3D: {
      name: 'f\u2081 espera',
      type: 'value',
      min: Math.min(...f1s) * 0.95,
      max: Math.max(...f1s) * 1.05,
      nameTextStyle: { color: CHART_COLORS.yellow, fontSize: 11 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9 },
    },
    yAxis3D: {
      name: 'f\u2082 disparidad',
      type: 'value',
      min: Math.min(...f2s) * 0.95,
      max: Math.max(...f2s) * 1.05,
      nameTextStyle: { color: CHART_COLORS.green, fontSize: 11 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9 },
    },
    zAxis3D: {
      name: 'f\u2083 desperdicio',
      type: 'value',
      min: Math.min(...f3s) * 0.95,
      max: Math.max(...f3s) * 1.05,
      nameTextStyle: { color: CHART_COLORS.blue, fontSize: 11 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9 },
    },
    series,
  }
})
</script>

<template>
  <VChart :option="option" autoresize class="w-full h-[600px]" />
</template>
