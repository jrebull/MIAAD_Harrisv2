<script setup lang="ts">
defineProps<{
  headers: string[]
  rows: any[][]
  highlightCol?: number
}>()
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-dark-border">
          <th
            v-for="(h, i) in headers"
            :key="i"
            class="px-3 py-2.5 text-left text-[10px] font-semibold text-gray-500 uppercase tracking-wider"
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
          class="border-b border-dark-border/50 hover:bg-white/[0.02] transition-colors"
        >
          <td
            v-for="(cell, ci) in row"
            :key="ci"
            class="px-3 py-2 font-mono text-xs"
            :class="{ 'bg-primary/5': ci === highlightCol }"
          >
            {{ cell }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
