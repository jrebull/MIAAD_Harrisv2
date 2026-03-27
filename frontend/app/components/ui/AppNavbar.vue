<script setup lang="ts">
const route = useRoute()

const tabs = [
  { path: '/', label: 'El Problema', icon: 'chart-bar' },
  { path: '/modelo', label: 'Modelo', icon: 'sigma' },
  { path: '/pareto', label: 'Pareto', icon: 'target' },
  { path: '/asignacion', label: 'Asignación', icon: 'grid' },
  { path: '/impacto', label: 'Impacto', icon: 'globe' },
  { path: '/convergencia', label: 'Convergencia', icon: 'trending-up' },
  { path: '/simulacion', label: 'Simulación', icon: 'hawk' },
  { path: '/datos', label: 'Datos', icon: 'database' },
]
</script>

<template>
  <header class="sticky top-0 z-50 bg-dark-bg1/80 backdrop-blur-xl border-b border-dark-border">
    <div class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <NuxtLink to="/" class="flex items-center gap-3 group">
          <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-accent-green flex items-center justify-center">
            <Icon name="hawk" :size="20" class="text-white" />
          </div>
          <div>
            <h1 class="text-lg font-bold text-white leading-tight group-hover:text-accent-yellow transition-colors">VISA PREDICT AI</h1>
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
            <Icon :name="tab.icon" :size="15" class="mr-1.5 opacity-70" />
            {{ tab.label }}
          </NuxtLink>
        </nav>
      </div>
    </div>
  </header>
</template>
