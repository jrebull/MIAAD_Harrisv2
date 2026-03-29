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

interface IndexedPoint extends ParetoPoint { _idx: number }

const sortedPareto = computed<IndexedPoint[]>(() => {
  if (!pareto.value?.points) return []
  const pts = pareto.value.points.map((p, i) => ({ ...p, _idx: i }))
  pts.sort((a, b) => sortAsc.value ? a[sortKey.value] - b[sortKey.value] : b[sortKey.value] - a[sortKey.value])
  return pts
})

const selectedSolution = computed(() => {
  if (!pareto.value?.points || selectedIdx.value < 0) return null
  return pareto.value.points[selectedIdx.value]
})

// Map a Pareto solution to its closest scenario
function closestScenario(sol: ParetoPoint): string {
  if (!summary.value) return 'equilibrio'
  const s = summary.value
  const targets: Record<string, number[]> = {
    humanitario: s.best_f1,
    equidad: s.best_f2,
    max_utilizacion: s.best_f3,
  }
  // Normalized distance to each scenario target
  let best = 'equilibrio'
  let bestDist = Infinity
  for (const [sc, t] of Object.entries(targets)) {
    const d = Math.sqrt(
      Math.pow((sol.f1 - t[0]) / 10, 2) +
      Math.pow((sol.f2 - t[1]) / 16, 2) +
      Math.pow((sol.f3 - t[2]) / 50000, 2),
    )
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
  // Find the pareto solution closest to this scenario
  if (!pareto.value?.points || !summary.value) return
  const s = summary.value
  let target: number[]
  if (sc === 'humanitario') target = s.best_f1
  else if (sc === 'equidad') target = s.best_f2
  else if (sc === 'max_utilizacion') target = s.best_f3
  else return // equilibrio / fifo — keep current selection

  let best = 0
  let bestDist = Infinity
  pareto.value.points.forEach((p, i) => {
    const d = Math.abs(p.f1 - target[0]) + Math.abs(p.f2 - target[1]) + Math.abs(p.f3 - target[2])
    if (d < bestDist) { bestDist = d; best = i }
  })
  selectedIdx.value = best
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
    <h1 class="section-title">Asignación de Visas</h1>

    <!-- ===== PARETO BROWSER ===== -->
    <section class="card space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-sm font-bold text-white">Frente de Pareto — {{ pareto?.count || '...' }} soluciones</h2>
          <p class="text-[10px] text-gray-500 mt-0.5">
            Cada fila es una solución óptima del archivo Pareto. Haz clic para seleccionar.
          </p>
        </div>

        <!-- Quick picks -->
        <div class="flex items-center gap-1.5">
          <span class="text-[10px] text-gray-600 mr-1">Accesos rápidos:</span>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'humanitario' ? 'bg-accent-red/20 text-accent-red' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('humanitario')"
          >
            Min f₁
          </button>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'equidad' ? 'bg-accent-green/20 text-accent-green' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('equidad')"
          >
            Min f₂
          </button>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'max_utilizacion' ? 'bg-accent-yellow/20 text-accent-yellow' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('max_utilizacion')"
          >
            Min f₃
          </button>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'equilibrio' ? 'bg-primary/20 text-primary-300' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('equilibrio')"
          >
            Balance
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="max-h-[320px] overflow-y-auto rounded-lg border border-dark-border">
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
                :class="sortKey === 'f3' ? 'text-accent-red' : 'text-gray-500 hover:text-gray-300'"
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
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(p, ri) in sortedPareto"
              :key="p._idx"
              class="border-b border-dark-border/20 cursor-pointer transition-colors"
              :class="selectedIdx === p._idx
                ? 'bg-primary/15 text-white'
                : 'hover:bg-white/[0.03] text-gray-400'"
              @click="selectSolution(p._idx)"
            >
              <td class="px-3 py-1.5 font-mono text-gray-600">{{ p._idx + 1 }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ p.f1.toFixed(2) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ p.f2.toFixed(2) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ p.f3.toLocaleString() }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ p.visas_used.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p class="text-[10px] text-gray-600">
        {{ pareto?.baseline ? `Baseline FIFO: f\u2081=${pareto.baseline.f1.toFixed(2)}, f\u2082=${pareto.baseline.f2.toFixed(2)}, f\u2083=${pareto.baseline.f3.toLocaleString()}` : '' }}
        · Ordenar por columna · Todas las soluciones son Pareto-óptimas (ninguna domina a otra)
      </p>
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
      <div class="card">
        <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1 font-semibold">
          Asignación detallada — escenario
          <span class="text-white">{{ currentScenario.name }}</span>
        </p>
        <p class="text-[10px] text-gray-600 mb-3">{{ currentScenario.description }}</p>

        <!-- Utilization bar -->
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm text-gray-400">
            <span class="text-white font-bold">{{ allocation.visas_used.toLocaleString() }}</span>
            de 140,000 visas — <span class="text-accent-green font-mono font-bold">{{ allocation.utilization }}%</span>
          </p>
        </div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden mb-1">
          <div
            class="h-full bg-gradient-to-r from-primary to-accent-green rounded-full transition-all duration-700"
            :style="{ width: allocation.utilization + '%' }"
          />
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
          <div class="card">
            <h2 class="text-sm font-bold text-white mb-1">Comparaci&oacute;n MOHHO vs FIFO</h2>
            <p class="text-[10px] text-gray-500 mb-3">
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
      <section v-if="allocation && sankeyOption" class="card space-y-3">
        <div>
          <h2 class="text-sm font-bold text-white">Cascada de Spillover</h2>
          <p class="text-[10px] text-gray-500 mt-0.5">Flujo de visas no utilizadas: EB-4/5 &rarr; EB-1 &rarr; EB-2 &rarr; EB-3</p>
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

      <!-- Stacked bar chart -->
      <ClientOnly>
        <div class="card">
          <AllocationBar
            :countries="allocation.rows.map(r => r.flag + ' ' + r.country)"
            :categories="categories"
            :matrix="allocation.matrix"
          />
        </div>
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
