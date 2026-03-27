<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  unit?: string
  color?: string
}>()
</script>

<template>
  <div class="metric-card">
    <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{{ label }}</p>
    <p class="hero-number text-3xl" :class="color">{{ value }}</p>
    <p v-if="unit" class="text-xs text-gray-500 mt-1">{{ unit }}</p>
  </div>
</template>
