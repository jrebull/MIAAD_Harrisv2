<script setup lang="ts">
import type { ParetoData, SummaryData, ParetoPoint, AllocationData } from '~/composables/useOptimizer'
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'
import { formatNumber } from '~/utils/formatters'

const { fetchPareto, fetchSummary, fetchCustomAllocation } = useOptimizer()

const pareto = ref<ParetoData | null>(null)
const summary = ref<SummaryData | null>(null)
const projection = ref<'f1f2' | 'f1f3' | 'f2f3' | '3d'>('f1f2')
const selectedPoint = ref<ParetoPoint | null>(null)

// Table state
const sortKey = ref<'f1' | 'f2' | 'f3' | 'visas_used'>('f1')
const sortAsc = ref(true)
const showTable = ref(false)

onMounted(async () => {
  const [p, s] = await Promise.all([fetchPareto(), fetchSummary()])
  pareto.value = p
  summary.value = s
})

function handleSelect(point: ParetoPoint) {
  selectedPoint.value = point
}

// ── Fetch allocation for selected point ──
const selectedAlloc = ref<AllocationData | null>(null)
const loadingAlloc = ref(false)

watch(selectedPoint, async (pt) => {
  if (!pt) { selectedAlloc.value = null; return }
  loadingAlloc.value = true
  try {
    selectedAlloc.value = await fetchCustomAllocation(pt.f1, pt.f2, pt.f3)
  } catch { selectedAlloc.value = null }
  loadingAlloc.value = false
})

// ── Knee point (max perpendicular distance on f1-f2) ──
const kneePoint = computed<ParetoPoint | null>(() => {
  if (!pareto.value?.points || pareto.value.points.length < 3) return null
  const pts = [...pareto.value.points].sort((a, b) => a.f1 - b.f1)
  const f1min = pts[0].f1, f1max = pts[pts.length - 1].f1
  const f2min = Math.min(...pts.map(p => p.f2))
  const f2max = Math.max(...pts.map(p => p.f2))
  const f1r = f1max - f1min || 1, f2r = f2max - f2min || 1
  const p1x = 0, p1y = (pts[0].f2 - f2min) / f2r
  const pnx = 1, pny = (pts[pts.length - 1].f2 - f2min) / f2r
  const dx = pnx - p1x, dy = pny - p1y
  const len = Math.sqrt(dx * dx + dy * dy) || 1
  const ux = dx / len, uy = dy / len
  let maxD = -1, best = pts[0]
  pts.forEach(p => {
    const px = (p.f1 - f1min) / f1r - p1x
    const py = (p.f2 - f2min) / f2r - p1y
    const proj = px * ux + py * uy
    const perpX = px - proj * ux, perpY = py - proj * uy
    const d = Math.sqrt(perpX * perpX + perpY * perpY)
    if (d > maxD) { maxD = d; best = p }
  })
  return best
})

// ── Scenario cards data ──
interface ScenarioCard {
  key: string
  name: string
  color: string
  border: string
  bg: string
  desc: string
  point: number[] // [f1, f2, f3]
  visas: number
}

const scenarioCards = computed<ScenarioCard[]>(() => {
  if (!summary.value || !pareto.value?.baseline) return []
  const s = summary.value
  const bl = pareto.value.baseline!
  const knee = kneePoint.value
  const cards: ScenarioCard[] = [
    {
      key: 'humanitario', name: 'Humanitario', color: 'text-accent-yellow', border: 'border-accent-yellow/30',
      bg: 'bg-accent-yellow/5', desc: 'Minimiza la espera global (f₁)',
      point: s.best_f1, visas: 140000 - s.best_f1[2],
    },
    {
      key: 'equilibrio', name: 'Equilibrio', color: 'text-primary-300', border: 'border-primary/30',
      bg: 'bg-primary/5', desc: 'Mejor compromiso (knee point)',
      point: knee ? [knee.f1, knee.f2, knee.f3] : s.best_f1, visas: knee ? knee.visas_used : 0,
    },
    {
      key: 'equidad', name: 'Equidad', color: 'text-accent-green', border: 'border-accent-green/30',
      bg: 'bg-accent-green/5', desc: 'Minimiza la brecha entre países (f₂)',
      point: s.best_f2, visas: 140000 - s.best_f2[2],
    },
    {
      key: 'max_utilizacion', name: 'Máx. Utilización', color: 'text-accent-blue', border: 'border-accent-blue/30',
      bg: 'bg-accent-blue/5', desc: 'Minimiza el desperdicio (f₃)',
      point: s.best_f3, visas: 140000 - s.best_f3[2],
    },
    {
      key: 'fifo', name: 'FIFO (actual)', color: 'text-accent-red', border: 'border-accent-red/30',
      bg: 'bg-accent-red/5', desc: 'Sistema vigente: orden de llegada',
      point: [bl.f1, bl.f2, bl.f3], visas: bl.visas_used,
    },
  ]
  return cards
})

function gapPct(val: number, fifo: number): string {
  const pct = ((val - fifo) / Math.abs(fifo)) * 100
  return (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%'
}
function gapClass(val: number, fifo: number): string {
  return val <= fifo ? 'text-accent-green' : 'text-accent-red'
}

// ── Sorted table ──
interface IndexedPoint extends ParetoPoint { _idx: number }
const sortedPoints = computed<IndexedPoint[]>(() => {
  if (!pareto.value?.points) return []
  const pts = pareto.value.points.map((p, i) => ({ ...p, _idx: i }))
  pts.sort((a, b) => sortAsc.value ? a[sortKey.value] - b[sortKey.value] : b[sortKey.value] - a[sortKey.value])
  return pts
})

function toggleSort(key: typeof sortKey.value) {
  if (sortKey.value === key) sortAsc.value = !sortAsc.value
  else { sortKey.value = key; sortAsc.value = true }
}
function sortArrow(key: string) {
  if (sortKey.value !== key) return ''
  return sortAsc.value ? ' ▲' : ' ▼'
}

// ── Visa distribution chart ──
const visaDistOption = computed<EChartsOption>(() => {
  if (!pareto.value?.points) return {}
  const pts = [...pareto.value.points].sort((a, b) => a.f1 - b.f1)
  const fifoUsed = pareto.value.baseline?.visas_used || 0
  return {
    ...baseChartOption,
    grid: { left: 60, right: 110, top: 40, bottom: 50 },
    title: {
      text: 'Distribución de Visas en el Frente',
      textStyle: { color: CHART_COLORS.text, fontSize: 13 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      confine: true,
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const pt = pts[p.dataIndex]
        return `<b>Solución ${p.dataIndex + 1}</b><br>Visas: <b>${pt.visas_used.toLocaleString()}</b> (${((pt.visas_used / 140000) * 100).toFixed(1)}%)<br>f₁: ${pt.f1.toFixed(3)} · f₂: ${pt.f2.toFixed(3)} · f₃: ${pt.f3.toLocaleString()}`
      },
    },
    xAxis: {
      type: 'category',
      data: pts.map((_: any, i: number) => i + 1),
      axisLabel: { show: false },
      name: `${pts.length} soluciones (ordenadas por f₁)`,
      nameLocation: 'center',
      nameGap: 25,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: 'Visas otorgadas',
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => (v / 1000).toFixed(0) + 'k' },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
      min: (value: any) => Math.max(0, value.min - 5000),
      max: 145000,
    },
    series: [
      {
        type: 'bar',
        data: pts.map((p: ParetoPoint) => ({
          value: p.visas_used,
          itemStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: CHART_COLORS.primary },
                { offset: 1, color: CHART_COLORS.green },
              ],
            },
            borderRadius: [2, 2, 0, 0],
          },
        })),
        barMaxWidth: 6,
        animationDuration: 800,
        animationDelay: (idx: number) => idx * 2,
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { type: 'dashed', width: 1.5 },
          data: [
            { yAxis: 140000, lineStyle: { color: CHART_COLORS.yellow }, label: { formatter: '140,000 total', color: CHART_COLORS.yellow, fontSize: 10 } },
            ...(fifoUsed ? [{ yAxis: fifoUsed, lineStyle: { color: CHART_COLORS.red, type: 'dotted' as const }, label: { formatter: `FIFO: ${fifoUsed.toLocaleString()}`, color: CHART_COLORS.red, fontSize: 10 } }] : []),
          ],
        },
      },
    ],
  }
})

// ── Allocation breakdown for selected point ──
const CATS = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']
const CAT_COLORS = [CHART_COLORS.primary, CHART_COLORS.green, CHART_COLORS.yellow, CHART_COLORS.blue, '#FF6B6B']

const selectedAllocOption = computed<EChartsOption>(() => {
  if (!selectedAlloc.value) return {}
  const rows = [...selectedAlloc.value.rows].sort((a, b) => b.total - a.total)
  return {
    ...baseChartOption,
    grid: { left: 110, right: 30, top: 40, bottom: 30 },
    title: {
      text: 'Distribución de Visas — Solución Seleccionada',
      textStyle: { color: CHART_COLORS.text, fontSize: 13 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      confine: true,
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const ps = Array.isArray(params) ? params : [params]
        if (!ps.length) return ''
        const row = rows[ps[0].dataIndex]
        let html = `<b>${row.flag} ${row.country}</b> — <b>${row.total.toLocaleString()}</b> visas<br>`
        ps.forEach((p: any) => {
          if (p.value > 0) html += `<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:4px;"></span>${p.seriesName}: <b>${p.value.toLocaleString()}</b><br>`
        })
        return html
      },
    },
    legend: {
      top: 8, right: 16,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
    },
    xAxis: {
      type: 'value',
      name: 'Visas',
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLabel: { color: CHART_COLORS.textMuted, formatter: (v: number) => (v / 1000).toFixed(0) + 'k' },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map(r => r.flag + ' ' + r.country),
      inverse: true,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      axisLine: { lineStyle: { color: CHART_COLORS.grid } },
    },
    series: CATS.map((cat, i) => ({
      name: cat,
      type: 'bar',
      stack: 'total',
      data: rows.map(r => r.categories[cat] || 0),
      itemStyle: { color: CAT_COLORS[i], borderRadius: i === CATS.length - 1 ? [0, 2, 2, 0] : undefined },
      barMaxWidth: 18,
      emphasis: { focus: 'series' },
    })),
  }
})

// ── Parallel Coordinates chart ──
const parallelOption = computed<EChartsOption>(() => {
  if (!pareto.value?.points || !summary.value) return {}
  const pts = pareto.value.points
  const bl = pareto.value.baseline
  const knee = kneePoint.value

  // Compute axis ranges from data
  const f1vals = pts.map(p => p.f1)
  const f2vals = pts.map(p => p.f2)
  const f3vals = pts.map(p => p.f3)
  const vvals = pts.map(p => p.visas_used)

  const f1min = Math.min(...f1vals), f1max = Math.max(...f1vals)
  const f2min = Math.min(...f2vals), f2max = Math.max(...f2vals)
  const f3min = Math.min(...f3vals), f3max = Math.max(...f3vals)
  const vmin = Math.min(...vvals), vmax = Math.max(...vvals)

  // Expand ranges slightly if baseline falls outside
  const axF1min = bl ? Math.min(f1min, bl.f1) : f1min
  const axF1max = bl ? Math.max(f1max, bl.f1) : f1max
  const axF2min = bl ? Math.min(f2min, bl.f2) : f2min
  const axF2max = bl ? Math.max(f2max, bl.f2) : f2max
  const axF3min = bl ? Math.min(f3min, bl.f3) : f3min
  const axF3max = bl ? Math.max(f3max, bl.f3) : f3max
  const axVmin = bl ? Math.min(vmin, bl.visas_used) : vmin
  const axVmax = bl ? Math.max(vmax, bl.visas_used) : vmax

  // Pad ranges by 5%
  const pad = (min: number, max: number) => {
    const d = (max - min) * 0.05 || 1
    return { min: min - d, max: max + d }
  }
  const r1 = pad(axF1min, axF1max)
  const r2 = pad(axF2min, axF2max)
  const r3 = pad(axF3min, axF3max)
  const rv = pad(axVmin, axVmax)

  // Build series data
  const allData = pts.map(p => [p.f1, p.f2, p.f3, p.visas_used])

  // Find scenario extremes
  const minF1pt = pts.reduce((best, p) => p.f1 < best.f1 ? p : best, pts[0])
  const minF2pt = pts.reduce((best, p) => p.f2 < best.f2 ? p : best, pts[0])
  const minF3pt = pts.reduce((best, p) => p.f3 < best.f3 ? p : best, pts[0])

  const highlightSeries: any[] = []

  // Scenario extreme lines
  const extremes = [
    { point: minF1pt, color: CHART_COLORS.yellow, name: 'Min f₁ (Humanitario)' },
    { point: minF2pt, color: CHART_COLORS.green, name: 'Min f₂ (Equidad)' },
    { point: minF3pt, color: CHART_COLORS.blue, name: 'Min f₃ (Máx. Utilización)' },
  ]
  if (knee) {
    extremes.push({ point: knee, color: CHART_COLORS.primaryLight, name: 'Equilibrio (knee)' })
  }

  extremes.forEach(e => {
    highlightSeries.push({
      type: 'parallel',
      data: [[e.point.f1, e.point.f2, e.point.f3, e.point.visas_used]],
      lineStyle: { width: 2.5, color: e.color, opacity: 0.9 },
      name: e.name,
      smooth: false,
      silent: false,
      z: 3,
    })
  })

  // FIFO baseline as thick red dashed line
  if (bl) {
    highlightSeries.push({
      type: 'parallel',
      data: [[bl.f1, bl.f2, bl.f3, bl.visas_used]],
      lineStyle: { width: 3, color: CHART_COLORS.red, opacity: 1, type: 'dashed' },
      name: 'FIFO baseline',
      smooth: false,
      silent: false,
      z: 4,
    })
  }

  // Selected point as thick orange line
  if (selectedPoint.value) {
    const sp = selectedPoint.value
    highlightSeries.push({
      type: 'parallel',
      data: [[sp.f1, sp.f2, sp.f3, sp.visas_used]],
      lineStyle: { width: 3.5, color: '#FF8C00', opacity: 1 },
      name: 'Seleccionada',
      smooth: false,
      silent: false,
      z: 5,
    })
  }

  return {
    ...baseChartOption,
    grid: undefined, // parallel doesn't use grid
    tooltip: {
      ...baseTooltip,
      trigger: 'item' as const,
      formatter: (params: any) => {
        if (!params.data) return ''
        const d = params.data
        return `<b>${params.seriesName || 'Solución Pareto'}</b><br/>` +
          `f₁ espera: <b>${Number(d[0]).toFixed(4)}</b> años<br/>` +
          `f₂ disparidad: <b>${Number(d[1]).toFixed(4)}</b> años<br/>` +
          `f₃ desperdicio: <b>${Number(d[2]).toLocaleString()}</b> visas<br/>` +
          `Visas usadas: <b>${Number(d[3]).toLocaleString()}</b>`
      },
    },
    parallelAxis: [
      {
        dim: 0,
        name: 'f₁ espera\n(años)',
        min: +r1.min.toFixed(4),
        max: +r1.max.toFixed(4),
        nameTextStyle: { color: CHART_COLORS.yellow, fontSize: 11, fontWeight: 'bold' as const },
        axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10, formatter: (v: number) => v.toFixed(2) },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        splitLine: { show: false },
      },
      {
        dim: 1,
        name: 'f₂ disparidad\n(años)',
        min: +r2.min.toFixed(4),
        max: +r2.max.toFixed(4),
        nameTextStyle: { color: CHART_COLORS.green, fontSize: 11, fontWeight: 'bold' as const },
        axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10, formatter: (v: number) => v.toFixed(2) },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        splitLine: { show: false },
      },
      {
        dim: 2,
        name: 'f₃ desperdicio\n(visas)',
        min: Math.floor(r3.min),
        max: Math.ceil(r3.max),
        nameTextStyle: { color: CHART_COLORS.blue, fontSize: 11, fontWeight: 'bold' as const },
        axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10, formatter: (v: number) => (v / 1000).toFixed(1) + 'k' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        splitLine: { show: false },
      },
      {
        dim: 3,
        name: 'Visas\nUsadas',
        min: Math.floor(rv.min),
        max: Math.ceil(rv.max),
        nameTextStyle: { color: CHART_COLORS.text, fontSize: 11, fontWeight: 'bold' as const },
        axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10, formatter: (v: number) => (v / 1000).toFixed(0) + 'k' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        splitLine: { show: false },
      },
    ],
    parallel: {
      left: 60,
      right: 60,
      top: 40,
      bottom: 40,
      parallelAxisDefault: {
        type: 'value',
        nameLocation: 'start' as const,
        nameGap: 20,
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
        axisTick: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      },
    },
    series: [
      {
        type: 'parallel',
        name: 'Soluciones Pareto',
        data: allData,
        lineStyle: {
          width: 1,
          opacity: 0.15,
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: CHART_COLORS.blue },
              { offset: 1, color: CHART_COLORS.green },
            ],
          },
        },
        smooth: false,
        z: 1,
      },
      ...highlightSeries,
    ],
  } as EChartsOption
})

// ── Pareto front density heatmap (f₁ × f₂) ──
const DENSITY_BINS = 20

const densityOption = computed<EChartsOption>(() => {
  if (!pareto.value?.points || pareto.value.points.length === 0) return {}
  const pts = pareto.value.points
  const bl = pareto.value.baseline
  const knee = kneePoint.value

  // Compute ranges
  const f1vals = pts.map(p => p.f1)
  const f2vals = pts.map(p => p.f2)
  const f1min = Math.min(...f1vals), f1max = Math.max(...f1vals)
  const f2min = Math.min(...f2vals), f2max = Math.max(...f2vals)

  // Bin sizes
  const f1step = (f1max - f1min) / DENSITY_BINS || 0.001
  const f2step = (f2max - f2min) / DENSITY_BINS || 0.001

  // Count solutions per bin
  const grid: number[][] = Array.from({ length: DENSITY_BINS }, () => Array(DENSITY_BINS).fill(0))
  let maxCount = 0
  pts.forEach(p => {
    let xi = Math.floor((p.f1 - f1min) / f1step)
    let yi = Math.floor((p.f2 - f2min) / f2step)
    xi = Math.min(xi, DENSITY_BINS - 1)
    yi = Math.min(yi, DENSITY_BINS - 1)
    grid[xi][yi]++
    if (grid[xi][yi] > maxCount) maxCount = grid[xi][yi]
  })

  // Build heatmap data: [xBinIndex, yBinIndex, count]
  const heatData: number[][] = []
  for (let xi = 0; xi < DENSITY_BINS; xi++) {
    for (let yi = 0; yi < DENSITY_BINS; yi++) {
      heatData.push([xi, yi, grid[xi][yi]])
    }
  }

  // Bin center labels
  const f1Labels = Array.from({ length: DENSITY_BINS }, (_, i) => (f1min + (i + 0.5) * f1step).toFixed(2))
  const f2Labels = Array.from({ length: DENSITY_BINS }, (_, i) => (f2min + (i + 0.5) * f2step).toFixed(2))

  // Overlay markers (FIFO + knee)
  const markSeries: any[] = []

  if (bl) {
    let bxi = Math.floor((bl.f1 - f1min) / f1step)
    let byi = Math.floor((bl.f2 - f2min) / f2step)
    bxi = Math.max(0, Math.min(bxi, DENSITY_BINS - 1))
    byi = Math.max(0, Math.min(byi, DENSITY_BINS - 1))
    markSeries.push({
      type: 'scatter',
      name: 'FIFO baseline',
      data: [[bxi, byi]],
      symbol: 'diamond',
      symbolSize: 18,
      itemStyle: { color: CHART_COLORS.red, borderColor: '#fff', borderWidth: 2 },
      z: 10,
    })
  }
  if (knee) {
    let kxi = Math.floor((knee.f1 - f1min) / f1step)
    let kyi = Math.floor((knee.f2 - f2min) / f2step)
    kxi = Math.max(0, Math.min(kxi, DENSITY_BINS - 1))
    kyi = Math.max(0, Math.min(kyi, DENSITY_BINS - 1))
    markSeries.push({
      type: 'scatter',
      name: 'Knee point',
      data: [[kxi, kyi]],
      symbol: 'pin',
      symbolSize: 20,
      itemStyle: { color: CHART_COLORS.yellow, borderColor: '#fff', borderWidth: 2 },
      z: 10,
    })
  }

  return {
    ...baseChartOption,
    grid: { left: 70, right: 80, top: 50, bottom: 60, containLabel: false },
    title: {
      text: 'Densidad del Frente de Pareto',
      subtext: 'Concentración de soluciones en el espacio f₁ × f₂',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 'bold' },
      subtextStyle: { color: CHART_COLORS.textMuted, fontSize: 11 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      formatter: (params: any) => {
        if (params.seriesType === 'scatter') {
          return `<b>${params.seriesName}</b>`
        }
        const xi = params.data[0]
        const yi = params.data[1]
        const count = params.data[2]
        const f1lo = (f1min + xi * f1step).toFixed(3)
        const f1hi = (f1min + (xi + 1) * f1step).toFixed(3)
        const f2lo = (f2min + yi * f2step).toFixed(3)
        const f2hi = (f2min + (yi + 1) * f2step).toFixed(3)
        return `<b>${count}</b> soluciones<br/>f₁: [${f1lo}, ${f1hi})<br/>f₂: [${f2lo}, ${f2hi})`
      },
    },
    xAxis: {
      type: 'category',
      data: f1Labels,
      name: 'f₁ Carga de espera (años)',
      nameLocation: 'center',
      nameGap: 35,
      nameTextStyle: { color: CHART_COLORS.yellow, fontSize: 11, fontWeight: 'bold' },
      axisLabel: {
        color: CHART_COLORS.textMuted,
        fontSize: 9,
        interval: 3,
        rotate: 30,
      },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisTick: { show: false },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'category',
      data: f2Labels,
      name: 'f₂ Disparidad (años)',
      nameLocation: 'center',
      nameGap: 50,
      nameTextStyle: { color: CHART_COLORS.green, fontSize: 11, fontWeight: 'bold' },
      axisLabel: {
        color: CHART_COLORS.textMuted,
        fontSize: 9,
        interval: 3,
      },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisTick: { show: false },
      splitLine: { show: false },
    },
    visualMap: {
      min: 0,
      max: maxCount,
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      inRange: {
        color: [
          'rgba(0,0,0,0)',       // 0: transparent
          '#0d1b3e',             // very dark blue
          '#0e4d92',             // dark blue
          '#1a7fa0',             // teal
          '#23b5a0',             // medium teal
          '#4de89e',             // bright green
          '#c8f740',             // lime
          '#ffe600',             // bright yellow
        ],
      },
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      itemWidth: 12,
      itemHeight: 120,
    },
    series: [
      {
        type: 'heatmap',
        data: heatData,
        emphasis: {
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(0,229,160,0.5)',
          },
        },
        itemStyle: {
          borderColor: 'rgba(255,255,255,0.03)',
          borderWidth: 0.5,
          borderRadius: 2,
        },
      },
      ...markSeries,
    ],
  } as EChartsOption
})

// ── f1 vs f2 vs f3 trade-off radar for selected point ──
const tradeoffOption = computed<EChartsOption>(() => {
  if (!selectedPoint.value || !pareto.value?.points) return {}
  const pts = pareto.value.points
  const sel = selectedPoint.value
  const bl = pareto.value.baseline
  const f1min = Math.min(...pts.map(p => p.f1)), f1max = Math.max(...pts.map(p => p.f1))
  const f2min = Math.min(...pts.map(p => p.f2)), f2max = Math.max(...pts.map(p => p.f2))
  const f3min = Math.min(...pts.map(p => p.f3)), f3max = Math.max(...pts.map(p => p.f3))
  // Inverted so higher = better (closer to min)
  const norm = (v: number, min: number, max: number) => max > min ? 1 - (v - min) / (max - min) : 0.5
  const selData = [
    +(norm(sel.f1, f1min, f1max) * 100).toFixed(1),
    +(norm(sel.f2, f2min, f2max) * 100).toFixed(1),
    +(norm(sel.f3, f3min, f3max) * 100).toFixed(1),
  ]
  const series: any[] = [
    {
      name: 'Seleccionado',
      type: 'radar',
      data: [{ value: selData, name: 'Seleccionado' }],
      symbol: 'circle', symbolSize: 6,
      lineStyle: { color: CHART_COLORS.primary, width: 2 },
      areaStyle: { color: 'rgba(0,60,166,0.2)' },
      itemStyle: { color: CHART_COLORS.primary },
    },
  ]
  if (bl) {
    series.push({
      name: 'FIFO',
      type: 'radar',
      data: [{
        value: [
          +(norm(bl.f1, f1min, f1max) * 100).toFixed(1),
          +(norm(bl.f2, f2min, f2max) * 100).toFixed(1),
          +(norm(bl.f3, f3min, f3max) * 100).toFixed(1),
        ],
        name: 'FIFO',
      }],
      symbol: 'diamond', symbolSize: 6,
      lineStyle: { color: CHART_COLORS.red, width: 1.5, type: 'dashed' },
      areaStyle: { color: 'rgba(255,51,102,0.08)' },
      itemStyle: { color: CHART_COLORS.red },
    })
  }
  return {
    ...baseChartOption,
    radar: {
      indicator: [
        { name: 'f₁ espera\n(↑ = menos espera)', max: 100 },
        { name: 'f₂ equidad\n(↑ = menos brecha)', max: 100 },
        { name: 'f₃ utilización\n(↑ = menos desperdicio)', max: 100 },
      ],
      shape: 'polygon',
      radius: '65%',
      axisName: { color: CHART_COLORS.textMuted, fontSize: 10 },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.04)'] } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    legend: {
      bottom: 0, textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      data: bl ? ['Seleccionado', 'FIFO'] : ['Seleccionado'],
    },
    series,
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h1 class="section-title">Frente de Pareto Interactivo</h1>
      <div class="flex gap-2">
        <button
          v-for="p in (['f1f2', 'f1f3', 'f2f3', '3d'] as const)"
          :key="p"
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200"
          :class="projection === p
            ? 'bg-primary text-white shadow-md shadow-primary/25'
            : 'bg-dark-card text-gray-400 hover:text-white hover:bg-white/5'"
          @click="projection = p"
        >
          {{ p === 'f1f2' ? 'f₁ vs f₂' : p === 'f1f3' ? 'f₁ vs f₃' : p === 'f2f3' ? 'f₂ vs f₃' : '3D' }}
        </button>
      </div>
    </div>

    <!-- Intro explanation -->
    <div class="card bg-primary/5 border-primary/20 space-y-2">
      <p class="text-sm text-gray-300 leading-relaxed">
        Cada punto del gráfico es una <strong class="text-white">distribución distinta</strong> de las 140,000 visas.
        Ninguna solución es "la mejor" — cada una representa un compromiso diferente.
        El decisor elige según sus prioridades.
      </p>
      <div class="flex flex-wrap gap-4 text-xs">
        <span><span class="inline-block w-2 h-2 rounded-full bg-accent-yellow mr-1" />f₁ Carga de espera (años) — menor es mejor</span>
        <span><span class="inline-block w-2 h-2 rounded-full bg-accent-green mr-1" />f₂ Disparidad entre países (años) — menor es mejor</span>
        <span><span class="inline-block w-2 h-2 rounded-full bg-accent-blue mr-1" />f₃ Desperdicio de visas — menor es mejor</span>
      </div>
    </div>

    <!-- 2D scatter -->
    <ClientOnly>
      <div v-if="pareto && projection !== '3d'" class="card">
        <ParetoScatter
          :points="pareto.points"
          :baseline="pareto.baseline"
          :projection="projection"
          @select="handleSelect"
        />
      </div>
    </ClientOnly>

    <!-- 3D scatter -->
    <ClientOnly>
      <div v-if="pareto && projection === '3d'" class="card">
        <Pareto3D
          :points="pareto.points"
          :baseline="pareto.baseline"
        />
        <p class="text-center text-[10px] text-gray-600 mt-2">Arrastra para rotar · scroll para zoom · cada punto es un reparto Pareto-óptimo</p>
      </div>
    </ClientOnly>

    <!-- ===== 5 SCENARIO CARDS ===== -->
    <section v-if="scenarioCards.length" class="space-y-3">
      <h2 class="text-sm font-semibold text-gray-400 uppercase tracking-wider">5 Escenarios del Frente</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div
          v-for="sc in scenarioCards"
          :key="sc.key"
          class="bg-dark-bg1 rounded-lg p-4 border transition-all duration-200 hover:scale-[1.02] cursor-default"
          :class="sc.border"
        >
          <p class="text-xs font-bold uppercase tracking-wider mb-1" :class="sc.color">{{ sc.name }}</p>
          <p class="text-[10px] text-gray-500 mb-3">{{ sc.desc }}</p>
          <div class="space-y-1.5 font-mono text-xs">
            <div class="flex justify-between">
              <span class="text-gray-500">f₁</span>
              <span class="text-gray-300">{{ sc.point[0].toFixed(3) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">f₂</span>
              <span class="text-gray-300">{{ sc.point[1].toFixed(3) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">f₃</span>
              <span class="text-gray-300">{{ sc.point[2].toLocaleString() }}</span>
            </div>
            <div class="border-t border-dark-border pt-1.5 mt-1.5 flex justify-between">
              <span class="text-gray-500">Visas</span>
              <span class="text-white font-semibold">{{ sc.visas.toLocaleString() }}
                <span class="text-gray-500 font-normal">({{ ((sc.visas / 140000) * 100).toFixed(1) }}%)</span>
              </span>
            </div>
          </div>
          <!-- Gap vs FIFO (skip for FIFO itself) -->
          <div v-if="sc.key !== 'fifo' && scenarioCards.length === 5" class="mt-2 pt-2 border-t border-dark-border">
            <p class="text-[9px] text-gray-600 uppercase mb-1">vs FIFO</p>
            <div class="flex gap-2 text-[10px] font-mono">
              <span :class="gapClass(sc.point[0], scenarioCards[4].point[0])">
                f₁ {{ gapPct(sc.point[0], scenarioCards[4].point[0]) }}
              </span>
              <span :class="gapClass(sc.point[1], scenarioCards[4].point[1])">
                f₂ {{ gapPct(sc.point[1], scenarioCards[4].point[1]) }}
              </span>
              <span :class="gapClass(sc.point[2], scenarioCards[4].point[2])">
                f₃ {{ gapPct(sc.point[2], scenarioCards[4].point[2]) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== KPI ROW ===== -->
    <section v-if="summary" class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <KpiCard label="Soluciones Pareto" :value="summary.combined_pareto_size" />
      <KpiCard label="Mejor f₁" :value="summary.best_f1[0].toFixed(2)" unit="años espera" color="text-accent-yellow" />
      <KpiCard label="Mejor f₂" :value="summary.best_f2[1].toFixed(2)" unit="años disparidad" color="text-accent-green" />
      <KpiCard label="Mejor f₃" :value="formatNumber(Math.round(summary.best_f3[2]))" unit="visas desperdiciadas" color="text-accent-blue" />
      <KpiCard label="HV Medio" :value="formatNumber(Math.round(summary.hv_stats.mean))" :unit="'± ' + formatNumber(Math.round(summary.hv_stats.std))" />
    </section>

    <!-- ===== PARALLEL COORDINATES ===== -->
    <ClientOnly>
      <div v-if="pareto" class="card space-y-2">
        <VChart :option="parallelOption" autoresize class="w-full h-[400px]" />
        <p class="text-[10px] text-gray-500 text-center">
          Cada línea es una solución Pareto. <span class="text-orange-400">Naranja</span> = seleccionada · <span class="text-accent-red">Rojo</span> = FIFO baseline.
        </p>
      </div>
    </ClientOnly>

    <!-- ===== DENSITY HEATMAP ===== -->
    <ClientOnly>
      <div v-if="pareto" class="card space-y-2">
        <VChart :option="densityOption" autoresize class="w-full h-[400px]" />
        <p class="text-[10px] text-gray-500 text-center">
          Zonas brillantes = alta concentración de soluciones. Zonas oscuras = regiones difíciles de alcanzar.
          <span class="text-accent-red">&#9670;</span> FIFO baseline · <span class="text-accent-yellow">&#9733;</span> Knee point
        </p>
      </div>
    </ClientOnly>

    <!-- ===== SELECTED POINT DETAIL + RADAR ===== -->
    <div v-if="selectedPoint" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Metrics -->
      <div class="lg:col-span-2 card border-primary/30 space-y-4">
        <h3 class="text-sm font-semibold text-primary-300 uppercase tracking-wider">Punto Seleccionado</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p class="text-[10px] text-gray-500 uppercase">f₁ espera</p>
            <p class="font-mono text-lg font-bold text-accent-yellow">{{ selectedPoint.f1.toFixed(4) }}</p>
            <p v-if="pareto?.baseline" class="text-[10px] font-mono" :class="gapClass(selectedPoint.f1, pareto.baseline.f1)">
              {{ gapPct(selectedPoint.f1, pareto.baseline.f1) }} vs FIFO
            </p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase">f₂ disparidad</p>
            <p class="font-mono text-lg font-bold text-accent-green">{{ selectedPoint.f2.toFixed(4) }}</p>
            <p v-if="pareto?.baseline" class="text-[10px] font-mono" :class="gapClass(selectedPoint.f2, pareto.baseline.f2)">
              {{ gapPct(selectedPoint.f2, pareto.baseline.f2) }} vs FIFO
            </p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase">f₃ desperdicio</p>
            <p class="font-mono text-lg font-bold text-accent-blue">{{ formatNumber(Math.round(selectedPoint.f3)) }}</p>
            <p v-if="pareto?.baseline" class="text-[10px] font-mono" :class="gapClass(selectedPoint.f3, pareto.baseline.f3)">
              {{ gapPct(selectedPoint.f3, pareto.baseline.f3) }} vs FIFO
            </p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase">Visas asignadas</p>
            <p class="font-mono text-lg font-bold text-white">{{ formatNumber(selectedPoint.visas_used) }}</p>
            <p class="text-[10px] text-gray-500">{{ ((selectedPoint.visas_used / 140000) * 100).toFixed(1) }}% de 140,000</p>
          </div>
        </div>
        <!-- Utilization bar -->
        <div>
          <div class="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-primary to-accent-green rounded-full transition-all duration-500"
              :style="{ width: ((selectedPoint.visas_used / 140000) * 100) + '%' }"
            />
          </div>
        </div>
      </div>

      <!-- Radar -->
      <ClientOnly>
        <div class="card">
          <VChart :option="tradeoffOption" autoresize class="w-full h-[260px]" />
        </div>
      </ClientOnly>
    </div>

    <!-- ===== SELECTED POINT ALLOCATION BREAKDOWN ===== -->
    <ClientOnly>
      <div v-if="selectedPoint" class="card space-y-2">
        <div v-if="loadingAlloc" class="flex items-center justify-center h-[300px]">
          <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
          <span class="ml-3 text-sm text-gray-500">Calculando distribución...</span>
        </div>
        <VChart v-else-if="selectedAlloc" :option="selectedAllocOption" autoresize :style="{ height: Math.max(350, selectedAlloc.rows.length * 28) + 'px' }" class="w-full" />
        <p v-if="selectedAlloc" class="text-[10px] text-gray-500 text-center">
          {{ selectedAlloc.rows.length }} países · {{ formatNumber(selectedAlloc.visas_used) }} visas asignadas ({{ ((selectedAlloc.visas_used / 140000) * 100).toFixed(1) }}%)
          · f₁={{ selectedAlloc.fitness.f1.toFixed(3) }} · f₂={{ selectedAlloc.fitness.f2.toFixed(3) }} · f₃={{ formatNumber(Math.round(selectedAlloc.fitness.f3)) }}
        </p>
      </div>
    </ClientOnly>

    <!-- ===== VISA DISTRIBUTION CHART ===== -->
    <ClientOnly>
      <div v-if="pareto" class="card">
        <VChart :option="visaDistOption" autoresize class="w-full h-[320px]" />
        <p class="text-[10px] text-gray-600 text-center mt-1">
          Cada barra = una solución Pareto-óptima · Línea amarilla = total disponible · Línea roja = FIFO actual
        </p>
      </div>
    </ClientOnly>

    <!-- ===== SORTABLE SOLUTIONS TABLE ===== -->
    <section v-if="pareto" class="card space-y-3">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-sm font-bold text-white">{{ pareto.count }} Soluciones Pareto-Óptimas</h2>
          <p class="text-[10px] text-gray-500 mt-0.5">
            Cada fila es un reparto que ningún otro puede superar en los tres objetivos a la vez.
            Haz clic en las columnas para ordenar.
          </p>
        </div>
        <button
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
          :class="showTable ? 'bg-primary text-white' : 'bg-dark-bg2 text-gray-400 hover:text-white'"
          @click="showTable = !showTable"
        >
          {{ showTable ? 'Ocultar tabla' : 'Ver tabla completa' }}
        </button>
      </div>

      <div v-if="showTable" class="max-h-[420px] overflow-y-auto rounded-lg border border-dark-border">
        <table class="w-full text-xs">
          <thead class="sticky top-0 z-10 bg-dark-bg2">
            <tr class="border-b border-dark-border">
              <th class="px-3 py-2 text-left text-[10px] text-gray-500 uppercase font-semibold w-12">#</th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f1' ? 'text-accent-yellow' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f1')"
              >
                f₁ espera{{ sortArrow('f1') }}
              </th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f2' ? 'text-accent-green' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f2')"
              >
                f₂ brecha{{ sortArrow('f2') }}
              </th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f3' ? 'text-accent-blue' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f3')"
              >
                f₃ desperdicio{{ sortArrow('f3') }}
              </th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'visas_used' ? 'text-primary-300' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('visas_used')"
              >
                Visas{{ sortArrow('visas_used') }}
              </th>
              <th class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">%</th>
              <th v-if="pareto.baseline" class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Δf₁</th>
              <th v-if="pareto.baseline" class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Δf₂</th>
              <th v-if="pareto.baseline" class="px-3 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Δf₃</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="pt in sortedPoints"
              :key="pt._idx"
              class="border-b border-dark-border/20 cursor-pointer transition-colors"
              :class="selectedPoint && selectedPoint.f1 === pt.f1 && selectedPoint.f2 === pt.f2
                ? 'bg-primary/15 text-white'
                : 'hover:bg-white/[0.03] text-gray-400'"
              @click="handleSelect(pt)"
            >
              <td class="px-3 py-1.5 font-mono text-gray-600">{{ pt._idx + 1 }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ pt.f1.toFixed(3) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ pt.f2.toFixed(3) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ pt.f3.toLocaleString() }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ pt.visas_used.toLocaleString() }}</td>
              <td class="px-3 py-1.5 text-right font-mono text-gray-500">{{ ((pt.visas_used / 140000) * 100).toFixed(1) }}</td>
              <td v-if="pareto.baseline" class="px-3 py-1.5 text-right font-mono text-[10px]" :class="gapClass(pt.f1, pareto.baseline.f1)">
                {{ gapPct(pt.f1, pareto.baseline.f1) }}
              </td>
              <td v-if="pareto.baseline" class="px-3 py-1.5 text-right font-mono text-[10px]" :class="gapClass(pt.f2, pareto.baseline.f2)">
                {{ gapPct(pt.f2, pareto.baseline.f2) }}
              </td>
              <td v-if="pareto.baseline" class="px-3 py-1.5 text-right font-mono text-[10px]" :class="gapClass(pt.f3, pareto.baseline.f3)">
                {{ gapPct(pt.f3, pareto.baseline.f3) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Baseline reference -->
      <p v-if="pareto.baseline" class="text-[10px] text-gray-600">
        Baseline FIFO: f₁={{ pareto.baseline.f1.toFixed(3) }}, f₂={{ pareto.baseline.f2.toFixed(3) }}, f₃={{ pareto.baseline.f3.toLocaleString() }}
        · Δ columns show % change vs FIFO (green = better)
      </p>
    </section>
  </div>
</template>
