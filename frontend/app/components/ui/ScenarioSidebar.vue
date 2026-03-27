<script setup lang="ts">
const { scenario, scenarios, currentScenario, selectedRun, setScenario } = useScenario()
const { allocation, loading, fetchAllocation } = useOptimizer()

onMounted(() => {
  fetchAllocation()
})

watch(scenario, () => {
  fetchAllocation()
})
</script>

<template>
  <aside class="w-72 shrink-0 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto
                 bg-gradient-to-b from-dark-bg2 to-dark-bg1 border-r border-dark-border p-5 space-y-6">
    <!-- Scenario selector -->
    <div>
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Escenario</h3>
      <div class="space-y-1.5">
        <button
          v-for="s in scenarios"
          :key="s.id"
          class="w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-start gap-2.5"
          :class="scenario === s.id
            ? 'bg-primary/20 text-white border border-primary/40'
            : 'text-gray-400 hover:text-white hover:bg-white/5'"
          @click="setScenario(s.id)"
        >
          <Icon :name="s.icon" :size="16" class="mt-0.5 shrink-0 opacity-80" />
          <div>
            <span class="font-medium">{{ s.name }}</span>
            <span class="block text-[10px] text-gray-500">{{ s.description }}</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Active scenario metrics -->
    <div v-if="allocation && !loading">
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
        <Icon :name="currentScenario.icon" :size="14" />
        {{ currentScenario.name }}
      </h3>
      <div class="space-y-2">
        <div class="bg-white/[0.04] rounded-lg px-3 py-2.5">
          <p class="text-[10px] text-gray-500 uppercase">Visas otorgadas</p>
          <p class="text-lg font-bold font-mono text-white">
            {{ allocation.visas_used.toLocaleString() }}
            <span class="text-xs text-gray-500">/ 140,000</span>
          </p>
          <div class="mt-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-accent-yellow to-accent-green rounded-full transition-all duration-500"
              :style="{ width: allocation.utilization + '%' }"
            />
          </div>
          <p class="text-[10px] text-gray-500 mt-0.5">{{ allocation.utilization }}% utilización</p>
        </div>

        <div class="bg-white/[0.04] rounded-lg px-3 py-2.5">
          <p class="text-[10px] text-gray-500 uppercase">f₁ espera</p>
          <p class="text-lg font-bold font-mono text-accent-yellow">
            {{ allocation.fitness.f1.toFixed(3) }}
            <span class="text-xs text-gray-500">años</span>
          </p>
        </div>

        <div class="bg-white/[0.04] rounded-lg px-3 py-2.5">
          <p class="text-[10px] text-gray-500 uppercase">f₂ disparidad</p>
          <p class="text-lg font-bold font-mono text-accent-green">
            {{ allocation.fitness.f2.toFixed(3) }}
            <span class="text-xs text-gray-500">años</span>
          </p>
        </div>

        <div class="bg-white/[0.04] rounded-lg px-3 py-2.5">
          <p class="text-[10px] text-gray-500 uppercase">f₃ desperdicio</p>
          <p class="text-lg font-bold font-mono text-accent-blue">
            {{ allocation.fitness.f3.toLocaleString() }}
            <span class="text-xs text-gray-500">visas</span>
          </p>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="flex justify-center py-8">
      <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <!-- Run selector -->
    <div>
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Corrida</h3>
      <select
        v-model.number="selectedRun"
        class="w-full bg-dark-bg2 border border-dark-border rounded-lg px-3 py-2 text-sm text-white"
      >
        <option v-for="i in 30" :key="i - 1" :value="i - 1">
          #{{ i - 1 }} (seed={{ 42 + i - 1 }})
        </option>
      </select>
    </div>
  </aside>
</template>
