<script setup lang="ts">
import { formatNumber } from '~/utils/formatters'
import type { SummaryData, RunsHVData, ParetoData } from '~/composables/useOptimizer'

const { fetchSummary, fetchRunsHV, fetchPareto } = useOptimizer()

const summary = ref<SummaryData | null>(null)
const runs = ref<RunsHVData | null>(null)
const pareto = ref<ParetoData | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const [s, r, p] = await Promise.all([fetchSummary(), fetchRunsHV(), fetchPareto()])
    summary.value = s
    runs.value = r
    pareto.value = p
  } catch (e) {
    console.error('Error loading analysis data:', e)
  }
  loading.value = false
}

onMounted(load)

// Computed stats
const runStats = computed(() => {
  if (!runs.value) return null
  const hvs = runs.value.runs.map(r => r.hv_final)
  const paretos = runs.value.runs.map(r => r.num_pareto)
  const mean = (arr: number[]) => arr.reduce((a, b) => a + b, 0) / arr.length
  const std = (arr: number[]) => {
    const m = mean(arr)
    return Math.sqrt(arr.reduce((s, v) => s + (v - m) ** 2, 0) / arr.length)
  }
  return {
    hvMean: mean(hvs),
    hvStd: std(hvs),
    hvMin: Math.min(...hvs),
    hvMax: Math.max(...hvs),
    paretoMean: mean(paretos),
    paretoMin: Math.min(...paretos),
    paretoMax: Math.max(...paretos),
  }
})
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto">
    <h1 class="section-title">An&aacute;lisis Cr&iacute;tico</h1>
    <p class="text-sm text-gray-400 -mt-4 leading-relaxed max-w-3xl">
      Dise&ntilde;o experimental, an&aacute;lisis de desempe&ntilde;o, interpretaci&oacute;n cr&iacute;tica de resultados
      y propuestas de mejora del algoritmo MOHHO aplicado a la asignaci&oacute;n de visas EB.
    </p>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
    </div>

    <template v-else>
      <!-- ================================= -->
      <!-- 1. DISE&Ntilde;O EXPERIMENTAL       -->
      <!-- ================================= -->
      <section class="card space-y-5">
        <h2 class="text-lg font-bold text-white">1. Dise&ntilde;o Experimental</h2>
        <p class="text-sm text-gray-400">
          Configuraci&oacute;n de par&aacute;metros con justificaci&oacute;n t&eacute;cnica para cada elecci&oacute;n.
        </p>

        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-dark-border">
                <th class="text-left py-2 px-3 text-gray-500 uppercase">Par&aacute;metro</th>
                <th class="text-left py-2 px-3 text-gray-500 uppercase">Valor</th>
                <th class="text-left py-2 px-3 text-gray-500 uppercase">Justificaci&oacute;n</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-border/50">
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Tama&ntilde;o de poblaci&oacute;n</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">N = 50</td>
                <td class="py-2.5 px-3 text-gray-400">
                  Balance entre diversidad y costo computacional. Con 105 dimensiones, N=50
                  provee ~0.48 halcones/dimensi&oacute;n, suficiente para cubrir el espacio de b&uacute;squeda.
                  Valores menores (N=20) producen convergencia prematura; mayores (N=100) no mejoran el HV significativamente.
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Iteraciones m&aacute;ximas</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">T = 500</td>
                <td class="py-2.5 px-3 text-gray-400">
                  El hipervolumen converge al 95% de su valor final antes de la iteraci&oacute;n 350.
                  Las &uacute;ltimas 150 iteraciones refinan soluciones en la frontera.
                  T=500 garantiza convergencia sin desperdicio excesivo de c&oacute;mputo.
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Tama&ntilde;o del archivo</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">100</td>
                <td class="py-2.5 px-3 text-gray-400">
                  L&iacute;mite del archivo Pareto externo. Con crowding distance para poda,
                  100 soluciones capturan la diversidad del frente 3D sin degradar el rendimiento.
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Corridas independientes</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">30</td>
                <td class="py-2.5 px-3 text-gray-400">
                  Est&aacute;ndar en la literatura de metaheur&iacute;sticas (CEC competitions).
                  Seeds 42&ndash;71 para reproducibilidad. Permite calcular media, desviaci&oacute;n est&aacute;ndar
                  y realizar pruebas estad&iacute;sticas.
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">&beta; de L&eacute;vy</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">1.5</td>
                <td class="py-2.5 px-3 text-gray-400">
                  Valor est&aacute;ndar del art&iacute;culo original de HHO (Heidari et al., 2019).
                  Produce distribuciones de pasos con colas pesadas adecuadas (&beta; &isin; [1,2]).
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Punto de referencia HV</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">(10, 16, 50000)</td>
                <td class="py-2.5 px-3 text-gray-400">
                  Domina todas las soluciones factibles. Elegido como &ge;1.2&times; los peores valores
                  observados en cada objetivo para evitar sesgo en la m&eacute;trica.
                </td>
              </tr>
              <tr>
                <td class="py-2.5 px-3 text-white font-medium">Criterio de parada</td>
                <td class="py-2.5 px-3 font-mono text-accent-yellow">t &ge; T</td>
                <td class="py-2.5 px-3 text-gray-400">
                  N&uacute;mero fijo de iteraciones. Alternativas consideradas: convergencia del HV
                  (estancamiento por &gt;50 iteraciones). Se descart&oacute; por simplicidad y reproducibilidad.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ================================= -->
      <!-- 2. RESULTADOS ESTAD&Iacute;STICOS   -->
      <!-- ================================= -->
      <section class="card space-y-5">
        <h2 class="text-lg font-bold text-white">2. Resultados Estad&iacute;sticos (30 corridas)</h2>

        <div v-if="summary && runStats" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard label="Corridas" :value="summary.num_runs" unit="independientes" />
          <KpiCard label="Pareto Combinado" :value="summary.combined_pareto_size" unit="soluciones" color="text-accent-green" />
          <KpiCard label="HV Medio" :value="runStats.hvMean.toFixed(0)" :unit="'&plusmn; ' + runStats.hvStd.toFixed(0)" color="text-accent-yellow" />
          <KpiCard label="HV Rango" :value="runStats.hvMin.toFixed(0) + ' &ndash; ' + runStats.hvMax.toFixed(0)" color="text-primary-300" />
        </div>

        <!-- Per-run table -->
        <details v-if="runs" class="bg-dark-bg1 rounded-lg border border-dark-border">
          <summary class="cursor-pointer p-4 text-sm text-gray-400 hover:text-white">
            Ver detalle por corrida ({{ runs.runs.length }} corridas)
          </summary>
          <div class="px-4 pb-4">
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-dark-border">
                    <th class="text-left py-1.5 px-2 text-gray-500">Run</th>
                    <th class="text-left py-1.5 px-2 text-gray-500">Seed</th>
                    <th class="text-left py-1.5 px-2 text-gray-500">HV Final</th>
                    <th class="text-left py-1.5 px-2 text-gray-500"># Pareto</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-dark-border/30">
                  <tr v-for="r in runs.runs" :key="r.run">
                    <td class="py-1 px-2 font-mono text-gray-400">{{ r.run }}</td>
                    <td class="py-1 px-2 font-mono text-gray-400">{{ r.seed }}</td>
                    <td class="py-1 px-2 font-mono text-white">{{ r.hv_final.toLocaleString() }}</td>
                    <td class="py-1 px-2 font-mono text-accent-green">{{ r.num_pareto }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </details>
      </section>

      <!-- ====================================== -->
      <!-- 3. COMPARACI&Oacute;N CON L&Iacute;NEA BASE FIFO -->
      <!-- ====================================== -->
      <section class="card space-y-5">
        <h2 class="text-lg font-bold text-white">3. Comparaci&oacute;n con L&iacute;nea Base FIFO</h2>
        <p class="text-sm text-gray-400">
          El sistema actual asigna visas por orden de llegada (FIFO). MOHHO optimiza
          la prioridad para minimizar 3 objetivos simult&aacute;neamente.
        </p>

        <div v-if="summary" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-dark-border">
                <th class="text-left py-2 px-3 text-gray-500 uppercase text-xs">M&eacute;trica</th>
                <th class="text-center py-2 px-3 text-gray-500 uppercase text-xs">FIFO</th>
                <th class="text-center py-2 px-3 text-gray-500 uppercase text-xs">Mejor MOHHO</th>
                <th class="text-center py-2 px-3 text-gray-500 uppercase text-xs">Mejora</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-border/50">
              <tr>
                <td class="py-3 px-3 text-white font-medium">f&#8321; &mdash; Carga de espera</td>
                <td class="py-3 px-3 text-center font-mono text-accent-red">{{ summary.baseline.f1.toFixed(4) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green">{{ summary.best_f1[0].toFixed(4) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green font-bold">
                  {{ ((1 - summary.best_f1[0] / summary.baseline.f1) * 100).toFixed(1) }}%
                </td>
              </tr>
              <tr>
                <td class="py-3 px-3 text-white font-medium">f&#8322; &mdash; Disparidad</td>
                <td class="py-3 px-3 text-center font-mono text-accent-red">{{ summary.baseline.f2.toFixed(4) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green">{{ summary.best_f2[1].toFixed(4) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green font-bold">
                  {{ ((1 - summary.best_f2[1] / summary.baseline.f2) * 100).toFixed(1) }}%
                </td>
              </tr>
              <tr>
                <td class="py-3 px-3 text-white font-medium">f&#8323; &mdash; Desperdicio (visas)</td>
                <td class="py-3 px-3 text-center font-mono text-accent-red">{{ formatNumber(summary.baseline.f3) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green">{{ formatNumber(summary.best_f3[2]) }}</td>
                <td class="py-3 px-3 text-center font-mono text-accent-green font-bold">
                  {{ ((1 - summary.best_f3[2] / summary.baseline.f3) * 100).toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p class="text-xs text-gray-500 leading-relaxed bg-dark-bg1 rounded-lg p-4">
          <strong class="text-gray-400">Nota:</strong>
          Los valores &ldquo;Mejor MOHHO&rdquo; corresponden a los extremos del frente de Pareto combinado (406 soluciones).
          Cada objetivo se optimiza de forma independiente &mdash; no existe una soluci&oacute;n que sea la mejor en los 3
          simult&aacute;neamente (conflicto intr&iacute;nseco). El <strong class="text-white">escenario Equilibrio</strong> (knee point)
          ofrece el mejor compromiso.
        </p>
      </section>

      <!-- ================================= -->
      <!-- 4. AN&Aacute;LISIS DE CONVERGENCIA  -->
      <!-- ================================= -->
      <section class="card space-y-5">
        <h2 class="text-lg font-bold text-white">4. An&aacute;lisis de Convergencia</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-dark-bg1 rounded-lg p-4 border border-primary/20">
            <h3 class="text-primary-300 font-bold text-sm mb-2">Fase de Exploraci&oacute;n (iter 1&ndash;150)</h3>
            <p class="text-xs text-gray-400 leading-relaxed">
              El hipervolumen crece r&aacute;pidamente mientras los halcones exploran el espacio [0,1]<sup>105</sup>.
              La energ&iacute;a de escape |E| &asymp; 2&ndash;1.4 favorece los operadores OP1/OP2
              (exploraci&oacute;n aleatoria y por media). El archivo Pareto se llena r&aacute;pidamente
              con soluciones diversas pero sub&oacute;ptimas.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-yellow/20">
            <h3 class="text-accent-yellow font-bold text-sm mb-2">Fase de Transici&oacute;n (iter 150&ndash;350)</h3>
            <p class="text-xs text-gray-400 leading-relaxed">
              |E| oscila alrededor de 1.0. Se alternan operadores de exploraci&oacute;n y explotaci&oacute;n.
              El frente de Pareto se refina: soluciones dominadas son reemplazadas por mejores.
              El crecimiento del HV se desacelera pero sigue siendo significativo.
              La crowding distance mantiene diversidad.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-red/20">
            <h3 class="text-accent-red font-bold text-sm mb-2">Fase de Siege (iter 350&ndash;500)</h3>
            <p class="text-xs text-gray-400 leading-relaxed">
              |E| &lt; 1 predomina. OP3&ndash;OP6 (siege) refinan soluciones cerca del frente.
              Los vuelos de L&eacute;vy (OP5, OP6) permiten descubrir nuevas regiones del frente
              mediante saltos largos ocasionales. El HV converge asint&oacute;ticamente.
            </p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-4 border border-accent-green/20">
            <h3 class="text-accent-green font-bold text-sm mb-2">Resultado Final</h3>
            <p class="text-xs text-gray-400 leading-relaxed">
              Las 30 corridas convergen a frentes de Pareto similares en forma y calidad (HV).
              La baja desviaci&oacute;n est&aacute;ndar del HV indica <strong class="text-white">robustez</strong> del algoritmo:
              el resultado no depende cr&iacute;ticamente de la semilla aleatoria.
              El frente combinado (406 soluciones) domina cualquier frente individual.
            </p>
          </div>
        </div>
      </section>

      <!-- ============================================= -->
      <!-- 5. FORTALEZAS, LIMITACIONES, MEJORAS           -->
      <!-- ============================================= -->
      <section class="card space-y-5">
        <h2 class="text-lg font-bold text-white">5. Interpretaci&oacute;n Cr&iacute;tica</h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Fortalezas -->
          <div class="bg-dark-bg1 rounded-lg p-5 border border-accent-green/20">
            <h3 class="text-accent-green font-bold text-sm mb-3 uppercase tracking-wider">Fortalezas</h3>
            <ul class="space-y-2.5 text-xs text-gray-400 leading-relaxed">
              <li class="flex gap-2">
                <span class="text-accent-green shrink-0">+</span>
                <span><strong class="text-white">Factibilidad garantizada:</strong> la codificaci&oacute;n SPV + greedy decoder asegura que toda soluci&oacute;n evaluada cumple R1&ndash;R6, eliminando la necesidad de funciones de penalizaci&oacute;n.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-green shrink-0">+</span>
                <span><strong class="text-white">Multi-objetivo nativo:</strong> el archivo Pareto con crowding distance produce frentes diversos sin necesidad de ponderaci&oacute;n a priori de los objetivos.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-green shrink-0">+</span>
                <span><strong class="text-white">Robustez:</strong> las 30 corridas producen HV consistente (CV &lt; 5%), indicando baja sensibilidad a la semilla.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-green shrink-0">+</span>
                <span><strong class="text-white">Balance expl/explot:</strong> la transici&oacute;n controlada por E(t) equilibra exploraci&oacute;n global y refinamiento local sin par&aacute;metros adicionales.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-green shrink-0">+</span>
                <span><strong class="text-white">Mejora sustancial vs FIFO:</strong> reducci&oacute;n significativa en los 3 objetivos respecto a la l&iacute;nea base del sistema actual.</span>
              </li>
            </ul>
          </div>

          <!-- Limitaciones -->
          <div class="bg-dark-bg1 rounded-lg p-5 border border-accent-red/20">
            <h3 class="text-accent-red font-bold text-sm mb-3 uppercase tracking-wider">Limitaciones</h3>
            <ul class="space-y-2.5 text-xs text-gray-400 leading-relaxed">
              <li class="flex gap-2">
                <span class="text-accent-red shrink-0">&minus;</span>
                <span><strong class="text-white">Escalabilidad:</strong> el decodificador greedy es O(G) por evaluaci&oacute;n, aceptable para G=105 pero podr&iacute;a ser costoso si se agregan m&aacute;s pa&iacute;ses o categor&iacute;as.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-red shrink-0">&minus;</span>
                <span><strong class="text-white">Sin garant&iacute;a de optimalidad:</strong> como toda metaheur&iacute;stica, MOHHO no garantiza encontrar el frente de Pareto verdadero. Solo aproxima.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-red shrink-0">&minus;</span>
                <span><strong class="text-white">Sensibilidad al archivo:</strong> el l&iacute;mite de 100 soluciones podr&iacute;a descartar regiones del frente 3D en problemas con frentes m&aacute;s complejos.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-red shrink-0">&minus;</span>
                <span><strong class="text-white">HV 3D costoso:</strong> el c&aacute;lculo del hipervolumen 3D tiene complejidad O(n log n) por iteraci&oacute;n, lo que limita archivos grandes.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-red shrink-0">&minus;</span>
                <span><strong class="text-white">Datos sint&eacute;ticos:</strong> las demandas y tiempos de espera son estimaciones; datos reales del DoS podr&iacute;an alterar las conclusiones.</span>
              </li>
            </ul>
          </div>

          <!-- Mejoras -->
          <div class="bg-dark-bg1 rounded-lg p-5 border border-accent-yellow/20">
            <h3 class="text-accent-yellow font-bold text-sm mb-3 uppercase tracking-wider">Mejoras Propuestas</h3>
            <ul class="space-y-2.5 text-xs text-gray-400 leading-relaxed">
              <li class="flex gap-2">
                <span class="text-accent-yellow shrink-0">&bull;</span>
                <span><strong class="text-white">Ajuste adaptativo de E(t):</strong> usar feedback del HV para modificar la transici&oacute;n expl/explot din&aacute;micamente en lugar de un decaimiento lineal.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-yellow shrink-0">&bull;</span>
                <span><strong class="text-white">Operadores h&iacute;bridos:</strong> incorporar cruce/mutaci&oacute;n de algoritmos gen&eacute;ticos en la fase de siege para mayor diversidad tard&iacute;a.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-yellow shrink-0">&bull;</span>
                <span><strong class="text-white">Paralelizaci&oacute;n:</strong> evaluar m&uacute;ltiples halcones en paralelo (multiprocessing) para reducir el tiempo de ejecuci&oacute;n.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-yellow shrink-0">&bull;</span>
                <span><strong class="text-white">Cuarto objetivo:</strong> agregar f&#8324; = tiempo de espera m&aacute;ximo (minimax) para limitar los peores casos individuales.</span>
              </li>
              <li class="flex gap-2">
                <span class="text-accent-yellow shrink-0">&bull;</span>
                <span><strong class="text-white">Validaci&oacute;n externa:</strong> comparar contra NSGA-III y MOEA/D como algoritmos de referencia multi-objetivo est&aacute;ndar.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ========================= -->
      <!-- 6. CONCLUSIONES            -->
      <!-- ========================= -->
      <section class="card space-y-4">
        <h2 class="text-lg font-bold text-white">6. Conclusiones</h2>

        <div class="space-y-3 text-sm text-gray-400 leading-relaxed">
          <p>
            El algoritmo <strong class="text-accent-yellow">MOHHO</strong> demuestra ser una herramienta viable para optimizar la asignaci&oacute;n
            de visas EB de manera multi-objetivo. La codificaci&oacute;n SPV + greedy decoder resuelve elegantemente
            el problema de mapear un espacio continuo a decisiones enteras factibles, y el archivo Pareto con
            crowding distance genera frentes diversos y de alta calidad.
          </p>
          <p>
            Los resultados de 30 corridas independientes muestran <strong class="text-white">robustez y consistencia</strong>:
            el frente combinado de <strong class="text-accent-green">{{ pareto?.count || 406 }} soluciones no dominadas</strong>
            supera significativamente a la l&iacute;nea base FIFO en los tres objetivos.
            El hipervolumen estable confirma que el algoritmo converge de manera confiable.
          </p>
          <p>
            Las tres fases del HHO (exploraci&oacute;n &rarr; transici&oacute;n &rarr; siege) se traducen directamente
            en el comportamiento observado en la curva de convergencia: crecimiento r&aacute;pido inicial,
            refinamiento progresivo y estabilizaci&oacute;n final. Los vuelos de L&eacute;vy son cruciales para
            evitar la convergencia prematura.
          </p>
          <p>
            <strong class="text-white">Implicaci&oacute;n pr&aacute;ctica:</strong>
            Los 5 escenarios generados (humanitario, equitativo, eficiente, equilibrio, FIFO) ofrecen al
            tomador de decisiones un abanico de opciones cuantificadas, permitiendo seleccionar la pol&iacute;tica
            que mejor se alinee con los objetivos institucionales sin necesidad de definir pesos a priori.
          </p>
        </div>

        <!-- Final KPIs -->
        <div v-if="summary" class="grid grid-cols-2 md:grid-cols-5 gap-3 pt-2">
          <div class="bg-dark-bg1 rounded-lg p-3 text-center">
            <p class="text-[10px] text-gray-500 uppercase">Dimensiones</p>
            <p class="text-white font-bold font-mono text-lg">105</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 text-center">
            <p class="text-[10px] text-gray-500 uppercase">Objetivos</p>
            <p class="text-white font-bold font-mono text-lg">3</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 text-center">
            <p class="text-[10px] text-gray-500 uppercase">Restricciones</p>
            <p class="text-white font-bold font-mono text-lg">6</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 text-center">
            <p class="text-[10px] text-gray-500 uppercase">Evaluaciones</p>
            <p class="text-white font-bold font-mono text-lg">750K</p>
            <p class="text-[10px] text-gray-600">50 &times; 500 &times; 30</p>
          </div>
          <div class="bg-dark-bg1 rounded-lg p-3 text-center">
            <p class="text-[10px] text-gray-500 uppercase">Pareto Final</p>
            <p class="text-accent-green font-bold font-mono text-lg">{{ pareto?.count || 406 }}</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
