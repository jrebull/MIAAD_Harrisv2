<script setup lang="ts">
const props = defineProps<{
  name: string
  size?: number
}>()

const s = computed(() => props.size || 18)
</script>

<template>
  <svg
    :width="s" :height="s" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" stroke-width="1.8"
    stroke-linecap="round" stroke-linejoin="round"
    class="inline-block shrink-0"
  >
    <!-- Navigation / General -->
    <template v-if="name === 'chart-bar'">
      <rect x="3" y="12" width="4" height="9" rx="1" fill="currentColor" opacity="0.3" />
      <rect x="10" y="7" width="4" height="14" rx="1" fill="currentColor" opacity="0.5" />
      <rect x="17" y="3" width="4" height="18" rx="1" fill="currentColor" opacity="0.7" />
    </template>

    <template v-else-if="name === 'sigma'">
      <path d="M18 4H7l5 8-5 8h11" />
    </template>

    <template v-else-if="name === 'target'">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" fill="currentColor" />
    </template>

    <template v-else-if="name === 'grid'">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </template>

    <template v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </template>

    <template v-else-if="name === 'trending-up'">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
      <polyline points="16 7 22 7 22 13" />
    </template>

    <template v-else-if="name === 'database'">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
    </template>

    <template v-else-if="name === 'list'">
      <line x1="8" y1="6" x2="21" y2="6" />
      <line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <circle cx="4" cy="6" r="1" fill="currentColor" />
      <circle cx="4" cy="12" r="1" fill="currentColor" />
      <circle cx="4" cy="18" r="1" fill="currentColor" />
    </template>

    <!-- Scenarios -->
    <template v-else-if="name === 'heart'">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </template>

    <template v-else-if="name === 'scale'">
      <path d="M12 3v18" />
      <path d="M4 7l8-4 8 4" />
      <path d="M4 7l-1 7h6l-1-7" />
      <path d="M20 7l-1 7h6l-1-7" transform="translate(-4,0)" />
    </template>

    <template v-else-if="name === 'handshake'">
      <path d="M11 17l-2 2-4-4 4.5-4.5" />
      <path d="M13 17l2 2 4-4-4.5-4.5" />
      <path d="M3 11l4-4 4 4" />
      <path d="M21 11l-4-4-4 4" />
    </template>

    <template v-else-if="name === 'zap'">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="currentColor" opacity="0.15" />
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </template>

    <!-- Hawk -->
    <template v-else-if="name === 'hawk'">
      <path d="M22 4c-1 3-3.5 5.5-7 7l-2 1-1 4-3-1 1-3-5-2 1-3 4 1 1-2c1.5-3.5 4-6 7-7z" fill="currentColor" opacity="0.15" />
      <path d="M22 4c-1 3-3.5 5.5-7 7l-2 1-1 4-3-1 1-3-5-2 1-3 4 1 1-2c1.5-3.5 4-6 7-7z" />
      <path d="M2 21l7-7" />
      <path d="M9 14l-2 5 5-2" />
    </template>

    <!-- Rabbit -->
    <template v-else-if="name === 'rabbit'">
      <path d="M13 16V6a3 3 0 0 0-6 0v1" />
      <path d="M18 10c0-3-2-5-4-6" />
      <path d="M6 10c0-3 2-5 4-6" />
      <circle cx="12" cy="17" r="5" />
      <circle cx="10" cy="16" r="1" fill="currentColor" />
      <circle cx="14" cy="16" r="1" fill="currentColor" />
      <path d="M10 20h4" />
    </template>

    <!-- Fallback circle -->
    <template v-else>
      <circle cx="12" cy="12" r="10" />
    </template>
  </svg>
</template>
