<script setup lang="ts">
defineProps<{
  headers: string[]
  rows: any[][]
  highlightCol?: number
}>()
</script>

<template>
  <div class="overflow-x-auto rounded-lg">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-dark-border bg-white/[0.02]">
          <th
            v-for="(h, i) in headers"
            :key="i"
            class="px-3 py-3 text-left text-[10px] font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
            :class="{ 'bg-primary/10': i === highlightCol }"
          >
            {{ h }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, ri) in rows"
          :key="ri"
          class="border-b border-dark-border/30 hover:bg-white/[0.03] transition-colors"
        >
          <td
            v-for="(cell, ci) in row"
            :key="ci"
            class="px-3 py-2 font-mono text-xs whitespace-nowrap"
            :class="[
              ci === highlightCol ? 'bg-primary/5' : '',
              ci === 0 ? 'text-gray-300 font-medium' : 'text-gray-400',
            ]"
          >
            {{ cell }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
