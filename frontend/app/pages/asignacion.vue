<script setup lang="ts">
const { scenario } = useScenario()
const { allocation, loading, fetchAllocation } = useOptimizer()

const categories = ['EB-1', 'EB-2', 'EB-3', 'EB-4', 'EB-5']

onMounted(() => {
  fetchAllocation()
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Asignación de Visas</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else-if="allocation">
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
            :title="'Asignación: ' + scenario"
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
            :headers="['País', ...categories, 'Total']"
            :rows="allocation.rows.map(r => [
              r.flag + ' ' + r.country,
              ...categories.map(c => r.categories[c]?.toLocaleString() || '0'),
              r.total.toLocaleString()
            ])"
          />
        </div>
      </details>
    </template>
  </div>
</template>
