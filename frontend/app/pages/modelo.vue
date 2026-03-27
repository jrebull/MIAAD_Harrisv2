<script setup lang="ts">
definePageMeta({ prerender: true })
</script>

<template>
  <div class="space-y-8">
    <h1 class="section-title">Modelo Matemático</h1>
    <p class="text-gray-400 max-w-3xl">
      Imagina un hospital con cientos de pacientes en espera. El modelo decide cuántas "citas" (visas)
      se asignan a cada grupo, balanceando urgencia, equidad y eficiencia.
    </p>

    <!-- Decision variable -->
    <section class="card">
      <h2 class="text-lg font-bold text-white mb-3">Variable de Decisión</h2>
      <div class="bg-dark-bg1 rounded-lg p-4 font-mono text-sm">
        <p class="text-accent-yellow">x = (x₁, x₂, ..., x₁₀₅)</p>
        <p class="text-gray-500 mt-1">xᵍ ∈ ℤ⁺₀ — visas asignadas al grupo g</p>
        <p class="text-gray-500">G = 21 países × 5 categorías = 105 grupos</p>
      </div>
    </section>

    <!-- Three objectives -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card border-accent-yellow/20">
        <h3 class="text-accent-yellow font-bold text-lg mb-2">f₁ — Carga de Espera</h3>
        <div class="bg-dark-bg1 rounded-lg p-3 font-mono text-xs mb-3">
          f₁(x) = Σᵍ (nᵍ - xᵍ) · wᵍ / Σᵍ nᵍ
        </div>
        <p class="text-xs text-gray-400">
          Media ponderada de años de espera para los no atendidos.
          <strong>Minimizar</strong> prioriza a quienes más han esperado.
        </p>
      </div>
      <div class="card border-accent-green/20">
        <h3 class="text-accent-green font-bold text-lg mb-2">f₂ — Disparidad</h3>
        <div class="bg-dark-bg1 rounded-lg p-3 font-mono text-xs mb-3">
          <p>W̄c = Σ xᵍ·wᵍ / Σ xᵍ</p>
          <p>f₂(x) = max |W̄c₁ - W̄c₂|</p>
        </div>
        <p class="text-xs text-gray-400">
          Brecha máxima de espera promedio entre dos países cualesquiera.
          <strong>Minimizar</strong> busca equidad entre naciones.
        </p>
      </div>
      <div class="card border-accent-blue/20">
        <h3 class="text-accent-blue font-bold text-lg mb-2">f₃ — Desperdicio</h3>
        <div class="bg-dark-bg1 rounded-lg p-3 font-mono text-xs mb-3">
          f₃(x) = V - Σᵍ xᵍ
        </div>
        <p class="text-xs text-gray-400">
          Visas no utilizadas. La interacción de topes por país y categoría
          genera desperdicio. <strong>Minimizar</strong> maximiza aprovechamiento.
        </p>
      </div>
    </section>

    <!-- Constraints -->
    <section class="card">
      <h2 class="text-lg font-bold text-white mb-4">Restricciones</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R1: Σᵍ xᵍ ≤ V</p>
          <p class="text-xs text-gray-500 mt-1">No exceder 140,000 visas totales</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R2: xᵍ ≤ nᵍ</p>
          <p class="text-xs text-gray-500 mt-1">No asignar más de lo demandado</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R3: Σ xᵍ|c ≤ Pc</p>
          <p class="text-xs text-gray-500 mt-1">Tope por país: 25,620 (7%)</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R4: Σ xᵍ|j ≤ Kj,eff</p>
          <p class="text-xs text-gray-500 mt-1">Tope por categoría (con spillover)</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R5: xᵍ ≥ 0</p>
          <p class="text-xs text-gray-500 mt-1">No negativo</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3">
          <p class="text-accent-yellow font-mono text-sm">R6: xᵍ ∈ ℤ</p>
          <p class="text-xs text-gray-500 mt-1">Enteros (una visa es indivisible)</p>
        </div>
      </div>
    </section>

    <!-- Spillover -->
    <section class="card">
      <h2 class="text-lg font-bold text-white mb-3">Spillover (Cascada)</h2>
      <p class="text-sm text-gray-400 mb-4">
        Cuando una categoría no usa su cuota completa, las visas sobrantes fluyen
        a otra categoría:
      </p>
      <div class="flex flex-wrap items-center gap-2 text-sm font-mono">
        <span class="bg-accent-red/20 text-accent-red px-3 py-1 rounded">EB-4/5</span>
        <span class="text-gray-500">→</span>
        <span class="bg-accent-yellow/20 text-accent-yellow px-3 py-1 rounded">EB-1</span>
        <span class="text-gray-500">→</span>
        <span class="bg-accent-green/20 text-accent-green px-3 py-1 rounded">EB-2</span>
        <span class="text-gray-500">→</span>
        <span class="bg-accent-blue/20 text-accent-blue px-3 py-1 rounded">EB-3</span>
      </div>
    </section>

    <!-- 3-layer encoding -->
    <section class="card">
      <h2 class="text-lg font-bold text-white mb-3">Codificación en 3 Capas</h2>
      <div class="space-y-3">
        <div class="flex items-start gap-3">
          <span class="bg-primary/20 text-primary-300 px-2 py-0.5 rounded text-xs font-bold">1</span>
          <div>
            <p class="text-sm text-white font-medium">Continuo → Halcón H ∈ ℝ¹⁰⁵</p>
            <p class="text-xs text-gray-500">Cada dimensión ∈ [0, 1]</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <span class="bg-primary/20 text-primary-300 px-2 py-0.5 rounded text-xs font-bold">2</span>
          <div>
            <p class="text-sm text-white font-medium">SPV → Permutación π = argsort(H)</p>
            <p class="text-xs text-gray-500">Prioridad basada en valores más pequeños</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <span class="bg-primary/20 text-primary-300 px-2 py-0.5 rounded text-xs font-bold">3</span>
          <div>
            <p class="text-sm text-white font-medium">Greedy Decoder → Asignación x ∈ ℤ¹⁰⁵</p>
            <p class="text-xs text-gray-500">Siempre factible, respeta R1-R6</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
