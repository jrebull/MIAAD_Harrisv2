<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  unit?: string
  color?: string
}>()
</script>

<template>
  <div class="metric-card group">
    <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1.5 font-semibold">{{ label }}</p>
    <p class="hero-number text-2xl md:text-3xl" :class="color">{{ value }}</p>
    <p v-if="unit" class="text-[11px] text-gray-500 mt-1.5 font-mono">{{ unit }}</p>
  </div>
</template>
