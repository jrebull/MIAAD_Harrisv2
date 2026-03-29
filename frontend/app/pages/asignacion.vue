<script setup lang="ts">
import type { ParetoData, ParetoPoint, SummaryData, AllocationData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'

const { scenario, setScenario, currentScenario } = useScenario()
const { allocation, loading, fetchAllocation, fetchPareto, fetchSummary } = useOptimizer()
const { get } = useApi()

const categories = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

// ---- FIFO baseline allocation ----
const fifoAlloc = ref<AllocationData | null>(null)

async function loadFifoAllocation() {
  try {
    fifoAlloc.value = await get<AllocationData>('/api/allocation/fifo')
  } catch (e) {
    console.error('[FIFO allocation fetch]', e)
  }
}

// ---- Comparison heatmap options ----
const sharedMax = computed(() => {
  let maxVal = 0
  const matrices = [allocation.value?.matrix, fifoAlloc.value?.matrix].filter(Boolean) as number[][][]
  for (const matrix of matrices) {
    for (const row of matrix) {
      for (const val of row) {
        if (val > maxVal) maxVal = val
      }
    }
  }
  return maxVal
})

function buildHeatmapOption(
  matrix: number[][],
  countries: string[],
  title: string,
  colorScheme: 'fifo' | 'mohho',
  otherMatrix?: number[][] | null,
): EChartsOption {
  const data: [number, number, number][] = []
  for (let i = 0; i < countries.length; i++) {
    for (let j = 0; j < categories.length; j++) {
      data.push([j, i, matrix[i]?.[j] || 0])
    }
  }

  const fifoColors = ['#1a1520', '#4a1a1a', '#8b2020', '#c43a2a', '#e85040']
  const mohhoColors = ['#0a1520', '#0d3a4e', '#1a8f7a', '#4dd8a0', '#00E5A0']

  return {
    ...baseChartOption,
    title: {
      text: title,
      textStyle: { color: CHART_COLORS.text, fontSize: 13, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      position: 'top',
      formatter: (p: any) => {
        const [j, i, val] = p.data
        const country = countries[i]
        const cat = categories[j]
        let deltaStr = ''
        if (otherMatrix) {
          const otherVal = otherMatrix[i]?.[j] || 0
          const delta = val - otherVal
          const sign = delta > 0 ? '+' : ''
          const color = delta > 0 ? CHART_COLORS.green : delta < 0 ? CHART_COLORS.red : CHART_COLORS.textMuted
          deltaStr = `<br><span style="color:${color};font-size:11px">${sign}${delta.toLocaleString()} vs ${colorScheme === 'mohho' ? 'FIFO' : 'MOHHO'}</span>`
        }
        return `<b>${country}</b><br><span style="opacity:0.6">${cat}:</span> <b style="color:${CHART_COLORS.yellow}">${val.toLocaleString()}</b> visas${deltaStr}`
      },
    },
    grid: { left: 110, right: 50, top: 48, bottom: 32 },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 11, fontWeight: 600 },
      splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0.02)', 'transparent'] } },
      axisTick: { show: false },
      position: 'top',
    },
    yAxis: {
      type: 'category',
      data: countries,
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: sharedMax.value || 1,
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      itemHeight: 160,
      textStyle: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inRange: { color: colorScheme === 'fifo' ? fifoColors : mohhoColors },
    },
    series: [{
      type: 'heatmap',
      data,
      label: {
        show: true,
        color: '#fff',
        fontSize: 8,
        fontWeight: 500,
        textShadowBlur: 2,
        textShadowColor: 'rgba(0,0,0,0.6)',
        formatter: (p: any) => {
          const val = p.data[2]
          if (val === 0) return '0'
          // Show delta annotation if other matrix is available
          if (otherMatrix) {
            const [j, i] = p.data
            const otherVal = otherMatrix[i]?.[j] || 0
            const delta = val - otherVal
            if (delta !== 0) {
              const sign = delta > 0 ? '+' : ''
              return `${val.toLocaleString()}\n{delta|${sign}${delta.toLocaleString()}}`
            }
          }
          return val.toLocaleString()
        },
        rich: {
          delta: {
            fontSize: 7,
            color: 'rgba(255,255,255,0.7)',
            lineHeight: 10,
          },
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
}

const fifoHeatmapOption = computed<EChartsOption | null>(() => {
  if (!fifoAlloc.value) return null
  return buildHeatmapOption(
    fifoAlloc.value.matrix,
    fifoAlloc.value.rows.map(r => r.flag + ' ' + r.country),
    'FIFO (Baseline)',
    'fifo',
    allocation.value?.matrix || null,
  )
})

const mohhoHeatmapOption = computed<EChartsOption | null>(() => {
  if (!allocation.value) return null
  return buildHeatmapOption(
    allocation.value.matrix,
    allocation.value.rows.map(r => r.flag + ' ' + r.country),
    `MOHHO — ${currentScenario.value.name}`,
    'mohho',
    fifoAlloc.value?.matrix || null,
  )
})

// ---- Category totals for Sankey ----
const catTotals = computed(() => {
  if (!allocation.value) return null
  const totals: Record<string, number> = { 'EB-1': 0, 'EB-2': 0, 'EB-3': 0, 'EB-4': 0, 'EB-5': 0 }
  allocation.value.rows.forEach(r => {
    Object.entries(r.categories).forEach(([cat, val]) => { totals[cat] = (totals[cat] ?? 0) + val })
  })
  return totals
})

// ---- Sankey spillover cascade ----
const sankeyOption = computed<EChartsOption | null>(() => {
  if (!catTotals.value) return null
  const t = catTotals.value
  const BUDGET = 28000

  // Calculate spillover cascade
  const eb4Used = t['EB-4'] ?? 0
  const eb5Used = t['EB-5'] ?? 0
  const eb4Unused = Math.max(0, BUDGET - eb4Used)
  const eb5Unused = Math.max(0, BUDGET - eb5Used)

  // Spillover based on actual assignments vs base budgets
  // Any category total above 28K means it received spillover visas
  const toEb1 = Math.max(0, (t['EB-1'] ?? 0) - BUDGET)
  const toEb2 = Math.max(0, (t['EB-2'] ?? 0) - BUDGET)
  const toEb3 = Math.max(0, (t['EB-3'] ?? 0) - BUDGET)

  // EB-4/5 unused goes to spillover pool
  const spillPool = eb4Unused + eb5Unused
  // Any spillover not absorbed = waste
  const unabsorbed = Math.max(0, spillPool - toEb1 - toEb2 - toEb3)

  // Node colors
  const nodeColors: Record<string, string> = {
    'Presup. EB-4': '#a78bfa',
    'Presup. EB-5': '#818cf8',
    'EB-4 Asignado': '#7c3aed',
    'EB-5 Asignado': '#6366f1',
    'Sobrante EB-4/5': CHART_COLORS.yellow,
    'EB-1 (+spillover)': '#ef4444',
    'EB-2 (+spillover)': '#f97316',
    'EB-3 (+spillover)': '#22c55e',
    'Sin Usar': '#6b7280',
  }

  const nodes = [
    { name: 'Presup. EB-4', itemStyle: { color: nodeColors['Presup. EB-4'], borderColor: 'rgba(167,139,250,0.4)' } },
    { name: 'Presup. EB-5', itemStyle: { color: nodeColors['Presup. EB-5'], borderColor: 'rgba(129,140,248,0.4)' } },
    { name: 'EB-4 Asignado', itemStyle: { color: nodeColors['EB-4 Asignado'], borderColor: 'rgba(124,58,237,0.4)' } },
    { name: 'EB-5 Asignado', itemStyle: { color: nodeColors['EB-5 Asignado'], borderColor: 'rgba(99,102,241,0.4)' } },
    { name: 'Sobrante EB-4/5', itemStyle: { color: nodeColors['Sobrante EB-4/5'], borderColor: 'rgba(255,214,0,0.4)' } },
    { name: 'EB-1 (+spillover)', itemStyle: { color: nodeColors['EB-1 (+spillover)'], borderColor: 'rgba(239,68,68,0.4)' } },
    { name: 'EB-2 (+spillover)', itemStyle: { color: nodeColors['EB-2 (+spillover)'], borderColor: 'rgba(249,115,22,0.4)' } },
    { name: 'EB-3 (+spillover)', itemStyle: { color: nodeColors['EB-3 (+spillover)'], borderColor: 'rgba(34,197,94,0.4)' } },
    ...(unabsorbed > 0 ? [{ name: 'Sin Usar', itemStyle: { color: nodeColors['Sin Usar'], borderColor: 'rgba(107,114,128,0.4)' } }] : []),
  ]

  const links: { source: string; target: string; value: number; lineStyle?: any }[] = []

  // EB-4 budget splits into used and unused
  if (eb4Used > 0)
    links.push({ source: 'Presup. EB-4', target: 'EB-4 Asignado', value: eb4Used,
      lineStyle: { color: 'rgba(167,139,250,0.35)' } })
  if (eb4Unused > 0)
    links.push({ source: 'Presup. EB-4', target: 'Sobrante EB-4/5', value: eb4Unused,
      lineStyle: { color: 'rgba(255,214,0,0.35)' } })

  // EB-5 budget splits into used and unused
  if (eb5Used > 0)
    links.push({ source: 'Presup. EB-5', target: 'EB-5 Asignado', value: eb5Used,
      lineStyle: { color: 'rgba(129,140,248,0.35)' } })
  if (eb5Unused > 0)
    links.push({ source: 'Presup. EB-5', target: 'Sobrante EB-4/5', value: eb5Unused,
      lineStyle: { color: 'rgba(255,214,0,0.35)' } })

  // Spillover cascade: pool → EB-1 → EB-2 → EB-3
  if (toEb1 > 0)
    links.push({ source: 'Sobrante EB-4/5', target: 'EB-1 (+spillover)', value: toEb1,
      lineStyle: { color: 'rgba(239,68,68,0.35)' } })
  if (toEb2 > 0)
    links.push({ source: 'Sobrante EB-4/5', target: 'EB-2 (+spillover)', value: toEb2,
      lineStyle: { color: 'rgba(249,115,22,0.35)' } })
  if (toEb3 > 0)
    links.push({ source: 'Sobrante EB-4/5', target: 'EB-3 (+spillover)', value: toEb3,
      lineStyle: { color: 'rgba(34,197,94,0.35)' } })
  if (unabsorbed > 0)
    links.push({ source: 'Sobrante EB-4/5', target: 'Sin Usar', value: unabsorbed,
      lineStyle: { color: 'rgba(107,114,128,0.35)' } })

  // If spillover pool is 0 but we still need visible nodes, handle edge case
  // Filter out any links with value 0 (shouldn't happen but just in case)
  const validLinks = links.filter(l => l.value > 0)

  // If no spillover at all, show a minimal diagram
  if (validLinks.length === 0) return null

  return {
    ...baseChartOption,
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `<b>${params.data.source}</b> → <b>${params.data.target}</b><br/><span style="color:${CHART_COLORS.yellow};font-weight:700">${params.data.value.toLocaleString()}</span> visas`
        }
        return `<b>${params.name}</b>`
      },
    },
    series: [{
      type: 'sankey',
      layoutIterations: 32,
      nodeAlign: 'justify',
      orient: 'horizontal',
      nodeWidth: 22,
      nodeGap: 14,
      left: 60,
      right: 60,
      top: 20,
      bottom: 20,
      data: nodes,
      links: validLinks,
      label: {
        show: true,
        position: 'right',
        color: CHART_COLORS.text,
        fontSize: 11,
        fontWeight: 500,
        fontFamily: 'Inter, sans-serif',
        formatter: (p: any) => {
          // Show value next to name
          const val = validLinks
            .filter(l => l.target === p.name)
            .reduce((sum, l) => sum + l.value, 0)
            || validLinks
            .filter(l => l.source === p.name)
            .reduce((sum, l) => sum + l.value, 0)
          return `${p.name}\n{val|${val > 0 ? val.toLocaleString() : ''}}`
        },
        rich: {
          val: {
            fontSize: 10,
            color: CHART_COLORS.textMuted,
            fontFamily: 'Inter, monospace',
            lineHeight: 16,
          },
        },
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { opacity: 0.6 },
      },
      lineStyle: {
        curveness: 0.5,
        opacity: 0.3,
      },
      itemStyle: {
        borderWidth: 1,
        borderRadius: 3,
      },
    }],
  } as EChartsOption
})

// ---- Pareto browser state ----
const pareto = ref<ParetoData | null>(null)
const summary = ref<SummaryData | null>(null)
const selectedIdx = ref(0)
const sortKey = ref<'f1' | 'f2' | 'f3' | 'visas_used'>('f1')
const sortAsc = ref(true)

interface IndexedPoint extends ParetoPoint { _idx: number; _scenario: string; _util: number; _champion: boolean }

const sortedPareto = computed<IndexedPoint[]>(() => {
  if (!pareto.value?.points) return []
  const scenarios = pointScenarios.value
  const champs = championIdxs.value
  const champSet = new Set(Object.values(champs))
  const pts = pareto.value.points.map((p, i) => ({
    ...p,
    _idx: i,
    _scenario: scenarios[i] || 'equilibrio',
    _util: +(p.visas_used / 140000 * 100).toFixed(1),
    _champion: champSet.has(i),
  }))
  pts.sort((a, b) => sortAsc.value ? a[sortKey.value] - b[sortKey.value] : b[sortKey.value] - a[sortKey.value])
  return pts
})

const selectedSolution = computed(() => {
  if (!pareto.value?.points || selectedIdx.value < 0) return null
  return pareto.value.points[selectedIdx.value]
})

// Scenario type metadata for display
const SCENARIO_META: Record<string, { label: string; short: string; color: string; bg: string; border: string }> = {
  humanitario: { label: 'Humanitario', short: 'HUM', color: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30' },
  equidad: { label: 'Equidad', short: 'EQU', color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30' },
  max_utilizacion: { label: 'Max Utilización', short: 'MAX', color: 'text-yellow-400', bg: 'bg-yellow-500/15', border: 'border-yellow-500/30' },
  equilibrio: { label: 'Equilibrio', short: 'BAL', color: 'text-blue-400', bg: 'bg-blue-500/15', border: 'border-blue-500/30' },
}

// Find the single closest point index to a target
function closestIdx(pts: ParetoPoint[], target: number[]): number {
  let best = 0, bestD = Infinity
  pts.forEach((p, i) => {
    const d = ((p.f1 - target[0]) / 10) ** 2 + ((p.f2 - target[1]) / 16) ** 2 + ((p.f3 - target[2]) / 50000) ** 2
    if (d < bestD) { bestD = d; best = i }
  })
  return best
}

// Find knee point: max perpendicular distance from line connecting min-f1 and min-f2 extremes
function findKneeIdx(pts: ParetoPoint[]): number {
  if (pts.length < 3) return 0
  // Normalize all objectives to [0,1]
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2), f3s = pts.map(p => p.f3)
  const r1 = Math.max(...f1s) - Math.min(...f1s) || 1
  const r2 = Math.max(...f2s) - Math.min(...f2s) || 1
  const r3 = Math.max(...f3s) - Math.min(...f3s) || 1
  const norm = pts.map(p => [
    (p.f1 - Math.min(...f1s)) / r1,
    (p.f2 - Math.min(...f2s)) / r2,
    (p.f3 - Math.min(...f3s)) / r3,
  ])
  // Ideal and anti-ideal corners
  const ideal = [0, 0, 0]
  const anti = [1, 1, 1]
  // Line direction
  const dir = [anti[0] - ideal[0], anti[1] - ideal[1], anti[2] - ideal[2]]
  const dirLen = Math.sqrt(dir[0] ** 2 + dir[1] ** 2 + dir[2] ** 2)
  // Point with max perpendicular distance from ideal-anti line
  let knee = 0, maxDist = -1
  norm.forEach((n, i) => {
    const v = [n[0] - ideal[0], n[1] - ideal[1], n[2] - ideal[2]]
    const proj = (v[0] * dir[0] + v[1] * dir[1] + v[2] * dir[2]) / dirLen
    const distSq = v[0] ** 2 + v[1] ** 2 + v[2] ** 2 - proj ** 2
    // We want low values = close to ideal, so use negative projected component as tiebreak
    const score = Math.sqrt(Math.max(0, distSq))
    // Knee is the point closest to ideal that is "most balanced" — use sum of normalized objectives
    // Actually: knee = min sum of normalized objectives (most balanced compromise)
    const sumNorm = n[0] + n[1] + n[2]
    if (i === 0 || sumNorm < maxDist) { maxDist = sumNorm; knee = i }
  })
  return knee
}

// Champion indices: the single best point for each scenario
const championIdxs = computed<Record<string, number>>(() => {
  const pts = pareto.value?.points
  if (!pts?.length || !summary.value) return {}
  const s = summary.value
  return {
    humanitario: closestIdx(pts, s.best_f1),
    equidad: closestIdx(pts, s.best_f2),
    max_utilizacion: closestIdx(pts, s.best_f3),
    equilibrio: findKneeIdx(pts),
  }
})

// Every point gets a scenario tag based on closest target
const pointScenarios = computed<string[]>(() => {
  const pts = pareto.value?.points
  if (!pts?.length || !summary.value) return []
  const s = summary.value
  const targets: Record<string, number[]> = {
    humanitario: s.best_f1,
    equidad: s.best_f2,
    max_utilizacion: s.best_f3,
  }
  // Knee point target = the actual knee solution's fitness
  const kneeIdx = championIdxs.value.equilibrio ?? 0
  const knee = pts[kneeIdx]
  if (knee) targets.equilibrio = [knee.f1, knee.f2, knee.f3]

  return pts.map(p => {
    let best = 'equilibrio'
    let bestDist = Infinity
    for (const [sc, t] of Object.entries(targets)) {
      const d = ((p.f1 - t[0]) / 10) ** 2 + ((p.f2 - t[1]) / 16) ** 2 + ((p.f3 - t[2]) / 50000) ** 2
      if (d < bestDist) { bestDist = d; best = sc }
    }
    return best
  })
})

// Map a solution to its scenario (for selectSolution)
function closestScenario(sol: ParetoPoint): string {
  if (!summary.value) return 'equilibrio'
  const s = summary.value
  const targets: Record<string, number[]> = {
    humanitario: s.best_f1,
    equidad: s.best_f2,
    max_utilizacion: s.best_f3,
  }
  let best = 'equilibrio'
  let bestDist = Infinity
  for (const [sc, t] of Object.entries(targets)) {
    const d = ((sol.f1 - t[0]) / 10) ** 2 + ((sol.f2 - t[1]) / 16) ** 2 + ((sol.f3 - t[2]) / 50000) ** 2
    if (d < bestDist) { bestDist = d; best = sc }
  }
  return best
}

function selectSolution(idx: number) {
  selectedIdx.value = idx
  const sol = pareto.value!.points[idx]
  const sc = closestScenario(sol)
  if (sc !== scenario.value) setScenario(sc)
}

function toggleSort(key: typeof sortKey.value) {
  if (sortKey.value === key) { sortAsc.value = !sortAsc.value }
  else { sortKey.value = key; sortAsc.value = true }
}

function sortArrow(key: string) {
  if (sortKey.value !== key) return ''
  return sortAsc.value ? ' ▲' : ' ▼'
}

// ---- Quick scenario picks ----
function pickScenario(sc: string) {
  setScenario(sc)
  if (!pareto.value?.points) return
  // Find the tagged point for this scenario
  const tags = pointScenarios.value
  const taggedIdx = tags.findIndex(t => t === sc)
  if (taggedIdx >= 0) {
    selectedIdx.value = taggedIdx
    return
  }
  // Fallback: closest to target
  if (!summary.value) return
  const s = summary.value
  let target: number[]
  if (sc === 'humanitario') target = s.best_f1
  else if (sc === 'equidad') target = s.best_f2
  else if (sc === 'max_utilizacion') target = s.best_f3
  else return
  selectedIdx.value = closestIdx(pareto.value.points, target)
}

// ---- Init ----
onMounted(async () => {
  const [p, s] = await Promise.all([fetchPareto(), fetchSummary(), loadFifoAllocation()])
  pareto.value = p
  summary.value = s
  fetchAllocation()
})

watch(scenario, () => fetchAllocation())
</script>

<template>
  <div class="space-y-6">

    <!-- ===== CINEMATIC HERO ===== -->
    <section class="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-dark-bg1 via-[#0a0a2e] to-dark-bg1">
      <!-- Animated background layers -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_20%,rgba(0,60,166,0.15),transparent_60%)]" />
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_80%_80%,rgba(0,229,160,0.08),transparent_50%)]" />
        <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent" />
        <div class="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-accent-green/30 to-transparent" />
      </div>

      <div class="relative px-6 py-8 md:px-10 md:py-10">
        <div class="flex items-start justify-between flex-wrap gap-4">
          <div class="max-w-2xl">
            <div class="flex items-center gap-2 mb-3">
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 text-sm font-bold text-primary-300">5</span>
              <span class="text-[10px] text-gray-500 uppercase tracking-[0.2em] font-semibold">Asignaci&oacute;n de Visas</span>
            </div>
            <h1 class="text-2xl md:text-3xl font-black text-white leading-tight">
              Del Frente de Pareto a la
              <span class="bg-gradient-to-r from-primary-300 to-accent-green bg-clip-text text-transparent"> Asignaci&oacute;n Real</span>
            </h1>
            <p class="text-sm text-gray-400 mt-3 leading-relaxed max-w-xl">
              Cada una de las <span class="text-white font-bold">{{ pareto?.count || 406 }}</span> soluciones Pareto-&oacute;ptimas
              define una distribuci&oacute;n completa de <span class="text-accent-green font-bold">140,000</span> visas
              entre 21 pa&iacute;ses &times; 5 categor&iacute;as. Selecciona una soluci&oacute;n para explorar su impacto.
            </p>
          </div>
          <!-- KPI cluster -->
          <div v-if="summary" class="flex items-center gap-3">
            <div class="bg-dark-bg2/80 backdrop-blur rounded-xl px-4 py-3 border border-emerald-500/20 text-center min-w-[90px]">
              <p class="text-[9px] text-gray-500 uppercase tracking-wider">Hipervolumen</p>
              <p class="text-lg font-black text-emerald-400 font-mono">{{ Math.round(summary.hv_stats.mean).toLocaleString() }}</p>
              <p class="text-[9px] text-gray-600 font-mono">&pm;{{ Math.round(summary.hv_stats.std).toLocaleString() }}</p>
            </div>
            <div class="bg-dark-bg2/80 backdrop-blur rounded-xl px-4 py-3 border border-blue-500/20 text-center min-w-[90px]">
              <p class="text-[9px] text-gray-500 uppercase tracking-wider">Ejecuciones</p>
              <p class="text-lg font-black text-blue-400 font-mono">{{ summary.num_runs }}</p>
              <p class="text-[9px] text-gray-600 font-mono">{{ summary.max_iter }} iter</p>
            </div>
            <div class="bg-dark-bg2/80 backdrop-blur rounded-xl px-4 py-3 border border-yellow-500/20 text-center min-w-[90px]">
              <p class="text-[9px] text-gray-500 uppercase tracking-wider">Soluciones</p>
              <p class="text-lg font-black text-yellow-400 font-mono">{{ pareto?.count || '...' }}</p>
              <p class="text-[9px] text-gray-600 font-mono">no-dominadas</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== PARETO BROWSER ===== -->
    <section class="card space-y-4 relative overflow-hidden">
      <!-- Background glow -->
      <div class="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      <!-- Header -->
      <div class="relative">
        <h2 class="text-sm font-bold text-white flex items-center gap-2">
          <span class="w-1.5 h-4 rounded-full bg-gradient-to-b from-primary to-accent-green" />
          Explorador del Frente de Pareto
        </h2>
        <p class="text-[10px] text-gray-500 mt-0.5 pl-4">
          {{ pareto?.count || '...' }} soluciones Pareto-&oacute;ptimas clasificadas por escenario. Las ★ marcan al campe&oacute;n de cada categor&iacute;a.
        </p>
      </div>

      <!-- Quick scenario picks with colored labels -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-[10px] text-gray-600 mr-1">Escenarios:</span>
        <button
          class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all border"
          :class="scenario === 'humanitario'
            ? 'bg-red-500/15 text-red-400 border-red-500/30'
            : 'bg-dark-bg2 text-gray-500 border-transparent hover:text-red-400'"
          @click="pickScenario('humanitario')"
        >
          Humanitario (min f₁)
        </button>
        <button
          class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all border"
          :class="scenario === 'equidad'
            ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
            : 'bg-dark-bg2 text-gray-500 border-transparent hover:text-emerald-400'"
          @click="pickScenario('equidad')"
        >
          Equidad (min f₂)
        </button>
        <button
          class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all border"
          :class="scenario === 'max_utilizacion'
            ? 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30'
            : 'bg-dark-bg2 text-gray-500 border-transparent hover:text-yellow-400'"
          @click="pickScenario('max_utilizacion')"
        >
          Max Utilización (min f₃)
        </button>
        <button
          class="px-2.5 py-1 rounded text-[10px] font-semibold transition-all border"
          :class="scenario === 'equilibrio'
            ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
            : 'bg-dark-bg2 text-gray-500 border-transparent hover:text-blue-400'"
          @click="pickScenario('equilibrio')"
        >
          Equilibrio (knee)
        </button>
      </div>

      <!-- Table -->
      <div class="max-h-[360px] overflow-y-auto rounded-lg border border-dark-border relative">
        <table class="w-full text-xs">
          <thead class="sticky top-0 z-10 bg-dark-bg2">
            <tr class="border-b border-dark-border">
              <th class="px-2 py-2 text-left text-[10px] text-gray-500 uppercase font-semibold w-10">#</th>
              <th class="px-2 py-2 text-center text-[10px] text-gray-500 uppercase font-semibold">Tipo</th>
              <th
                class="px-2 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f1' ? 'text-accent-yellow' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f1')"
              >
                f₁ espera{{ sortArrow('f1') }}
              </th>
              <th
                class="px-2 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f2' ? 'text-accent-green' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f2')"
              >
                f₂ brecha{{ sortArrow('f2') }}
              </th>
              <th
                class="px-2 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f3' ? 'text-accent-red' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f3')"
              >
                f₃ desperdicio{{ sortArrow('f3') }}
              </th>
              <th
                class="px-2 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'visas_used' ? 'text-primary-300' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('visas_used')"
              >
                Visas{{ sortArrow('visas_used') }}
              </th>
              <th class="px-2 py-2 text-right text-[10px] text-gray-500 uppercase font-semibold">Util %</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in sortedPareto"
              :key="p._idx"
              class="border-b cursor-pointer transition-all"
              :class="[
                selectedIdx === p._idx
                  ? 'bg-primary/15 text-white border-primary/30'
                  : p._champion
                    ? `${SCENARIO_META[p._scenario]?.bg} border-l-2 ${SCENARIO_META[p._scenario]?.border} font-semibold text-white`
                    : 'hover:bg-white/[0.03] text-gray-400 border-dark-border/20',
              ]"
              @click="selectSolution(p._idx)"
            >
              <td class="px-2 py-1.5 font-mono text-gray-600 text-[10px]">
                <span v-if="p._champion" class="text-[10px]">★</span>
                <span v-else>{{ p._idx + 1 }}</span>
              </td>
              <td class="px-2 py-1.5 text-center">
                <span
                  class="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold border"
                  :class="[
                    SCENARIO_META[p._scenario]?.bg,
                    SCENARIO_META[p._scenario]?.color,
                    SCENARIO_META[p._scenario]?.border,
                    p._champion ? 'ring-1 ring-offset-1 ring-offset-dark-bg1' : '',
                    p._champion ? SCENARIO_META[p._scenario]?.border.replace('border-', 'ring-') : '',
                  ]"
                >{{ SCENARIO_META[p._scenario]?.short }}</span>
              </td>
              <td class="px-2 py-1.5 text-right font-mono" :class="p._champion && p._scenario === 'humanitario' ? 'text-red-400 font-bold' : ''">{{ p.f1.toFixed(2) }}</td>
              <td class="px-2 py-1.5 text-right font-mono" :class="p._champion && p._scenario === 'equidad' ? 'text-emerald-400 font-bold' : ''">{{ p.f2.toFixed(2) }}</td>
              <td class="px-2 py-1.5 text-right font-mono" :class="p._champion && p._scenario === 'max_utilizacion' ? 'text-yellow-400 font-bold' : ''">{{ p.f3.toLocaleString() }}</td>
              <td class="px-2 py-1.5 text-right font-mono">{{ p.visas_used.toLocaleString() }}</td>
              <td class="px-2 py-1.5 text-right font-mono" :class="p._util >= 99 ? 'text-emerald-400 font-bold' : p._util >= 90 ? 'text-yellow-400' : 'text-gray-500'">{{ p._util }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer with baseline info -->
      <div class="flex items-center justify-between flex-wrap gap-2">
        <p class="text-[10px] text-gray-600">
          {{ pareto?.baseline ? `FIFO baseline: f\u2081=${pareto.baseline.f1.toFixed(2)}, f\u2082=${pareto.baseline.f2.toFixed(2)}, f\u2083=${pareto.baseline.f3.toLocaleString()}` : '' }}
          · Todas las soluciones son Pareto-óptimas (ninguna domina a otra)
        </p>
        <div class="flex items-center gap-3 text-[9px]">
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-red-500/30 border border-red-500/30" /> HUM = Humanitario</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-emerald-500/30 border border-emerald-500/30" /> EQU = Equidad</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-yellow-500/30 border border-yellow-500/30" /> MAX = Max Util.</span>
          <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-blue-500/30 border border-blue-500/30" /> BAL = Equilibrio</span>
        </div>
      </div>
    </section>

    <!-- ===== SELECTED SOLUTION KPIs ===== -->
    <section v-if="selectedSolution" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="f&#8321; espera" :value="selectedSolution.f1.toFixed(2)" unit="años" color="text-accent-yellow" />
      <KpiCard label="f&#8322; brecha" :value="selectedSolution.f2.toFixed(2)" unit="años" color="text-accent-green" />
      <KpiCard label="f&#8323; desperdicio" :value="selectedSolution.f3.toLocaleString()" unit="visas" color="text-accent-red" />
      <KpiCard label="Visas Asignadas" :value="selectedSolution.visas_used.toLocaleString()" unit="de 140,000" color="text-primary-300" />
    </section>

    <!-- ===== ALLOCATION DETAILS ===== -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else-if="allocation">
      <div class="card relative overflow-hidden">
        <!-- Section accent -->
        <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-primary/40 via-accent-green/40 to-transparent" />
        <div class="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

        <div class="relative">
          <div class="flex items-center gap-2 mb-1">
            <span class="w-1.5 h-4 rounded-full bg-gradient-to-b from-accent-green to-primary" />
            <p class="text-[10px] text-gray-500 uppercase tracking-[0.15em] font-bold">
              Asignaci&oacute;n detallada
            </p>
          </div>
          <h2 class="text-lg font-bold text-white mb-1">
            Escenario <span :class="SCENARIO_META[scenario]?.color || 'text-primary-300'">{{ currentScenario.name }}</span>
          </h2>
          <p class="text-[10px] text-gray-500 mb-4">{{ currentScenario.description }}</p>

          <!-- Utilization gauge -->
          <div class="bg-dark-bg2/60 rounded-xl p-4 border border-dark-border">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm text-gray-400">
                <span class="text-white font-bold text-base">{{ allocation.visas_used.toLocaleString() }}</span>
                <span class="text-gray-600"> / 140,000 visas</span>
              </p>
              <span
                class="px-2.5 py-1 rounded-full text-xs font-bold font-mono"
                :class="allocation.utilization >= 99 ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : allocation.utilization >= 90 ? 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30' : 'bg-red-500/15 text-red-400 border border-red-500/30'"
              >{{ allocation.utilization }}%</span>
            </div>
            <div class="h-3 bg-white/5 rounded-full overflow-hidden relative">
              <div class="absolute inset-0 bg-white/[0.02] rounded-full" style="background-image: repeating-linear-gradient(90deg, transparent, transparent 9.9%, rgba(255,255,255,0.03) 10%, rgba(255,255,255,0.03) 10.1%)" />
              <div
                class="h-full bg-gradient-to-r from-primary via-primary-300 to-accent-green rounded-full transition-all duration-1000 relative"
                :style="{ width: allocation.utilization + '%' }"
              >
                <div class="absolute inset-0 bg-gradient-to-t from-transparent to-white/10 rounded-full" />
              </div>
            </div>
            <div class="flex justify-between mt-1.5 text-[9px] font-mono text-gray-600">
              <span>0</span>
              <span>{{ (allocation.visas_used - (140000 - allocation.visas_used)).toLocaleString() > '0' ? (140000 - allocation.visas_used).toLocaleString() + ' sin usar' : 'Uso completo' }}</span>
              <span>140K</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Heatmap -->
      <ClientOnly>
        <div class="card">
          <ImpactHeatmap
            :countries="allocation.rows.map(r => r.flag + ' ' + r.country)"
            :categories="categories"
            :matrix="allocation.matrix"
            :title="'Asignaci\u00f3n: ' + currentScenario.name"
          />
        </div>
      </ClientOnly>

      <!-- ===== MOHHO vs FIFO COMPARISON HEATMAPS ===== -->
      <ClientOnly>
        <section v-if="fifoAlloc && allocation" class="space-y-3">
          <div class="card relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-red-500/30 via-transparent to-emerald-500/30" />
            <div class="flex items-center gap-2 mb-1">
              <span class="w-1.5 h-4 rounded-full bg-gradient-to-b from-red-400 to-emerald-400" />
              <h2 class="text-sm font-bold text-white">Batalla: MOHHO vs FIFO</h2>
            </div>
            <p class="text-[10px] text-gray-500 mb-3 pl-4">
              Ambos mapas de calor usan la misma escala de color para una comparaci&oacute;n justa.
              El tooltip muestra la diferencia (delta) respecto al otro m&eacute;todo.
            </p>

            <!-- Summary delta KPIs -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <div class="bg-dark-bg2 rounded-lg p-3 text-center">
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Visas FIFO</p>
                <p class="text-sm font-bold text-accent-red font-mono">{{ fifoAlloc.visas_used.toLocaleString() }}</p>
              </div>
              <div class="bg-dark-bg2 rounded-lg p-3 text-center">
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Visas MOHHO</p>
                <p class="text-sm font-bold text-accent-green font-mono">{{ allocation.visas_used.toLocaleString() }}</p>
              </div>
              <div class="bg-dark-bg2 rounded-lg p-3 text-center">
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Delta visas</p>
                <p
                  class="text-sm font-bold font-mono"
                  :class="allocation.visas_used - fifoAlloc.visas_used >= 0 ? 'text-accent-green' : 'text-accent-red'"
                >
                  {{ (allocation.visas_used - fifoAlloc.visas_used) >= 0 ? '+' : '' }}{{ (allocation.visas_used - fifoAlloc.visas_used).toLocaleString() }}
                </p>
              </div>
              <div class="bg-dark-bg2 rounded-lg p-3 text-center">
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Utilizaci&oacute;n &Delta;</p>
                <p
                  class="text-sm font-bold font-mono"
                  :class="allocation.utilization - fifoAlloc.utilization >= 0 ? 'text-accent-green' : 'text-accent-red'"
                >
                  {{ (allocation.utilization - fifoAlloc.utilization) >= 0 ? '+' : '' }}{{ (allocation.utilization - fifoAlloc.utilization).toFixed(1) }}%
                </p>
              </div>
            </div>

            <!-- Side-by-side heatmaps -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div class="bg-dark-bg2/50 rounded-lg p-2">
                <VChart v-if="fifoHeatmapOption" :option="fifoHeatmapOption" autoresize class="w-full h-[600px]" />
              </div>
              <div class="bg-dark-bg2/50 rounded-lg p-2">
                <VChart v-if="mohhoHeatmapOption" :option="mohhoHeatmapOption" autoresize class="w-full h-[600px]" />
              </div>
            </div>

            <p class="text-[10px] text-gray-600 mt-2">
              Izquierda: asignaci&oacute;n FIFO (baseline) en tonos rojos.
              Derecha: asignaci&oacute;n MOHHO ({{ currentScenario.name }}) en tonos verdes.
              Los valores en cada celda incluyen la diferencia respecto al otro m&eacute;todo.
            </p>
          </div>
        </section>
      </ClientOnly>

      <!-- ===== SANKEY SPILLOVER CASCADE ===== -->
      <section v-if="allocation && sankeyOption" class="card space-y-3 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-1.5 h-4 rounded-full bg-gradient-to-b from-purple-400 to-yellow-400" />
            <h2 class="text-sm font-bold text-white">Cascada de Spillover</h2>
          </div>
          <p class="text-[10px] text-gray-500 mt-0.5 pl-4">Flujo de visas no utilizadas: EB-4/5 &rarr; EB-1 &rarr; EB-2 &rarr; EB-3. Las visas que una categor&iacute;a no consume se redistribuyen inteligentemente.</p>
        </div>
        <ClientOnly>
          <VChart :option="sankeyOption" autoresize class="w-full h-[400px]" />
        </ClientOnly>
        <div class="grid grid-cols-5 gap-2">
          <div v-for="cat in categories" :key="cat" class="bg-dark-bg2 rounded-lg p-2 text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-wider">{{ cat }}</p>
            <p class="text-xs font-bold font-mono text-white">{{ catTotals ? (catTotals[cat] ?? 0).toLocaleString() : '...' }}</p>
            <p class="text-[9px] font-mono" :class="catTotals && (catTotals[cat] ?? 0) > 28000 ? 'text-accent-green' : catTotals && (catTotals[cat] ?? 0) < 28000 ? 'text-accent-yellow' : 'text-gray-500'">
              {{ catTotals ? ((catTotals[cat] ?? 0) >= 28000 ? '+' : '') + ((catTotals[cat] ?? 0) - 28000).toLocaleString() : '' }} vs presup.
            </p>
          </div>
        </div>
      </section>

      <!-- ===== STACKED BAR CHART ===== -->
      <ClientOnly>
        <section class="card relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-yellow-500/30 to-transparent" />
          <div class="flex items-center gap-2 mb-1">
            <span class="w-1.5 h-4 rounded-full bg-gradient-to-b from-yellow-400 to-primary" />
            <h2 class="text-sm font-bold text-white">Distribuci&oacute;n por Pa&iacute;s</h2>
          </div>
          <p class="text-[10px] text-gray-500 mb-2 pl-4">
            Visas asignadas por categor&iacute;a EB para cada pa&iacute;s. L&iacute;nea roja: tope per-c&aacute;pita (25,620).
          </p>
          <AllocationBar
            :countries="allocation.rows.map(r => r.flag + ' ' + r.country)"
            :categories="categories"
            :matrix="allocation.matrix"
            :cap-line="25620"
            :title="'Asignaci\u00f3n: ' + currentScenario.name"
          />
        </section>
      </ClientOnly>

      <!-- Data table -->
      <details class="card">
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
          Ver tabla de datos
        </summary>
        <div class="mt-4">
          <DataTable
            :headers="['Pa\u00eds', ...categories, 'Total']"
            :rows="allocation.rows.map(r => [
              r.flag + ' ' + r.country,
              ...categories.map(c => formatNumber(r.categories[c] || 0)),
              formatNumber(r.total)
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
