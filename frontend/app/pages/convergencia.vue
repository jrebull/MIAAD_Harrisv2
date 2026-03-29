<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'
import type { ConvergenceData, RunsHVData, SummaryData, ParetoRunData, RunHV } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchConvergence, fetchRunsHV, fetchSummary, fetchParetoRun } = useOptimizer()

const convergence = ref<ConvergenceData | null>(null)
const runsHV = ref<RunsHVData | null>(null)
const summary = ref<SummaryData | null>(null)
const selectedRunIdx = ref<number | null>(null)
const selectedRunData = ref<ParetoRunData | null>(null)

onMounted(async () => {
  const [c, r, s] = await Promise.all([fetchConvergence(), fetchRunsHV(), fetchSummary()])
  convergence.value = c
  runsHV.value = r
  summary.value = s
})

async function loadRun(runIdx: number) {
  selectedRunIdx.value = runIdx
  selectedRunData.value = await fetchParetoRun(runIdx)
}

// ── Derived stats ──
const convergence95 = computed(() => {
  if (!convergence.value) return null
  const hvFinal = convergence.value.hv_mean[convergence.value.hv_mean.length - 1]
  const threshold = hvFinal * 0.95
  const idx = convergence.value.hv_mean.findIndex((h: number) => h >= threshold)
  return idx >= 0 ? idx : null
})

const hvGainPct = computed(() => {
  if (!convergence.value) return '...'
  const m = convergence.value.hv_mean
  return ((m[m.length - 1] / m[0] - 1) * 100).toFixed(1) + '%'
})

const cv = computed(() => {
  if (!summary.value) return null
  return ((summary.value.hv_stats.std / summary.value.hv_stats.mean) * 100).toFixed(2)
})

const bestRun = computed(() => {
  if (!runsHV.value) return null
  return [...runsHV.value.runs].sort((a, b) => b.hv_final - a.hv_final)[0]
})

const worstRun = computed(() => {
  if (!runsHV.value) return null
  return [...runsHV.value.runs].sort((a, b) => a.hv_final - b.hv_final)[0]
})

const selectedRunRank = computed(() => {
  if (!selectedRunIdx.value || !runsHV.value) return null
  const sorted = [...runsHV.value.runs].sort((a, b) => b.hv_final - a.hv_final)
  const idx = sorted.findIndex(r => r.run === selectedRunIdx.value)
  return idx >= 0 ? idx + 1 : null
})

const selectedRunHV = computed(() => {
  if (!selectedRunIdx.value || !runsHV.value) return null
  return runsHV.value.runs.find(r => r.run === selectedRunIdx.value) ?? null
})

// ── Main convergence chart (inlined for annotations) ──
const mainConvergenceOption = computed<EChartsOption>(() => {
  if (!convergence.value) return {}
  const c = convergence.value
  const upper = c.hv_mean.map((m: number, i: number) => m + c.hv_std[i])
  const lower = c.hv_mean.map((m: number, i: number) => m - c.hv_std[i])
  const upper2 = c.hv_mean.map((m: number, i: number) => m + 2 * c.hv_std[i])
  const lower2 = c.hv_mean.map((m: number, i: number) => m - 2 * c.hv_std[i])
  const hvFinal = c.hv_mean[c.hv_mean.length - 1]
  const hv0 = c.hv_mean[0]
  const conv95Iter = convergence95.value

  const markLines: any[] = [
    { yAxis: Math.round(hvFinal), lineStyle: { color: CHART_COLORS.green, type: 'dashed', width: 1.5 }, label: { formatter: `HV final: ${Math.round(hvFinal).toLocaleString()}`, color: CHART_COLORS.green, fontSize: 10, position: 'insideEndTop' } },
  ]
  if (conv95Iter !== null) {
    markLines.push({ xAxis: String(c.iterations[conv95Iter]), lineStyle: { color: CHART_COLORS.yellow, type: 'dotted', width: 1.5 }, label: { formatter: `95% en iter ${conv95Iter}`, color: CHART_COLORS.yellow, fontSize: 10, position: 'insideEndTop' } })
  }

  return {
    ...baseChartOption,
    grid: { left: 80, right: 30, top: 50, bottom: 75 },
    title: {
      text: 'Convergencia del Hipervolumen (30 corridas)',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params : [params]
        const meanSeries = p.find((s: any) => s.seriesName === 'HV medio')
        if (!meanSeries) return ''
        const idx = meanSeries.dataIndex
        const mean = c.hv_mean[idx], std = c.hv_std[idx]
        return `<span style="opacity:0.6">Iteración</span> <b>${c.iterations[idx]}</b><br><span style="opacity:0.6">HV medio:</span> <b>${Math.round(mean).toLocaleString()}</b><br><span style="opacity:0.6">±1σ:</span> ${Math.round(std).toLocaleString()}<br><span style="opacity:0.6">Rango:</span> ${Math.round(mean - std).toLocaleString()} – ${Math.round(mean + std).toLocaleString()}`
      },
    },
    legend: { top: 8, right: 16, textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 } },
    xAxis: {
      type: 'category', data: c.iterations.map(String),
      name: 'Iteración', nameLocation: 'center', nameGap: 32,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLabel: { color: CHART_COLORS.textMuted, interval: Math.floor(c.iterations.length / 10) },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'value', name: 'Hipervolumen (3D)', nameLocation: 'center', nameGap: 65,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0 },
      { type: 'slider', xAxisIndex: 0, height: 20, bottom: 4, borderColor: CHART_COLORS.grid, fillerColor: 'rgba(0,60,166,0.15)', handleStyle: { color: CHART_COLORS.primary } },
    ],
    series: [
      // ±2σ lower bound
      { name: '- 2σ', type: 'line', data: lower2, lineStyle: { opacity: 0 }, areaStyle: { opacity: 0 }, stack: 'band2', symbol: 'none' },
      // ±2σ band
      { name: '± 2σ', type: 'line', data: c.hv_mean.map((_: number, i: number) => upper2[i] - lower2[i]), lineStyle: { opacity: 0 }, areaStyle: { color: 'rgba(0,60,166,0.08)' }, stack: 'band2', symbol: 'none' },
      // ±1σ lower bound
      { name: '- 1σ', type: 'line', data: lower, lineStyle: { opacity: 0 }, areaStyle: { opacity: 0 }, stack: 'band1', symbol: 'none' },
      // ±1σ band
      {
        name: '± 1σ', type: 'line',
        data: c.hv_mean.map((_: number, i: number) => upper[i] - lower[i]),
        lineStyle: { opacity: 0 },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,60,166,0.25)' }, { offset: 1, color: 'rgba(0,60,166,0.02)' }] } },
        stack: 'band1', symbol: 'none',
      },
      // Mean line
      {
        name: 'HV medio', type: 'line', data: c.hv_mean,
        lineStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: CHART_COLORS.primary }, { offset: 1, color: CHART_COLORS.green }] }, width: 2.5 },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,60,166,0.12)' }, { offset: 1, color: 'rgba(0,60,166,0)' }] } },
        itemStyle: { color: CHART_COLORS.primary }, symbol: 'none', smooth: true,
        markLine: { silent: true, symbol: 'none', lineStyle: { width: 1.5 }, data: markLines },
      },
    ],
  }
})

// ── Velocity chart (ΔHV per iteration) ──
const velocityOption = computed<EChartsOption>(() => {
  if (!convergence.value) return {}
  const c = convergence.value
  const delta: number[] = []
  for (let i = 1; i < c.hv_mean.length; i++) delta.push(c.hv_mean[i] - c.hv_mean[i - 1])
  // Moving average (window=10)
  const w = 10
  const smoothed = delta.map((_, i) => {
    const start = Math.max(0, i - w + 1)
    const slice = delta.slice(start, i + 1)
    return slice.reduce((s, v) => s + v, 0) / slice.length
  })
  return {
    ...baseChartOption,
    grid: { left: 70, right: 25, top: 40, bottom: 55 },
    title: { text: 'Velocidad de Mejora (ΔHV por iteración)', textStyle: { color: CHART_COLORS.text, fontSize: 13 }, left: 'center' },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        return `<span style="opacity:0.6">Iteración</span> <b>${c.iterations[p.dataIndex + 1]}</b><br><span style="opacity:0.6">ΔHV:</span> <b>${p.value.toFixed(1)}</b>`
      },
    },
    xAxis: {
      type: 'category', data: c.iterations.slice(1).map(String),
      name: 'Iteración', nameLocation: 'center', nameGap: 32,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, interval: Math.floor(c.iterations.length / 10) },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    yAxis: {
      type: 'value', name: 'ΔHV', nameLocation: 'center', nameGap: 55,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    series: [{
      type: 'line', data: smoothed, symbol: 'none', smooth: true,
      lineStyle: { color: CHART_COLORS.green, width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,229,160,0.3)' }, { offset: 1, color: 'rgba(0,229,160,0)' }] } },
      markLine: { silent: true, symbol: 'none', data: [{ yAxis: 0, lineStyle: { color: 'rgba(255,255,255,0.1)', type: 'solid' }, label: { show: false } }] },
    }],
  }
})

// ── HV Distribution (dot strip + markArea box plot) ──
const distributionOption = computed<EChartsOption>(() => {
  if (!runsHV.value || !summary.value) return {}
  const hvs = runsHV.value.runs.map(r => r.hv_final).sort((a, b) => a - b)
  const mean = summary.value.hv_stats.mean
  const std = summary.value.hv_stats.std
  const min = hvs[0], max = hvs[hvs.length - 1]
  const q1 = hvs[Math.floor(hvs.length * 0.25)]
  const median = hvs[Math.floor(hvs.length * 0.5)]
  const q3 = hvs[Math.floor(hvs.length * 0.75)]
  const pad = Math.max(std * 0.5, (max - min) * 0.2, 1)
  return {
    ...baseChartOption,
    grid: { left: 80, right: 30, top: 40, bottom: 40 },
    title: { text: 'Distribución del HV Final', textStyle: { color: CHART_COLORS.text, fontSize: 13 }, left: 'center' },
    tooltip: { ...baseTooltip, trigger: 'item', confine: true },
    xAxis: {
      type: 'value',
      min: Math.floor(min - pad),
      max: Math.ceil(max + pad),
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => (v / 1000).toFixed(0) + 'k' },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: { type: 'value', show: false, min: -0.3, max: 1.3 },
    series: [
      // Individual points (jittered scatter)
      {
        type: 'scatter',
        data: hvs.map((h, i) => [h, 0.5 + (Math.sin(i * 2.1) * 0.35)]),
        symbolSize: 10,
        itemStyle: { color: CHART_COLORS.green, opacity: 0.8, borderColor: 'rgba(255,255,255,0.3)', borderWidth: 1 },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: CHART_COLORS.green, borderColor: '#fff' } },
        tooltip: { formatter: (p: any) => `HV: <b>${Math.round(p.value[0]).toLocaleString()}</b>` },
        // IQR box via markArea
        markArea: {
          silent: true,
          itemStyle: { color: 'rgba(0,60,166,0.3)', borderColor: CHART_COLORS.primaryLight, borderWidth: 1, borderType: 'solid' },
          data: [[{ xAxis: q1, yAxis: 0.15 }, { xAxis: q3, yAxis: 0.85 }]],
        },
        // Median + whiskers via markLine
        markLine: {
          silent: true,
          symbol: 'none',
          label: { show: false },
          data: [
            [{ coord: [median, 0.1], lineStyle: { color: CHART_COLORS.yellow, width: 2.5, type: 'solid' } }, { coord: [median, 0.9] }],
            [{ coord: [min, 0.5], lineStyle: { color: 'rgba(255,255,255,0.3)', width: 1, type: 'dashed' } }, { coord: [q1, 0.5] }],
            [{ coord: [q3, 0.5], lineStyle: { color: 'rgba(255,255,255,0.3)', width: 1, type: 'dashed' } }, { coord: [max, 0.5] }],
          ],
        },
      },
      // Mean marker (diamond)
      {
        type: 'scatter', data: [[mean, 0.5]], symbol: 'diamond', symbolSize: 16,
        itemStyle: { color: CHART_COLORS.red, borderColor: '#fff', borderWidth: 2 },
        tooltip: { formatter: () => `<span style="color:${CHART_COLORS.red}">Media (μ) = ${Math.round(mean).toLocaleString()}</span>` },
        zlevel: 1,
      },
    ],
  }
})

// ── HV bars sorted ──
const hvBarsOption = computed<EChartsOption>(() => {
  if (!runsHV.value || !summary.value) return {}
  const runs = [...runsHV.value.runs].sort((a: RunHV, b: RunHV) => b.hv_final - a.hv_final)
  const mean = summary.value.hv_stats.mean
  const hvMin = runs[runs.length - 1].hv_final
  const hvMax = runs[0].hv_final
  const hvRange = hvMax - hvMin
  const yMin = Math.floor((hvMin - hvRange * 0.3) / 1000) * 1000
  return {
    ...baseChartOption,
    grid: { left: 70, right: 20, top: 30, bottom: 50 },
    title: { text: 'HV por Corrida (ordenado)', textStyle: { color: CHART_COLORS.text, fontSize: 13 }, left: 'center' },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const r = runs[p.dataIndex]
        return `<b>Corrida #${r.run}</b> (seed ${r.seed})<br>HV: <b>${Math.round(r.hv_final).toLocaleString()}</b><br>Pareto: ${r.num_pareto} sol.<br>Ranking: #${p.dataIndex + 1} de ${runs.length}`
      },
    },
    xAxis: { type: 'category', data: runs.map((r: RunHV) => `#${r.run}`), axisLabel: { color: CHART_COLORS.textMuted, fontSize: 8, rotate: 45 } },
    yAxis: { type: 'value', min: yMin, axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => (v / 1000).toFixed(0) + 'k' }, splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } } },
    series: [{
      type: 'bar',
      data: runs.map((r: RunHV, i: number) => ({
        value: Math.round(r.hv_final),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: CHART_COLORS.primary }, { offset: 1, color: CHART_COLORS.green }] },
          opacity: 0.4 + 0.6 * (1 - i / runs.length),
          borderRadius: [4, 4, 0, 0],
        },
      })),
      markLine: { silent: true, symbol: 'none', data: [{ yAxis: Math.round(mean), lineStyle: { color: CHART_COLORS.red, type: 'dashed' }, label: { formatter: `μ = ${Math.round(mean).toLocaleString()}`, color: CHART_COLORS.red, fontSize: 9 } }] },
      animationDuration: 800, animationDelay: (idx: number) => idx * 25,
    }],
  }
})

// ── Pareto size bars ──
const paretoSizeOption = computed<EChartsOption>(() => {
  if (!runsHV.value) return {}
  const runs = runsHV.value.runs
  const meanPareto = runs.reduce((s: number, r: RunHV) => s + r.num_pareto, 0) / runs.length
  return {
    ...baseChartOption,
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    title: { text: 'Soluciones Pareto por Corrida', textStyle: { color: CHART_COLORS.text, fontSize: 13 }, left: 'center' },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const r = runs[p.dataIndex]
        return `<b>Corrida #${r.run}</b><br>Pareto: <b>${r.num_pareto}</b> soluciones<br>HV: ${Math.round(r.hv_final).toLocaleString()}`
      },
    },
    xAxis: { type: 'category', data: runs.map((r: RunHV) => `#${r.run}`), axisLabel: { color: CHART_COLORS.textMuted, fontSize: 8, rotate: 45 } },
    yAxis: { type: 'value', axisLabel: { color: CHART_COLORS.textMuted }, splitLine: { lineStyle: { color: CHART_COLORS.grid } } },
    series: [{
      type: 'bar',
      data: runs.map((r: RunHV) => ({
        value: r.num_pareto,
        itemStyle: {
          color: r.num_pareto >= meanPareto
            ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: CHART_COLORS.yellow }, { offset: 1, color: 'rgba(255,214,0,0.3)' }] }
            : { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: CHART_COLORS.blue }, { offset: 1, color: 'rgba(96,165,250,0.2)' }] },
          borderRadius: [4, 4, 0, 0],
        },
      })),
      markLine: { silent: true, symbol: 'none', data: [{ yAxis: Math.round(meanPareto), lineStyle: { color: CHART_COLORS.red, type: 'dashed' }, label: { formatter: `μ = ${Math.round(meanPareto)}`, color: CHART_COLORS.red, fontSize: 9 } }] },
      animationDuration: 800, animationDelay: (idx: number) => idx * 25,
    }],
  }
})

// ── Per-run Pareto scatter ──
const runParetoOption = computed<EChartsOption>(() => {
  if (!selectedRunData.value) return {}
  const pts = selectedRunData.value.points
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2)
  const f1Min = Math.min(...f1s), f1Max = Math.max(...f1s)
  const f2Min = Math.min(...f2s), f2Max = Math.max(...f2s)
  const f1Pad = Math.max((f1Max - f1Min) * 0.12, 0.02)
  const f2Pad = Math.max((f2Max - f2Min) * 0.12, 0.2)
  return {
    ...baseChartOption,
    grid: { left: 70, right: 30, top: 50, bottom: 55 },
    title: { text: `Frente de Pareto — Corrida #${selectedRunData.value.run}`, textStyle: { color: CHART_COLORS.text, fontSize: 13 }, left: 'center' },
    tooltip: {
      ...baseTooltip, trigger: 'item', confine: true,
      formatter: (p: any) => {
        const pt = pts[p.dataIndex]
        return `f₁: <b>${p.value[0].toFixed(4)}</b><br>f₂: <b>${p.value[1].toFixed(4)}</b><br>f₃: <b>${pt.f3.toLocaleString()}</b><br>Visas: ${pt.visas_used.toLocaleString()}`
      },
    },
    xAxis: {
      type: 'value', name: 'f₁ espera (años)', nameLocation: 'center', nameGap: 35,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      min: +((f1Min - f1Pad).toFixed(2)), max: +((f1Max + f1Pad).toFixed(2)),
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => v.toFixed(2) },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'value', name: 'f₂ disparidad (años)', nameLocation: 'center', nameGap: 55,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      min: +((f2Min - f2Pad).toFixed(2)), max: +((f2Max + f2Pad).toFixed(2)),
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => v.toFixed(1) },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    series: [{
      type: 'scatter', data: pts.map(p => [p.f1, p.f2]),
      symbolSize: (val: number[]) => { const t = pts.length > 1 ? (val[0] - f1Min) / (f1Max - f1Min || 1) : 0.5; return 8 + t * 10 },
      itemStyle: { color: { type: 'radial', x: 0.5, y: 0.5, r: 0.5, colorStops: [{ offset: 0, color: CHART_COLORS.green }, { offset: 1, color: 'rgba(0,229,160,0.4)' }] }, borderColor: 'rgba(255,255,255,0.15)', borderWidth: 1 },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: CHART_COLORS.green, borderColor: '#fff' } },
      animationDelay: (idx: number) => idx * 5,
    }],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Convergencia del Algoritmo</h1>

    <!-- ===== INTRO ===== -->
    <div class="card bg-primary/5 border-primary/20 space-y-2">
      <p class="text-sm text-gray-300 leading-relaxed">
        El <strong class="text-white">hipervolumen (HV)</strong> mide el volumen del espacio tridimensional
        (f₁ × f₂ × f₃) dominado por el frente de Pareto. Un HV mayor indica soluciones más cercanas al óptimo
        y mayor diversidad de compromisos.
      </p>
      <p class="text-xs text-gray-500">
        Analizamos <strong class="text-white">30 corridas independientes</strong> con 500 iteraciones cada una
        para verificar que el algoritmo converge de forma consistente y no fue suerte de una sola ejecución.
      </p>
    </div>

    <!-- ===== KPIs ===== -->
    <section v-if="summary && convergence" class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <KpiCard
        label="HV Final Medio"
        :value="formatNumber(Math.round(summary.hv_stats.mean))"
        :unit="'± ' + formatNumber(Math.round(summary.hv_stats.std)) + (cv ? ' (CV ' + cv + '%)' : '')"
      />
      <KpiCard
        label="Mejor Corrida"
        :value="bestRun ? '#' + bestRun.run : '...'"
        :unit="bestRun ? 'HV ' + formatNumber(Math.round(bestRun.hv_final)) + ' · seed ' + bestRun.seed : ''"
        color="text-accent-green"
      />
      <KpiCard
        label="Peor Corrida"
        :value="worstRun ? '#' + worstRun.run : '...'"
        :unit="worstRun ? 'HV ' + formatNumber(Math.round(worstRun.hv_final)) : ''"
        color="text-accent-red"
      />
      <KpiCard label="Mejora vs Inicio" :value="hvGainPct" unit="de crecimiento" color="text-accent-yellow" />
      <KpiCard label="95% Convergencia" :value="convergence95 !== null ? 'Iter ' + convergence95 : '...'" unit="de 500 iteraciones" />
    </section>

    <!-- ===== MAIN CONVERGENCE CHART ===== -->
    <ClientOnly>
      <div v-if="convergence" class="card space-y-2">
        <VChart :option="mainConvergenceOption" autoresize class="w-full h-[480px]" />
        <div class="flex flex-wrap gap-4 text-[10px] text-gray-500 justify-center">
          <span><span class="inline-block w-6 h-0.5 bg-gradient-to-r from-primary to-accent-green mr-1 align-middle" /> HV medio</span>
          <span><span class="inline-block w-4 h-3 bg-primary/25 mr-1 align-middle rounded-sm" /> ± 1σ (68% de corridas)</span>
          <span><span class="inline-block w-4 h-3 bg-primary/10 mr-1 align-middle rounded-sm" /> ± 2σ (95% de corridas)</span>
          <span class="text-accent-yellow">┊ 95% convergencia</span>
          <span class="text-accent-green">┈ HV final</span>
        </div>
      </div>
    </ClientOnly>

    <!-- ===== HV EXPLANATION ===== -->
    <details class="card">
      <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors font-medium">
        ¿Cómo se lee esta gráfica?
      </summary>
      <div class="mt-3 space-y-3 text-xs text-gray-400 leading-relaxed">
        <p>
          <strong class="text-white">La línea central</strong> muestra el HV promedio de las 30 corridas en cada iteración.
          Sube rápidamente al inicio (el algoritmo aprende) y se aplana al final (convergencia).
        </p>
        <p>
          <strong class="text-white">La banda ± 1σ</strong> indica dónde caen el 68% de las corridas.
          Una banda estrecha = resultados consistentes entre corridas.
          <strong class="text-white">La banda ± 2σ</strong> cubre el 95%.
        </p>
        <p>
          <strong class="text-accent-yellow">La línea punteada vertical</strong> marca la iteración donde el HV alcanza el 95% de su valor final
          — a partir de ahí, la mejora marginal es mínima.
        </p>
        <p>
          <strong class="text-accent-green">La línea horizontal</strong> es el HV final alcanzado.
          Se expresa en unidades de años² × visas (producto de las tres dimensiones del espacio objetivo).
        </p>
      </div>
    </details>

    <!-- ===== VELOCITY CHART ===== -->
    <ClientOnly>
      <div v-if="convergence" class="card space-y-2">
        <VChart :option="velocityOption" autoresize class="w-full h-[300px]" />
        <p class="text-[10px] text-gray-500 text-center">
          Derivada suavizada del HV medio (promedio móvil de 10 iteraciones).
          Barras altas = aprendizaje rápido · zona plana = convergencia alcanzada.
        </p>
      </div>
    </ClientOnly>

    <!-- ===== HV CALCULATION EXAMPLE ===== -->
    <section class="card space-y-5">
      <div>
        <h2 class="text-sm font-bold text-white">Ejemplo paso a paso: Cálculo del Hipervolumen</h2>
        <p class="text-xs text-gray-400 mt-1 leading-relaxed">
          Cada solución del Pareto "reclama" una <strong class="text-white">caja 3D</strong> en el espacio de objetivos.
          El HV es el volumen total de la <strong class="text-white">unión</strong> de todas esas cajas.
          Usamos <strong class="text-white">datos reales</strong> de la corrida #0.
        </p>
      </div>

      <div class="space-y-5">
        <!-- Step 1: Reference point -->
        <div class="flex gap-3">
          <div class="flex-none w-7 h-7 rounded-full bg-accent-red/20 border border-accent-red/40 flex items-center justify-center text-xs font-bold text-accent-red">1</div>
          <div class="flex-1 space-y-2">
            <h3 class="text-xs font-semibold text-white">Fijar el punto de referencia r (el "rincón peor")</h3>
            <p class="text-[11px] text-gray-400">Elegimos un punto <strong class="text-accent-red">peor que cualquier solución</strong> — el techo del espacio:</p>
            <div class="grid grid-cols-3 gap-2">
              <div class="bg-dark-bg1 rounded-lg p-2.5 text-center border border-dark-border">
                <p class="text-[9px] text-gray-500">r₁ espera</p>
                <p class="font-mono text-sm font-bold text-accent-red">10.0 <span class="text-[9px] text-gray-600 font-normal">años</span></p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-2.5 text-center border border-dark-border">
                <p class="text-[9px] text-gray-500">r₂ disparidad</p>
                <p class="font-mono text-sm font-bold text-accent-red">16.0 <span class="text-[9px] text-gray-600 font-normal">años</span></p>
              </div>
              <div class="bg-dark-bg1 rounded-lg p-2.5 text-center border border-dark-border">
                <p class="text-[9px] text-gray-500">r₃ desperdicio</p>
                <p class="font-mono text-sm font-bold text-accent-red">50,000 <span class="text-[9px] text-gray-600 font-normal">visas</span></p>
              </div>
            </div>
            <p class="text-[10px] text-gray-500">Volumen máximo teórico = 10 × 16 × 50,000 = <strong class="text-white">8,000,000</strong></p>
          </div>
        </div>

        <!-- Step 2: Two real solutions -->
        <div class="flex gap-3">
          <div class="flex-none w-7 h-7 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-xs font-bold text-primary-300">2</div>
          <div class="flex-1 space-y-2">
            <h3 class="text-xs font-semibold text-white">Tomar dos soluciones reales del Pareto</h3>
            <p class="text-[11px] text-gray-400">Cada solución es buena en algo distinto — por eso sus cajas cubren zonas diferentes:</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div class="bg-primary/5 rounded-lg p-3 border border-primary/20 space-y-1.5">
                <p class="text-[10px] text-primary-300 font-semibold uppercase tracking-wider">Sol. A — mejor espera (f₁)</p>
                <div class="grid grid-cols-3 gap-1 font-mono text-xs">
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₁</p><p class="text-primary-300 font-bold">7.19</p></div>
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₂</p><p class="text-gray-400">12.00</p></div>
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₃</p><p class="text-gray-400">16,280</p></div>
                </div>
                <p class="text-[9px] text-gray-600">Caja <strong class="text-gray-400">chica</strong>: buena en f₁, pero f₂ y f₃ altos → Δ₂ y Δ₃ pequeños</p>
              </div>
              <div class="bg-accent-green/5 rounded-lg p-3 border border-accent-green/20 space-y-1.5">
                <p class="text-[10px] text-accent-green font-semibold uppercase tracking-wider">Sol. B — cero desperdicio (f₃)</p>
                <div class="grid grid-cols-3 gap-1 font-mono text-xs">
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₁</p><p class="text-gray-400">7.37</p></div>
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₂</p><p class="text-accent-green font-bold">5.35</p></div>
                  <div class="text-center"><p class="text-[9px] text-gray-500">f₃</p><p class="text-accent-green font-bold">0</p></div>
                </div>
                <p class="text-[9px] text-gray-600">Caja <strong class="text-gray-400">enorme</strong>: f₂=5.35 → Δ₂=10.65 y f₃=0 → Δ₃=50,000</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Calculate boxes -->
        <div class="flex gap-3">
          <div class="flex-none w-7 h-7 rounded-full bg-accent-yellow/20 border border-accent-yellow/40 flex items-center justify-center text-xs font-bold text-accent-yellow">3</div>
          <div class="flex-1 space-y-3">
            <h3 class="text-xs font-semibold text-white">Calcular el volumen de cada caja</h3>
            <p class="text-[11px] text-gray-400">La caja va desde la solución hasta el punto de referencia: <strong class="text-white">Δ = r − f</strong></p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <!-- Box A -->
              <div class="bg-dark-bg1 rounded-lg p-3 space-y-1.5 font-mono text-xs border border-primary/20">
                <p class="text-primary-300 font-semibold text-[10px]">CAJA A</p>
                <p><span class="text-gray-500">Δ₁ =</span> <span class="text-accent-red">10.0</span> − <span class="text-primary-300">7.19</span> = <span class="text-white font-bold">2.81</span></p>
                <p><span class="text-gray-500">Δ₂ =</span> <span class="text-accent-red">16.0</span> − 12.00 = <span class="text-white font-bold">4.00</span></p>
                <p><span class="text-gray-500">Δ₃ =</span> <span class="text-accent-red">50,000</span> − 16,280 = <span class="text-white font-bold">33,720</span></p>
                <div class="border-t border-dark-border pt-1.5 mt-1.5">
                  <p class="text-gray-400">Vol = 2.81 × 4.00 × 33,720</p>
                  <p class="text-primary-300 font-bold text-sm">= 379,013</p>
                </div>
              </div>
              <!-- Box B -->
              <div class="bg-dark-bg1 rounded-lg p-3 space-y-1.5 font-mono text-xs border border-accent-green/20">
                <p class="text-accent-green font-semibold text-[10px]">CAJA B</p>
                <p><span class="text-gray-500">Δ₁ =</span> <span class="text-accent-red">10.0</span> − 7.37 = <span class="text-white font-bold">2.63</span></p>
                <p><span class="text-gray-500">Δ₂ =</span> <span class="text-accent-red">16.0</span> − <span class="text-accent-green">5.35</span> = <span class="text-white font-bold">10.65</span></p>
                <p><span class="text-gray-500">Δ₃ =</span> <span class="text-accent-red">50,000</span> − <span class="text-accent-green">0</span> = <span class="text-white font-bold">50,000</span></p>
                <div class="border-t border-dark-border pt-1.5 mt-1.5">
                  <p class="text-gray-400">Vol = 2.63 × 10.65 × 50,000</p>
                  <p class="text-accent-green font-bold text-sm">= 1,400,475</p>
                </div>
              </div>
            </div>
            <div class="bg-accent-yellow/5 rounded-lg p-3 border border-accent-yellow/20">
              <p class="text-[11px] text-gray-300">
                <strong class="text-accent-yellow">La clave:</strong> la caja B es <strong class="text-white">3.7× más grande</strong> que A
                porque Sol. B tiene f₂ = 5.35 (Δ₂ = 10.65, casi 3× más que A)
                y f₃ = 0 (Δ₃ = 50,000 vs 33,720). Las soluciones con mejor equidad/utilización
                generan cajas enormes.
              </p>
            </div>
          </div>
        </div>

        <!-- Step 4: Union -->
        <div class="flex gap-3">
          <div class="flex-none w-7 h-7 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-xs font-bold text-white">4</div>
          <div class="flex-1 space-y-2">
            <h3 class="text-xs font-semibold text-white">Unir las cajas (restar el traslape)</h3>
            <p class="text-[11px] text-gray-400">Las dos cajas se solapan en la zona donde ambas "cubren" el mismo espacio. Para no contar doble:</p>
            <div class="bg-dark-bg1 rounded-lg p-3 space-y-2 font-mono text-xs border border-dark-border">
              <div>
                <p class="text-gray-500 text-[10px]">Intersección = caja desde max(f₁,f₂,f₃) de ambas hasta r:</p>
                <p class="text-gray-400 mt-1">max(f₁) = max(7.19, 7.37) = 7.37 → Δ₁ = 2.63</p>
                <p class="text-gray-400">max(f₂) = max(12.00, 5.35) = 12.00 → Δ₂ = 4.00</p>
                <p class="text-gray-400">max(f₃) = max(16,280, 0) = 16,280 → Δ₃ = 33,720</p>
                <p class="text-gray-300 mt-1">Vol(A∩B) = 2.63 × 4.00 × 33,720 = <span class="text-white font-bold">354,734</span></p>
              </div>
              <div class="border-t border-dark-border pt-2 space-y-1">
                <p class="text-white text-sm font-semibold">HV = Vol(A) + Vol(B) − Vol(A∩B)</p>
                <p class="text-gray-300">= <span class="text-primary-300">379,013</span> + <span class="text-accent-green">1,400,475</span> − 354,734</p>
                <p class="text-accent-yellow font-bold text-lg">= 1,424,754</p>
              </div>
            </div>
            <p class="text-[11px] text-gray-400">
              Con solo 2 soluciones ya tenemos <strong class="text-white">1.42 millones</strong>.
              La caja B contribuye la mayor parte porque cubre una región enorme del espacio.
            </p>
          </div>
        </div>

        <!-- Step 5: Progression table -->
        <div class="flex gap-3">
          <div class="flex-none w-7 h-7 rounded-full bg-accent-yellow/20 border border-accent-yellow/40 flex items-center justify-center text-xs font-bold text-accent-yellow">5</div>
          <div class="flex-1 space-y-2">
            <h3 class="text-xs font-semibold text-white">Escalar a 100 soluciones → 1.8M</h3>
            <p class="text-[11px] text-gray-400">Cada nueva solución Pareto añade una caja que cubre una zona diferente. La unión crece rápido al principio y luego se estabiliza:</p>
            <div class="bg-dark-bg1 rounded-lg border border-dark-border overflow-hidden">
              <table class="w-full text-xs font-mono">
                <thead>
                  <tr class="border-b border-dark-border bg-dark-bg2">
                    <th class="px-3 py-2 text-left text-[9px] text-gray-500 uppercase font-semibold">Soluciones</th>
                    <th class="px-3 py-2 text-right text-[9px] text-gray-500 uppercase font-semibold">HV (unión)</th>
                    <th class="px-3 py-2 text-right text-[9px] text-gray-500 uppercase font-semibold">% del máximo</th>
                    <th class="px-3 py-2 text-left text-[9px] text-gray-500 uppercase font-semibold">Notas</th>
                  </tr>
                </thead>
                <tbody class="text-gray-400">
                  <tr class="border-b border-dark-border/30">
                    <td class="px-3 py-1.5 text-primary-300 font-semibold">1 (Sol A)</td>
                    <td class="px-3 py-1.5 text-right text-white">379,013</td>
                    <td class="px-3 py-1.5 text-right">4.7%</td>
                    <td class="px-3 py-1.5 text-[10px]">Solo la caja de mejor f₁</td>
                  </tr>
                  <tr class="border-b border-dark-border/30">
                    <td class="px-3 py-1.5 text-accent-green font-semibold">2 (A + B)</td>
                    <td class="px-3 py-1.5 text-right text-white">1,424,754</td>
                    <td class="px-3 py-1.5 text-right">17.8%</td>
                    <td class="px-3 py-1.5 text-[10px]">B agrega una caja enorme</td>
                  </tr>
                  <tr class="border-b border-dark-border/30">
                    <td class="px-3 py-1.5 font-semibold">100</td>
                    <td class="px-3 py-1.5 text-right text-accent-yellow font-bold">1,776,161</td>
                    <td class="px-3 py-1.5 text-right text-accent-yellow">22.2%</td>
                    <td class="px-3 py-1.5 text-[10px]">Corrida #0 completa</td>
                  </tr>
                  <tr>
                    <td class="px-3 py-1.5 font-semibold">406</td>
                    <td class="px-3 py-1.5 text-right text-white font-bold">1,785,803</td>
                    <td class="px-3 py-1.5 text-right">22.3%</td>
                    <td class="px-3 py-1.5 text-[10px]">30 corridas combinadas (HV medio)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="bg-primary/5 rounded-lg p-3 border border-primary/20">
              <p class="text-[11px] text-gray-300 leading-relaxed">
                <strong class="text-white">¿Por qué llega a millones?</strong>
                Porque la dimensión f₃ (visas) está en las <strong class="text-white">decenas de miles</strong>.
                Multiplicar Δ₁ (~3 años) × Δ₂ (~10 años) × Δ₃ (~40,000 visas)
                ya da ~1.2M para una sola caja. Las unidades del HV son
                <strong class="text-white">años² × visas</strong> — un número grande, pero correcto.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== STATISTICAL ANALYSIS ===== -->
    <section class="space-y-4">
      <div>
        <h2 class="text-sm font-bold text-white">Variabilidad entre Corridas</h2>
        <p class="text-[10px] text-gray-500 mt-0.5">Distribución y ranking del hipervolumen final de las 30 ejecuciones independientes.</p>
      </div>

      <ClientOnly>
        <div v-if="runsHV && summary" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <!-- Distribution -->
          <div class="card space-y-2">
            <VChart :option="distributionOption" autoresize class="w-full h-[280px]" />
            <div class="flex flex-wrap gap-3 text-[10px] text-gray-500 justify-center">
              <span><span class="inline-block w-3 h-3 rounded-sm bg-primary/30 border border-primary-300/50 mr-1 align-middle" /> IQR (Q1–Q3)</span>
              <span class="text-accent-yellow">| Mediana</span>
              <span><span class="inline-block w-2 h-2 rounded-full bg-accent-green mr-1 align-middle" /> Corrida individual</span>
              <span><span class="inline-block w-2 h-2 rounded-sm bg-accent-red mr-1 align-middle" style="transform: rotate(45deg)" /> Media (μ)</span>
            </div>
          </div>
          <!-- Sorted HV bars -->
          <div class="card">
            <VChart :option="hvBarsOption" autoresize class="w-full h-[300px]" />
          </div>
        </div>
      </ClientOnly>

      <!-- Pareto sizes -->
      <ClientOnly>
        <div v-if="runsHV" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-2 card">
            <VChart :option="paretoSizeOption" autoresize class="w-full h-[280px]" />
          </div>
          <div v-if="summary" class="card space-y-3">
            <h3 class="text-xs text-gray-500 uppercase tracking-wider font-semibold">Resumen Pareto</h3>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Media por corrida</span>
                <span class="font-mono text-white">{{ Math.round(runsHV.runs.reduce((s, r) => s + r.num_pareto, 0) / runsHV.runs.length) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Mínimo</span>
                <span class="font-mono text-gray-400">{{ Math.min(...runsHV.runs.map(r => r.num_pareto)) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Máximo</span>
                <span class="font-mono text-gray-400">{{ Math.max(...runsHV.runs.map(r => r.num_pareto)) }}</span>
              </div>
              <div class="border-t border-dark-border pt-2 flex justify-between text-sm">
                <span class="text-gray-500">Combinado (sin duplicados)</span>
                <span class="font-mono text-accent-yellow font-bold">{{ summary.combined_pareto_size }}</span>
              </div>
            </div>
            <p class="text-[10px] text-gray-600 leading-relaxed">
              Al combinar las 30 corridas y eliminar soluciones dominadas, quedan
              <strong class="text-gray-400">{{ summary.combined_pareto_size }}</strong> soluciones únicas.
              Esto es menos que la suma porque muchas corridas encuentran soluciones similares.
            </p>
          </div>
        </div>
      </ClientOnly>
    </section>

    <!-- ===== PER-RUN EXPLORER ===== -->
    <section v-if="runsHV" class="card space-y-4">
      <div>
        <h2 class="text-sm font-bold text-white">Explorar Corrida Individual</h2>
        <p class="text-[10px] text-gray-500 mt-0.5">
          Selecciona una corrida para ver su frente de Pareto y estadísticas.
        </p>
      </div>

      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="r in runsHV.runs"
          :key="r.run"
          class="px-2.5 py-1 text-xs font-mono rounded-md transition-all duration-150"
          :class="selectedRunIdx === r.run
            ? 'bg-primary text-white shadow-md shadow-primary/25'
            : 'bg-dark-bg2 text-gray-500 hover:text-white hover:bg-white/5'"
          @click="loadRun(r.run)"
        >
          #{{ r.run }}
        </button>
      </div>

      <!-- Run stats -->
      <div v-if="selectedRunHV" class="grid grid-cols-3 gap-3">
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-[10px] text-gray-500 uppercase">HV Final</p>
          <p class="font-mono text-lg font-bold text-white">{{ formatNumber(Math.round(selectedRunHV.hv_final)) }}</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-[10px] text-gray-500 uppercase">Ranking</p>
          <p class="font-mono text-lg font-bold" :class="selectedRunRank && selectedRunRank <= 5 ? 'text-accent-green' : selectedRunRank && selectedRunRank >= 25 ? 'text-accent-red' : 'text-white'">
            #{{ selectedRunRank }} <span class="text-gray-500 text-sm font-normal">/ 30</span>
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-[10px] text-gray-500 uppercase">Soluciones Pareto</p>
          <p class="font-mono text-lg font-bold text-accent-yellow">{{ selectedRunHV.num_pareto }}</p>
        </div>
      </div>

      <!-- Scatter -->
      <ClientOnly>
        <div v-if="selectedRunData">
          <VChart :option="runParetoOption" autoresize class="w-full h-[420px]" />
        </div>
      </ClientOnly>
    </section>

    <!-- ===== SUMMARY TABLE ===== -->
    <details v-if="runsHV" class="card">
      <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors font-medium">
        Ver tabla de todas las corridas
      </summary>
      <div class="mt-4 max-h-[400px] overflow-y-auto rounded-lg border border-dark-border">
        <table class="w-full text-xs">
          <thead class="sticky top-0 z-10 bg-dark-bg2">
            <tr class="border-b border-dark-border">
              <th class="px-3 py-2 text-left text-[10px] text-gray-500 uppercase font-semibold">Corrida</th>
              <th class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Seed</th>
              <th class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">HV Final</th>
              <th class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold"># Pareto</th>
              <th class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Ranking</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(r, ri) in [...runsHV.runs].sort((a, b) => b.hv_final - a.hv_final)"
              :key="r.run"
              class="border-b border-dark-border/20 transition-colors cursor-pointer"
              :class="selectedRunIdx === r.run ? 'bg-primary/15 text-white' : 'hover:bg-white/[0.03] text-gray-400'"
              @click="loadRun(r.run)"
            >
              <td class="px-3 py-1.5 font-mono">#{{ r.run }}</td>
              <td class="px-3 py-1.5 text-right font-mono text-gray-500">{{ r.seed }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ formatNumber(Math.round(r.hv_final)) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ r.num_pareto }}</td>
              <td class="px-3 py-1.5 text-right font-mono" :class="ri < 5 ? 'text-accent-green' : ri >= 25 ? 'text-accent-red' : ''">
                #{{ ri + 1 }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </div>
</template>
