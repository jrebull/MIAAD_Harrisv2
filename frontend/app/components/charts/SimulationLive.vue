<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const FIFO = { f1: 7.2138, f2: 12.6377, f3: 17540 }

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  hvHistory: number[]
  iteration: number
  maxIter: number
  f1History: number[]
  f2History: number[]
  f3History: number[]
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
    grid: { left: 55, right: 20, top: 55, bottom: 40 },
    title: {
      text: `Pareto en vivo — Iter ${props.iteration}/${props.maxIter} (${pct}%)`,
      subtext: `${data.length} soluciones no-dominadas`,
      textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
      subtextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      left: 'center',
    },
    xAxis: {
      name: 'f₁ espera', nameLocation: 'center', nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      min: xB.min, max: xB.max,
    },
    yAxis: {
      name: 'f₂ disparidad', nameLocation: 'center', nameGap: 40,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      min: yB.min, max: yB.max,
    },
    tooltip: {
      ...baseTooltip, trigger: 'item',
      formatter: (p: any) => `<span style="opacity:0.5">f₁:</span> <b>${p.data[0].toFixed(4)}</b><br><span style="opacity:0.5">f₂:</span> <b>${p.data[1].toFixed(4)}</b><br><span style="opacity:0.5">f₃:</span> <b>${Math.round(p.data[2]).toLocaleString()}</b>`,
    },
    series: [
      {
        name: 'FIFO',
        type: 'effectScatter',
        data: [[FIFO.f1, FIFO.f2, FIFO.f3]],
        symbolSize: 14,
        itemStyle: { color: CHART_COLORS.red },
        rippleEffect: { brushType: 'stroke', scale: 3 },
        z: 5,
      },
      {
        type: 'scatter',
        data,
        symbolSize: 8,
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 1,
            colorStops: [{ offset: 0, color: '#60a5fa' }, { offset: 1, color: CHART_COLORS.green }],
          },
          borderColor: 'rgba(255,255,255,0.2)', borderWidth: 1,
        },
        emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(96,165,250,0.6)', borderColor: '#fff' } },
        animationDuration: 200,
      },
    ],
  }
})

const hvOption = computed<EChartsOption>(() => ({
  ...baseChartOption,
  grid: { left: 60, right: 20, top: 55, bottom: 40 },
  title: {
    text: 'Hipervolumen',
    subtext: props.hvHistory.length ? `Actual: ${props.hvHistory[props.hvHistory.length - 1].toLocaleString()}` : '',
    textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
    subtextStyle: { color: CHART_COLORS.green, fontSize: 11, fontWeight: 700 },
    left: 'center',
  },
  xAxis: {
    type: 'category', name: 'Iteración', nameLocation: 'center', nameGap: 28,
    nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    data: props.hvHistory.map((_, i) => i),
    axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10, interval: Math.max(1, Math.floor(props.hvHistory.length / 8)) },
    axisLine: { lineStyle: { color: CHART_COLORS.grid } },
  },
  yAxis: {
    type: 'value', name: 'HV',
    nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
    splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
  },
  tooltip: { ...baseTooltip, trigger: 'axis' },
  series: [{
    type: 'line', data: props.hvHistory, smooth: true,
    lineStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: CHART_COLORS.primary }, { offset: 1, color: CHART_COLORS.green }] }, width: 2.5 },
    itemStyle: { color: CHART_COLORS.green }, symbol: 'none',
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,229,160,0.2)' }, { offset: 1, color: 'rgba(0,229,160,0)' }] } },
    animationDuration: 200,
  }],
}))

// Radar: MOHHO best vs FIFO (normalized 0-1)
const radarOption = computed<EChartsOption>(() => {
  if (!props.paretoFront.length) return { ...baseChartOption }
  const bestF1 = Math.min(...props.paretoFront.map(p => p.f1))
  const bestF2 = Math.min(...props.paretoFront.map(p => p.f2))
  const bestF3 = Math.min(...props.paretoFront.map(p => p.f3))
  // Normalize: value / FIFO value (1.0 = same as FIFO, lower = better)
  const mohhoPct = [bestF1 / FIFO.f1, bestF2 / FIFO.f2, bestF3 / FIFO.f3]

  return {
    ...baseChartOption,
    title: {
      text: 'MOHHO vs FIFO',
      subtext: 'Radar normalizado (menor = mejor)',
      textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
      subtextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      left: 'center',
    },
    legend: {
      bottom: 0, textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      data: ['FIFO (baseline)', 'MOHHO (mejor)'],
    },
    radar: {
      indicator: [
        { name: 'f₁ Espera', max: 1.15 },
        { name: 'f₂ Disparidad', max: 1.15 },
        { name: 'f₃ Desperdicio', max: 1.15 },
      ],
      center: ['50%', '52%'],
      radius: '60%',
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: CHART_COLORS.textMuted, fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitArea: { areaStyle: { color: ['rgba(0,60,166,0.05)', 'rgba(0,60,166,0.02)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
    },
    series: [{
      type: 'radar',
      data: [
        {
          name: 'FIFO (baseline)',
          value: [1, 1, 1],
          lineStyle: { color: CHART_COLORS.red, width: 2, type: 'dashed' },
          areaStyle: { color: 'rgba(255,51,102,0.08)' },
          itemStyle: { color: CHART_COLORS.red },
          symbol: 'diamond', symbolSize: 6,
        },
        {
          name: 'MOHHO (mejor)',
          value: mohhoPct,
          lineStyle: {
            color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 1,
              colorStops: [{ offset: 0, color: CHART_COLORS.primary }, { offset: 1, color: CHART_COLORS.green }] },
            width: 2.5,
          },
          areaStyle: {
            color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [{ offset: 0, color: 'rgba(0,60,166,0.25)' }, { offset: 1, color: 'rgba(0,229,160,0.08)' }] },
          },
          itemStyle: { color: CHART_COLORS.green },
          symbol: 'circle', symbolSize: 8,
        },
      ],
    }],
  }
})

// Objective convergence — normalized to FIFO ratio (1.0 = FIFO baseline)
const objectivesOption = computed<EChartsOption>(() => {
  if (!props.f1History.length) return { ...baseChartOption }
  const iters = props.f1History.map((_, i) => i)
  const f1Norm = props.f1History.map(v => v / FIFO.f1)
  const f2Norm = props.f2History.map(v => v / FIFO.f2)
  const f3Norm = props.f3History.map(v => v / FIFO.f3)

  return {
    ...baseChartOption,
    grid: { left: 55, right: 20, top: 50, bottom: 60 },
    title: {
      text: 'Convergencia vs FIFO',
      subtext: 'Debajo de 1.0 = supera FIFO',
      textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
      subtextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      left: 'center',
    },
    legend: {
      bottom: 4, textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      itemGap: 16,
    },
    xAxis: {
      type: 'category', data: iters,
      name: 'Iteración', nameLocation: 'center', nameGap: 26,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9, interval: Math.max(1, Math.floor(iters.length / 6)) },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'value', name: 'Ratio vs FIFO',
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9, formatter: (v: number) => v.toFixed(2) },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    tooltip: {
      ...baseTooltip, trigger: 'axis',
      formatter: (params: any) => {
        if (!Array.isArray(params)) return ''
        let s = `<b>Iter ${params[0].axisValue}</b><br>`
        params.forEach((p: any) => {
          const pct = p.data < 1
            ? `<span style="color:#00e5a0">\u2193${((1 - p.data) * 100).toFixed(1)}%</span>`
            : `<span style="color:#ff3366">\u2191${((p.data - 1) * 100).toFixed(1)}%</span>`
          s += `${p.marker} ${p.seriesName}: <b>${p.data.toFixed(4)}</b> ${pct}<br>`
        })
        return s
      },
    },
    series: [
      {
        name: 'f\u2081 Espera', type: 'line', data: f1Norm, smooth: true, symbol: 'none',
        lineStyle: { color: CHART_COLORS.yellow, width: 2 },
        itemStyle: { color: CHART_COLORS.yellow },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(250,204,21,0.12)' }, { offset: 1, color: 'rgba(250,204,21,0)' }],
        }},
      },
      {
        name: 'f\u2082 Disparidad', type: 'line', data: f2Norm, smooth: true, symbol: 'none',
        lineStyle: { color: CHART_COLORS.green, width: 2 },
        itemStyle: { color: CHART_COLORS.green },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(0,229,160,0.12)' }, { offset: 1, color: 'rgba(0,229,160,0)' }],
        }},
      },
      {
        name: 'f\u2083 Desperdicio', type: 'line', data: f3Norm, smooth: true, symbol: 'none',
        lineStyle: { color: CHART_COLORS.primary, width: 2 },
        itemStyle: { color: CHART_COLORS.primary },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(0,60,166,0.12)' }, { offset: 1, color: 'rgba(0,60,166,0)' }],
        }},
        markLine: {
          silent: true,
          data: [{
            yAxis: 1,
            label: { formatter: 'FIFO', color: CHART_COLORS.red, fontSize: 10, position: 'end' },
            lineStyle: { color: CHART_COLORS.red, type: 'dashed', width: 1.5 },
          }],
        },
      },
    ],
  }
})
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <VChart :option="paretoOption" autoresize class="w-full h-[340px]" />
    <VChart :option="radarOption" autoresize class="w-full h-[340px]" />
    <VChart :option="hvOption" autoresize class="w-full h-[340px]" />
    <VChart :option="objectivesOption" autoresize class="w-full h-[340px]" />
  </div>
</template>
