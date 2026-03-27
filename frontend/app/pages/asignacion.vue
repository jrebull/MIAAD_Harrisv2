<script setup lang="ts">
import type { ParetoData, ParetoPoint, SummaryData, AllocationData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { scenario, setScenario, currentScenario } = useScenario()
const { allocation, loading, fetchAllocation, fetchPareto, fetchSummary } = useOptimizer()

const categories = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

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
  const [p, s] = await Promise.all([fetchPareto(), fetchSummary()])
  pareto.value = p
  summary.value = s
  fetchAllocation()
})

watch(scenario, () => fetchAllocation())
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Asignaci&oacute;n de Visas</h1>

    <!-- ===== PARETO BROWSER ===== -->
    <section class="card space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-sm font-bold text-white">Frente de Pareto &mdash; {{ pareto?.count || '...' }} soluciones</h2>
          <p class="text-[10px] text-gray-500 mt-0.5">
            Cada fila es una soluci&oacute;n &oacute;ptima del archivo Pareto. Haz clic para seleccionar.
          </p>
        </div>

        <!-- Quick picks -->
        <div class="flex items-center gap-1.5">
          <span class="text-[10px] text-gray-600 mr-1">Accesos r&aacute;pidos:</span>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'humanitario' ? 'bg-accent-red/20 text-accent-red' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('humanitario')"
          >
            Min f&sub1;
          </button>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'equidad' ? 'bg-accent-green/20 text-accent-green' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('equidad')"
          >
            Min f&sub2;
          </button>
          <button
            class="px-2 py-0.5 rounded text-[10px] font-medium transition-colors"
            :class="scenario === 'max_utilizacion' ? 'bg-accent-yellow/20 text-accent-yellow' : 'bg-dark-bg2 text-gray-500 hover:text-white'"
            @click="pickScenario('max_utilizacion')"
          >
            Min f&sub3;
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
                f&sub1; espera{{ sortArrow('f1') }}
              </th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f2' ? 'text-accent-green' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f2')"
              >
                f&sub2; brecha{{ sortArrow('f2') }}
              </th>
              <th
                class="px-3 py-2 text-right text-[10px] uppercase font-semibold cursor-pointer select-none transition-colors"
                :class="sortKey === 'f3' ? 'text-accent-red' : 'text-gray-500 hover:text-gray-300'"
                @click="toggleSort('f3')"
              >
                f&sub3; desperdicio{{ sortArrow('f3') }}
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
        &middot; Ordenar por columna &middot; Todas las soluciones son Pareto-&oacute;ptimas (ninguna domina a otra)
      </p>
    </section>

    <!-- ===== SELECTED SOLUTION KPIs ===== -->
    <section v-if="selectedSolution" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="f&#8321; espera" :value="selectedSolution.f1.toFixed(2)" unit="a&ntilde;os" color="text-accent-yellow" />
      <KpiCard label="f&#8322; brecha" :value="selectedSolution.f2.toFixed(2)" unit="a&ntilde;os" color="text-accent-green" />
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
          Asignaci&oacute;n detallada &mdash; escenario
          <span class="text-white">{{ currentScenario.name }}</span>
        </p>
        <p class="text-[10px] text-gray-600 mb-3">{{ currentScenario.description }}</p>

        <!-- Utilization bar -->
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm text-gray-400">
            <span class="text-white font-bold">{{ allocation.visas_used.toLocaleString() }}</span>
            de 140,000 visas &mdash; <span class="text-accent-green font-mono font-bold">{{ allocation.utilization }}%</span>
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
