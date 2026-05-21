<script setup lang="ts">
defineProps<{ error: string | null }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <div v-if="error" class="card border-accent-red/30 bg-accent-red/[0.04]">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-lg bg-accent-red/15 flex items-center justify-center shrink-0">
        <Icon name="alert-triangle" :size="18" class="text-accent-red" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-bold text-accent-red">No se pudieron cargar los datos</p>
        <p class="text-xs text-gray-400 truncate">{{ error }}</p>
        <p class="text-[10px] text-gray-500 mt-0.5">
          El servidor puede estar iniciando — en Render (plan gratuito) la primera carga tarda ~30 s.
        </p>
      </div>
      <button
        class="btn-secondary text-xs shrink-0"
        @click="$emit('retry')"
      >
        Reintentar
      </button>
    </div>
  </div>
</template>
