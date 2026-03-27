<script setup lang="ts">
import type { GroupsData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

const { fetchGroups } = useOptimizer()
const groups = ref<GroupsData | null>(null)

onMounted(async () => {
  groups.value = await fetchGroups()
})

function sourceTag(source: string) {
  if (source === 'REAL') return 'tag-real'
  if (source === 'EST') return 'tag-est'
  return 'tag-calc'
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="section-title">Datos y Fuentes</h1>

    <div v-if="!groups" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else>
      <!-- Summary -->
      <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Total Demanda" :value="formatNumber(groups.total_demand)" unit="peticiones" />
        <KpiCard label="Total Visas" :value="formatNumber(groups.total_visas)" unit="por año" />
        <KpiCard label="Países" :value="groups.countries.length" />
        <KpiCard label="Grupos" :value="groups.groups.length" unit="(21 × 5)" />
      </section>

      <!-- Source legend -->
      <div class="card flex gap-4 items-center">
        <span class="text-xs text-gray-500 uppercase">Fuentes:</span>
        <span class="tag tag-real">REAL — USCIS oficial</span>
        <span class="tag tag-est">EST — DHS Yearbook estimado</span>
        <span class="tag tag-calc">EST-DEM — Demanda estimada</span>
      </div>

      <!-- Data table -->
      <div class="card overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-dark-border">
              <th class="px-2 py-2 text-left text-gray-500">País</th>
              <th class="px-2 py-2 text-left text-gray-500">Cat.</th>
              <th class="px-2 py-2 text-right text-gray-500">Demanda</th>
              <th class="px-2 py-2 text-center text-gray-500">Fuente</th>
              <th class="px-2 py-2 text-center text-gray-500">Fecha Prior.</th>
              <th class="px-2 py-2 text-right text-gray-500">Espera</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="g in groups.groups"
              :key="g.index"
              class="border-b border-dark-border/50 hover:bg-white/[0.02]"
            >
              <td class="px-2 py-1.5 text-gray-300">
                {{ groups.flags[g.country] || '' }} {{ g.country }}
              </td>
              <td class="px-2 py-1.5 font-mono text-gray-400">{{ g.category }}</td>
              <td class="px-2 py-1.5 font-mono text-right text-white">{{ formatNumber(g.n) }}</td>
              <td class="px-2 py-1.5 text-center">
                <span class="tag" :class="sourceTag(g.source)">{{ g.source }}</span>
              </td>
              <td class="px-2 py-1.5 font-mono text-center text-gray-400">{{ g.d }}</td>
              <td class="px-2 py-1.5 font-mono text-right" :class="g.w > 5 ? 'text-accent-red' : 'text-gray-400'">
                {{ g.w }} años
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Sources detail -->
      <section class="card space-y-3">
        <h3 class="text-sm font-bold text-white uppercase tracking-wider">Fuentes de Datos</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-green font-bold">USCIS FY2025 Q2</p>
            <p class="text-gray-500 mt-1">Approved I-140/I-360/I-526 Petitions Awaiting Visa (India, China, Philippines, Mexico)</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-bold">Visa Bulletin April 2026</p>
            <p class="text-gray-500 mt-1">Final Action Dates for Employment-Based Preference Cases — Dept. of State</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-blue font-bold">DHS Yearbook FY2023</p>
            <p class="text-gray-500 mt-1">Immigration shares by country for 16 estimated blocs from "All Other"</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-white font-bold">Spillover Rules</p>
            <p class="text-gray-500 mt-1">INA Section 203(b) — Cascade: EB-4/5 → EB-1 → EB-2 → EB-3</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
