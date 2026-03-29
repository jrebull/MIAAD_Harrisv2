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

      <!-- Plain language intro (hospital metaphor) -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-2">
        <p class="text-sm text-gray-300 leading-relaxed">
          <strong class="text-primary-300">Imagina una sala de espera de hospital</strong> con 140,000 citas disponibles
          y miles de pacientes de 21 países. Algunos llevan <strong class="text-white">más de una década esperando</strong>.
          ¿Cómo repartes las citas de forma que: (a) los que más han esperado sean atendidos primero,
          (b) ningún país sea tratado injustamente, y (c) no quede ninguna cita vacía?
        </p>
        <p class="text-sm text-gray-400 leading-relaxed">
          Ese es exactamente el problema de las visas EB. No hay una respuesta perfecta — mejorar un
          objetivo empeora otro. Por eso necesitamos un <strong class="text-white">modelo matemático</strong>
          que formalice los trade-offs y un <strong class="text-white">algoritmo de optimización</strong>
          que encuentre los mejores compromisos posibles.
        </p>
      </div>

      <p class="text-sm text-gray-400 leading-relaxed">
        El gobierno de EE.UU. dispone cada año fiscal de <strong class="text-accent-yellow">V = 140,000 visas</strong>
        de empleo (EB) que deben distribuirse entre <strong class="text-white">G = 105 grupos</strong>
        (21 países × 5 categorías EB). El problema consiste en encontrar una asignación
        que minimice simultáneamente tres objetivos en conflicto, sujeta a restricciones legales.
      </p>

      <!-- Variable de decisión -->
      <div>
        <h3 class="text-sm font-semibold text-accent-yellow uppercase tracking-wider mb-2">Variable de Decisión</h3>
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
          <div class="bg-dark-bg1 rounded-lg p-3">
            <span class="font-mono text-accent-green">Pc = 25,620</span>
            <span class="text-gray-500 ml-2">— Tope por país: 7% de V total (incluyendo las ~226,000 visas familiares). La ley INA §202(a)(2) establece el 7% sobre <em class="text-gray-400">todas</em> las visas de preferencia (EB + FB), no solo las 140,000 EB. El resultado: 0.07 × 366,000 ≈ 25,620 visas máximo por país.</span>
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
            <span class="text-accent-green">dᵍ ∈ ℤ</span>
            <span class="text-gray-500 ml-2">— Fecha de prioridad del grupo g</span>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 font-mono">
            <span class="text-accent-green">Kⱼ,eff</span>
            <span class="text-gray-500 ml-2">— Tope efectivo por categoría j (con spillover)</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================= -->
    <!-- 2. ¿POR QUÉ LOS OBJETIVOS ENTRAN EN CONFLICTO? -->
    <!-- ========================================= -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">2. ¿Por qué los Objetivos Entran en Conflicto?</h2>

      <p class="text-sm text-gray-400 leading-relaxed">
        Para entender por qué no existe una solución perfecta, comparemos dos estrategias extremas:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
          <h3 class="text-accent-yellow font-bold text-sm mb-2">Estrategia A: "Priorizar espera"</h3>
          <p class="text-xs text-gray-400 leading-relaxed">
            Dar todas las visas a India y China (que llevan 10+ años esperando).
            <strong class="text-accent-yellow">f₁ baja</strong> (menos espera acumulada), pero
            <strong class="text-accent-red">f₂ sube</strong> (los demás países no reciben nada → máxima disparidad)
            y <strong class="text-accent-red">f₃ puede subir</strong> (topes por país limitan cuántas puede absorber un solo país).
          </p>
        </div>
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
          <h3 class="text-accent-green font-bold text-sm mb-2">Estrategia B: "Igualar países"</h3>
          <p class="text-xs text-gray-400 leading-relaxed">
            Repartir equitativamente entre todos los países.
            <strong class="text-accent-green">f₂ baja</strong> (todos esperan lo mismo), pero
            <strong class="text-accent-red">f₁ sube</strong> (India/China siguen esperando décadas)
            y <strong class="text-accent-red">f₃ puede subir</strong> (países con poca demanda no usan su cuota).
          </p>
        </div>
      </div>

      <!-- Why f3 matters -->
      <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-blue/20">
        <h3 class="text-accent-blue font-bold text-sm mb-2">¿Por qué f₃ (desperdicio) es un objetivo separado?</h3>
        <p class="text-xs text-gray-400 leading-relaxed mb-2">
          En teoría, si no hubiera topes por país ni por categoría, se podrían asignar todas las 140,000 visas (f₃ = 0).
          Pero las restricciones legales (R3, R4) crean un <strong class="text-white">conflicto estructural</strong>:
          a veces no hay suficientes solicitantes elegibles en una categoría/país para llenar su cuota,
          y esas visas no siempre pueden transferirse.
        </p>
        <div class="bg-dark-bg2 rounded p-3 text-xs font-mono text-gray-300">
          <p>Datos reales de nuestro experimento (406 soluciones Pareto):</p>
          <p class="mt-1">
            <span class="text-accent-yellow">Mejor f₁ = 7.186</span> → desperdicia 16,280 visas
          </p>
          <p>
            <span class="text-accent-green">Mejor f₂ = 2.064</span> → desperdicia 17,105 visas
          </p>
          <p>
            <span class="text-accent-blue">Mejor f₃ = 0</span> → espera sube a 7.258 años
          </p>
          <p class="mt-1 text-gray-500">Las tres son Pareto-óptimas: cada una gana en un objetivo y pierde en otro.</p>
        </div>
      </div>
    </section>

    <!-- ============================== -->
    <!-- 3. FORMULACIÓN MATEMÁTICA      -->
    <!-- ============================== -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">3. Formulación Matemática</h2>

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
            <p class="text-accent-yellow font-mono text-sm">R1: Σᵍ xᵍ ≤ V = 140,000</p>
            <p class="text-xs text-gray-500 mt-1">Total de visas asignadas no excede el presupuesto anual</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R2: 0 ≤ xᵍ ≤ nᵍ ∀g</p>
            <p class="text-xs text-gray-500 mt-1">No asignar más visas de las demandadas por cada grupo</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3">
            <p class="text-accent-yellow font-mono text-sm">R3: Σ{g∈c} xᵍ ≤ Pc = 25,620 ∀c</p>
            <p class="text-xs text-gray-500 mt-1">Tope por país: 7% del total de visas de preferencia EB + familiares (INA §202(a)(2)). Se calcula como 0.07 × 366,000 ≈ 25,620.</p>
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
    <!-- 4. INTEGRACIÓN CON LA METAHEURÍSTICA (MOHHO) -->
    <!-- ============================================ -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">4. Integración del Modelo con MOHHO</h2>
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
          El hipercubo [0, 1]¹⁰⁵ es un espacio de búsqueda compacto y acotado donde cada punto
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

      <!-- HHO ↔ Math model mapping -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-3">Conexión: Naturaleza ↔ Modelo Matemático</h3>
        <p class="text-xs text-gray-400 mb-3">
          Cada elemento de la caza cooperativa de halcones se traduce a un componente del modelo:
        </p>
        <div class="space-y-2">
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Halcón (posición H)</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Vector continuo</p>
            </div>
            <p class="text-xs text-gray-400">Cada halcón es un vector H ∈ ℝ¹⁰⁵ (un número real por cada uno de los 105 grupos). No es una solución directamente — es un código que el decodificador SPV+Greedy traduce a una asignación factible.</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Presa (líder)</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Solución no dominada</p>
            </div>
            <p class="text-xs text-gray-400">En MOHHO, la presa se elige aleatoriamente del archivo de Pareto, con preferencia por soluciones en zonas poco densas (crowding distance). Así los halcones exploran todo el frente, no solo un extremo.</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Energía de escape (E)</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Exploración/Explotación</p>
            </div>
            <p class="text-xs text-gray-400">E = 2·E₀·(1 − t/T). Al inicio |E| es grande: exploración global. Conforme avanzan las iteraciones, |E| decrece: explotación local. Esto es lo que hace que HHO converja.</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Vuelo de Lévy</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Saltos largos</p>
            </div>
            <p class="text-xs text-gray-400">Cuando |E| &lt; 0.5, el halcón puede hacer una "picada rápida" con salto de Lévy: pasos cortos frecuentes + saltos largos raros. Esto evita que el algoritmo se quede atrapado en óptimos locales.</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Archivo externo</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Frente de Pareto</p>
            </div>
            <p class="text-xs text-gray-400">Las mejores soluciones no dominadas se guardan en un archivo de tamaño 100. Cuando se llena, se eliminan las de zonas densas (menor crowding distance), garantizando diversidad.</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 flex gap-3 items-start">
            <div class="shrink-0 w-36">
              <p class="text-accent-yellow font-bold text-xs">Decodificador SPV</p>
              <p class="text-primary-300 text-[10px] font-semibold">→ Factibilidad garantizada</p>
            </div>
            <p class="text-xs text-gray-400">El halcón vuela libremente en ℝ¹⁰⁵ sin preocuparse por restricciones. SPV convierte los números en un orden de prioridad, y el decoder greedy reparte visas respetando R1–R6. <strong class="text-white">No hay soluciones inválidas.</strong></p>
          </div>
        </div>
      </div>

      <!-- Worked example -->
      <div>
        <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-3">Ejemplo Paso a Paso</h3>
        <div class="bg-dark-bg1 rounded-lg p-5 space-y-3 text-sm text-gray-400 leading-relaxed">
          <p>
            <strong class="text-accent-yellow">Paso 1:</strong> El halcón genera:
            <span class="font-mono text-primary-300">H = (0.72, 0.15, 0.91, 0.03, 0.58)</span>
            <span class="text-gray-500">(simplificado a 5 dimensiones)</span>
          </p>
          <p>
            <strong class="text-accent-green">Paso 2 (SPV):</strong> Ordenamos de menor a mayor →
            <span class="font-mono text-primary-300">π = (4, 2, 5, 1, 3)</span>
            <br>
            <span class="text-gray-500 text-xs">El grupo 4 (valor 0.03) va primero, luego el 2 (0.15), etc.</span>
          </p>
          <p>
            <strong class="text-accent-blue">Paso 3 (Decoder):</strong> Recorremos π y repartimos:
          </p>
          <div class="ml-4 text-xs text-gray-500 space-y-0.5">
            <p>• Grupo 4: pide 8,000 → le damos min(8,000, disponible, cupo_país, cupo_cat)</p>
            <p>• Grupo 2: pide 15,000 → le damos lo que se pueda sin violar R1–R6</p>
            <p>• ... y así hasta agotar las 140,000 visas.</p>
          </div>
          <p class="text-xs border-t border-dark-border pt-2">
            <strong class="text-white">Propiedad clave:</strong> <em>cualquier</em> orden que genere el halcón produce una asignación válida. No se necesitan penalizaciones — la factibilidad está garantizada por diseño.
          </p>
          <p>
            <strong class="text-accent-yellow">Paso 4 (Evaluar):</strong> Calculamos los tres objetivos sobre la asignación resultante x:
          </p>
          <div class="ml-4 text-xs text-gray-500 space-y-0.5 font-mono">
            <p>• f₁ = Σ(nᵍ − xᵍ) · wᵍ / Σ nᵍ</p>
            <p>• f₂ = max|W̄c₁ − W̄c₂| entre todos los pares de países</p>
            <p>• f₃ = V − Σ xᵍ (visas sin asignar)</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- 5. ¿QUÉ ES EL FRENTE DE PARETO?              -->
    <!-- ============================================= -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">5. ¿Qué es el Frente de Pareto?</h2>
      <p class="text-sm text-gray-400 leading-relaxed">
        Imagina que comparas dos repartos de visas, <strong class="text-white">A</strong> y <strong class="text-white">B</strong>:
      </p>
      <div class="text-sm text-gray-400 space-y-2 ml-2">
        <p>
          • Si A tiene <strong class="text-white">menor espera, menor brecha Y menos desperdicio</strong> que B → A es claramente mejor.
          Decimos que A <em>domina</em> a B.
        </p>
        <p>
          • Si A tiene <strong class="text-white">menor espera PERO mayor brecha</strong> → ninguno domina al otro.
          Ambos son válidos, solo son compromisos diferentes.
        </p>
      </div>
      <p class="text-sm text-gray-400 leading-relaxed">
        El <strong class="text-accent-yellow">frente de Pareto</strong> es el grupo de soluciones que nadie puede superar
        en los tres objetivos a la vez. Son las "mejores opciones disponibles" — <strong class="text-white">406</strong> en nuestro caso.
      </p>

      <!-- Formal dominance -->
      <details class="bg-dark-bg1 rounded-lg p-4">
        <summary class="cursor-pointer text-sm text-gray-400 hover:text-white transition-colors font-medium">
          Ver definición formal de dominancia
        </summary>
        <div class="mt-3 space-y-3">
          <div class="bg-dark-bg2 rounded p-3 font-mono text-sm text-center text-gray-300">
            a ≻ b ⟺ ∀m ∈ {1,2,3}: fₘ(a) ≤ fₘ(b) ∧ ∃m: fₘ(a) &lt; fₘ(b)
          </div>
          <p class="text-xs text-gray-500">a domina a b si es al menos igual en los tres objetivos y estrictamente mejor en al menos uno.</p>
          <div class="bg-dark-bg2 rounded p-3 font-mono text-sm text-center text-gray-300">
            Frente de Pareto = { x | no existe x' que domine a x }
          </div>
        </div>
      </details>

      <!-- Numerical example table -->
      <div>
        <h3 class="text-sm font-semibold text-primary-300 uppercase tracking-wider mb-3">Ejemplo con Números Reales</h3>
        <p class="text-xs text-gray-400 mb-3">
          Estos son los resultados de cuatro soluciones reales del experimento:
        </p>
        <div class="overflow-x-auto rounded-lg border border-dark-border">
          <table class="w-full text-xs">
            <thead class="bg-dark-bg2">
              <tr class="border-b border-dark-border">
                <th class="px-4 py-2 text-left text-gray-400 font-semibold">Solución</th>
                <th class="px-4 py-2 text-right text-accent-yellow font-semibold">f₁ (espera)</th>
                <th class="px-4 py-2 text-right text-accent-green font-semibold">f₂ (disparidad)</th>
                <th class="px-4 py-2 text-right text-accent-blue font-semibold">f₃ (desperdicio)</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-dark-border/30">
                <td class="px-4 py-2 text-gray-300">Mejor f₁</td>
                <td class="px-4 py-2 text-right font-mono text-accent-yellow font-bold">7.186 años</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">10.744 años</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">16,280</td>
              </tr>
              <tr class="border-b border-dark-border/30 bg-white/[0.02]">
                <td class="px-4 py-2 text-gray-300">Mejor f₂</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">7.514 años</td>
                <td class="px-4 py-2 text-right font-mono text-accent-green font-bold">2.064 años</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">17,105</td>
              </tr>
              <tr class="border-b border-dark-border/30">
                <td class="px-4 py-2 text-gray-300">Mejor f₃</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">7.258 años</td>
                <td class="px-4 py-2 text-right font-mono text-gray-400">9.390 años</td>
                <td class="px-4 py-2 text-right font-mono text-accent-blue font-bold">0</td>
              </tr>
              <tr class="bg-accent-red/5">
                <td class="px-4 py-2 text-accent-red font-semibold">FIFO (actual)</td>
                <td class="px-4 py-2 text-right font-mono text-accent-red">7.214 años</td>
                <td class="px-4 py-2 text-right font-mono text-accent-red">12.638 años</td>
                <td class="px-4 py-2 text-right font-mono text-accent-red">17,540</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-xs text-gray-500 mt-2 leading-relaxed">
          <strong class="text-gray-400">¿Por qué ninguna es la "mejor"?</strong>
          Mejor-f₁ tiene la menor espera (7.186) pero desperdicia 16,280 visas.
          Mejor-f₃ no desperdicia ninguna visa pero su espera es 7.258.
          Mejor-f₂ tiene la menor brecha (2.064) pero la peor espera (7.514).
          <strong class="text-white">Las tres son óptimas</strong> — cada una gana en un objetivo y pierde en otro.
        </p>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- 6. HIPERVOLUMEN                               -->
    <!-- ============================================= -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">6. ¿Cómo Sabemos si las Soluciones son Buenas? (Hipervolumen)</h2>
      <p class="text-sm text-gray-400 leading-relaxed">
        El <strong class="text-white">hipervolumen (HV)</strong> es como medir el "volumen" que cubre el frente de Pareto
        en el espacio tridimensional de f₁ × f₂ × f₃. Si el frente se expande (mejores soluciones),
        el volumen crece.
      </p>

      <!-- Qué es el punto de referencia -->
      <div class="bg-dark-bg1 rounded-lg p-5 space-y-4">
        <h3 class="text-primary-300 font-bold text-sm">¿Qué es el punto de referencia (r₁, r₂, r₃)?</h3>
        <p class="text-sm text-gray-400 leading-relaxed">
          Para medir el hipervolumen necesitamos un <strong class="text-white">punto de referencia</strong> que represente
          el <strong class="text-accent-red">"peor caso imaginable"</strong> — un límite superior para cada objetivo.
          El HV mide cuánto espacio hay entre nuestras soluciones y ese peor caso.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold mb-1">r₁ = 10.0 años</p>
            <p class="text-gray-400">Peor espera aceptable. Nuestras soluciones van de 7.18 a 7.51 → todas están <strong class="text-white">lejos</strong> del peor caso.</p>
          </div>
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-green/20">
            <p class="text-accent-green font-bold mb-1">r₂ = 16.0 años</p>
            <p class="text-gray-400">Peor disparidad aceptable. Nuestras van de 2.06 a 12.64 → algunas buenas, otras cerca del límite.</p>
          </div>
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-blue/20">
            <p class="text-accent-blue font-bold mb-1">r₃ = 50,000 visas</p>
            <p class="text-gray-400">Peor desperdicio aceptable. Nuestras van de 0 a 17,540 → todas mucho mejor que el límite.</p>
          </div>
        </div>
      </div>

      <!-- Fórmula -->
      <div class="bg-dark-bg1 rounded-lg p-4 font-mono text-sm text-center space-y-2">
        <p class="text-gray-500 text-xs">Fórmula del hipervolumen:</p>
        <p class="text-accent-yellow text-base">HV = volumen( ∪ₖ [f₁ᵏ, r₁] × [f₂ᵏ, r₂] × [f₃ᵏ, r₃] )</p>
        <p class="text-gray-500 text-xs">
          Para cada solución k del frente, se forma un "bloque" desde sus valores (f₁ᵏ, f₂ᵏ, f₃ᵏ)
          hasta el punto de referencia (r₁, r₂, r₃). El HV es el volumen total de la unión de todos esos bloques.
        </p>
      </div>

      <!-- Ejemplo concreto -->
      <div class="bg-dark-bg1 rounded-lg p-5 space-y-3">
        <h3 class="text-primary-300 font-bold text-sm">Ejemplo concreto con una sola solución</h3>
        <p class="text-sm text-gray-400 leading-relaxed">
          Tomemos la solución <strong class="text-accent-yellow">"Mejor f₁"</strong> con valores
          <span class="font-mono text-gray-300">(f₁=7.186, f₂=10.744, f₃=16,280)</span>:
        </p>
        <div class="bg-dark-bg2 rounded-lg p-4 font-mono text-sm space-y-2">
          <p class="text-gray-400">El "bloque" de esta solución mide:</p>
          <div class="ml-2 space-y-1">
            <p><span class="text-accent-yellow">Lado 1:</span> <span class="text-white">r₁ − f₁</span> = 10.0 − 7.186 = <strong class="text-accent-yellow">2.814</strong> años de margen en espera</p>
            <p><span class="text-accent-green">Lado 2:</span> <span class="text-white">r₂ − f₂</span> = 16.0 − 10.744 = <strong class="text-accent-green">5.256</strong> años de margen en disparidad</p>
            <p><span class="text-accent-blue">Lado 3:</span> <span class="text-white">r₃ − f₃</span> = 50,000 − 16,280 = <strong class="text-accent-blue">33,720</strong> visas de margen en desperdicio</p>
          </div>
          <div class="border-t border-dark-border pt-2 mt-2">
            <p class="text-gray-400">Volumen de este bloque:</p>
            <p class="text-white">2.814 × 5.256 × 33,720 = <strong class="text-accent-yellow">498,524</strong></p>
          </div>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed">
          Con <strong class="text-white">406 soluciones</strong> los bloques se superponen parcialmente.
          El HV es el volumen de la <em>unión</em> (sin contar la superposición dos veces).
          Una solución que mejora f₁ pero empeora f₂ "estira" el volumen en una dirección diferente
          — por eso el HV recompensa tanto calidad como diversidad del frente.
        </p>
      </div>

      <!-- Interpretación -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-2">
        <p class="text-sm text-gray-300 leading-relaxed">
          <strong class="text-primary-300">Interpretación:</strong>
          Cuanto <strong class="text-white">mayor</strong> es el HV, más espacio "conquistaron" las soluciones
          entre sus valores y el peor caso. Significa que el algoritmo encontró soluciones que son
          simultáneamente buenas en múltiples objetivos y diversas (cubren diferentes trade-offs).
        </p>
        <div class="flex flex-wrap gap-4 text-xs text-gray-400">
          <span>HV medio: <strong class="text-accent-green">35.92</strong></span>
          <span>Desviación estándar: <strong class="text-white">0.98</strong> (muy estable en 30 corridas)</span>
          <span>Punto de referencia: <strong class="text-white">(10.0, 16.0, 50,000)</strong></span>
        </div>
      </div>
    </section>

    <!-- ============================ -->
    <!-- 7. EVALUACIÓN DEL KNEE POINT -->
    <!-- ============================ -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">7. Selección del Punto Knee (Punto de Compromiso Óptimo)</h2>

      <!-- Intuitive explanation with analogy -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-2">
        <p class="text-sm text-gray-300 leading-relaxed">
          <strong class="text-primary-300">¿Qué es el punto knee?</strong>
          El frente de Pareto contiene 406 soluciones, todas igualmente "óptimas" en sentido matemático.
          Pero necesitamos elegir <strong class="text-white">una sola</strong> para el escenario
          <strong class="text-accent-yellow">"Equilibrio"</strong>. El <strong class="text-white">punto knee</strong>
          (punto de rodilla) es la solución que representa el
          <strong class="text-accent-yellow">mejor compromiso</strong> entre los objetivos — la que ofrece
          lo mejor de ambos mundos antes de que los rendimientos se vuelvan decrecientes.
        </p>
        <p class="text-sm text-gray-400 leading-relaxed">
          <strong class="text-white">Analogía:</strong> Es como encontrar el
          <strong class="text-white">codo en una curva</strong> — el punto donde la curva "dobla"
          más pronunciadamente. Antes del codo, mejorar un objetivo cuesta poco en el otro.
          Después del codo, cada mejora pequeña exige un sacrificio enorme. El knee es exactamente
          ese punto de inflexión donde el costo de oportunidad cambia drásticamente.
        </p>
      </div>

      <!-- Visual diagram of the concept -->
      <div class="bg-dark-bg1 rounded-lg p-5 space-y-3">
        <h3 class="text-primary-300 font-bold text-sm">Diagrama: ¿Cómo se identifica el punto knee?</h3>
        <p class="text-xs text-gray-400 mb-2">
          El frente de Pareto forma una curva convexa en el plano f₁ vs f₂. El knee es el punto
          que más se aleja de la línea recta trazada entre los dos extremos del frente:
        </p>
        <div class="bg-dark-bg2 rounded-lg p-4 font-mono text-xs leading-relaxed overflow-x-auto">
          <pre class="text-gray-400">
  f₂ (Disparidad)
  ^
  |                                         LEYENDA
  | <span class="text-accent-blue">A</span>                                      ──────
  | <span class="text-accent-blue">●</span> (f₁=7.19, f₂=10.74)                 <span class="text-accent-blue">●───●</span>  Línea A-B (trade-off lineal)
  |  <span class="text-accent-blue"> ╲</span>                                    <span class="text-gray-500">●</span>      Soluciones Pareto
  |    <span class="text-accent-blue"> ╲</span>    <span class="text-gray-500">●</span>  <span class="text-gray-500">●</span>                         <span class="text-accent-yellow font-bold">★</span>      Knee point
  |      <span class="text-accent-blue"> ╲</span>         <span class="text-gray-500">●</span>                    <span class="text-accent-red">←——→</span>   d⊥ (distancia perpendicular)
  |        <span class="text-accent-blue"> ╲</span>  <span class="text-accent-red">←———→</span> <span class="text-accent-yellow font-bold">★</span> <span class="text-accent-yellow">KNEE</span>
  |          <span class="text-accent-blue"> ╲</span>  <span class="text-accent-red">d⊥</span>    (f₁=7.33, f₂=5.12)
  |            <span class="text-accent-blue"> ╲</span>       <span class="text-gray-500">●</span>
  |              <span class="text-accent-blue"> ╲</span>  <span class="text-gray-500">●</span>
  |                <span class="text-accent-blue"> ╲</span>   <span class="text-gray-500">●</span>
  |                  <span class="text-accent-blue">●</span>
  |                  <span class="text-accent-blue">B</span> (f₁=7.53, f₂=2.50)
  |
  +──────────────────────────────────────→ f₁ (Espera)
          </pre>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed">
          La línea diagonal azul (A–B) conecta los dos extremos del frente de Pareto.
          Si el trade-off fuera perfectamente lineal, todas las soluciones estarían sobre esa línea.
          Pero el frente es curvo: las soluciones se "abomban" hacia el origen.
          La estrella amarilla (knee) es la solución que más se aleja de esa línea recta,
          marcando la zona de máxima curvatura donde el trade-off cambia drásticamente.
        </p>
      </div>

      <!-- Step-by-step algorithm as numbered cards -->
      <div class="space-y-3">
        <h3 class="text-primary-300 font-bold text-sm">Algoritmo paso a paso</h3>

        <!-- Step 1 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-accent-yellow">
          <div class="flex items-start gap-3">
            <span class="bg-accent-yellow/20 text-accent-yellow font-bold text-sm rounded-full w-7 h-7 flex items-center justify-center shrink-0">1</span>
            <div class="space-y-2">
              <p class="text-white font-medium text-sm">Normalizar los objetivos al rango [0, 1]</p>
              <p class="text-xs text-gray-400 leading-relaxed">
                Los objetivos f₁ (espera, rango 7.19–7.53) y f₂ (disparidad, rango 2.38–12.00) tienen
                escalas muy diferentes. Sin normalizar, f₂ dominaría el cálculo por tener un rango
                27× mayor. Se normalizan al intervalo [0, 1]:
              </p>
              <div class="bg-dark-bg2 rounded-lg p-3 font-mono text-sm space-y-1">
                <p class="text-accent-yellow">f̂₁ᵢ = (f₁ᵢ − f₁_min) / (f₁_max − f₁_min)</p>
                <p class="text-accent-yellow">f̂₂ᵢ = (f₂ᵢ − f₂_min) / (f₂_max − f₂_min)</p>
              </div>
              <p class="text-xs text-gray-500 leading-relaxed">
                Después de normalizar: 0 = el mejor valor del frente en ese objetivo, 1 = el peor.
                Ahora ambos ejes tienen el mismo "peso visual" y la distancia se calcula justamente.
              </p>
            </div>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-accent-green">
          <div class="flex items-start gap-3">
            <span class="bg-accent-green/20 text-accent-green font-bold text-sm rounded-full w-7 h-7 flex items-center justify-center shrink-0">2</span>
            <div class="space-y-2">
              <p class="text-white font-medium text-sm">Identificar los dos extremos del frente</p>
              <p class="text-xs text-gray-400 leading-relaxed">
                Se ordena el frente por f₁ ascendente. El primer punto (menor f₁) y el último
                (mayor f₁) definen los extremos de la curva:
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-yellow/20">
                  <p class="text-accent-yellow font-bold mb-1">Extremo A (menor espera)</p>
                  <p class="text-gray-400">
                    Original: <span class="font-mono text-white">f₁=7.186, f₂=10.744</span>
                  </p>
                  <p class="text-gray-500 mt-1">Normalizado: <span class="font-mono text-gray-300">(0.000, 0.869)</span></p>
                  <p class="text-gray-500 text-[10px]">Buena espera, pero alta disparidad</p>
                </div>
                <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-green/20">
                  <p class="text-accent-green font-bold mb-1">Extremo B (menor disparidad)</p>
                  <p class="text-gray-400">
                    Original: <span class="font-mono text-white">f₁=7.532, f₂=2.501</span>
                  </p>
                  <p class="text-gray-500 mt-1">Normalizado: <span class="font-mono text-gray-300">(1.000, 0.013)</span></p>
                  <p class="text-gray-500 text-[10px]">Baja disparidad, pero más espera</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-accent-blue">
          <div class="flex items-start gap-3">
            <span class="bg-accent-blue/20 text-accent-blue font-bold text-sm rounded-full w-7 h-7 flex items-center justify-center shrink-0">3</span>
            <div class="space-y-2">
              <p class="text-white font-medium text-sm">Trazar la línea recta L entre los extremos A y B</p>
              <p class="text-xs text-gray-400 leading-relaxed">
                En el espacio normalizado, se traza una línea recta desde
                A = <span class="font-mono text-gray-300">(0.000, 0.869)</span> hasta
                B = <span class="font-mono text-gray-300">(1.000, 0.013)</span>.
                Esta línea representa el "trade-off lineal ingenuo" — si ceder en f₁ siempre
                produjera la misma ganancia proporcional en f₂, todas las soluciones estarían
                sobre ella. Pero el frente real es curvo, y las mejores soluciones de compromiso
                se desvían de esta línea.
              </p>
            </div>
          </div>
        </div>

        <!-- Step 4 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-accent-red">
          <div class="flex items-start gap-3">
            <span class="bg-accent-red/20 text-accent-red font-bold text-sm rounded-full w-7 h-7 flex items-center justify-center shrink-0">4</span>
            <div class="space-y-2">
              <p class="text-white font-medium text-sm">Calcular la distancia perpendicular de cada solución a la línea</p>
              <p class="text-xs text-gray-400 leading-relaxed">
                Para cada solución pᵢ del frente de Pareto, se mide cuánto se desvía
                de la línea L. La distancia perpendicular se calcula con la fórmula del
                producto cruzado 2D:
              </p>
              <div class="bg-dark-bg2 rounded-lg p-4 font-mono text-sm text-center space-y-3">
                <p class="text-gray-500 text-xs font-sans">Fórmula de la distancia perpendicular de un punto al segmento A–B:</p>
                <p class="text-accent-red text-base">d⊥(pᵢ) = | (xᵢ − xₐ)(yᵦ − yₐ) − (yᵢ − yₐ)(xᵦ − xₐ) | / ‖B − A‖</p>
                <div class="text-left text-xs text-gray-500 font-sans space-y-1 mt-2 border-t border-dark-border pt-2">
                  <p><span class="font-mono text-gray-400">(xᵢ, yᵢ)</span> = coordenadas normalizadas de la solución i</p>
                  <p><span class="font-mono text-gray-400">(xₐ, yₐ)</span> = extremo A normalizado = (0.000, 0.869)</p>
                  <p><span class="font-mono text-gray-400">(xᵦ, yᵦ)</span> = extremo B normalizado = (1.000, 0.013)</p>
                  <p><span class="font-mono text-gray-400">‖B − A‖</span> = √((1.000−0.000)² + (0.013−0.869)²) = <strong class="text-white">1.317</strong></p>
                </div>
              </div>
              <p class="text-xs text-gray-500 leading-relaxed">
                Forma vectorial equivalente: <span class="font-mono text-gray-400">d⊥(pᵢ) = ‖(pᵢ − A) − ((pᵢ − A) · û) · û‖</span>
                donde <span class="font-mono text-gray-400">û = (B − A) / ‖B − A‖</span> es el vector unitario de la línea.
                Ambas fórmulas dan exactamente el mismo resultado.
              </p>
            </div>
          </div>
        </div>

        <!-- Step 5 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-primary">
          <div class="flex items-start gap-3">
            <span class="bg-primary/20 text-primary-300 font-bold text-sm rounded-full w-7 h-7 flex items-center justify-center shrink-0">5</span>
            <div class="space-y-2">
              <p class="text-white font-medium text-sm">Seleccionar el punto con máxima distancia perpendicular</p>
              <p class="text-xs text-gray-400 leading-relaxed">
                De las 406 soluciones, el knee es la que tiene la
                <strong class="text-accent-yellow">mayor</strong> distancia perpendicular a la línea:
              </p>
              <div class="bg-dark-bg2 rounded-lg p-3 font-mono text-center">
                <p class="text-accent-yellow text-base">knee = argmax{pᵢ ∈ P} d⊥(pᵢ)</p>
              </div>
              <p class="text-xs text-gray-500 leading-relaxed">
                Esta solución es la que más se "aleja" de la interpolación lineal entre extremos,
                indicando la región de máxima curvatura del frente — el punto exacto donde el beneficio
                marginal de mejorar un objetivo comienza a costar desproporcionadamente en el otro.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Concrete numerical example with REAL verified data -->
      <div class="bg-dark-bg1 rounded-lg p-5 space-y-3">
        <h3 class="text-primary-300 font-bold text-sm">Ejemplo concreto con datos reales del frente</h3>
        <p class="text-sm text-gray-400 leading-relaxed">
          Con las 406 soluciones Pareto de nuestras 30 corridas, los valores reales son:
        </p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold mb-1">Extremo A</p>
            <p class="text-gray-300 font-mono">f₁ = 7.186 años</p>
            <p class="text-gray-300 font-mono">f₂ = 10.744 años</p>
            <p class="text-gray-500 mt-1 font-mono text-[10px]">Norm: (0.000, 0.869)</p>
            <p class="text-gray-500">d⊥ = 0.000 (sobre la línea)</p>
          </div>
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-yellow/30 ring-2 ring-accent-yellow/40">
            <p class="text-accent-yellow font-bold mb-1">Knee Point</p>
            <p class="text-gray-300 font-mono">f₁ = 7.326 años</p>
            <p class="text-gray-300 font-mono">f₂ = 5.118 años</p>
            <p class="text-gray-500 mt-1 font-mono text-[10px]">Norm: (0.405, 0.285)</p>
            <p class="text-accent-yellow font-semibold">d⊥ = 0.181 (MÁXIMO)</p>
          </div>
          <div class="bg-dark-bg2 rounded-lg p-3 border border-accent-green/20">
            <p class="text-accent-green font-bold mb-1">Extremo B</p>
            <p class="text-gray-300 font-mono">f₁ = 7.532 años</p>
            <p class="text-gray-300 font-mono">f₂ = 2.501 años</p>
            <p class="text-gray-500 mt-1 font-mono text-[10px]">Norm: (1.000, 0.013)</p>
            <p class="text-gray-500">d⊥ = 0.000 (sobre la línea)</p>
          </div>
        </div>

        <div class="bg-dark-bg2 rounded-lg p-4 font-mono text-xs space-y-2">
          <p class="text-gray-500 font-sans text-xs font-medium">Cálculo paso a paso para el knee point K = (0.405, 0.285):</p>
          <div class="ml-2 space-y-1">
            <p class="text-gray-500 font-sans mb-2">Datos: A = (0.000, 0.869), B = (1.000, 0.013), K = (0.405, 0.285)</p>
            <p>
              <span class="text-gray-500">Numerador:</span>
              <span class="text-white"> |(x<sub>K</sub>−x<sub>A</sub>)(y<sub>B</sub>−y<sub>A</sub>) − (y<sub>K</sub>−y<sub>A</sub>)(x<sub>B</sub>−x<sub>A</sub>)|</span>
            </p>
            <p class="ml-12 text-white">= |(0.405)(0.013 − 0.869) − (0.285 − 0.869)(1.000 − 0.000)|</p>
            <p class="ml-12 text-white">= |(0.405)(−0.857) − (−0.584)(1.000)|</p>
            <p class="ml-12 text-white">= |−0.347 − (−0.584)|</p>
            <p class="ml-12 text-white">= |0.238| = <strong class="text-accent-yellow">0.238</strong></p>
            <p class="mt-2">
              <span class="text-gray-500">Denominador:</span>
              <span class="text-white"> ‖B − A‖ = √(1.000² + 0.857²) = <strong class="text-accent-yellow">1.317</strong></span>
            </p>
            <div class="border-t border-dark-border pt-2 mt-2">
              <p>
                <span class="text-accent-yellow font-bold">d⊥ = 0.238 / 1.317 = 0.181</span>
              </p>
              <p class="text-gray-500 font-sans mt-1">
                Ninguna otra de las 406 soluciones tiene una distancia mayor → este punto es el knee.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Why this works - interpretation -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4 space-y-3">
        <h3 class="text-primary-300 font-bold text-sm">¿Por qué funciona este método?</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-gray-400">
          <div class="space-y-1">
            <p class="text-white font-medium">Antes del knee (zona A)</p>
            <p>Reducir f₁ (espera) cuesta <strong class="text-accent-green">poco</strong> en f₂ (disparidad).
            Cada mejora en espera es "barata" — el decisor obtiene mucho beneficio con poco sacrificio.</p>
          </div>
          <div class="space-y-1 bg-dark-bg1/50 rounded-lg p-2">
            <p class="text-accent-yellow font-medium">En el knee (punto óptimo)</p>
            <p>El <strong class="text-white">costo de oportunidad</strong> entre f₁ y f₂ se equilibra
            exactamente. Es el punto de transición donde una unidad de mejora en espera empieza a
            costar más de una unidad en disparidad.</p>
          </div>
          <div class="space-y-1">
            <p class="text-white font-medium">Después del knee (zona B)</p>
            <p>Cada mejora pequeña en f₁ empeora <strong class="text-accent-red">mucho</strong> f₂.
            Los rendimientos son fuertemente decrecientes — el sacrificio ya no vale la pena.</p>
          </div>
        </div>
        <p class="text-xs text-gray-500 leading-relaxed mt-2">
          <strong class="text-gray-400">En resumen:</strong>
          El knee point se convierte en el escenario <strong class="text-accent-yellow">"Equilibrio"</strong>
          de la aplicación. Se selecciona automáticamente, sin que el decisor asigne pesos subjetivos
          a los objetivos — es una elección puramente geométrica basada en la estructura del frente
          de Pareto. El resultado: <span class="font-mono text-gray-300">f₁ = 7.326 años de espera</span>
          y <span class="font-mono text-gray-300">f₂ = 5.118 años de disparidad</span>, un compromiso
          donde ambos objetivos obtienen valores razonables sin sacrificar excesivamente ninguno.
        </p>
      </div>
    </section>

    <!-- ============================== -->
    <!-- 8. COHERENCIA DEL PLANTEAMIENTO -->
    <!-- ============================== -->
    <section class="card space-y-4">
      <h2 class="text-lg font-bold text-white">8. Coherencia del Planteamiento</h2>

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
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">9. Configuración Experimental</h2>

      <p class="text-sm text-gray-400 leading-relaxed">
        Cada parámetro fue seleccionado con base en la literatura de HHO y optimización multiobjetivo,
        las características específicas de nuestro problema (105 variables de decisión, 3 objetivos),
        y validación empírica mediante análisis de convergencia. A continuación se justifica cada elección.
      </p>

      <!-- ── N = 50 ── -->
      <div class="bg-dark-bg1 rounded-lg overflow-hidden">
        <div class="flex items-center gap-4 p-4 border-b border-gray-700/50">
          <div class="flex-shrink-0 w-20 h-20 rounded-lg bg-accent-yellow/10 border border-accent-yellow/30 flex flex-col items-center justify-center">
            <span class="text-accent-yellow font-bold font-mono text-2xl leading-none">50</span>
            <span class="text-accent-yellow/70 text-[10px] uppercase mt-1">halcones</span>
          </div>
          <div>
            <h3 class="text-white font-semibold text-sm">N = 50 — Tamaño de Población</h3>
            <p class="text-gray-400 text-xs mt-1 leading-relaxed">
              Valor estándar en la literatura de HHO. Heidari et al. (2019) utilizaron N entre 30 y 50
              en su artículo original. Con <strong class="text-white">105 variables de decisión</strong>
              (21 países &times; 5 categorías), se necesita suficiente diversidad para explorar
              el espacio de búsqueda sin que cada iteración sea computacionalmente costosa.
            </p>
          </div>
        </div>
        <div class="grid grid-cols-3 divide-x divide-gray-700/50 text-xs">
          <div class="p-3 text-center">
            <p class="text-accent-red font-semibold mb-1">N &lt; 30 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Poca diversidad. Convergencia prematura: el frente de Pareto queda incompleto, perdiendo regiones de compromiso.</p>
          </div>
          <div class="p-3 text-center bg-accent-yellow/5">
            <p class="text-accent-yellow font-semibold mb-1">N = 50 &nbsp;&check;</p>
            <p class="text-gray-400 leading-snug">Equilibrio óptimo entre exploración del espacio y costo por iteración. Cobertura completa del frente de Pareto.</p>
          </div>
          <div class="p-3 text-center">
            <p class="text-accent-red font-semibold mb-1">N &gt; 100 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Rendimientos decrecientes. El ordenamiento por no-dominancia es O(N&sup2;): duplicar N cuadruplica el costo de selección.</p>
          </div>
        </div>
      </div>

      <!-- ── T = 500 ── -->
      <div class="bg-dark-bg1 rounded-lg overflow-hidden">
        <div class="flex items-center gap-4 p-4 border-b border-gray-700/50">
          <div class="flex-shrink-0 w-20 h-20 rounded-lg bg-accent-green/10 border border-accent-green/30 flex flex-col items-center justify-center">
            <span class="text-accent-green font-bold font-mono text-2xl leading-none">500</span>
            <span class="text-accent-green/70 text-[10px] uppercase mt-1">iteraciones</span>
          </div>
          <div>
            <h3 class="text-white font-semibold text-sm">T = 500 — Iteraciones por Corrida</h3>
            <p class="text-gray-400 text-xs mt-1 leading-relaxed">
              El análisis de convergencia muestra que el <strong class="text-white">95% del hipervolumen final</strong>
              se alcanza entre las iteraciones 80-120. Usar T = 500 proporciona un
              <strong class="text-white">margen de seguridad de 4-5&times;</strong>, asegurando convergencia total.
              El parámetro de energía E decrece linealmente de 2 &rarr; 0 a lo largo de T iteraciones;
              con 500 iteraciones, cada fase (exploración y explotación) dispone de suficientes ciclos
              para cubrir completamente su función.
            </p>
          </div>
        </div>
        <div class="grid grid-cols-3 divide-x divide-gray-700/50 text-xs">
          <div class="p-3 text-center">
            <p class="text-accent-red font-semibold mb-1">T &lt; 200 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Convergencia incompleta, especialmente para f&sub2; (equidad entre países), que requiere más iteraciones de ajuste fino.</p>
          </div>
          <div class="p-3 text-center bg-accent-green/5">
            <p class="text-accent-green font-semibold mb-1">T = 500 &nbsp;&check;</p>
            <p class="text-gray-400 leading-snug">Convergencia garantizada con margen amplio. La curva de HV se estabiliza completamente antes de la iteración 200.</p>
          </div>
          <div class="p-3 text-center">
            <p class="text-accent-red font-semibold mb-1">T &gt; 1000 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Cómputo desperdiciado: mejora &lt; 0.1% después de la iteración 500. Duplica el tiempo sin beneficio estadístico.</p>
          </div>
        </div>
      </div>

      <!-- ── Archive = 100 ── -->
      <div class="bg-dark-bg1 rounded-lg overflow-hidden">
        <div class="flex items-center gap-4 p-4 border-b border-gray-700/50">
          <div class="flex-shrink-0 w-20 h-20 rounded-lg bg-accent-blue/10 border border-accent-blue/30 flex flex-col items-center justify-center">
            <span class="text-accent-blue font-bold font-mono text-2xl leading-none">100</span>
            <span class="text-accent-blue/70 text-[10px] uppercase mt-1">archivo</span>
          </div>
          <div>
            <h3 class="text-white font-semibold text-sm">Archivo Pareto = 100 — Soluciones No-Dominadas</h3>
            <p class="text-gray-400 text-xs mt-1 leading-relaxed">
              El archivo externo almacena las mejores soluciones no-dominadas encontradas durante la optimización.
              Un tamaño de <strong class="text-white">100 soluciones</strong> proporciona cobertura densa del
              frente de Pareto 3D sin incurrir en sobrecarga de memoria ni comparaciones excesivas.
              Cuando el archivo se llena, las nuevas soluciones dominantes reemplazan a las de mayor
              <strong class="text-white">distancia de aglomeración</strong> (crowding distance), manteniendo
              diversidad en las regiones menos pobladas del frente.
            </p>
          </div>
        </div>
        <div class="grid grid-cols-1 text-xs">
          <div class="p-3 bg-accent-blue/5">
            <p class="text-accent-blue font-semibold mb-1 text-center">Pipeline de agregación</p>
            <div class="flex items-center justify-center gap-2 text-gray-400 flex-wrap">
              <span class="bg-dark-bg2 px-2 py-1 rounded font-mono">30 corridas</span>
              <span>&times;</span>
              <span class="bg-dark-bg2 px-2 py-1 rounded font-mono">100 max</span>
              <span>&rarr;</span>
              <span class="bg-dark-bg2 px-2 py-1 rounded font-mono">&le; 3,000</span>
              <span class="text-gray-500">&rarr; filtro no-dominancia &rarr;</span>
              <span class="bg-accent-blue/20 text-accent-blue px-2 py-1 rounded font-mono font-bold">406 Pareto</span>
            </div>
            <p class="text-gray-500 mt-2 text-center leading-snug">
              De hasta 3,000 soluciones candidatas, solo 406 sobreviven el filtro de no-dominancia combinado,
              formando el frente de Pareto final que representa los mejores compromisos posibles.
            </p>
          </div>
        </div>
      </div>

      <!-- ── 30 corridas ── -->
      <div class="bg-dark-bg1 rounded-lg overflow-hidden">
        <div class="flex items-center gap-4 p-4 border-b border-gray-700/50">
          <div class="flex-shrink-0 w-20 h-20 rounded-lg bg-primary/10 border border-primary/30 flex flex-col items-center justify-center">
            <span class="text-primary-300 font-bold font-mono text-2xl leading-none">30</span>
            <span class="text-primary-300/70 text-[10px] uppercase mt-1">corridas</span>
          </div>
          <div>
            <h3 class="text-white font-semibold text-sm">30 Corridas Independientes — Validez Estadística</h3>
            <p class="text-gray-400 text-xs mt-1 leading-relaxed">
              Con <strong class="text-white">n &ge; 30</strong>, el
              <strong class="text-white">Teorema del Límite Central</strong> garantiza que la distribución muestral
              de la media es aproximadamente normal, lo que habilita intervalos de confianza y pruebas de
              hipótesis válidas independientemente de la distribución subyacente. Cada corrida utiliza una
              <strong class="text-white">semilla diferente</strong> (seeds 42-71), generando poblaciones iniciales
              distintas que exploran regiones diferentes del espacio de búsqueda.
            </p>
          </div>
        </div>
        <div class="grid grid-cols-3 divide-x divide-gray-700/50 text-xs">
          <div class="p-3 text-center">
            <p class="text-accent-red font-semibold mb-1">n &lt; 20 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Muestra insuficiente para normalidad asintótica. Intervalos de confianza poco fiables; no se cumplen supuestos del TLC.</p>
          </div>
          <div class="p-3 text-center bg-primary/5">
            <p class="text-primary-300 font-semibold mb-1">n = 30 &nbsp;&check;</p>
            <p class="text-gray-400 leading-snug">CV = 1.56% entre corridas: alta consistencia. Estándar en competencias CEC (requieren 25-51 corridas).</p>
          </div>
          <div class="p-3 text-center">
            <p class="text-gray-500 font-semibold mb-1">n &gt; 50 &nbsp;&darr;</p>
            <p class="text-gray-500 leading-snug">Mayor precisión estadística marginal, pero el costo computacional crece linealmente sin cambio cualitativo en conclusiones.</p>
          </div>
        </div>
      </div>

      <!-- Métrica de convergencia -->
      <div class="bg-primary/5 border border-primary/20 rounded-lg p-4 text-xs space-y-2">
        <p class="text-gray-300 leading-relaxed">
          <strong class="text-primary-300">Métrica de convergencia:</strong>
          <strong class="text-white">Hipervolumen 3D</strong> con punto de referencia
          (10.0, 16.0, 50,000) — mide el volumen del espacio objetivo dominado por el frente de Pareto.
          Esta métrica captura simultáneamente la convergencia (cercanía al frente óptimo) y la diversidad
          (cobertura uniforme del frente), siendo el indicador más completo para evaluar algoritmos multiobjetivo.
        </p>
        <p class="text-gray-500 leading-relaxed">
          <strong class="text-gray-400">Resultado:</strong> HV medio = 0.8934, desviación estándar = 0.0139,
          CV = 1.56% — lo que confirma que MOHHO produce resultados estables y reproducibles
          a través de las 30 corridas independientes.
        </p>
      </div>
    </section>
  </div>
</template>
