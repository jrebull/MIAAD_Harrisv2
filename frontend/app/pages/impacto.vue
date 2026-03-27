<script setup lang="ts">
import { CHART_COLORS, baseChartOption, baseTooltip, type EChartsOption } from '~/composables/useEcharts'
import type { ImpactData, ImpactRow } from '~/composables/useOptimizer'
import { formatNumber, formatDelta } from '~/utils/formatters'

const { scenario, scenarios, setScenario, currentScenario } = useScenario()
const { fetchImpact } = useOptimizer()

const impact = ref<ImpactData | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  impact.value = await fetchImpact()
  loading.value = false
}

onMounted(load)
watch(scenario, load)

// Stats
const stats = computed(() => {
  if (!impact.value) return null
  const rows = impact.value.rows
  const winners = rows.filter(r => r.delta > 0).length
  const losers = rows.filter(r => r.delta < 0).length
  const totalGain = rows.filter(r => r.delta > 0).reduce((s, r) => s + r.delta, 0)
  const totalLoss = rows.filter(r => r.delta < 0).reduce((s, r) => s + Math.abs(r.delta), 0)
  const maxGainer = rows.reduce((best, r) => r.delta > best.delta ? r : best, rows[0])
  const maxLoser = rows.reduce((worst, r) => r.delta < worst.delta ? r : worst, rows[0])
  return { winners, losers, totalGain, totalLoss, maxGainer, maxLoser }
})

const deltaOption = computed<EChartsOption>(() => {
  if (!impact.value) return {}
  const rows = impact.value.rows
  return {
    ...baseChartOption,
    title: {
      text: `Cambio vs FIFO \u2014 ${currentScenario.value.name}`,
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.06)' } },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const r = rows[p.dataIndex]
        const arrow = r.delta >= 0 ? '\u25b2' : '\u25bc'
        const color = r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red
        return `<b>${r.flag} ${r.country}</b><br><span style="opacity:0.5">FIFO:</span> ${formatNumber(r.fifo_visas)}<br><span style="opacity:0.5">Escenario:</span> ${formatNumber(r.scenario_visas)}<br><span style="color:${color};font-weight:700">${arrow} ${formatDelta(r.delta)} visas</span><br><span style="opacity:0.5">Espera m\u00e1x:</span> ${r.max_wait} a\u00f1os`
      },
    },
    grid: { left: 120, right: 50, top: 48, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map((r: ImpactRow) => r.flag + ' ' + r.country),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    series: [{
      type: 'bar',
      data: rows.map((r: ImpactRow) => ({
        value: r.delta,
        itemStyle: {
          color: {
            type: 'linear',
            x: r.delta >= 0 ? 0 : 1, y: 0,
            x2: r.delta >= 0 ? 1 : 0, y2: 0,
            colorStops: [
              { offset: 0, color: r.delta >= 0 ? CHART_COLORS.green : CHART_COLORS.red },
              { offset: 1, color: r.delta >= 0 ? 'rgba(0,229,160,0.3)' : 'rgba(255,51,102,0.3)' },
            ],
          },
          borderRadius: r.delta >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
        },
      })),
      label: {
        show: true,
        position: 'right',
        color: CHART_COLORS.textMuted,
        fontSize: 9,
        formatter: (p: any) => formatDelta(p.value),
      },
      animationDuration: 800,
      animationDelay: (idx: number) => idx * 40,
    }],
  }
})

const comparisonOption = computed<EChartsOption>(() => {
  if (!impact.value) return {}
  const rows = impact.value.rows
  return {
    ...baseChartOption,
    title: {
      text: 'Visas: FIFO vs Escenario',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(0,60,166,0.04)' } },
    },
    legend: { top: 8, right: 16, textStyle: { color: CHART_COLORS.textMuted }, itemStyle: { borderWidth: 0 } },
    grid: { left: 120, right: 16, top: 56, bottom: 16 },
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map((r: ImpactRow) => r.flag + ' ' + r.country),
      axisLabel: { color: CHART_COLORS.textMuted, fontSize: 10 },
      inverse: true,
    },
    series: [
      {
        name: 'FIFO',
        type: 'bar',
        data: rows.map((r: ImpactRow) => r.fifo_visas),
        itemStyle: { color: CHART_COLORS.red, opacity: 0.5, borderRadius: [0, 2, 2, 0] },
      },
      {
        name: currentScenario.value.name,
        type: 'bar',
        data: rows.map((r: ImpactRow) => r.scenario_visas),
        itemStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: CHART_COLORS.primary },
              { offset: 1, color: CHART_COLORS.primaryLight },
            ],
          },
          borderRadius: [0, 2, 2, 0],
        },
      },
    ],
  }
})

// Wait time vs allocation scatter
const waitScatterOption = computed<EChartsOption>(() => {
  if (!impact.value) return {}
  const rows = impact.value.rows
  return {
    ...baseChartOption,
    title: {
      text: 'Espera M\u00e1xima vs Visas Asignadas',
      textStyle: { color: CHART_COLORS.text, fontSize: 14, fontWeight: 600 },
      left: 'center',
    },
    tooltip: {
      ...baseTooltip,
      trigger: 'item',
      formatter: (p: any) => {
        const d = p.data
        return `<b>${d[3]}</b><br><span style="opacity:0.5">Espera:</span> ${d[0]} a\u00f1os<br><span style="opacity:0.5">Visas:</span> <b>${formatNumber(d[1])}</b><br><span style="opacity:0.5">Delta:</span> <span style="color:${d[2] >= 0 ? CHART_COLORS.green : CHART_COLORS.red}">${formatDelta(d[2])}</span>`
      },
    },
    xAxis: {
      name: 'Espera m\u00e1xima (a\u00f1os)',
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    yAxis: {
      name: 'Visas escenario',
      nameLocation: 'center',
      nameGap: 55,
      nameTextStyle: { color: CHART_COLORS.textMuted },
      axisLabel: { color: CHART_COLORS.textMuted },
      splitLine: { lineStyle: { color: CHART_COLORS.grid, type: 'dashed' } },
    },
    series: [{
      type: 'scatter',
      data: rows.map((r: ImpactRow) => [r.max_wait, r.scenario_visas, r.delta, r.flag + ' ' + r.country]),
      symbolSize: (val: number[]) => Math.max(8, Math.sqrt(Math.abs(val[2])) * 0.8),
      itemStyle: {
        color: (params: any) => params.data[2] >= 0 ? CHART_COLORS.green : CHART_COLORS.red,
        opacity: 0.85,
        borderColor: 'rgba(255,255,255,0.2)',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: { shadowBlur: 14, shadowColor: 'rgba(0,60,166,0.5)', borderColor: '#fff' },
      },
      label: {
        show: true,
        formatter: (p: any) => {
          const name = p.data[3] as string
          return name.length > 8 ? name.slice(0, 8) : name
        },
        position: 'right',
        color: CHART_COLORS.textMuted,
        fontSize: 9,
      },
    }],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Impacto por Pa&iacute;s</h1>

    <!-- Scenario selector -->
    <div class="card">
      <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-3 font-semibold">Escenario a comparar vs FIFO</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="s in scenarios.filter(s => s.id !== 'fifo')"
          :key="s.id"
          class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
          :class="scenario === s.id
            ? 'bg-primary text-white shadow-md shadow-primary/25'
            : 'bg-dark-bg2 text-gray-400 hover:text-white hover:bg-white/5 border border-dark-border'"
          @click="setScenario(s.id)"
        >
          <Icon :name="s.icon" :size="14" />
          {{ s.name }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else-if="impact && stats">
      <!-- Impact KPIs -->
      <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Pa&iacute;ses Beneficiados" :value="stats.winners" :unit="'de 21'" color="text-accent-green" />
        <KpiCard label="Pa&iacute;ses Afectados" :value="stats.losers" :unit="'de 21'" color="text-accent-red" />
        <KpiCard label="Visas Redistribuidas" :value="'+' + formatNumber(stats.totalGain)" color="text-accent-green" />
        <KpiCard label="Mayor Ganador" :value="stats.maxGainer.flag + ' ' + stats.maxGainer.country" :unit="formatDelta(stats.maxGainer.delta) + ' visas'" color="text-accent-yellow" />
      </section>

      <!-- Winners vs Losers summary -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card border-accent-green/20">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 rounded-full bg-accent-green" />
            <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider">Beneficiados</h3>
          </div>
          <div class="space-y-1.5">
            <div
              v-for="r in impact.rows.filter((r: ImpactRow) => r.delta > 0).slice(0, 5)"
              :key="r.country"
              class="flex justify-between items-center text-sm"
            >
              <span class="text-gray-400">{{ r.flag }} {{ r.country }}</span>
              <span class="font-mono text-accent-green font-semibold">{{ formatDelta(r.delta) }}</span>
            </div>
          </div>
        </div>
        <div class="card border-accent-red/20">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-2 h-2 rounded-full bg-accent-red" />
            <h3 class="text-sm font-semibold text-accent-red uppercase tracking-wider">Afectados</h3>
          </div>
          <div class="space-y-1.5">
            <div
              v-for="r in [...impact.rows].filter((r: ImpactRow) => r.delta < 0).sort((a: ImpactRow, b: ImpactRow) => a.delta - b.delta).slice(0, 5)"
              :key="r.country"
              class="flex justify-between items-center text-sm"
            >
              <span class="text-gray-400">{{ r.flag }} {{ r.country }}</span>
              <span class="font-mono text-accent-red font-semibold">{{ formatDelta(r.delta) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <ClientOnly>
        <div class="card">
          <VChart :option="comparisonOption" autoresize class="w-full h-[600px]" />
        </div>
        <div class="card">
          <VChart :option="deltaOption" autoresize class="w-full h-[600px]" />
        </div>
        <div class="card">
          <VChart :option="waitScatterOption" autoresize class="w-full h-[450px]" />
        </div>
      </ClientOnly>

      <!-- Impact table -->
      <details class="card">
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white">Ver tabla completa</summary>
        <div class="mt-4">
          <DataTable
            :headers="['Pa\u00eds', 'FIFO', 'Escenario', 'Delta', 'Espera m\u00e1x.']"
            :rows="impact.rows.map((r: ImpactRow) => [
              r.flag + ' ' + r.country,
              formatNumber(r.fifo_visas),
              formatNumber(r.scenario_visas),
              formatDelta(r.delta),
              r.max_wait + ' a\u00f1os',
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
