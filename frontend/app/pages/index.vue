<script setup lang="ts">
import type { SummaryData, GroupsData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchSummary, fetchGroups } = useOptimizer()

const summary = ref<SummaryData | null>(null)
const groups = ref<GroupsData | null>(null)

onMounted(async () => {
  const [s, g] = await Promise.all([fetchSummary(), fetchGroups()])
  summary.value = s
  groups.value = g
})

const totalBacklog = computed(() => groups.value ? formatNumber(groups.value.total_demand) : '...')
const maxWait = computed(() => {
  if (!groups.value) return '...'
  return Math.max(...groups.value.groups.map(g => g.w))
})

const fifoWaste = computed(() => {
  if (!summary.value) return 0
  return Math.round(summary.value.baseline.f3)
})

const mohhoImprovement = computed(() => {
  if (!summary.value) return { f1: '0', f2: '0', waste: '0' }
  const b = summary.value.baseline
  return {
    f1: ((1 - summary.value.best_f1[0] / b.f1) * 100).toFixed(0),
    f2: ((1 - summary.value.best_f2[1] / b.f2) * 100).toFixed(0),
    waste: formatNumber(Math.round(b.f3 - summary.value.best_f3[2])),
  }
})
</script>

<template>
  <div class="space-y-10">
    <!-- Hero -->
    <section class="text-center py-10 relative">
      <div class="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent rounded-3xl" />
      <div class="relative">
        <p class="text-xs text-primary-300 font-semibold uppercase tracking-[0.25em] mb-3">Multi-Objective Harris Hawks Optimization</p>
        <h1 class="text-4xl md:text-6xl font-black tracking-tight leading-[1.1]">
          <span class="bg-gradient-to-r from-accent-yellow via-accent-green to-primary bg-clip-text text-transparent">
            VISA PREDICT AI
          </span>
        </h1>
        <p class="text-gray-400 mt-4 max-w-2xl mx-auto text-lg leading-relaxed">
          Optimizaci&oacute;n multi-objetivo para la asignaci&oacute;n de
          <span class="text-white font-semibold">140,000 visas EB</span> de EE.UU.
          entre <span class="text-white font-semibold">21 pa&iacute;ses</span> y
          <span class="text-white font-semibold">5 categor&iacute;as</span>.
        </p>
      </div>
    </section>

    <!-- KPI Cards -->
    <section v-if="summary && groups" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Total Visas EB" value="140,000" unit="por a&ntilde;o fiscal" color="text-accent-yellow" />
      <KpiCard label="Backlog Total" :value="totalBacklog" unit="peticiones aprobadas" color="text-accent-red" />
      <KpiCard label="Pa&iacute;ses Analizados" value="21" unit="bloques de pa&iacute;ses" />
      <KpiCard label="Mayor Espera" :value="maxWait + ' a&ntilde;os'" unit="India EB-3" color="text-accent-green" />
    </section>

    <!-- Skeleton while loading -->
    <section v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="metric-card">
        <div class="skeleton h-3 w-20 mx-auto mb-3" />
        <div class="skeleton h-8 w-24 mx-auto mb-2" />
        <div class="skeleton h-2.5 w-16 mx-auto" />
      </div>
    </section>

    <!-- Problem description -->
    <section class="card space-y-4">
      <h2 class="section-title">El Problema</h2>
      <p class="text-gray-400 leading-relaxed">
        Cada a&ntilde;o fiscal, EE.UU. otorga <strong class="text-accent-yellow">140,000 visas de empleo</strong>
        (EB) distribuidas en 5 categor&iacute;as y limitadas por topes por pa&iacute;s del 7%.
        El sistema actual (<strong class="text-accent-red">FIFO</strong>) genera esperas de hasta
        <strong class="text-white">13 a&ntilde;os</strong> para ciertos pa&iacute;ses y deja
        <strong class="text-accent-red">{{ fifoWaste > 0 ? formatNumber(fifoWaste) : '...' }}</strong> visas sin usar.
      </p>
      <p class="text-gray-400 leading-relaxed">
        <strong class="text-accent-green">MOHHO</strong> (Multi-Objective Harris Hawks Optimization) encuentra un
        <strong class="text-accent-green">frente de Pareto</strong> con cientos de soluciones que mejoran
        simult&aacute;neamente la espera, la equidad entre pa&iacute;ses y la utilizaci&oacute;n de visas.
      </p>
    </section>

    <!-- FIFO vs MOHHO comparison -->
    <section v-if="summary" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card border-accent-red/20 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-accent-red/60" />
        <h3 class="text-sm font-semibold text-accent-red uppercase tracking-wider mb-4 pl-3">FIFO (Sistema Actual)</h3>
        <div class="space-y-3 font-mono text-sm pl-3">
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; espera</span>
            <span class="text-white text-lg font-bold">{{ summary.baseline.f1.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">a&ntilde;os</span></span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; brecha</span>
            <span class="text-white text-lg font-bold">{{ summary.baseline.f2.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">a&ntilde;os</span></span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; desperdicio</span>
            <span class="text-white text-lg font-bold">{{ formatNumber(Math.round(summary.baseline.f3)) }} <span class="text-xs text-gray-500 font-normal">visas</span></span>
          </div>
        </div>
      </div>
      <div class="card border-accent-green/20 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-accent-green/60" />
        <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider mb-4 pl-3">MOHHO (Mejor Soluci&oacute;n)</h3>
        <div class="space-y-3 font-mono text-sm pl-3">
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; espera</span>
            <span class="text-white text-lg font-bold">
              {{ summary.best_f1[0].toFixed(3) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.f1 }}%</span>
            </span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; brecha</span>
            <span class="text-white text-lg font-bold">
              {{ summary.best_f2[1].toFixed(3) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.f2 }}%</span>
            </span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f&nbsp;&nbsp; desperdicio</span>
            <span class="text-white text-lg font-bold">
              {{ formatNumber(Math.round(summary.best_f3[2])) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.waste }}</span>
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Objectives explained -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-yellow to-accent-yellow/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="heart" :size="16" class="text-accent-yellow" />
          <h3 class="text-accent-yellow font-bold">f&#8321; &mdash; Carga de Espera</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide los a&ntilde;os de espera ponderados de las personas que NO reciben visa.
          Menor = m&aacute;s humanitario.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8321;(x) = &Sigma;(n&#7501; - x&#7501;)&middot;w&#7501; / &Sigma;n&#7501;
        </p>
      </div>
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-green to-accent-green/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="scale" :size="16" class="text-accent-green" />
          <h3 class="text-accent-green font-bold">f&#8322; &mdash; Disparidad</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide la brecha m&aacute;xima de espera entre pa&iacute;ses.
          Menor = m&aacute;s equitativo.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8322;(x) = max|W&#772;c&#8321; - W&#772;c&#8322;|
        </p>
      </div>
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-blue to-accent-blue/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="trending-up" :size="16" class="text-accent-blue" />
          <h3 class="text-accent-blue font-bold">f&#8323; &mdash; Desperdicio</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide las visas que quedan sin usar por la interacci&oacute;n de topes.
          Menor = m&aacute;s eficiente.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8323;(x) = V - &Sigma;x&#7501;
        </p>
      </div>
    </section>

    <!-- Experimental summary -->
    <section v-if="summary" class="card">
      <h2 class="section-title mb-4">Configuraci&oacute;n Experimental</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ summary.num_runs }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">corridas independientes</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ summary.pop_size }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">halcones (poblaci&oacute;n)</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ summary.max_iter }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">iteraciones</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-accent-green">{{ summary.combined_pareto_size }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">soluciones Pareto</p>
        </div>
      </div>
    </section>
  </div>
</template>
