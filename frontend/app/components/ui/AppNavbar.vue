<script setup lang="ts">
const route = useRoute()

const tabs = [
  { path: '/', label: 'El Problema', icon: '📊' },
  { path: '/modelo', label: 'Modelo', icon: '📐' },
  { path: '/pareto', label: 'Pareto', icon: '🎯' },
  { path: '/asignacion', label: 'Asignación', icon: '📋' },
  { path: '/impacto', label: 'Impacto', icon: '🌍' },
  { path: '/convergencia', label: 'Convergencia', icon: '📈' },
  { path: '/simulacion', label: 'Simulación', icon: '🦅' },
  { path: '/datos', label: 'Datos', icon: '🗄️' },
]
</script>

<template>
  <header class="sticky top-0 z-50 bg-dark-bg1/80 backdrop-blur-xl border-b border-dark-border">
    <div class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <NuxtLink to="/" class="flex items-center gap-3">
          <span class="text-2xl">🦅</span>
          <div>
            <h1 class="text-lg font-bold text-white leading-tight">VISA PREDICT AI</h1>
            <p class="text-[10px] text-gray-500 tracking-widest uppercase">MOHHO Optimizer v2.0</p>
          </div>
        </NuxtLink>

        <nav class="hidden md:flex items-center gap-1">
          <NuxtLink
            v-for="tab in tabs"
            :key="tab.path"
            :to="tab.path"
            class="nav-tab"
            :class="{ 'nav-tab-active': route.path === tab.path }"
          >
            <span class="mr-1.5">{{ tab.icon }}</span>
            {{ tab.label }}
          </NuxtLink>
        </nav>
      </div>
    </div>
  </header>
</template>
