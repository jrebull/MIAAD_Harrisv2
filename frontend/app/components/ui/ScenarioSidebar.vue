<script setup lang="ts">
const { scenario, scenarios, currentScenario, selectedRun, setScenario } = useScenario()
const { allocation, loading, fetchAllocation } = useOptimizer()

onMounted(() => {
  fetchAllocation()
})

watch(scenario, () => {
  fetchAllocation()
})

// Scenario accent colors
const scenarioColors: Record<string, { from: string; to: string; ring: string; text: string; bg: string }> = {
  humanitario: { from: 'from-red-500/20', to: 'to-red-500/5', ring: 'ring-red-500/40', text: 'text-red-400', bg: 'bg-red-500' },
  equilibrio: { from: 'from-blue-500/20', to: 'to-blue-500/5', ring: 'ring-blue-500/40', text: 'text-blue-400', bg: 'bg-blue-500' },
  equidad: { from: 'from-emerald-500/20', to: 'to-emerald-500/5', ring: 'ring-emerald-500/40', text: 'text-emerald-400', bg: 'bg-emerald-500' },
  max_utilizacion: { from: 'from-yellow-500/20', to: 'to-yellow-500/5', ring: 'ring-yellow-500/40', text: 'text-yellow-400', bg: 'bg-yellow-500' },
  fifo: { from: 'from-gray-500/20', to: 'to-gray-500/5', ring: 'ring-gray-500/40', text: 'text-gray-400', bg: 'bg-gray-500' },
}

// FIFO baselines for comparison
const FIFO_BASELINE = { f1: 7.2138, f2: 12.6377, f3: 17540 }

// Compute improvement percentages vs FIFO
const improvements = computed(() => {
  if (!allocation.value) return null
  const f = allocation.value.fitness
  return {
    f1: ((FIFO_BASELINE.f1 - f.f1) / FIFO_BASELINE.f1 * 100),
    f2: ((FIFO_BASELINE.f2 - f.f2) / FIFO_BASELINE.f2 * 100),
    f3: ((FIFO_BASELINE.f3 - f.f3) / FIFO_BASELINE.f3 * 100),
  }
})

// Mini fitness bar widths (normalized to FIFO baseline)
function fitnessBarWidth(val: number, fifoVal: number): number {
  return Math.min(100, Math.max(5, (val / fifoVal) * 100))
}
</script>

<template>
  <aside class="w-72 shrink-0 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto
                 bg-gradient-to-b from-dark-bg2 via-[#0c0c1e] to-dark-bg1 border-r border-dark-border/50 space-y-0">

    <!-- ===== LOGO ACCENT BAR ===== -->
    <div class="relative px-5 pt-5 pb-4">
      <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-primary/40 via-accent-green/20 to-transparent" />
      <div class="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full blur-2xl pointer-events-none" />
      <div class="flex items-center gap-2 relative">
        <div class="w-2 h-8 rounded-full bg-gradient-to-b from-primary to-accent-green" />
        <div>
          <h3 class="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em]">Panel de Control</h3>
          <p class="text-[9px] text-gray-600 font-mono">MOHHO Optimizer v2.0</p>
        </div>
      </div>
    </div>

    <!-- ===== SCENARIO SELECTOR ===== -->
    <div class="px-4 pb-4">
      <h3 class="text-[9px] font-bold text-gray-600 uppercase tracking-[0.15em] mb-2 px-1">Escenario Activo</h3>
      <div class="space-y-1">
        <button
          v-for="s in scenarios"
          :key="s.id"
          class="w-full text-left px-3 py-2 rounded-xl text-sm transition-all duration-300 flex items-start gap-2.5 group relative overflow-hidden"
          :class="scenario === s.id
            ? `bg-gradient-to-r ${scenarioColors[s.id]?.from} ${scenarioColors[s.id]?.to} text-white border border-white/10 shadow-lg`
            : 'text-gray-500 hover:text-white hover:bg-white/[0.03] border border-transparent'"
          @click="setScenario(s.id)"
        >
          <!-- Active indicator dot -->
          <div
            class="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 transition-all duration-300"
            :class="scenario === s.id
              ? `${scenarioColors[s.id]?.bg} shadow-[0_0_8px_rgba(255,255,255,0.3)] animate-pulse`
              : 'bg-gray-700 group-hover:bg-gray-500'"
          />
          <div class="min-w-0">
            <span class="font-semibold text-xs block leading-tight">{{ s.name }}</span>
            <span class="block text-[9px] text-gray-500 leading-tight mt-0.5">{{ s.description }}</span>
          </div>
          <!-- Active arrow -->
          <div
            v-if="scenario === s.id"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-[8px] opacity-40"
          >&rsaquo;</div>
        </button>
      </div>
    </div>

    <!-- ===== DIVIDER ===== -->
    <div class="mx-4 h-px bg-gradient-to-r from-transparent via-dark-border to-transparent" />

    <!-- ===== ACTIVE SCENARIO METRICS ===== -->
    <div v-if="allocation && !loading" class="px-4 py-4 space-y-3">
      <!-- Scenario badge header -->
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-lg flex items-center justify-center bg-white/[0.06]">
          <Icon :name="currentScenario.icon" :size="13" :class="scenarioColors[scenario]?.text" />
        </div>
        <div>
          <h3 class="text-xs font-bold" :class="scenarioColors[scenario]?.text">{{ currentScenario.name }}</h3>
          <p class="text-[9px] text-gray-600">M&eacute;tricas en tiempo real</p>
        </div>
      </div>

      <!-- VISA GAUGE -->
      <div class="bg-white/[0.03] rounded-xl px-3 py-3 border border-white/[0.04] relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-accent-green/20 via-transparent to-transparent" />
        <div class="flex items-baseline justify-between mb-1.5">
          <p class="text-[9px] text-gray-500 uppercase tracking-wider font-bold">Visas Otorgadas</p>
          <span
            class="text-[9px] font-bold font-mono px-1.5 py-0.5 rounded"
            :class="allocation.utilization >= 99 ? 'bg-emerald-500/15 text-emerald-400' : allocation.utilization >= 90 ? 'bg-yellow-500/15 text-yellow-400' : 'bg-red-500/15 text-red-400'"
          >{{ allocation.utilization }}%</span>
        </div>
        <p class="text-xl font-black font-mono text-white leading-tight">
          {{ allocation.visas_used.toLocaleString() }}
        </p>
        <p class="text-[9px] text-gray-600 font-mono mb-2">de 140,000</p>
        <!-- Progress bar with tick marks -->
        <div class="h-2 bg-white/[0.05] rounded-full overflow-hidden relative">
          <div class="absolute inset-0" style="background-image: repeating-linear-gradient(90deg, transparent, transparent 19.8%, rgba(255,255,255,0.04) 20%, rgba(255,255,255,0.04) 20.2%)" />
          <div
            class="h-full rounded-full transition-all duration-700 relative"
            :class="allocation.utilization >= 99 ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' : allocation.utilization >= 90 ? 'bg-gradient-to-r from-yellow-600 to-yellow-400' : 'bg-gradient-to-r from-red-600 to-red-400'"
            :style="{ width: allocation.utilization + '%' }"
          >
            <div class="absolute inset-0 bg-gradient-to-t from-transparent to-white/15 rounded-full" />
          </div>
        </div>
      </div>

      <!-- FITNESS METRICS with mini bars -->
      <div class="space-y-2">
        <!-- f1 -->
        <div class="bg-white/[0.03] rounded-xl px-3 py-2.5 border border-white/[0.04] relative overflow-hidden">
          <div class="flex items-baseline justify-between">
            <p class="text-[9px] text-gray-500 uppercase tracking-wider font-bold">f&#8321; Espera</p>
            <span
              v-if="improvements && scenario !== 'fifo'"
              class="text-[9px] font-mono font-bold"
              :class="improvements.f1 > 0 ? 'text-emerald-400' : 'text-red-400'"
            >{{ improvements.f1 > 0 ? '-' : '+' }}{{ Math.abs(improvements.f1).toFixed(1) }}%</span>
          </div>
          <p class="text-lg font-bold font-mono text-accent-yellow leading-tight">
            {{ allocation.fitness.f1.toFixed(2) }}
            <span class="text-[9px] text-gray-600 font-normal">a&ntilde;os</span>
          </p>
          <div class="mt-1.5 h-1 bg-white/[0.05] rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-accent-yellow/60 to-accent-yellow rounded-full transition-all duration-500"
              :style="{ width: fitnessBarWidth(allocation.fitness.f1, FIFO_BASELINE.f1) + '%' }"
            />
          </div>
          <p class="text-[8px] text-gray-700 mt-0.5 font-mono">FIFO: {{ FIFO_BASELINE.f1.toFixed(2) }}</p>
        </div>

        <!-- f2 -->
        <div class="bg-white/[0.03] rounded-xl px-3 py-2.5 border border-white/[0.04] relative overflow-hidden">
          <div class="flex items-baseline justify-between">
            <p class="text-[9px] text-gray-500 uppercase tracking-wider font-bold">f&#8322; Disparidad</p>
            <span
              v-if="improvements && scenario !== 'fifo'"
              class="text-[9px] font-mono font-bold"
              :class="improvements.f2 > 0 ? 'text-emerald-400' : 'text-red-400'"
            >{{ improvements.f2 > 0 ? '-' : '+' }}{{ Math.abs(improvements.f2).toFixed(1) }}%</span>
          </div>
          <p class="text-lg font-bold font-mono text-accent-green leading-tight">
            {{ allocation.fitness.f2.toFixed(2) }}
            <span class="text-[9px] text-gray-600 font-normal">a&ntilde;os</span>
          </p>
          <div class="mt-1.5 h-1 bg-white/[0.05] rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-accent-green/60 to-accent-green rounded-full transition-all duration-500"
              :style="{ width: fitnessBarWidth(allocation.fitness.f2, FIFO_BASELINE.f2) + '%' }"
            />
          </div>
          <p class="text-[8px] text-gray-700 mt-0.5 font-mono">FIFO: {{ FIFO_BASELINE.f2.toFixed(2) }}</p>
        </div>

        <!-- f3 -->
        <div class="bg-white/[0.03] rounded-xl px-3 py-2.5 border border-white/[0.04] relative overflow-hidden">
          <div class="flex items-baseline justify-between">
            <p class="text-[9px] text-gray-500 uppercase tracking-wider font-bold">f&#8323; Desperdicio</p>
            <span
              v-if="improvements && scenario !== 'fifo'"
              class="text-[9px] font-mono font-bold"
              :class="improvements.f3 > 0 ? 'text-emerald-400' : 'text-red-400'"
            >{{ improvements.f3 > 0 ? '-' : '+' }}{{ Math.abs(improvements.f3).toFixed(1) }}%</span>
          </div>
          <p class="text-lg font-bold font-mono text-accent-blue leading-tight">
            {{ allocation.fitness.f3.toLocaleString() }}
            <span class="text-[9px] text-gray-600 font-normal">visas</span>
          </p>
          <div class="mt-1.5 h-1 bg-white/[0.05] rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-blue-500/60 to-blue-400 rounded-full transition-all duration-500"
              :style="{ width: fitnessBarWidth(allocation.fitness.f3, FIFO_BASELINE.f3) + '%' }"
            />
          </div>
          <p class="text-[8px] text-gray-700 mt-0.5 font-mono">FIFO: {{ FIFO_BASELINE.f3.toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="flex flex-col items-center justify-center py-12 gap-3">
      <div class="relative">
        <div class="w-10 h-10 border-2 border-primary/30 rounded-full" />
        <div class="absolute inset-0 w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
      <p class="text-[10px] text-gray-600 animate-pulse">Calculando...</p>
    </div>

    <!-- ===== DIVIDER ===== -->
    <div class="mx-4 h-px bg-gradient-to-r from-transparent via-dark-border to-transparent" />

    <!-- ===== RUN SELECTOR ===== -->
    <div class="px-4 py-4">
      <h3 class="text-[9px] font-bold text-gray-600 uppercase tracking-[0.15em] mb-2 px-1">Corrida MOHHO</h3>
      <div class="relative">
        <select
          v-model.number="selectedRun"
          class="w-full appearance-none bg-white/[0.03] border border-white/[0.06] rounded-xl px-3 py-2.5 text-xs text-white font-mono
                 focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/20 transition-all cursor-pointer
                 hover:bg-white/[0.05]"
        >
          <option v-for="i in 30" :key="i - 1" :value="i - 1" class="bg-dark-bg2 text-white">
            Run #{{ String(i - 1).padStart(2, '0') }} &middot; seed={{ 42 + i - 1 }}
          </option>
        </select>
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-600 text-[10px]">&#9662;</div>
      </div>
    </div>

    <!-- ===== FOOTER STATUS ===== -->
    <div class="mt-auto px-4 py-4">
      <div class="mx-auto h-px bg-gradient-to-r from-transparent via-dark-border to-transparent mb-3" />
      <div class="flex items-center gap-2 px-1">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_6px_rgba(0,229,160,0.4)]" />
        <p class="text-[9px] text-gray-600 font-mono">30 runs &middot; 500 iter &middot; 406 soluciones</p>
      </div>
    </div>
  </aside>
</template>
