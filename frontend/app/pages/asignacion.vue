<script setup lang="ts">
import { formatNumber } from '~/utils/formatters'

const { scenario, scenarios, setScenario, currentScenario } = useScenario()
const { allocation, loading, fetchAllocation } = useOptimizer()

const categories = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

onMounted(() => {
  fetchAllocation()
})

watch(scenario, () => {
  fetchAllocation()
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Asignaci&oacute;n de Visas</h1>

    <!-- Scenario selector -->
    <div class="card">
      <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-3 font-semibold">Seleccionar escenario</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="s in scenarios"
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
      <p class="text-xs text-gray-500 mt-2">
        <Icon :name="currentScenario.icon" :size="12" class="inline" />
        {{ currentScenario.description }}
      </p>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else-if="allocation">
      <!-- Fitness + utilization KPIs -->
      <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Visas Asignadas" :value="formatNumber(allocation.visas_used)" unit="de 140,000" color="text-accent-green" />
        <KpiCard label="Utilizaci&oacute;n" :value="allocation.utilization + '%'" color="text-accent-yellow" />
        <KpiCard label="f&#8321; espera" :value="allocation.fitness.f1.toFixed(3)" unit="a&ntilde;os" />
        <KpiCard label="f&#8322; brecha" :value="allocation.fitness.f2.toFixed(3)" unit="a&ntilde;os" />
      </section>

      <!-- Utilization bar -->
      <div class="card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm text-gray-400">
            Utilizando <span class="text-white font-bold">{{ allocation.visas_used.toLocaleString() }}</span>
            de 140,000 visas
          </p>
          <span class="text-accent-green font-mono font-bold">{{ allocation.utilization }}%</span>
        </div>
        <div class="h-3 bg-white/10 rounded-full overflow-hidden">
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
              ...categories.map(c => (r.categories[c] || 0).toLocaleString()),
              r.total.toLocaleString()
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
