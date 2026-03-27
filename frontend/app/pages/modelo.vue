<script setup lang="ts">
definePageMeta({ prerender: true })
</script>

<template>
  <div class="space-y-8 max-w-5xl mx-auto">
    <h1 class="section-title">Modelo Matemático</h1>

    <!-- ========================== -->
    <!-- 1. DEFINICIÓN DEL PROBLEMA -->
    <!-- ========================== -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">1. Definición Formal del Problema de Optimización</h2>
      <p class="text-sm text-gray-400 leading-relaxed">
        El gobierno de EE.UU. dispone cada año fiscal de <strong class="text-accent-yellow">V = 140,000 visas</strong>
        de empleo (EB) que deben distribuirse entre <strong class="text-white">G = 105 grupos</strong>
        (21 países × 5 categorías EB). El problema consiste en encontrar una asignación
        que minimice simultáneamente tres objetivos en conflicto, sujeta a restricciones legales.
      </p>

      <!-- Variable de decisión -->
      <div>
        <h3 class="text-sm font-semibold text-accent-yellow uppercase tracking-wider mb-2">Variable de Decisi��n</h3>
        <div class="bg-dark-bg1 rounded-lg p-4 font-mono text-sm space-y-2">
          <p class="text-accent-yellow text-base">x = (x₁, x₂, ..., x₁₀₅) ∈ ℤ₊¹⁰⁵</p>
          <p class="text-gray-400">donde xᵍ = número de visas asignadas al grupo g</p>
          <p class="text-gray-500 text-xs">
            Cada grupo g corresponde a un par único (país c, categoría j), e.g. g₁ = (India, EB-1), g₂ = (India, EB-2), ...
          </p>
        </div>
      </div>

      <!-- Parámetros -->
      <div>
        <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider mb-2">Parámetros del Problema</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">V = 140,000</span>
            <span class="text-gray-500 ml-2">— Total de visas EB disponibles</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">Pc = 25,620</span>
            <span class="text-gray-500 ml-2">— Tope por país (7% de V)</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">nᵍ ∈ ℤ₊</span>
            <span class="text-gray-500 ml-2">— Demanda (peticiones aprobadas) del grupo g</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">wᵍ ∈ ℝ₊</span>
            <span class="text-gray-500 ml-2">— Años de espera del grupo g</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">d�� ∈ ℤ</span>
            <span class="text-gray-500 ml-2">— Fecha de prioridad del grupo g</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">Kⱼ,eff</span>
            <span class="text-gray-500 ml-2">— Tope efectivo por categoría j (con spillover)</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================== -->
    <!-- 2. FORMULACIÓN MATEMÁTICA      -->
    <!-- ============================== -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">2. Formulación Matemática</h2>

      <div class="bg-dark-bg1 rounded-lg p-4 font-mono text-sm text-center">
        <p class="text-accent-yellow text-base mb-2">min F(x) = ( f₁(x), f₂(x), f₃(x) )</p>
        <p class="text-gray-500 text-xs">sujeto a R1–R6</p>
      </div>

      <!-- Tres objetivos -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
          <h3 class="text-accent-yellow font-bold mb-2">f₁ — Carga de Espera</h3>
          <div class="font-mono text-xs mb-3 space-y-1">
            <p class="text-white">f₁(x) = Σᵍ (nᵍ - xᵍ) · wᵍ / Σᵍ nᵍ</p>
          </div>
          <p class="text-xs text-gray-400 leading-relaxed">
            Media ponderada de años de espera para las personas que <strong class="text-white">no</strong> reciben visa.
            Los grupos con mayor espera (wᵍ) contribuyen más al costo.
            <strong class="text-accent-yellow">Minimizar → priorizar a quienes más han esperado.</strong>
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
          <h3 class="text-accent-green font-bold mb-2">f₂ — Disparidad</h3>
          <div class="font-mono text-xs mb-3 space-y-1">
            <p class="text-gray-400">Sea W̄c = Σ{g∈c} xᵍ·wᵍ / Σ{g∈c} xᵍ</p>
            <p class="text-white">f₂(x) = max{c₁,c₂} |W̄c₁ - W̄c₂|</p>
          </div>
          <p class="text-xs text-gray-400 leading-relaxed">
            W̄c es la espera promedio ponderada del país c. f₂ mide la brecha
            máxima entre cualquier par de países.
            <strong class="text-accent-green">Minimizar → equidad entre naciones.</strong>
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-blue/20">
          <h3 class="text-accent-blue font-bold mb-2">f₃ — Desperdicio</h3>
          <div class="font-mono text-xs mb-3 space-y-1">
            <p class="text-white">f₃(x) = V - Σᵍ xᵍ</p>
          </div>
          <p class="text-xs text-gray-400 leading-relaxed">
            Visas que quedan sin asignar. La interacción entre topes por país (R3)
            y por categoría (R4) puede hacer imposible usar todas las visas.
            <strong class="text-accent-blue">Minimizar → máxima utilización.</strong>
          </p>
        </div>
      </div>

      <!-- Restricciones -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-3">Restricciones</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R1: Σᵍ x��� ≤ V = 140,000</p>
            <p class="text-xs text-gray-500 mt-1">Total de visas asignadas no excede el presupuesto anual</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R2: 0 ��� xᵍ ≤ nᵍ ∀g</p>
            <p class="text-xs text-gray-500 mt-1">No asignar más visas de las demandadas por cada grupo</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R3: Σ{g∈c} xᵍ ≤ Pc = 25,620 ∀c</p>
            <p class="text-xs text-gray-500 mt-1">Tope por país: 7% del total (INA §202)</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R4: Σ{g∈j} xᵍ ≤ Kⱼ,eff ∀j</p>
            <p class="text-xs text-gray-500 mt-1">Tope efectivo por categoría, incluyendo spillover (INA §203(b))</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R5: xᵍ ≥ 0 ∀g</p>
            <p class="text-xs text-gray-500 mt-1">No negatividad</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R6: xᵍ ∈ ℤ ∀g</p>
            <p class="text-xs text-gray-500 mt-1">Integralidad: una visa es indivisible</p>
          </div>
        </div>
      </div>

      <!-- Spillover -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-2">Cascada de Spillover (INA §203(b))</h3>
        <p class="text-xs text-gray-400 mb-3">
          Cuando una categoría no agota su cuota base, el sobrante fluye a la siguiente según la ley:
        </p>
        <div class="flex flex-wrap items-center gap-2 text-sm font-mono">
          <span class="bg-accent-red/20 text-accent-red px-3 py-1 rounded">EB-4/5 sobrante</span>
          <span class="text-gray-500">→</span>
          <span class="bg-accent-yellow/20 text-accent-yellow px-3 py-1 rounded">EB-1</span>
          <span class="text-gray-500">→</span>
          <span class="bg-accent-green/20 text-accent-green px-3 py-1 rounded">EB-2</span>
          <span class="text-gray-500">→</span>
          <span class="bg-accent-blue/20 text-accent-blue px-3 py-1 rounded">EB-3</span>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          Esto modifica los topes efectivos Kⱼ,eff, haciendo que R4 dependa de la asignación global.
        </p>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- 3. INTEGRACIÓN CON LA METAHEURÍSTICA (MOHHO) -->
    <!-- ============================================ -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">3. Integración del Modelo con MOHHO</h2>
      <p class="text-sm text-gray-400 leading-relaxed">
        El problema anterior es un <strong class="text-white">programa entero multi-objetivo con restricciones acopladas</strong>
        (NP-difícil). No se puede resolver con métodos exactos en tiempo razonable.
        Aplicamos <strong class="text-accent-yellow">MOHHO</strong> (Multi-Objective Harris Hawks Optimization),
        una metaheurística poblacional inspirada en la caza cooperativa de halcones de Harris.
      </p>

      <!-- Justificación del espacio de búsqueda -->
      <div class="bg-dark-bg1 rounded-lg p-5 border border-primary/30 space-y-4">
        <h3 class="text-primary-300 font-bold">¿Por qué el espacio de búsqueda es [0, 1]¹⁰⁵?</h3>

        <div class="space-y-3 text-sm text-gray-400 leading-relaxed">
          <p>
            <strong class="text-white">Dimensionalidad = 105:</strong>
            Existen exactamente <strong class="text-accent-yellow">G = 21 × 5 = 105</strong> grupos (pares país-categoría)
            que compiten por las visas. Cada dimensión del vector de búsqueda corresponde a un grupo,
            estableciendo una <strong class="text-white">biyección</strong> entre las dimensiones del halcón y los grupos del problema.
            Así, la dimensión k-ésima del halcón codifica la prioridad relativa del grupo k-ésimo.
          </p>
          <p>
            <strong class="text-white">Valores continuos [0, 1]:</strong>
            MOHHO opera sobre espacios continuos (sus 6 operadores —exploración, siege suave/duro, vuelos de Lévy—
            usan aritmética de punto flotante). Sin embargo, la variable de decisión x es <em>entera</em>.
            La solución es una <strong class="text-accent-green">codificación indirecta en 3 capas</strong>:
          </p>
        </div>

        <!-- Codificación en 3 capas -->
        <div class="space-y-3 ml-4">
          <div class="flex items-start gap-3">
            <span class="bg-primary/20 text-primary-300 px-2.5 py-0.5 rounded text-xs font-bold shrink-0">Capa 1</span>
            <div>
              <p class="text-sm text-white font-medium">Halcón continuo: H ∈ [0, 1]¹⁰⁵</p>
              <p class="text-xs text-gray-500">
                Cada halcón es un vector de 105 valores reales en [0, 1].
                MOHHO evoluciona estos vectores usando sus operadores estándar sin modificación.
              </p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <span class="bg-primary/20 text-primary-300 px-2.5 py-0.5 rounded text-xs font-bold shrink-0">Capa 2</span>
            <div>
              <p class="text-sm text-white font-medium">SPV (Smallest Position Value): π = argsort(H)</p>
              <p class="text-xs text-gray-500">
                Se convierte el vector continuo en una <strong>permutación</strong> de los 105 grupos
                mediante argsort: el grupo con el valor más pequeño en H obtiene la mayor prioridad.
                Esto transforma el espacio continuo en el espacio combinatorio de permutaciones de forma suave y diferenciable.
              </p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <span class="bg-primary/20 text-primary-300 px-2.5 py-0.5 rounded text-xs font-bold shrink-0">Capa 3</span>
            <div>
              <p class="text-sm text-white font-medium">Decodificador Greedy: π → x ∈ ℤ₊¹⁰⁵</p>
              <p class="text-xs text-gray-500">
                Recorre los grupos en el orden de π. A cada grupo le asigna el mínimo entre
                su demanda nᵍ y la capacidad residual (R1, R3, R4). Resultado: una asignación
                <strong>siempre factible</strong> que satisface R1–R6 por construcción.
              </p>
            </div>
          </div>
        </div>

        <p class="text-xs text-gray-500 border-t border-dark-border pt-3">
          <strong class="text-gray-400">Justificación geométrica:</strong>
          El hipercubo [0, 1]��⁰⁵ es un espacio de búsqueda compacto y acotado donde cada punto
          induce una permutación única (salvo empates de medida cero). Los operadores de MOHHO
          (exploración, siege, Lévy) generan movimientos suaves en este hipercubo, que se traducen
          en <em>intercambios locales</em> de prioridad entre grupos en el espacio de permutaciones.
          Vecinos cercanos en ℝ¹⁰⁵ tienden a producir permutaciones similares, preservando la
          localidad necesaria para que la búsqueda heurística sea efectiva.
        </p>
      </div>

      <!-- Operadores MOHHO -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-3">Operadores de MOHHO</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-white font-medium">Fase de Exploración (|E| ≥ 1)</p>
            <p class="text-gray-500 mt-1">
              <strong>Op1:</strong> Posición aleatoria basada en presa + miembro aleatorio.
              <strong>Op2:</strong> Posición basada en media de la población.
              Diversifica la búsqueda en regiones no exploradas del hipercubo.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-white font-medium">Siege Suave (|E| < 1, r ≥ 0.5)</p>
            <p class="text-gray-500 mt-1">
              <strong>Op3:</strong> Persecución gradual hacia el líder Pareto.
              <strong>Op5:</strong> Con vuelo de Lévy para escape de óptimos locales.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-white font-medium">Siege Duro (|E| < 1, r < 0.5)</p>
            <p class="text-gray-500 mt-1">
              <strong>Op4:</strong> Convergencia agresiva al líder.
              <strong>Op6:</strong> Con Lévy, mayor capacidad de escape.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-white font-medium">Energía de escape</p>
            <p class="text-gray-500 mt-1">
              E(t) = 2(1 - t/T) · r₀ controla la transición de exploración a explotación.
              Cuando |E| ≥ 1 → exploración; |E| < 1 → explotación.
            </p>
          </div>
        </div>
      </div>

      <!-- Archivo Pareto -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-2">Archivo Pareto y Selección de Líder</h3>
        <p class="text-xs text-gray-400 leading-relaxed mb-2">
          MOHHO mantiene un <strong class="text-white">archivo externo de soluciones no dominadas</strong>
          (máximo 100). En cada iteración:
        </p>
        <ol class="text-xs text-gray-400 space-y-1 list-decimal list-inside">
          <li>Se evalúan todos los halcones: H → π → x → F(x) = (f₁, f₂, f₃)</li>
          <li>Se actualiza el archivo eliminando soluciones dominadas y agregando las nuevas no dominadas</li>
          <li>Si el archivo excede su capacidad, se podan los puntos con menor <strong class="text-white">distancia de crowding</strong></li>
          <li>El <strong class="text-accent-yellow">líder</strong> (presa del halcón) se selecciona del archivo
            usando torneo por crowding distance, favoreciendo regiones menos densas del frente</li>
        </ol>
      </div>
    </section>

    <!-- ============================ -->
    <!-- 4. EVALUACIÓN DEL KNEE POINT -->
    <!-- ============================ -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">4. Selección del Punto Knee</h2>
      <p class="text-sm text-gray-400 leading-relaxed">
        El escenario <strong class="text-accent-yellow">"Equilibrio"</strong> selecciona la solución del frente de Pareto
        que representa el mejor compromiso entre los tres objetivos. Utilizamos el
        <strong class="text-white">método de máxima distancia perpendicular</strong> sobre la proyección f₁–f₂:
      </p>

      <div class="bg-dark-bg1 rounded-lg p-5 space-y-4">
        <h3 class="text-primary-300 font-bold text-sm">Algoritmo formal del Knee Point</h3>

        <ol class="text-xs text-gray-400 space-y-3 list-decimal list-inside leading-relaxed">
          <li>
            <strong class="text-white">Ordenar</strong> las soluciones del frente de Pareto por f₁ ascendente:
            <span class="font-mono text-gray-300">P = sort(Pareto, key=f₁)</span>
          </li>
          <li>
            <strong class="text-white">Normalizar</strong> f₁ y f₂ al rango [0, 1]:
            <div class="font-mono text-gray-300 mt-1 ml-4">
              f̂₁ᵢ = (f₁ᵢ - f₁_min) / (f₁_max - f₁_min)<br>
              f̂₂ᵢ = (f₂ᵢ - f₂_min) / (f₂_max - f₂_min)
            </div>
            <p class="text-gray-500 mt-1 ml-4">La normalización evita que un objetivo domine por escala.</p>
          </li>
          <li>
            <strong class="text-white">Trazar la línea</strong> L entre los extremos normalizados:
            <span class="font-mono text-gray-300">L: p₁ = (f̂₁₁, f̂₂₁) → p₂ = (f̂₁ₙ, f̂₂ₙ)</span>
          </li>
          <li>
            <strong class="text-white">Calcular la distancia perpendicular</strong> de cada punto a L:
            <div class="font-mono text-gray-300 mt-1 ml-4">
              d_⊥(pᵢ) = ‖(pᵢ - p₁) - ((pᵢ - p₁) · û) · û‖
            </div>
            <p class="text-gray-500 mt-1 ml-4">donde û = (p₂ - p₁) / ‖p��� - p₁‖ es el vector unitario de L.</p>
          </li>
          <li>
            <strong class="text-white">Seleccionar</strong> el punto con máxima distancia perpendicular:
            <div class="font-mono text-accent-yellow mt-1 ml-4">
              knee = argmax{pᵢ ∈ P} d_⊥(pᵢ)
            </div>
            <p class="text-gray-500 mt-1 ml-4">
              Este punto es el que más se "aleja" de la interpolación lineal entre extremos,
              representando la región de máxima curvatura del frente — donde la mejora marginal
              en un objetivo comienza a costar mucho en el otro.
            </p>
          </li>
        </ol>
      </div>

      <p class="text-xs text-gray-500 leading-relaxed">
        <strong class="text-gray-400">Interpretación:</strong>
        El knee point es la solución donde el <em>costo de oportunidad</em> entre f₁ y f₂ se equilibra.
        A la izquierda del knee, reducir f₁ (espera) cuesta poco en f₂ (disparidad).
        A la derecha, cada mejora en f₁ empeora significativamente f₂.
        El knee es el punto de "rendimientos decrecientes" del frente.
      </p>
    </section>

    <!-- ============================== -->
    <!-- 5. COHERENCIA DEL PLANTEAMIENTO -->
    <!-- ============================== -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">5. Coherencia del Planteamiento</h2>

      <div class="space-y-3 text-sm text-gray-400 leading-relaxed">
        <div class="bg-dark-bg1 rounded-lg p-4">
          <p class="text-white font-medium mb-1">Problema → Modelo</p>
          <p class="text-xs">
            El problema real (asignar visas limitadas entre grupos con demanda heterogénea)
            se traduce fielmente al modelo: las variables xᵍ representan las visas por grupo,
            los tres objetivos capturan las tres dimensiones de calidad (humanitaria, equitativa, eficiente),
            y las restricciones R1–R6 reflejan la legislación (INA §202, §203(b)).
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-4">
          <p class="text-white font-medium mb-1">Modelo → Metaheurística</p>
          <p class="text-xs">
            El modelo entero multi-objetivo con restricciones acopladas es NP-difícil y no admite
            solución exacta eficiente. MOHHO es adecuado porque: (a) maneja múltiples objetivos
            nativamente vía archivo Pareto, (b) la codificación SPV + decodificador greedy garantiza
            factibilidad sin penalización, y (c) el balance exploración/explotación del HHO
            permite encontrar frentes de Pareto diversos.
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-4">
          <p class="text-white font-medium mb-1">Metaheurística → Decisión</p>
          <p class="text-xs">
            El frente de Pareto generado (406 soluciones) se traduce en 5 escenarios interpretables:
            el decisor selecciona según su prioridad (humanitaria, equitativa, eficiente, equilibrada)
            sin necesidad de asignar pesos a priori. El knee point ofrece un compromiso matemáticamente
            fundamentado para cuando no hay preferencia explícita.
          </p>
        </div>
      </div>
    </section>

    <!-- Configuración experimental -->
    <section class="card space-y-3">
      <h2 class="text-lg font-bold text-white">6. Configuración Experimental</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-gray-500 uppercase">Población</p>
          <p class="text-white font-bold font-mono text-lg">50</p>
          <p class="text-gray-500">halcones</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-gray-500 uppercase">Iteraciones</p>
          <p class="text-white font-bold font-mono text-lg">500</p>
          <p class="text-gray-500">por corrida</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-gray-500 uppercase">Archivo</p>
          <p class="text-white font-bold font-mono text-lg">100</p>
          <p class="text-gray-500">soluciones máx.</p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-3 text-center">
          <p class="text-gray-500 uppercase">Corridas</p>
          <p class="text-white font-bold font-mono text-lg">30</p>
          <p class="text-gray-500">seeds 42–71</p>
        </div>
      </div>
      <p class="text-xs text-gray-500">
        Métrica de convergencia: <strong class="text-gray-400">Hipervolumen 3D</strong> con punto de referencia
        (10.0, 16.0, 50,000) — mide el volumen del espacio objetivo dominado por el frente de Pareto.
      </p>
    </section>
  </div>
</template>
