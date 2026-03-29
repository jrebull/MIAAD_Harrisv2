<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'
import type { ParetoData, ParetoPoint, SummaryData, ImpactData, ImpactRow, AllocationData, GroupsData, GroupInfo } from '~/composables/useOptimizer'
import { formatNumber, formatDelta } from '~/utils/formatters'

const { fetchPareto, fetchSummary, fetchImpact, fetchCustomAllocation, fetchGroups } = useOptimizer()

// ── State ──
const pareto = ref<ParetoData | null>(null)
const summary = ref<SummaryData | null>(null)
const groupsData = ref<GroupsData | null>(null)
const impactRows = ref<ImpactRow[]>([])
const fifoMap = ref<Map<string, { fifo_visas: number; max_wait: number }>>(new Map())
const selectedPoint = ref<ParetoPoint | null>(null)
const activeScenario = ref<string | null>('equilibrio')
const loading = ref(true)
const initialLoading = ref(true)
const countryFilter = ref<'all' | 'winners' | 'losers'>('all')
const sortBy = ref<'delta' | 'country' | 'visas'>('delta')
const highlightCountry = ref<string | null>(null)

// ── Quick scenarios ──
const quickScenarios = [
  { id: 'humanitario', name: 'Humanitario', short: 'Min f₁', color: 'text-accent-yellow', bg: 'bg-accent-yellow/15', border: 'border-accent-yellow/30' },
  { id: 'equilibrio', name: 'Equilibrio', short: 'Knee', color: 'text-primary-300', bg: 'bg-primary/15', border: 'border-primary/30' },
  { id: 'equidad', name: 'Equidad', short: 'Min f₂', color: 'text-accent-green', bg: 'bg-accent-green/15', border: 'border-accent-green/30' },
  { id: 'max_utilizacion', name: 'Máx. Uso', short: 'Min f₃', color: 'text-accent-blue', bg: 'bg-accent-blue/15', border: 'border-accent-blue/30' },
]

// ── Init ──
onMounted(async () => {
  const [p, s, impact, gd] = await Promise.all([fetchPareto(), fetchSummary(), fetchImpact('equilibrio'), fetchGroups()])
  pareto.value = p
  summary.value = s
  groupsData.value = gd
  impactRows.value = impact.rows
  // Store FIFO baseline per country
  impact.rows.forEach(r => fifoMap.value.set(r.country, { fifo_visas: r.fifo_visas, max_wait: r.max_wait }))
  // Set equilibrio as initial selection
  if (p.points.length) {
    const knee = computeKnee(p.points)
    selectedPoint.value = knee
  }
  initialLoading.value = false
  loading.value = false
})

// ── Knee point ──
function computeKnee(pts: ParetoPoint[]): ParetoPoint {
  const sorted = [...pts].sort((a, b) => a.f1 - b.f1)
  if (sorted.length < 3) return sorted[0]
  const f1min = sorted[0].f1, f1max = sorted[sorted.length - 1].f1
  const f2min = Math.min(...sorted.map(p => p.f2)), f2max = Math.max(...sorted.map(p => p.f2))
  const f1r = f1max - f1min || 1, f2r = f2max - f2min || 1
  const p1y = (sorted[0].f2 - f2min) / f2r
  const pny = (sorted[sorted.length - 1].f2 - f2min) / f2r
  const dx = 1, dy = pny - p1y, len = Math.sqrt(dx * dx + dy * dy) || 1
  const ux = dx / len, uy = dy / len
  let maxD = -1, best = sorted[0]
  sorted.forEach(p => {
    const px = (p.f1 - f1min) / f1r, py = (p.f2 - f2min) / f2r - p1y
    const proj = px * ux + py * uy
    const d = Math.sqrt((px - proj * ux) ** 2 + (py - proj * uy) ** 2)
    if (d > maxD) { maxD = d; best = p }
  })
  return best
}

// ── Select named scenario (fast endpoint) ──
async function selectScenario(sc: string) {
  activeScenario.value = sc
  loading.value = true
  const impact = await fetchImpact(sc)
  impactRows.value = impact.rows
  // Find closest Pareto point to this scenario
  if (pareto.value && summary.value) {
    const s = summary.value
    let target: number[]
    if (sc === 'humanitario') target = s.best_f1
    else if (sc === 'equidad') target = s.best_f2
    else if (sc === 'max_utilizacion') target = s.best_f3
    else { selectedPoint.value = computeKnee(pareto.value.points); loading.value = false; return }
    let best = pareto.value.points[0], bestDist = Infinity
    pareto.value.points.forEach(p => {
      const d = Math.abs(p.f1 - target[0]) + Math.abs(p.f2 - target[1]) + Math.abs(p.f3 - target[2])
      if (d < bestDist) { bestDist = d; best = p }
    })
    selectedPoint.value = best
  }
  loading.value = false
}

// ── Select any Pareto point (custom endpoint) ──
async function selectParetoPoint(point: ParetoPoint) {
  selectedPoint.value = point
  activeScenario.value = null
  loading.value = true
  try {
    const alloc = await fetchCustomAllocation(point.f1, point.f2, point.f3)
    impactRows.value = alloc.rows.map(r => {
      const bl = fifoMap.value.get(r.country)
      return {
        country: r.country,
        flag: r.flag,
        fifo_visas: bl?.fifo_visas ?? 0,
        scenario_visas: r.total,
        delta: r.total - (bl?.fifo_visas ?? 0),
        max_wait: bl?.max_wait ?? 0,
      }
    }).sort((a, b) => b.delta - a.delta)
  } catch {
    // Fallback — just keep existing data
  }
  loading.value = false
}

// ── Filtered & sorted rows ──
const filteredRows = computed(() => {
  let rows = [...impactRows.value]
  if (countryFilter.value === 'winners') rows = rows.filter(r => r.delta > 0)
  else if (countryFilter.value === 'losers') rows = rows.filter(r => r.delta < 0)
  if (sortBy.value === 'country') rows.sort((a, b) => a.country.localeCompare(b.country))
  else if (sortBy.value === 'visas') rows.sort((a, b) => b.scenario_visas - a.scenario_visas)
  else rows.sort((a, b) => b.delta - a.delta)
  return rows
})

// ── Stats ──
const stats = computed(() => {
  if (!impactRows.value.length) return null
  const rows = impactRows.value
  const winners = rows.filter(r => r.delta > 0)
  const losers = rows.filter(r => r.delta < 0)
  const totalGain = winners.reduce((s, r) => s + r.delta, 0)
  const totalLoss = losers.reduce((s, r) => s + Math.abs(r.delta), 0)
  const maxGainer = rows.reduce((best, r) => r.delta > best.delta ? r : best, rows[0])
  const maxLoser = rows.reduce((worst, r) => r.delta < worst.delta ? r : worst, rows[0])
  return { winners: winners.length, losers: losers.length, totalGain, totalLoss, maxGainer, maxLoser }
})

// ── Highlight shortcuts ──
function highlightTopWinner() {
  if (!stats.value) return
  highlightCountry.value = stats.value.maxGainer.country
  countryFilter.value = 'all'
  sortBy.value = 'delta'
}
function highlightTopLoser() {
  if (!stats.value) return
  highlightCountry.value = stats.value.maxLoser.country
  countryFilter.value = 'all'
  sortBy.value = 'delta'
}

// ── Label for current selection ──
const selectionLabel = computed(() => {
  if (activeScenario.value) {
    const sc = quickScenarios.find(s => s.id === activeScenario.value)
    return sc?.name ?? activeScenario.value
  }
  return 'Punto personalizado'
})

// ── Mini Pareto scatter ──
const miniParetoOption = computed<EChartsOption>(() => {
  if (!pareto.value?.points) return {}
  const pts = pareto.value.points
  const bl = pareto.value.baseline
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2)
  const f1min = Math.min(...f1s), f1max = Math.max(...f1s)
  const f2min = Math.min(...f2s), f2max = Math.max(...f2s)
  const f1pad = (f1max - f1min) * 0.08, f2pad = (f2max - f2min) * 0.08

  const series: any[] = [
    {
      name: 'Pareto',
      type: 'scatter',
      data: pts.map(p => [p.f1, p.f2, p.f3, p.visas_used]),
      symbolSize: 7,
      itemStyle: { color: 'rgba(96,165,250,0.5)', borderColor: 'rgba(255,255,255,0.15)', borderWidth: 0.5 },
      emphasis: { itemStyle: { color: CHART_COLORS.blue, borderColor: '#fff', borderWidth: 2, shadowBlur: 12, shadowColor: 'rgba(96,165,250,0.6)' }, scale: 2 },
      zlevel: 0,
    },
  ]
  // Selected point marker
  if (selectedPoint.value) {
    series.push({
      name: 'Seleccionado',
      type: 'effectScatter',
      data: [[selectedPoint.value.f1, selectedPoint.value.f2]],
      symbolSize: 16,
      itemStyle: { color: CHART_COLORS.yellow, shadowBlur: 10, shadowColor: CHART_COLORS.yellow },
      rippleEffect: { brushType: 'stroke', scale: 3, period: 3 },
      zlevel: 2,
    })
  }
  // FIFO baseline
  if (bl) {
    series.push({
      name: 'FIFO',
      type: 'scatter',
      data: [[bl.f1, bl.f2]],
      symbolSize: 14, symbol: 'diamond',
      itemStyle: { color: CHART_COLORS.red, borderColor: '#fff', borderWidth: 1.5 },
      zlevel: 1,
    })
  }

  return {
    ...baseChartOption,
    grid: { left: 55, right: 20, top: 30, bottom: 50 },
    tooltip: {
      ...baseTooltip, trigger: 'item', confine: true,
      formatter: (p: any) => {
        if (p.seriesName === 'FIFO') return '<span style="color:#FF3366;font-weight:700">FIFO Baseline</span>'
        if (p.seriesName === 'Seleccionado') return '<span style="color:#FFD600;font-weight:700">Punto actual</span>'
        const d = p.data
        return `f₁: <b>${d[0].toFixed(3)}</b> · f₂: <b>${d[1].toFixed(3)}</b> · f₃: <b>${Math.round(d[2]).toLocaleString()}</b><br>Visas: ${d[3].toLocaleString()}<br><span style="opacity:0.5">Click para seleccionar</span>`
      },
    },
    xAxis: {
      type: 'value', name: 'f₁ espera', nameLocation: 'center', nameGap: 30,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      min: f1min - f1pad, max: f1max + f1pad,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9, formatter: (v: number) => v.toFixed(2) },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'value', name: 'f₂ disparidad', nameLocation: 'center', nameGap: 42,
      nameTextStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      min: f2min - f2pad, max: f2max + f2pad,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 9, formatter: (v: number) => v.toFixed(1) },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    legend: { show: false },
    series,
  }
})

function handleMiniParetoClick(params: any) {
  if (params.seriesName === 'Pareto' && params.data) {
    const [f1, f2, f3, visas_used] = params.data
    selectParetoPoint({ f1, f2, f3, visas_used })
  }
}

// ── Delta bar chart ──
const deltaOption = computed<EChartsOption>(() => {
  if (!filteredRows.value.length) return {}
  const rows = filteredRows.value
  return {
    ...baseChartOption,
    grid: { left: 120, right: 60, top: 16, bottom: 16 },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const r = rows[p.dataIndex]
        const arrow = r.delta >= 0 ? '▲' : '▼'
        const color = r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red
        return `<b>${r.flag} ${r.country}</b><br><span style="opacity:0.5">FIFO:</span> ${formatNumber(r.fifo_visas)}<br><span style="opacity:0.5">Selección:</span> ${formatNumber(r.scenario_visas)}<br><span style="color:${color};font-weight:700">${arrow} ${formatDelta(r.delta)} visas</span>`
      },
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map(r => r.flag + ' ' + r.country),
      axisLabel: {
        color: (value: string) => {
          if (!highlightCountry.value) return CHART_COLORS.textMuted
          return value.includes(highlightCountry.value) ? '#FFD600' : CHART_COLORS.textMuted
        },
        fontSize: 10,
        fontWeight: (value: string) => highlightCountry.value && value.includes(highlightCountry.value) ? 'bold' as any : 'normal' as any,
      },
      inverse: true,
    },
    series: [{
      type: 'bar',
      data: rows.map(r => ({
        value: r.delta,
        itemStyle: {
          color: {
            type: 'linear',
            x: r.delta >= 0 ? 0 : 1, y: 0, x2: r.delta >= 0 ? 1 : 0, y2: 0,
            colorStops: [
              { offset: 0, color: r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red },
              { offset: 1, color: r.delta >= 0 ? 'rgba(0,229,160,0.3)' : 'rgba(255,51,102,0.3)' },
            ],
          },
          borderRadius: r.delta >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
          opacity: highlightCountry.value ? (rows[rows.indexOf(rows.find(row => row.country === highlightCountry.value)!)]?.country === r.country ? 1 : 0.3) : 1,
        },
      })),
      label: {
        show: true, position: 'right', color: CHART_COLORS.textMuted, fontSize: 9,
        formatter: (p: any) => formatDelta(p.value),
      },
      animationDuration: 600,
      animationDelay: (idx: number) => idx * 30,
    }],
  }
})

// ── Comparison chart ──
const comparisonOption = computed<EChartsOption>(() => {
  if (!filteredRows.value.length) return {}
  const rows = filteredRows.value
  return {
    ...baseChartOption,
    grid: { left: 120, right: 16, top: 40, bottom: 16 },
    tooltip: {
      ...baseTooltip, trigger: 'axis', confine: true,
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.04)' } },
    },
    legend: { top: 8, right: 16, textStyle: { color: CHART_COLORS.textMuted }, itemStyle: { borderWidth: 0 } },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map(r => r.flag + ' ' + r.country),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    series: [
      {
        name: 'FIFO',
        type: 'bar',
        data: rows.map(r => r.fifo_visas),
        itemStyle: { color: CHART_COLORS.red, opacity: 0.45, borderRadius: [0, 2, 2, 0] },
      },
      {
        name: selectionLabel.value,
        type: 'bar',
        data: rows.map(r => r.scenario_visas),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: CHART_COLORS.primary }, { offset: 1, color: CHART_COLORS.primaryLight }] },
          borderRadius: [0, 2, 2, 0],
        },
      },
    ],
  }
})

// ── Wait time by country data ──
interface CountryWait {
  country: string
  flag: string
  waits: Record<string, number>       // category -> wait years
  applicants: Record<string, number>  // category -> applicants waiting
  maxWait: number
  totalApplicants: number
}

const EB_CATEGORIES = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

const EB_COLORS = {
  'EB-1': { solid: '#60a5fa', start: '#60a5fa', end: '#3b82f6' },     // blue
  'EB-2': { solid: '#a78bfa', start: '#a78bfa', end: '#7c3aed' },     // purple
  'EB-3': { solid: '#FF3366', start: '#FF3366', end: '#cc1a4a' },     // red/pink
  'EB-4': { solid: '#FFD600', start: '#FFD600', end: '#d4a800' },     // yellow
  'EB-5': { solid: '#00E5A0', start: '#00E5A0', end: '#00b37d' },     // green
} as Record<string, { solid: string; start: string; end: string }>

const waitTimeData = computed<CountryWait[]>(() => {
  if (!groupsData.value) return []
  const gd = groupsData.value
  const countryMap = new Map<string, CountryWait>()

  for (const g of gd.groups) {
    if (!countryMap.has(g.country)) {
      countryMap.set(g.country, {
        country: g.country,
        flag: gd.flags[g.country] || '',
        waits: {},
        applicants: {},
        maxWait: 0,
        totalApplicants: 0,
      })
    }
    const entry = countryMap.get(g.country)!
    entry.waits[g.category] = g.w
    entry.applicants[g.category] = g.n
    if (g.w > entry.maxWait) entry.maxWait = g.w
    entry.totalApplicants += g.n
  }

  const all = Array.from(countryMap.values())
  // Countries with any wait > 0, sorted by maxWait descending
  const withWait = all.filter(c => c.maxWait > 0).sort((a, b) => b.maxWait - a.maxWait)
  // Group zero-wait countries
  const zeroCount = all.filter(c => c.maxWait === 0).length
  if (zeroCount > 0) {
    const zeroApplicants = all.filter(c => c.maxWait === 0).reduce((sum, c) => sum + c.totalApplicants, 0)
    withWait.push({
      country: `Otros (${zeroCount} países, 0 años)`,
      flag: '',
      waits: {},
      applicants: {},
      maxWait: 0,
      totalApplicants: zeroApplicants,
    })
  }
  return withWait
})

// Dramatic highlight stats
const dramaticStats = computed(() => {
  if (!groupsData.value) return []
  const gd = groupsData.value
  const highlights: { label: string; wait: number; applicants: number; color: string }[] = []

  for (const g of gd.groups) {
    if (g.country === 'India' && g.category === 'EB-3') {
      highlights.push({ label: 'India EB-3', wait: g.w, applicants: g.n, color: '#FF3366' })
    }
    if (g.country === 'China' && g.category === 'EB-5') {
      highlights.push({ label: 'China EB-5', wait: g.w, applicants: g.n, color: '#00E5A0' })
    }
    if (g.country === 'India' && g.category === 'EB-2') {
      highlights.push({ label: 'India EB-2', wait: g.w, applicants: g.n, color: '#a78bfa' })
    }
  }
  return highlights.sort((a, b) => b.wait - a.wait)
})

const waitTimeOption = computed<EChartsOption>(() => {
  const data = waitTimeData.value
  if (!data.length) return {}

  const countries = data.map(c => c.flag ? `${c.flag} ${c.country}` : c.country)
  const maxVal = Math.max(...data.map(c => c.maxWait), 1)
  // Compute average wait across all countries with wait > 0
  const countriesWithWait = data.filter(c => c.maxWait > 0)
  const avgWait = countriesWithWait.length
    ? countriesWithWait.reduce((s, c) => s + c.maxWait, 0) / countriesWithWait.length
    : 0

  const series: any[] = EB_CATEGORIES.map((cat) => {
    const colors = EB_COLORS[cat] ?? { solid: '#888', start: '#888', end: '#666' }
    return {
      name: cat,
      type: 'bar',
      stack: 'wait',
      itemStyle: {
        color: colors.solid,
      },
      data: data.map(c => ({
        value: c.waits[cat] || 0,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: colors.start },
              { offset: 1, color: colors.end + 'cc' },
            ],
          },
          borderRadius: 0,
          shadowBlur: c.waits[cat] && c.waits[cat] >= 10 ? 8 : 0,
          shadowColor: c.waits[cat] && c.waits[cat] >= 10 ? colors.solid + '80' : 'transparent',
        },
      })),
      emphasis: {
        itemStyle: {
          color: colors.solid,
          shadowBlur: 20,
          shadowColor: colors.solid + 'aa',
          borderColor: '#fff',
          borderWidth: 1,
        },
      },
      barMaxWidth: 28,
      animationDuration: 1200,
      animationDelay: (idx: number) => idx * 60,
    }
  })

  return {
    backgroundColor: 'transparent',
    textStyle: { color: CHART_COLORS.text, fontFamily: 'Inter, sans-serif' },
    title: {
      text: 'Años de Espera por País y Categoría',
      subtext: 'Cada barra representa años de vida esperando una visa',
      left: 'center',
      top: 8,
      textStyle: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        fontFamily: 'Inter, sans-serif',
        textShadowColor: 'rgba(255,51,102,0.3)',
        textShadowBlur: 8,
      },
      subtextStyle: {
        color: 'rgba(255,255,255,0.45)',
        fontSize: 12,
        fontFamily: 'Inter, sans-serif',
        fontStyle: 'italic',
      },
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      confine: true,
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(255,51,102,0.06)' } },
      formatter: (params: any) => {
        if (!Array.isArray(params) || !params.length) return ''
        const idx = params[0].dataIndex
        const entry = data[idx]
        if (!entry) return ''
        let html = `<div style="font-weight:700;font-size:14px;margin-bottom:6px">${entry.flag} ${entry.country}</div>`
        let totalWait = 0
        for (const cat of EB_CATEGORIES) {
          const w = entry.waits[cat] || 0
          const n = entry.applicants[cat] || 0
          if (w > 0 || n > 0) {
            const color = (EB_COLORS[cat] ?? { solid: '#888' }).solid
            const barWidth = Math.round((w / maxVal) * 80)
            html += `<div style="display:flex;align-items:center;gap:6px;margin:3px 0">`
            html += `<span style="color:${color};font-weight:600;width:36px">${cat}</span>`
            html += `<div style="width:${barWidth}px;height:6px;background:${color};border-radius:3px;opacity:0.7"></div>`
            html += `<span style="font-weight:700;color:#fff">${w} años</span>`
            if (n > 0) html += `<span style="opacity:0.4;font-size:11px"> · ${n.toLocaleString()} personas</span>`
            html += `</div>`
            totalWait += w
          }
        }
        html += `<div style="border-top:1px solid rgba(255,255,255,0.1);margin-top:6px;padding-top:6px;font-size:11px;opacity:0.5">`
        html += `Total solicitantes: ${entry.totalApplicants.toLocaleString()}`
        html += `</div>`
        return html
      },
    },
    legend: {
      top: 58,
      left: 'center',
      data: EB_CATEGORIES,
      textStyle: { color: 'rgba(255,255,255,0.7)', fontSize: 11 },
      itemStyle: { borderWidth: 0 },
      itemWidth: 14,
      itemHeight: 10,
      itemGap: 18,
    },
    grid: { left: 140, right: 40, top: 100, bottom: 20, containLabel: false },
    xAxis: {
      type: 'value',
      name: 'Años de espera',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: 'rgba(255,255,255,0.4)', fontSize: 11 },
      max: Math.ceil(maxVal * 1.15),
      axisLabel: {
        color: 'rgba(255,255,255,0.5)',
        fontSize: 11,
        formatter: (v: number) => v + ' años',
      },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)', type: 'dashed' } },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'category',
      data: countries,
      inverse: true,
      axisLabel: {
        color: (value: string) => {
          if (value.includes('India')) return '#FF3366'
          if (value.includes('China')) return '#FFD600'
          if (value.includes('Otros')) return 'rgba(255,255,255,0.3)'
          return 'rgba(255,255,255,0.65)'
        },
        fontSize: 12,
        fontWeight: (value: string) => {
          if (value.includes('India') || value.includes('China')) return 'bold' as any
          return 'normal' as any
        },
      },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
    },
    series: [
      ...series,
      // Invisible helper for avg markLine (excluded from legend via legendHoverLink)
      {
        name: 'Promedio',
        type: 'bar',
        stack: 'wait',
        data: data.map(() => 0),
        silent: true,
        itemStyle: { color: 'transparent' },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: 'rgba(255,214,0,0.6)', type: 'dashed', width: 1.5 },
          label: {
            formatter: `Prom. {c} años`,
            color: 'rgba(255,214,0,0.8)',
            fontSize: 11,
            fontWeight: 'bold' as any,
            position: 'insideEndTop',
          },
          data: [{ xAxis: Math.round(avgWait * 10) / 10, name: 'Promedio' }],
        },
      },
    ],
    animationDuration: 1200,
    animationEasing: 'cubicOut',
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Impacto por País</h1>

    <div v-if="initialLoading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else>
      <!-- ===== PARETO POINT SELECTOR ===== -->
      <section class="card space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 class="text-sm font-bold text-white">Selecciona una solución del frente</h2>
            <p class="text-[10px] text-gray-500 mt-0.5">
              Haz clic en cualquier punto para ver su impacto por país · {{ pareto?.count || 0 }} soluciones disponibles
            </p>
          </div>
          <!-- Quick scenario buttons -->
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] text-gray-600 mr-1">Atajos:</span>
            <button
              v-for="sc in quickScenarios"
              :key="sc.id"
              class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all duration-200 border"
              :class="activeScenario === sc.id
                ? `${sc.bg} ${sc.color} ${sc.border}`
                : 'bg-dark-bg2 text-gray-500 border-transparent hover:text-white'"
              @click="selectScenario(sc.id)"
            >
              {{ sc.short }}
            </button>
          </div>
        </div>

        <!-- Mini Pareto scatter -->
        <ClientOnly>
          <VChart
            v-if="pareto"
            :option="miniParetoOption"
            autoresize
            class="w-full h-[280px]"
            @click="handleMiniParetoClick"
          />
        </ClientOnly>

        <!-- Current selection strip -->
        <div v-if="selectedPoint" class="flex flex-wrap items-center gap-4 pt-2 border-t border-dark-border">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-accent-yellow animate-pulse" />
            <span class="text-xs text-gray-400">
              <strong class="text-white">{{ selectionLabel }}</strong>
            </span>
          </div>
          <div class="flex gap-3 text-xs font-mono">
            <span class="text-accent-yellow">f₁ {{ selectedPoint.f1.toFixed(3) }}</span>
            <span class="text-accent-green">f₂ {{ selectedPoint.f2.toFixed(3) }}</span>
            <span class="text-accent-blue">f₃ {{ Math.round(selectedPoint.f3).toLocaleString() }}</span>
            <span class="text-white">{{ selectedPoint.visas_used.toLocaleString() }} visas</span>
          </div>
          <div v-if="loading" class="ml-auto">
            <div class="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full" />
          </div>
        </div>
      </section>

      <!-- ===== WAIT TIME BY COUNTRY — HUMAN COST ===== -->
      <section v-if="waitTimeData.length" class="space-y-5">
        <!-- Section intro -->
        <div class="text-center space-y-1">
          <h2 class="text-lg font-bold text-white tracking-tight">El Costo Humano de la Espera</h2>
          <p class="text-xs text-gray-500 max-w-xl mx-auto">Tiempo de espera real por país y categoría EB bajo el sistema FIFO actual. India EB-3 enfrenta más de una década de espera.</p>
        </div>

        <!-- Chart -->
        <div class="card relative overflow-hidden" style="border-color: rgba(255,51,102,0.2);">
          <!-- Subtle background glow for drama -->
          <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-red-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
          <div class="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-purple-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

          <ClientOnly>
            <VChart
              :option="waitTimeOption"
              autoresize
              class="w-full relative z-10"
              :style="{ height: Math.max(420, waitTimeData.length * 44 + 120) + 'px' }"
            />
          </ClientOnly>
        </div>

        <!-- Dramatic statistics cards -->
        <div v-if="dramaticStats.length" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="stat in dramaticStats"
            :key="stat.label"
            class="card relative overflow-hidden group transition-all duration-300 hover:scale-[1.02]"
            :style="{
              borderColor: stat.color + '30',
              background: `linear-gradient(135deg, ${stat.color}08, transparent 60%)`,
            }"
          >
            <!-- Glow accent -->
            <div
              class="absolute top-0 left-0 w-1 h-full rounded-r transition-all duration-300 group-hover:w-1.5"
              :style="{ background: `linear-gradient(to bottom, ${stat.color}, ${stat.color}40)` }"
            />

            <div class="pl-4">
              <p class="text-xs uppercase tracking-widest mb-2" :style="{ color: stat.color + '99' }">
                {{ stat.label }}
              </p>
              <div class="flex items-baseline gap-2">
                <span
                  class="text-4xl font-black tabular-nums tracking-tight"
                  :style="{ color: stat.color }"
                >
                  {{ stat.wait }}
                </span>
                <span class="text-lg text-gray-500 font-medium">años de espera</span>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <div class="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-1000"
                    :style="{
                      width: Math.min(100, (stat.wait / 13) * 100) + '%',
                      background: `linear-gradient(to right, ${stat.color}60, ${stat.color})`,
                    }"
                  />
                </div>
                <span class="text-xs text-gray-600 whitespace-nowrap">
                  {{ stat.applicants.toLocaleString() }} personas afectadas
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== FILTER BAR ===== -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Country filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-[10px] text-gray-600">Filtro:</span>
          <button
            v-for="f in ([
              { id: 'all', label: 'Todos (21)' },
              { id: 'winners', label: 'Ganadores' },
              { id: 'losers', label: 'Perdedores' },
            ] as const)"
            :key="f.id"
            class="px-2.5 py-1 rounded text-[10px] font-medium transition-colors"
            :class="countryFilter === f.id
              ? 'bg-primary/20 text-primary-300'
              : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="countryFilter = f.id; highlightCountry = null"
          >
            {{ f.label }}
          </button>
        </div>

        <!-- Sort -->
        <div class="flex items-center gap-1.5">
          <span class="text-[10px] text-gray-600">Ordenar:</span>
          <button
            v-for="s in ([
              { id: 'delta', label: 'Por cambio' },
              { id: 'visas', label: 'Por visas' },
              { id: 'country', label: 'Alfabético' },
            ] as const)"
            :key="s.id"
            class="px-2.5 py-1 rounded text-[10px] font-medium transition-colors"
            :class="sortBy === s.id
              ? 'bg-white/10 text-white'
              : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="sortBy = s.id"
          >
            {{ s.label }}
          </button>
        </div>

        <!-- Highlight shortcuts -->
        <div class="flex items-center gap-1.5 ml-auto">
          <button
            class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all"
            :class="highlightCountry === stats?.maxGainer?.country
              ? 'bg-accent-green/20 text-accent-green ring-1 ring-accent-green/40'
              : 'bg-dark-bg2 text-gray-500 hover:text-accent-green'"
            @click="highlightTopWinner()"
          >
            Mayor ganador
          </button>
          <button
            class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all"
            :class="highlightCountry === stats?.maxLoser?.country
              ? 'bg-accent-red/20 text-accent-red ring-1 ring-accent-red/40'
              : 'bg-dark-bg2 text-gray-500 hover:text-accent-red'"
            @click="highlightTopLoser()"
          >
            Mayor perdedor
          </button>
          <button
            v-if="highlightCountry"
            class="px-2 py-1 rounded text-[10px] text-gray-500 hover:text-white bg-dark-bg2"
            @click="highlightCountry = null"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- ===== IMPACT KPIs ===== -->
      <section v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Países beneficiados" :value="stats.winners" unit="de 21" color="text-accent-green" />
        <KpiCard label="Países afectados" :value="stats.losers" unit="de 21" color="text-accent-red" />
        <KpiCard label="Visas redistribuidas" :value="'+' + formatNumber(stats.totalGain)" color="text-accent-green" />
        <KpiCard label="Visas recortadas" :value="'-' + formatNumber(stats.totalLoss)" color="text-accent-red" />
      </section>

      <!-- ===== HIGHLIGHTED COUNTRY CARD ===== -->
      <div v-if="highlightCountry && stats" class="card border-accent-yellow/30 bg-accent-yellow/5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-500 uppercase tracking-wider">País destacado</p>
            <p class="text-lg font-bold text-white mt-1">
              {{ impactRows.find(r => r.country === highlightCountry)?.flag }}
              {{ highlightCountry }}
            </p>
          </div>
          <div class="flex gap-6 text-right">
            <div>
              <p class="text-[10px] text-gray-500 uppercase">FIFO</p>
              <p class="font-mono text-sm text-gray-400">{{ formatNumber(impactRows.find(r => r.country === highlightCountry)?.fifo_visas ?? 0) }}</p>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase">Selección</p>
              <p class="font-mono text-sm text-white">{{ formatNumber(impactRows.find(r => r.country === highlightCountry)?.scenario_visas ?? 0) }}</p>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase">Cambio</p>
              <p class="font-mono text-sm font-bold"
                :class="(impactRows.find(r => r.country === highlightCountry)?.delta ?? 0) >= 0 ? 'text-accent-green' : 'text-accent-red'"
              >
                {{ formatDelta(impactRows.find(r => r.country === highlightCountry)?.delta ?? 0) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== WINNERS / LOSERS CARDS ===== -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card border-accent-green/20">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 rounded-full bg-accent-green" />
            <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider">Top 5 beneficiados</h3>
          </div>
          <div class="space-y-2">
            <div
              v-for="(r, i) in impactRows.filter(r => r.delta > 0).slice(0, 5)"
              :key="r.country"
              class="flex justify-between items-center text-sm cursor-pointer rounded px-2 py-1 -mx-2 transition-colors"
              :class="highlightCountry === r.country ? 'bg-accent-green/10' : 'hover:bg-white/[0.03]'"
              @click="highlightCountry = highlightCountry === r.country ? null : r.country"
            >
              <span class="text-gray-400">
                <span class="text-gray-600 font-mono text-xs mr-2">{{ i + 1 }}</span>
                {{ r.flag }} {{ r.country }}
              </span>
              <div class="flex items-center gap-3">
                <span class="font-mono text-accent-green font-semibold">{{ formatDelta(r.delta) }}</span>
                <div class="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div class="h-full bg-accent-green/60 rounded-full" :style="{ width: Math.min(100, (r.delta / (stats?.maxGainer?.delta || 1)) * 100) + '%' }" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="card border-accent-red/20">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 rounded-full bg-accent-red" />
            <h3 class="text-sm font-semibold text-accent-red uppercase tracking-wider">Top 5 afectados</h3>
          </div>
          <div class="space-y-2">
            <div
              v-for="(r, i) in [...impactRows].filter(r => r.delta < 0).sort((a, b) => a.delta - b.delta).slice(0, 5)"
              :key="r.country"
              class="flex justify-between items-center text-sm cursor-pointer rounded px-2 py-1 -mx-2 transition-colors"
              :class="highlightCountry === r.country ? 'bg-accent-red/10' : 'hover:bg-white/[0.03]'"
              @click="highlightCountry = highlightCountry === r.country ? null : r.country"
            >
              <span class="text-gray-400">
                <span class="text-gray-600 font-mono text-xs mr-2">{{ i + 1 }}</span>
                {{ r.flag }} {{ r.country }}
              </span>
              <div class="flex items-center gap-3">
                <span class="font-mono text-accent-red font-semibold">{{ formatDelta(r.delta) }}</span>
                <div class="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div class="h-full bg-accent-red/60 rounded-full" :style="{ width: Math.min(100, Math.abs(r.delta) / Math.abs(stats?.maxLoser?.delta || 1) * 100) + '%' }" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== CHARTS ===== -->
      <ClientOnly>
        <div class="card">
          <h3 class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
            Cambio vs FIFO — {{ selectionLabel }}
            <span v-if="filteredRows.length < 21" class="text-gray-600">({{ filteredRows.length }} países)</span>
          </h3>
          <VChart :option="deltaOption" autoresize :class="'w-full'" :style="{ height: Math.max(350, filteredRows.length * 32) + 'px' }" />
        </div>
        <div class="card">
          <h3 class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">Visas: FIFO vs {{ selectionLabel }}</h3>
          <VChart :option="comparisonOption" autoresize :class="'w-full'" :style="{ height: Math.max(350, filteredRows.length * 32) + 'px' }" />
        </div>
      </ClientOnly>

      <!-- ===== TABLE ===== -->
      <details class="card">
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
          Ver tabla completa ({{ impactRows.length }} países)
        </summary>
        <div class="mt-4">
          <DataTable
            :headers="['País', 'FIFO', selectionLabel, 'Delta', '% cambio', 'Espera máx.']"
            :rows="filteredRows.map(r => [
              r.flag + ' ' + r.country,
              formatNumber(r.fifo_visas),
              formatNumber(r.scenario_visas),
              formatDelta(r.delta),
              r.fifo_visas > 0 ? ((r.delta / r.fifo_visas) * 100).toFixed(1) + '%' : '—',
              r.max_wait + ' años',
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
