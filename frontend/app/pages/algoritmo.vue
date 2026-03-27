<script setup lang="ts">
definePageMeta({ prerender: true })
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto">
    <h1 class="section-title">Algoritmo MOHHO</h1>
    <p class="text-sm text-gray-400 -mt-4 leading-relaxed max-w-3xl">
      Multi-Objective Harris Hawks Optimization: arquitectura completa, operadores,
      codificaci&oacute;n y conexi&oacute;n entre la teor&iacute;a y el c&oacute;digo Python.
    </p>

    <!-- ============================= -->
    <!-- 1. ARQUITECTURA DEL SISTEMA   -->
    <!-- ============================= -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">1. Arquitectura del Sistema</h2>
      <p class="text-sm text-gray-400">
        La aplicaci&oacute;n se divide en un backend Python (FastAPI) que ejecuta el algoritmo y un frontend
        TypeScript (Nuxt&nbsp;4) que visualiza resultados en tiempo real.
      </p>

      <div class="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-4 items-start">
        <!-- Frontend -->
        <div class="space-y-2">
          <div class="bg-primary/10 border border-primary/30 rounded-lg px-4 py-2 text-center">
            <p class="text-primary-300 font-bold text-sm">FRONTEND &mdash; Nuxt 4 + Vue 3</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-dark-border text-xs space-y-1.5">
            <p class="text-white font-medium">8 p&aacute;ginas interactivas</p>
            <p class="text-gray-500">Modelo, Pareto, Asignaci&oacute;n, Impacto, Convergencia, Simulaci&oacute;n&hellip;</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-dark-border text-xs space-y-1.5">
            <p class="text-white font-medium">Composables reactivos</p>
            <p class="text-gray-500">useSimulation (WebSocket), useOptimizer (REST), useScenario (estado global)</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-dark-border text-xs space-y-1.5">
            <p class="text-white font-medium">Visualizaci&oacute;n</p>
            <p class="text-gray-500">ECharts (2D/3D), Canvas (HawkHunt animaci&oacute;n cin&eacute;matica)</p>
          </div>
        </div>

        <!-- Connection -->
        <div class="hidden lg:flex flex-col items-center justify-center gap-2 py-8">
          <div class="text-accent-yellow text-xs font-mono">REST API</div>
          <div class="flex items-center gap-1 text-accent-yellow">
            <span>&larr;</span>
            <span class="w-16 h-px bg-accent-yellow/40" />
            <span>&rarr;</span>
          </div>
          <div class="text-accent-green text-xs font-mono mt-4">WebSocket</div>
          <div class="flex items-center gap-1 text-accent-green">
            <span>&larr;</span>
            <span class="w-16 h-px bg-accent-green/40 border-dashed" />
            <span>&rarr;</span>
          </div>
        </div>

        <!-- Backend -->
        <div class="space-y-2">
          <div class="bg-accent-green/10 border border-accent-green/30 rounded-lg px-4 py-2 text-center">
            <p class="text-accent-green font-bold text-sm">BACKEND &mdash; FastAPI + Python 3.12</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-dark-border text-xs space-y-1.5">
            <p class="text-white font-medium">app/api/</p>
            <p class="text-gray-500">12 endpoints REST + 1 WebSocket (/ws/simulation)</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/20 text-xs space-y-1.5">
            <p class="text-accent-yellow font-medium">app/core/mohho.py</p>
            <p class="text-gray-500">Runner MOHHO: archivo Pareto, crowding distance, hipervolumen</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/20 text-xs space-y-1.5">
            <p class="text-accent-yellow font-medium">app/core/hho.py</p>
            <p class="text-gray-500">6 operadores HHO + vuelo de L&eacute;vy + energ&iacute;a de escape</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/20 text-xs space-y-1.5">
            <p class="text-accent-yellow font-medium">app/core/decoder.py</p>
            <p class="text-gray-500">SPV (argsort) + decodificador greedy con restricciones</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 border border-accent-yellow/20 text-xs space-y-1.5">
            <p class="text-accent-yellow font-medium">app/core/problem.py</p>
            <p class="text-gray-500">Evaluador: f&#8321;(espera), f&#8322;(disparidad), f&#8323;(desperdicio)</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================== -->
    <!-- 2. FLUJO DEL ALGORITMO MOHHO   -->
    <!-- ============================== -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">2. Flujo del Algoritmo MOHHO</h2>
      <p class="text-sm text-gray-400">
        Diagrama del ciclo completo de optimizaci&oacute;n, desde la inicializaci&oacute;n hasta la convergencia del frente de Pareto.
      </p>

      <div class="relative pl-10">
        <!-- Vertical gradient line -->
        <div class="absolute left-[14px] top-2 bottom-2 w-0.5 bg-gradient-to-b from-primary via-accent-yellow to-accent-red rounded-full" />

        <!-- Step 1 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-primary border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
            <p class="text-primary-300 font-bold text-sm mb-1">1. Inicializaci&oacute;n</p>
            <p class="text-xs text-gray-400">Generar <strong class="text-white">N</strong> halcones aleatorios en el hipercubo [0,&nbsp;1]<sup>105</sup></p>
            <pre class="mt-2 text-[11px] text-gray-500 font-mono bg-black/30 rounded p-2 overflow-x-auto">population = rng.random((pop_size, 105))   # N vectores continuos
archive = []                                # Archivo Pareto vac&iacute;o</pre>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-primary border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
            <p class="text-primary-300 font-bold text-sm mb-1">2. Evaluaci&oacute;n (por cada halc&oacute;n)</p>
            <div class="flex flex-wrap items-center gap-2 mt-2 text-xs font-mono">
              <span class="bg-primary/20 text-primary-300 px-2 py-1 rounded">H &isin; [0,1]<sup>105</sup></span>
              <span class="text-gray-500">&rarr;</span>
              <span class="bg-accent-yellow/20 text-accent-yellow px-2 py-1 rounded">&pi; = argsort(H)</span>
              <span class="text-gray-500">&rarr;</span>
              <span class="bg-accent-green/20 text-accent-green px-2 py-1 rounded">x = greedy(&pi;)</span>
              <span class="text-gray-500">&rarr;</span>
              <span class="bg-accent-red/20 text-accent-red px-2 py-1 rounded">F(x) = (f&#8321;, f&#8322;, f&#8323;)</span>
            </div>
            <p class="text-[11px] text-gray-500 mt-2">SPV convierte continuo &rarr; permutaci&oacute;n; el greedy decoder asigna visas respetando R1&ndash;R6.</p>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-green border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
            <p class="text-accent-green font-bold text-sm mb-1">3. Actualizar Archivo Pareto</p>
            <p class="text-xs text-gray-400">
              Insertar soluciones no dominadas. Eliminar las dominadas.
              Si el archivo excede 100 soluciones, podar por <strong class="text-white">crowding distance</strong> m&iacute;nima.
            </p>
          </div>
        </div>

        <!-- Step 4: Iteration loop -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-yellow border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold text-sm mb-2">4. Bucle Principal (t = 1 &hellip; max_iter)</p>
            <p class="text-xs text-gray-400 mb-3">Para cada halc&oacute;n, seleccionar l&iacute;der del archivo y calcular energ&iacute;a:</p>
            <div class="bg-black/30 rounded-lg p-3 font-mono text-[11px] text-gray-400 mb-3">
              E(t) = 2 &middot; (1 - t/T) &middot; r&#8320;&nbsp;&nbsp;&nbsp;<span class="text-gray-600"># r&#8320; &isin; [-1,1] aleatorio</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div class="bg-blue-500/10 rounded-lg p-3 border border-blue-500/20">
                <p class="text-blue-400 font-bold mb-1">|E| &ge; 1 &rarr; Exploraci&oacute;n</p>
                <p class="text-gray-500"><strong>OP1:</strong> Posici&oacute;n aleatoria de la poblaci&oacute;n</p>
                <p class="text-gray-500"><strong>OP2:</strong> Media de la poblaci&oacute;n + presa</p>
              </div>
              <div class="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/20">
                <p class="text-yellow-400 font-bold mb-1">|E| &lt; 1, r &ge; 0.5 &rarr; Siege Suave</p>
                <p class="text-gray-500"><strong>OP3:</strong> Siege suave est&aacute;ndar</p>
                <p class="text-gray-500"><strong>OP5:</strong> Siege suave + L&eacute;vy</p>
              </div>
              <div class="bg-red-500/10 rounded-lg p-3 border border-red-500/20">
                <p class="text-red-400 font-bold mb-1">|E| &lt; 1, r &lt; 0.5 &rarr; Siege Duro</p>
                <p class="text-gray-500"><strong>OP4:</strong> Convergencia agresiva</p>
                <p class="text-gray-500"><strong>OP6:</strong> Siege duro + L&eacute;vy</p>
              </div>
            </div>

            <p class="text-[11px] text-gray-500 mt-3">
              Aceptaci&oacute;n greedy: si el candidato domina al halc&oacute;n actual, se reemplaza.
              Luego se actualiza el archivo Pareto y se calcula el hipervolumen 3D.
            </p>
          </div>
        </div>

        <!-- Step 5 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-yellow border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
            <p class="text-accent-yellow font-bold text-sm mb-1">5. Selecci&oacute;n de L&iacute;der (Presa)</p>
            <p class="text-xs text-gray-400">
              El &ldquo;rabbit&rdquo; (presa) se selecciona del archivo mediante <strong class="text-white">torneo por crowding distance</strong>,
              favoreciendo soluciones en regiones menos densas del frente para mantener diversidad.
            </p>
          </div>
        </div>

        <!-- Step 6 -->
        <div class="relative pb-5">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-green border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
            <p class="text-accent-green font-bold text-sm mb-1">6. Criterio de Parada</p>
            <p class="text-xs text-gray-400">
              Si <code class="text-white">t &lt; max_iter</code> &rarr; volver al paso 4.
              Si no, retornar el <strong class="text-accent-green">Frente de Pareto</strong> (archivo completo) y el historial de hipervolumen.
            </p>
          </div>
        </div>

        <!-- Step 7 -->
        <div class="relative">
          <div class="absolute left-[-30px] top-1 w-4 h-4 rounded-full bg-accent-red border-2 border-dark-bg1 z-10" />
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-red/20">
            <p class="text-accent-red font-bold text-sm mb-1">7. Post-Procesamiento</p>
            <p class="text-xs text-gray-400">
              Se decodifica cada soluci&oacute;n Pareto en una asignaci&oacute;n de visas.
              Se seleccionan 5 escenarios (knee point, extremos de cada objetivo, FIFO).
              Se calcula el impacto &Delta; por pa&iacute;s vs. la l&iacute;nea base FIFO.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================ -->
    <!-- 3. PIPELINE DE CODIFICACI&Oacute;N -->
    <!-- ================================ -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">3. Pipeline de Codificaci&oacute;n: Continuo &rarr; Entero</h2>
      <p class="text-sm text-gray-400">
        La codificaci&oacute;n indirecta en 3 capas es el puente entre el espacio continuo de MOHHO y el espacio
        discreto del problema de asignaci&oacute;n.
      </p>

      <!-- Visual pipeline -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-primary/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-primary/20 text-primary-300 px-2 py-0.5 rounded text-xs font-bold">CAPA 1</span>
            <span class="text-white font-semibold text-sm">Halc&oacute;n Continuo</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-primary-300">H = [0.32, 0.87, 0.15, 0.64, ...]</p>
            <p class="text-gray-500"># 105 valores &isin; [0, 1]</p>
            <p class="text-gray-500"># cada posici&oacute;n = 1 grupo (pa&iacute;s,cat)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            MOHHO evoluciona estos vectores con sus 6 operadores sin modificaci&oacute;n.
            El espacio [0,1]<sup>105</sup> es compacto y continuo.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-accent-yellow/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-accent-yellow/20 text-accent-yellow px-2 py-0.5 rounded text-xs font-bold">CAPA 2</span>
            <span class="text-white font-semibold text-sm">SPV &rarr; Permutaci&oacute;n</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-accent-yellow">&pi; = argsort(H)</p>
            <p class="text-gray-400">H  = [0.32, 0.87, <span class="text-accent-green">0.15</span>, 0.64, ...]</p>
            <p class="text-gray-400">&pi; = [<span class="text-accent-green">2</span>, 0, 3, 1, ...]</p>
            <p class="text-gray-500"># grupo 2 tiene prioridad m&aacute;xima</p>
          </div>
          <p class="text-[11px] text-gray-500">
            <strong class="text-gray-400">argsort</strong> ordena &iacute;ndices por valor ascendente.
            El grupo con menor valor en H recibe la mayor prioridad de asignaci&oacute;n.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-xl p-5 border-2 border-accent-green/30 space-y-3">
          <div class="flex items-center gap-2">
            <span class="bg-accent-green/20 text-accent-green px-2 py-0.5 rounded text-xs font-bold">CAPA 3</span>
            <span class="text-white font-semibold text-sm">Decodificador Greedy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-3 space-y-1">
            <p class="text-gray-400">for g in &pi;:</p>
            <p class="text-accent-green">&nbsp;&nbsp;x[g] = min(demand[g],</p>
            <p class="text-accent-green">&nbsp;&nbsp;&nbsp;&nbsp;remaining_visas,</p>
            <p class="text-accent-green">&nbsp;&nbsp;&nbsp;&nbsp;country_cap[g],</p>
            <p class="text-accent-green">&nbsp;&nbsp;&nbsp;&nbsp;category_cap[g])</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Asigna visas en orden de prioridad respetando <strong class="text-gray-400">todas las restricciones</strong>
            (R1&ndash;R6). Resultado: asignaci&oacute;n <em>siempre factible</em>.
          </p>
        </div>
      </div>

      <!-- Detailed SPV explanation -->
      <div class="bg-dark-bg1 rounded-xl p-5 border border-primary/20 space-y-4">
        <h3 class="text-sm font-bold text-primary-300">&iquest;Por qu&eacute; valores de 0 a 1? &iquest;Por qu&eacute; 105 dimensiones?</h3>
        <div class="text-xs text-gray-400 space-y-2 leading-relaxed">
          <p>
            Cada <strong class="text-white">halc&oacute;n</strong> es un vector de <strong class="text-accent-yellow">105 n&uacute;meros reales &isin; [0, 1]</strong>.
            Los 105 valores corresponden a los 105 grupos del problema: <strong class="text-white">21 pa&iacute;ses &times; 5 categor&iacute;as EB</strong>.
          </p>
          <div class="font-mono text-[11px] bg-black/40 rounded p-3 space-y-1.5">
            <p class="text-gray-500"># Ejemplo: un halc&oacute;n con 105 valores</p>
            <p>
              <span class="text-gray-500">Pos 0</span> <span class="text-primary-300">(China, EB-1)</span> &rarr; <span class="text-accent-yellow">0.71</span>
              <span class="text-gray-600 ml-2">&larr; prioridad baja (valor alto)</span>
            </p>
            <p>
              <span class="text-gray-500">Pos 1</span> <span class="text-primary-300">(China, EB-2)</span> &rarr; <span class="text-accent-green">0.12</span>
              <span class="text-gray-600 ml-2">&larr; prioridad alta (valor bajo)</span>
            </p>
            <p>
              <span class="text-gray-500">Pos 2</span> <span class="text-primary-300">(China, EB-3)</span> &rarr; <span class="text-accent-yellow">0.48</span>
              <span class="text-gray-600 ml-2">&larr; prioridad media</span>
            </p>
            <p class="text-gray-500">... (105 posiciones en total)</p>
            <p>
              <span class="text-gray-500">Pos 104</span> <span class="text-primary-300">(Otros, EB-5)</span> &rarr; <span class="text-accent-red">0.95</span>
              <span class="text-gray-600 ml-2">&larr; prioridad muy baja</span>
            </p>
          </div>
          <p>
            Los valores <strong class="text-white">NO representan visas</strong>. Un valor como 0.71 indica la
            <em>prioridad relativa</em> del grupo. Al aplicar <strong class="text-accent-yellow">argsort</strong>,
            los grupos con valores m&aacute;s bajos reciben visas primero:
          </p>
          <div class="font-mono text-[11px] bg-black/40 rounded p-3 space-y-1">
            <p>H = [<span class="text-accent-yellow">0.71</span>, <span class="text-accent-green">0.12</span>, <span class="text-accent-yellow">0.48</span>, <span class="text-accent-red">0.95</span>, ...]</p>
            <p>&pi; = argsort(H) = [<span class="text-accent-green">1</span>, 2, 0, 3, ...]</p>
            <p class="text-gray-500">&darr;</p>
            <p class="text-white">Grupo 1 (China, EB-2) recibe visas primero &rarr; 0.12 es el valor m&aacute;s bajo</p>
            <p class="text-white">Grupo 2 (China, EB-3) recibe visas segundo &rarr; 0.48</p>
            <p class="text-white">Grupo 0 (China, EB-1) recibe visas tercero &rarr; 0.71</p>
            <p class="text-gray-500">... y as&iacute; sucesivamente hasta agotar las 140,000 visas</p>
          </div>
          <p>
            <strong class="text-gray-300">&iquest;Por qu&eacute; [0, 1] y no enteros?</strong> Porque MOHHO es una metaheur&iacute;stica
            <em>continua</em>: sus 6 operadores (exploraci&oacute;n, asedio, vuelo de L&eacute;vy) mueven los halcones
            en un espacio continuo. SPV es el puente que transforma ese espacio continuo
            en una asignaci&oacute;n discreta v&aacute;lida.
          </p>
        </div>
      </div>

      <p class="text-xs text-gray-500 leading-relaxed bg-dark-bg1 rounded-lg p-4">
        <strong class="text-gray-400">Propiedad clave:</strong>
        Vecinos cercanos en [0,1]<sup>105</sup> producen permutaciones similares (pocos intercambios),
        lo que a su vez genera asignaciones similares. Esto preserva la <em>localidad</em> necesaria
        para que la b&uacute;squeda heur&iacute;stica sea efectiva: peque&ntilde;os movimientos del halc&oacute;n
        &rarr; peque&ntilde;os cambios en prioridad &rarr; peque&ntilde;os ajustes en la asignaci&oacute;n.
      </p>
    </section>

    <!-- ================================= -->
    <!-- 4. LOS 6 OPERADORES DE HHO        -->
    <!-- ================================= -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">4. Los 6 Operadores de Harris Hawks</h2>
      <p class="text-sm text-gray-400">
        La energ&iacute;a de escape E(t) = 2(1 - t/T)&middot;r controla la transici&oacute;n entre fases.
        Cada operador modifica la posici&oacute;n del halc&oacute;n de forma diferente.
      </p>

      <!-- Energy diagram -->
      <div class="bg-dark-bg1 rounded-lg p-4 text-center">
        <div class="flex items-center justify-center gap-4 text-xs font-mono flex-wrap">
          <span class="text-blue-400">|E| = 2.0</span>
          <span class="w-8 h-px bg-blue-400/40" />
          <span class="text-blue-400">Exploraci&oacute;n</span>
          <span class="w-8 h-px bg-gray-600" />
          <span class="text-accent-yellow">|E| = 1.0</span>
          <span class="w-8 h-px bg-accent-yellow/40" />
          <span class="text-accent-yellow">Transici&oacute;n</span>
          <span class="w-8 h-px bg-gray-600" />
          <span class="text-accent-red">|E| = 0.0</span>
          <span class="w-8 h-px bg-accent-red/40" />
          <span class="text-accent-red">Siege</span>
        </div>
        <p class="text-[10px] text-gray-600 mt-2">t = 0 &rarr; Exploraci&oacute;n pura &nbsp;&nbsp;|&nbsp;&nbsp; t = T &rarr; Explotaci&oacute;n pura</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- OP1 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-blue-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-blue-400/20 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded">OP1</span>
            <span class="text-white font-medium text-sm">Exploraci&oacute;n &mdash; Aleatoria</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-blue-300">X(t+1) = X_rand - r&#8321; |X_rand - 2r&#8322; X(t)|</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Usa un halc&oacute;n aleatorio de la poblaci&oacute;n como referencia.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &ge; 1, q &ge; 0.5
          </p>
        </div>

        <!-- OP2 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-blue-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-blue-400/20 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded">OP2</span>
            <span class="text-white font-medium text-sm">Exploraci&oacute;n &mdash; Media</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-blue-300">X(t+1) = (X_rabbit - X_mean) - r&#8323; (lb + r&#8324; (ub - lb))</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Combina la posici&oacute;n del l&iacute;der (presa) con la media de toda la poblaci&oacute;n.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &ge; 1, q &lt; 0.5
          </p>
        </div>

        <!-- OP3 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-yellow-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-yellow-400/20 text-yellow-400 text-[10px] font-bold px-2 py-0.5 rounded">OP3</span>
            <span class="text-white font-medium text-sm">Siege Suave</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-yellow-300">X(t+1) = &Delta;X(t) - E |J&middot;X_rabbit - X(t)|</p>
            <p class="text-gray-500">&Delta;X = X_rabbit - X(t),  J = 2(1 - r&#8325;)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Acercamiento progresivo. J simula el salto de la presa.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &lt; 1, |E| &ge; 0.5, r &ge; 0.5
          </p>
        </div>

        <!-- OP4 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-red-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-red-400/20 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded">OP4</span>
            <span class="text-white font-medium text-sm">Siege Duro</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-red-300">X(t+1) = X_rabbit - E |&Delta;X(t)|</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Convergencia agresiva directa hacia la presa.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &lt; 1, |E| &lt; 0.5, r &ge; 0.5
          </p>
        </div>

        <!-- OP5 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-yellow-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-yellow-400/20 text-yellow-400 text-[10px] font-bold px-2 py-0.5 rounded">OP5</span>
            <span class="text-white font-medium text-sm">Siege Suave + L&eacute;vy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-yellow-300">Y = X_rabbit - E |J&middot;X_rabbit - X(t)|</p>
            <p class="text-yellow-300">Z = Y + S &times; L&eacute;vy(&beta;=1.5)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Siege suave con perturbaci&oacute;n L&eacute;vy para escape de &oacute;ptimos locales.
            Se acepta el mejor entre Y y Z.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &ge; 0.5, r &lt; 0.5
          </p>
        </div>

        <!-- OP6 -->
        <div class="bg-dark-bg1 rounded-lg p-4 border-l-4 border-red-400">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-red-400/20 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded">OP6</span>
            <span class="text-white font-medium text-sm">Siege Duro + L&eacute;vy</span>
          </div>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
            <p class="text-red-300">Y = X_rabbit - E |J&middot;X_rabbit - X_mean|</p>
            <p class="text-red-300">Z = Y + S &times; L&eacute;vy(&beta;=1.5)</p>
          </div>
          <p class="text-[11px] text-gray-500">
            Siege duro usando la media poblacional. L&eacute;vy proporciona saltos largos
            para mayor exploraci&oacute;n tard&iacute;a.
            <strong class="text-gray-400">Condici&oacute;n:</strong> |E| &lt; 0.5, r &lt; 0.5
          </p>
        </div>
      </div>

      <!-- Lévy flight detail -->
      <div class="bg-dark-bg1 rounded-lg p-4 border border-purple-500/20">
        <h3 class="text-purple-400 font-bold text-sm mb-2">Vuelo de L&eacute;vy (&beta; = 1.5)</h3>
        <div class="font-mono text-[11px] bg-black/30 rounded p-2 mb-2">
          <p class="text-purple-300">&sigma; = (&Gamma;(1+&beta;) &middot; sin(&pi;&beta;/2) / (&Gamma;((1+&beta;)/2) &middot; &beta; &middot; 2<sup>(&beta;-1)/2</sup>))<sup>1/&beta;</sup></p>
          <p class="text-purple-300">L&eacute;vy = u &middot; &sigma; / |v|<sup>1/&beta;</sup>,&nbsp;&nbsp;u,v ~ N(0,1)</p>
        </div>
        <p class="text-[11px] text-gray-500">
          Los vuelos de L&eacute;vy generan movimientos con <strong class="text-gray-400">colas pesadas</strong>:
          mayoritariamente pasos cortos con saltos largos ocasionales. Esto permite
          escapar de &oacute;ptimos locales sin perder la convergencia general.
        </p>
      </div>
    </section>

    <!-- ===================================== -->
    <!-- 5. CONEXI&Oacute;N TEOR&Iacute;A &harr; C&Oacute;DIGO -->
    <!-- ===================================== -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">5. Conexi&oacute;n Teor&iacute;a &harr; C&oacute;digo</h2>
      <p class="text-sm text-gray-400">
        Cada componente te&oacute;rico del algoritmo tiene su implementaci&oacute;n directa en el c&oacute;digo.
      </p>

      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-dark-border">
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Concepto Te&oacute;rico</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Archivo</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Funci&oacute;n / Clase</th>
              <th class="text-left py-2 px-3 text-gray-500 uppercase tracking-wider">Descripci&oacute;n</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-border/50">
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Energ&iacute;a de escape E(t)</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">escape_energy()</td>
              <td class="py-2.5 px-3 text-gray-500">E = 2(1 - t/T) &middot; (2r - 1)</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-blue-400 font-medium">OP1: Exploraci&oacute;n aleatoria</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op1_exploration_random()</td>
              <td class="py-2.5 px-3 text-gray-500">Referencia: miembro aleatorio</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-blue-400 font-medium">OP2: Exploraci&oacute;n media</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op2_exploration_mean()</td>
              <td class="py-2.5 px-3 text-gray-500">Referencia: centroide + presa</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-yellow-400 font-medium">OP3: Siege suave</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op3_soft_siege()</td>
              <td class="py-2.5 px-3 text-gray-500">Persecuci&oacute;n gradual</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-red-400 font-medium">OP4: Siege duro</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op4_hard_siege()</td>
              <td class="py-2.5 px-3 text-gray-500">Convergencia directa</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-yellow-400 font-medium">OP5: Siege suave + L&eacute;vy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op5_soft_siege_levy()</td>
              <td class="py-2.5 px-3 text-gray-500">Con perturbaci&oacute;n L&eacute;vy</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-red-400 font-medium">OP6: Siege duro + L&eacute;vy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">op6_hard_siege_levy()</td>
              <td class="py-2.5 px-3 text-gray-500">Media + L&eacute;vy para escape</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-purple-400 font-medium">Vuelo de L&eacute;vy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">hho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">levy_flight()</td>
              <td class="py-2.5 px-3 text-gray-500">&beta;=1.5, Mantegna's algorithm</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">SPV &rarr; Permutaci&oacute;n</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">decoder.py</td>
              <td class="py-2.5 px-3 font-mono text-white">spv(hawk)</td>
              <td class="py-2.5 px-3 text-gray-500">argsort estable del vector</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">Decodificador greedy</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">decoder.py</td>
              <td class="py-2.5 px-3 font-mono text-white">decode(perm, ...)</td>
              <td class="py-2.5 px-3 text-gray-500">Asignaci&oacute;n factible R1&ndash;R6</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-green font-medium">Evaluador 3 objetivos</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">problem.py</td>
              <td class="py-2.5 px-3 font-mono text-white">evaluate(allocation)</td>
              <td class="py-2.5 px-3 text-gray-500">f&#8321;, f&#8322;, f&#8323; + visas usadas</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Dominancia Pareto</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">dominates(a, b)</td>
              <td class="py-2.5 px-3 text-gray-500">&le; en todos, &lt; en al menos uno</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Crowding distance</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">crowding_distance()</td>
              <td class="py-2.5 px-3 text-gray-500">NSGA-II para diversidad</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-yellow font-medium">Hipervolumen 3D</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">mohho.py</td>
              <td class="py-2.5 px-3 font-mono text-white">hypervolume_3d()</td>
              <td class="py-2.5 px-3 text-gray-500">Ref: (10, 16, 50000)</td>
            </tr>
            <tr>
              <td class="py-2.5 px-3 text-accent-red font-medium">L&iacute;nea base FIFO</td>
              <td class="py-2.5 px-3 font-mono text-gray-400">fifo.py</td>
              <td class="py-2.5 px-3 font-mono text-white">fifo_allocation()</td>
              <td class="py-2.5 px-3 text-gray-500">Orden por fecha de prioridad</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ================================= -->
    <!-- 6. GESTI&Oacute;N DEL ARCHIVO PARETO -->
    <!-- ================================= -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">6. Gesti&oacute;n del Archivo Pareto</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
          <h3 class="text-accent-green font-bold text-sm mb-2">Dominancia de Pareto</h3>
          <p class="text-xs text-gray-400 mb-2">
            Una soluci&oacute;n <strong class="text-white">a</strong> domina a <strong class="text-white">b</strong> si:
          </p>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2">
            <p class="text-accent-green">a &le; b en todos los objetivos</p>
            <p class="text-accent-green">a &lt; b en al menos un objetivo</p>
          </div>
          <p class="text-[11px] text-gray-500 mt-2">
            El archivo solo contiene soluciones <strong class="text-gray-400">mutuamente no dominadas</strong>.
          </p>
        </div>

        <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
          <h3 class="text-accent-yellow font-bold text-sm mb-2">Crowding Distance (NSGA-II)</h3>
          <p class="text-xs text-gray-400 mb-2">
            Mide el espacio alrededor de cada soluci&oacute;n en el frente:
          </p>
          <div class="font-mono text-[11px] bg-black/30 rounded p-2">
            <p class="text-accent-yellow">CD(i) = &Sigma;<sub>m</sub> (f<sub>m</sub>[i+1] - f<sub>m</sub>[i-1]) / (f<sub>m,max</sub> - f<sub>m,min</sub>)</p>
          </div>
          <p class="text-[11px] text-gray-500 mt-2">
            Mayor CD = regi&oacute;n menos densa. Se usa para:
            (1) seleccionar l&iacute;der, (2) podar archivo cuando excede capacidad.
          </p>
        </div>
      </div>

      <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
        <h3 class="text-primary-300 font-bold text-sm mb-2">Hipervolumen 3D</h3>
        <p class="text-xs text-gray-400 mb-2">
          M&eacute;trica de calidad del frente de Pareto. Mide el volumen del espacio objetivo
          dominado entre el frente y un punto de referencia.
        </p>
        <div class="font-mono text-[11px] bg-black/30 rounded p-2">
          <p class="text-primary-300">HV = Vol({y &isin; &real;<sup>3</sup> : &exist; x &isin; PF tal que x &le; y &le; ref})</p>
          <p class="text-gray-500">ref = (10.0, 16.0, 50000)   # siempre domina al frente</p>
        </div>
        <p class="text-[11px] text-gray-500 mt-2">
          <strong class="text-gray-400">Mayor HV = mejor frente.</strong>
          Es la &uacute;nica m&eacute;trica unaria que es Pareto-compatible:
          si el frente A domina completamente al frente B, entonces HV(A) &gt; HV(B).
        </p>
      </div>
    </section>

    <!-- ============================ -->
    <!-- 7. C&Oacute;DIGO CLAVE          -->
    <!-- ============================ -->
    <section class="card space-y-5">
      <h2 class="text-lg font-bold text-white">7. C&oacute;digo Clave</h2>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-yellow">hho.py</strong> &mdash; Operador de escape energy + Siege suave
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">escape_energy</span>(t: int, max_t: int, rng) -> float:
    <span class="text-gray-600">"""E(t) decrece de 2 a 0 con ruido."""</span>
    E0 = 2 * rng.random() - 1
    <span class="text-blue-400">return</span> 2 * E0 * (1 - t / max_t)

<span class="text-blue-400">def</span> <span class="text-accent-green">op3_soft_siege</span>(x, x_rabbit, E, J, rng):
    <span class="text-gray-600">"""Siege suave: persecuci&oacute;n gradual."""</span>
    delta = x_rabbit - x
    <span class="text-blue-400">return</span> clip_bounds(delta - E * np.abs(J * x_rabbit - x))</pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-green">decoder.py</strong> &mdash; SPV + Greedy decoder
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">spv</span>(hawk: np.ndarray) -> np.ndarray:
    <span class="text-gray-600">"""Smallest Position Value: continuo &rarr; permutaci&oacute;n."""</span>
    <span class="text-blue-400">return</span> np.argsort(hawk, kind=<span class="text-accent-yellow">"stable"</span>)

<span class="text-blue-400">def</span> <span class="text-accent-green">decode</span>(perm, groups, total_visas, country_cap, cat_caps):
    allocation = np.zeros(len(groups), dtype=int)
    remaining = total_visas
    used_country = defaultdict(int)
    used_cat = defaultdict(int)

    <span class="text-blue-400">for</span> idx <span class="text-blue-400">in</span> perm:
        g = groups[idx]
        available = <span class="text-accent-yellow">min</span>(
            g.n,                                  <span class="text-gray-600"># R2: demanda</span>
            remaining,                            <span class="text-gray-600"># R1: presupuesto total</span>
            country_cap - used_country[g.country], <span class="text-gray-600"># R3: tope pa&iacute;s</span>
            cat_caps[g.cat] - used_cat[g.cat],     <span class="text-gray-600"># R4: tope categor&iacute;a</span>
        )
        allocation[idx] = available
        remaining -= available
        used_country[g.country] += available
        used_cat[g.cat] += available

    <span class="text-blue-400">return</span> allocation</pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-primary-300">mohho.py</strong> &mdash; Bucle principal + archivo Pareto
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">run_mohho</span>(pop_size, max_iter, seed, callback):
    rng = np.random.default_rng(seed)
    pop = rng.random((pop_size, DIM))         <span class="text-gray-600"># DIM = 105</span>
    archive, archive_fit = [], []

    <span class="text-blue-400">for</span> t <span class="text-blue-400">in</span> range(max_iter):
        x_mean = pop.mean(axis=0)
        rabbit = select_leader(archive, archive_fit, rng)

        <span class="text-blue-400">for</span> i <span class="text-blue-400">in</span> range(pop_size):
            E = escape_energy(t, max_iter, rng)
            r = rng.random()

            <span class="text-blue-400">if</span> abs(E) >= 1:                    <span class="text-gray-600"># Exploraci&oacute;n</span>
                candidate = op1(...) <span class="text-blue-400">if</span> r >= 0.5 <span class="text-blue-400">else</span> op2(...)
            <span class="text-blue-400">elif</span> r >= 0.5:                     <span class="text-gray-600"># Siege suave</span>
                candidate = op3(...) <span class="text-blue-400">if</span> abs(E) >= 0.5 <span class="text-blue-400">else</span> op4(...)
            <span class="text-blue-400">else</span>:                              <span class="text-gray-600"># Siege + L&eacute;vy</span>
                candidate = op5(...) <span class="text-blue-400">if</span> abs(E) >= 0.5 <span class="text-blue-400">else</span> op6(...)

            fit_cand = evaluate(decode(spv(candidate)))
            <span class="text-blue-400">if</span> dominates(fit_cand, fitness[i]):
                pop[i] = candidate
            update_archive(candidate, fit_cand)

        hv = hypervolume_3d(archive_fit, REF_POINT)
        callback(t, archive, hv)            <span class="text-gray-600"># Stream a frontend</span></pre>
      </details>

      <details class="bg-dark-bg1 rounded-lg border border-dark-border">
        <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
          <strong class="text-accent-red">problem.py</strong> &mdash; Funciones objetivo
        </summary>
        <pre class="px-4 pb-4 text-[11px] font-mono text-gray-400 overflow-x-auto leading-relaxed">
<span class="text-blue-400">def</span> <span class="text-accent-green">evaluate</span>(alloc, groups):
    total_demand = sum(g.n <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups)

    <span class="text-gray-600"># f1: carga de espera ponderada</span>
    f1 = sum((g.n - alloc[g.idx]) * g.w <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups) / total_demand

    <span class="text-gray-600"># f2: disparidad m&aacute;xima entre pa&iacute;ses</span>
    country_waits = {}
    <span class="text-blue-400">for</span> g <span class="text-blue-400">in</span> groups:
        <span class="text-gray-600"># calcular espera promedio ponderada por pa&iacute;s</span>
        ...
    f2 = max(country_waits.values()) - min(country_waits.values())

    <span class="text-gray-600"># f3: visas desperdiciadas</span>
    f3 = TOTAL_VISAS - sum(alloc)

    <span class="text-blue-400">return</span> (f1, f2, f3)</pre>
      </details>
    </section>

    <!-- ============================= -->
    <!-- 8. RESUMEN DE ARCHIVOS         -->
    <!-- ============================= -->
    <section class="card space-y-3">
      <h2 class="text-lg font-bold text-white">8. Mapa de Archivos del Proyecto</h2>

      <div class="bg-dark-bg1 rounded-lg p-4 font-mono text-xs leading-loose">
        <p class="text-gray-500">backend/app/core/</p>
        <p class="ml-4"><span class="text-accent-yellow">config.py</span> <span class="text-gray-600">&mdash; Par&aacute;metros: V=140k, caps, &beta;=1.5, pop=50, iter=500</span></p>
        <p class="ml-4"><span class="text-accent-yellow">problem.py</span> <span class="text-gray-600">&mdash; 105 grupos, 3 objetivos f&#8321;/f&#8322;/f&#8323;, restricciones R1&ndash;R6</span></p>
        <p class="ml-4"><span class="text-accent-yellow">decoder.py</span> <span class="text-gray-600">&mdash; SPV (argsort) + greedy allocation</span></p>
        <p class="ml-4"><span class="text-accent-yellow">hho.py</span> <span class="text-gray-600">&mdash; 6 operadores + L&eacute;vy flight + escape energy</span></p>
        <p class="ml-4"><span class="text-accent-yellow">mohho.py</span> <span class="text-gray-600">&mdash; Runner multi-objetivo, archivo Pareto, HV 3D</span></p>
        <p class="ml-4"><span class="text-accent-yellow">fifo.py</span> <span class="text-gray-600">&mdash; L&iacute;nea base: asignaci&oacute;n por fecha de prioridad</span></p>
        <p class="text-gray-500 mt-3">backend/app/api/</p>
        <p class="ml-4"><span class="text-accent-green">scenarios.py</span> <span class="text-gray-600">&mdash; REST: /allocation, /impact, /summary, /groups</span></p>
        <p class="ml-4"><span class="text-accent-green">pareto.py</span> <span class="text-gray-600">&mdash; REST: /pareto, /pareto/run/{idx}</span></p>
        <p class="ml-4"><span class="text-accent-green">convergence.py</span> <span class="text-gray-600">&mdash; REST: /convergence, /convergence/runs</span></p>
        <p class="ml-4"><span class="text-accent-green">ws.py</span> <span class="text-gray-600">&mdash; WebSocket: /ws/simulation (streaming en vivo)</span></p>
        <p class="text-gray-500 mt-3">backend/app/data/</p>
        <p class="ml-4"><span class="text-gray-400">combined_pareto.csv</span> <span class="text-gray-600">&mdash; 406 soluciones Pareto de 30 corridas</span></p>
        <p class="ml-4"><span class="text-gray-400">convergence.json</span> <span class="text-gray-600">&mdash; HV medio/std por iteraci&oacute;n (500 puntos)</span></p>
        <p class="ml-4"><span class="text-gray-400">run_*.csv</span> <span class="text-gray-600">&mdash; Frente Pareto por corrida (30 archivos)</span></p>
      </div>
    </section>
  </div>
</template>
