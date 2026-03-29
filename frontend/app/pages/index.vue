<script setup lang="ts">
import type { SummaryData, GroupsData } from '~/composables/useOptimizer'
import { formatNumber } from '~/utils/formatters'

// Inline composable: animated count-up with easeOutExpo
function useCountUp(target: Ref<number | null>, duration = 2000) {
  const current = ref(0)
  let animationId: number | null = null

  function easeOutExpo(t: number): number {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
  }

  watch(target, (newVal) => {
    if (newVal === null || newVal === undefined) return
    if (animationId !== null) cancelAnimationFrame(animationId)

    const startVal = current.value
    const delta = newVal - startVal
    const startTime = performance.now()

    function step(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const easedProgress = easeOutExpo(progress)
      current.value = Math.round(startVal + delta * easedProgress)

      if (progress < 1) {
        animationId = requestAnimationFrame(step)
      } else {
        current.value = newVal!
        animationId = null
      }
    }

    animationId = requestAnimationFrame(step)
  }, { immediate: true })

  onUnmounted(() => {
    if (animationId !== null) cancelAnimationFrame(animationId)
  })

  return current
}

const { fetchSummary, fetchGroups } = useOptimizer()

const summary = ref<SummaryData | null>(null)
const groups = ref<GroupsData | null>(null)

onMounted(async () => {
  const [s, g] = await Promise.all([fetchSummary(), fetchGroups()])
  summary.value = s
  groups.value = g
})

const totalBacklog = computed(() => groups.value ? formatNumber(groups.value.total_demand) : '...')
const maxWait = computed(() => {
  if (!groups.value) return '...'
  return Math.max(...groups.value.groups.map(g => g.w))
})

const fifoWaste = computed(() => {
  if (!summary.value) return 0
  return Math.round(summary.value.baseline.f3)
})

const mohhoImprovement = computed(() => {
  if (!summary.value) return { f1: '0', f2: '0', waste: '0' }
  const b = summary.value.baseline
  return {
    f1: ((1 - summary.value.best_f1[0] / b.f1) * 100).toFixed(0),
    f2: ((1 - summary.value.best_f2[1] / b.f2) * 100).toFixed(0),
    waste: formatNumber(Math.round(b.f3 - summary.value.best_f3[2])),
  }
})

// --- Animated KPI targets ---
const kpiVisas = computed(() => (summary.value && groups.value) ? 140000 : null)
const kpiBacklog = computed(() => groups.value ? groups.value.total_demand : null)
const kpiCountries = computed(() => (summary.value && groups.value) ? 21 : null)
const kpiMaxWait = computed(() => {
  if (!groups.value) return null
  return Math.max(...groups.value.groups.map(g => g.w))
})

const animVisas = useCountUp(kpiVisas, 2000)
const animBacklog = useCountUp(kpiBacklog, 2000)
const animCountries = useCountUp(kpiCountries, 1500)
const animMaxWait = useCountUp(kpiMaxWait, 1800)

// --- Animated Experimental Config targets ---
const expNumRuns = computed(() => summary.value ? summary.value.num_runs : null)
const expPopSize = computed(() => summary.value ? summary.value.pop_size : null)
const expMaxIter = computed(() => summary.value ? summary.value.max_iter : null)
const expParetoSize = computed(() => summary.value ? summary.value.combined_pareto_size : null)

const animNumRuns = useCountUp(expNumRuns, 1500)
const animPopSize = useCountUp(expPopSize, 1800)
const animMaxIter = useCountUp(expMaxIter, 2000)
const animParetoSize = useCountUp(expParetoSize, 2200)
</script>

<template>
  <div class="space-y-10">
    <!-- Hero -->
    <section class="text-center py-10 relative">
      <div class="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent rounded-3xl" />
      <div class="relative">
        <p class="text-xs text-primary-300 font-semibold uppercase tracking-[0.25em] mb-3">Multi-Objective Harris Hawks Optimization</p>
        <h1 class="text-4xl md:text-6xl font-black tracking-tight leading-[1.1]">
          <span class="bg-gradient-to-r from-accent-yellow via-accent-green to-primary bg-clip-text text-transparent">
            VISA PREDICT AI
          </span>
        </h1>
        <p class="text-gray-400 mt-4 max-w-2xl mx-auto text-lg leading-relaxed">
          Optimización multi-objetivo para la asignación de
          <span class="text-white font-semibold">140,000 visas EB</span> de EE.UU.
          entre <span class="text-white font-semibold">21 países</span> y
          <span class="text-white font-semibold">5 categorías</span>.
        </p>
      </div>
    </section>

    <!-- KPI Cards -->
    <section v-if="summary && groups" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Total Visas EB" :value="formatNumber(animVisas)" unit="por año fiscal" color="text-accent-yellow" />
      <KpiCard label="Backlog Total" :value="formatNumber(animBacklog)" unit="peticiones aprobadas" color="text-accent-red" />
      <KpiCard label="Países Analizados" :value="String(animCountries)" unit="bloques de países" />
      <KpiCard label="Mayor Espera" :value="animMaxWait + ' años'" unit="India EB-3" color="text-accent-green" />
    </section>

    <!-- Skeleton while loading -->
    <section v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="metric-card">
        <div class="skeleton h-3 w-20 mx-auto mb-3" />
        <div class="skeleton h-8 w-24 mx-auto mb-2" />
        <div class="skeleton h-2.5 w-16 mx-auto" />
      </div>
    </section>

    <!-- Problem description -->
    <section class="card space-y-4">
      <h2 class="section-title">El Problema</h2>
      <p class="text-gray-400 leading-relaxed">
        Cada año fiscal, EE.UU. otorga <strong class="text-accent-yellow">140,000 visas de empleo</strong>
        (EB) distribuidas en 5 categorías y limitadas por topes por país del 7%.
        El sistema actual (<strong class="text-accent-red">FIFO</strong>) genera esperas de hasta
        <strong class="text-white">13 años</strong> para ciertos países y deja
        <strong class="text-accent-red">{{ fifoWaste > 0 ? formatNumber(fifoWaste) : '...' }}</strong> visas sin usar.
      </p>
      <p class="text-gray-400 leading-relaxed">
        <strong class="text-accent-green">MOHHO</strong> (Multi-Objective Harris Hawks Optimization) encuentra un
        <strong class="text-accent-green">frente de Pareto</strong> con cientos de soluciones que mejoran
        simultáneamente la espera, la equidad entre países y la utilización de visas.
      </p>
    </section>

    <!-- FIFO vs MOHHO comparison -->
    <section v-if="summary" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card border-accent-red/20 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-accent-red/60" />
        <h3 class="text-sm font-semibold text-accent-red uppercase tracking-wider mb-4 pl-3">FIFO (Sistema Actual)</h3>
        <div class="space-y-3 font-mono text-sm pl-3">
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f espera</span>
            <span class="text-white text-lg font-bold">{{ summary.baseline.f1.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">años</span></span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f brecha</span>
            <span class="text-white text-lg font-bold">{{ summary.baseline.f2.toFixed(3) }} <span class="text-xs text-gray-500 font-normal">años</span></span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f desperdicio</span>
            <span class="text-white text-lg font-bold">{{ formatNumber(Math.round(summary.baseline.f3)) }} <span class="text-xs text-gray-500 font-normal">visas</span></span>
          </div>
        </div>
      </div>
      <div class="card border-accent-green/20 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-accent-green/60" />
        <h3 class="text-sm font-semibold text-accent-green uppercase tracking-wider mb-4 pl-3">MOHHO (Mejor Solución)</h3>
        <div class="space-y-3 font-mono text-sm pl-3">
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f espera</span>
            <span class="text-white text-lg font-bold">
              {{ summary.best_f1[0].toFixed(3) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.f1 }}%</span>
            </span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f brecha</span>
            <span class="text-white text-lg font-bold">
              {{ summary.best_f2[1].toFixed(3) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.f2 }}%</span>
            </span>
          </div>
          <div class="flex justify-between items-baseline">
            <span class="text-gray-500">f desperdicio</span>
            <span class="text-white text-lg font-bold">
              {{ formatNumber(Math.round(summary.best_f3[2])) }}
              <span class="text-accent-green text-xs font-semibold ml-1">-{{ mohhoImprovement.waste }}</span>
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Objectives explained -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-yellow to-accent-yellow/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="heart" :size="16" class="text-accent-yellow" />
          <h3 class="text-accent-yellow font-bold">f&#8321; — Carga de Espera</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide los años de espera ponderados de las personas que NO reciben visa.
          Menor = más humanitario.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8321;(x) = Σ(n&#7501; - x&#7501;)·w&#7501; / Σn&#7501;
        </p>
      </div>
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-green to-accent-green/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="scale" :size="16" class="text-accent-green" />
          <h3 class="text-accent-green font-bold">f&#8322; — Disparidad</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide la brecha máxima de espera entre países.
          Menor = más equitativo.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8322;(x) = max|W&#772;c&#8321; - W&#772;c&#8322;|
        </p>
      </div>
      <div class="card group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-blue to-accent-blue/0" />
        <div class="flex items-center gap-2 mb-3">
          <Icon name="trending-up" :size="16" class="text-accent-blue" />
          <h3 class="text-accent-blue font-bold">f&#8323; — Desperdicio</h3>
        </div>
        <p class="text-xs text-gray-400 leading-relaxed">
          Mide las visas que quedan sin usar por la interacción de topes.
          Menor = más eficiente.
        </p>
        <p class="font-mono text-[11px] text-gray-600 mt-3 bg-white/[0.03] rounded px-2 py-1">
          f&#8323;(x) = V - Σx&#7501;
        </p>
      </div>
    </section>

    <!-- Experimental summary -->
    <section v-if="summary" class="card">
      <h2 class="section-title mb-4">Configuración Experimental</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ animNumRuns }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">corridas independientes</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ animPopSize }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">halcones (población)</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-white">{{ formatNumber(animMaxIter) }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">iteraciones</p>
        </div>
        <div>
          <p class="text-2xl font-mono font-bold text-accent-green">{{ formatNumber(animParetoSize) }}</p>
          <p class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">soluciones Pareto</p>
        </div>
      </div>
    </section>

    <!-- Glosario de Términos -->
    <section class="card">
      <h2 class="section-title mb-2">Glosario de Términos</h2>
      <p class="text-xs text-gray-500 mb-5">Referencia completa de la terminología técnica empleada en este sistema.</p>

      <!-- EB Visa Types -->
      <details class="mb-4 group" open>
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-yellow tracking-wide">Tipos de Visa EB (Employment-Based)</span>
        </summary>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-3 pl-5">
          <!-- EB-1 -->
          <div class="rounded-xl border border-accent-yellow/20 bg-accent-yellow/[0.04] p-4 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-yellow to-accent-yellow/0" />
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-accent-yellow font-mono font-bold text-lg">EB-1</span>
              <span class="text-[10px] text-accent-yellow/70 uppercase tracking-wider font-semibold">Prioridad</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">
              Trabajadores con <strong class="text-white">habilidades extraordinarias</strong>: premios Nobel, CEOs de multinacionales,
              investigadores destacados, atletas y artistas de reconocimiento internacional.
            </p>
          </div>
          <!-- EB-2 -->
          <div class="rounded-xl border border-accent-green/20 bg-accent-green/[0.04] p-4 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-green to-accent-green/0" />
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-accent-green font-mono font-bold text-lg">EB-2</span>
              <span class="text-[10px] text-accent-green/70 uppercase tracking-wider font-semibold">Grado Avanzado</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">
              Profesionales con <strong class="text-white">maestría o doctorado</strong>, o personas con habilidad excepcional
              en ciencias, artes o negocios. Incluye exenciones por interés nacional (NIW).
            </p>
          </div>
          <!-- EB-3 -->
          <div class="rounded-xl border border-accent-blue/20 bg-accent-blue/[0.04] p-4 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-blue to-accent-blue/0" />
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-accent-blue font-mono font-bold text-lg">EB-3</span>
              <span class="text-[10px] text-accent-blue/70 uppercase tracking-wider font-semibold">Calificados</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">
              <strong class="text-white">Trabajadores calificados</strong> (min. 2 años experiencia),
              profesionales con licenciatura y otros trabajadores para puestos que requieren menos de 2 años de formación.
            </p>
          </div>
          <!-- EB-4 -->
          <div class="rounded-xl border border-primary-300/20 bg-primary-300/[0.04] p-4 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-primary-300 to-primary-300/0" />
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-primary-300 font-mono font-bold text-lg">EB-4</span>
              <span class="text-[10px] text-primary-300/70 uppercase tracking-wider font-semibold">Especiales</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">
              <strong class="text-white">Inmigrantes especiales</strong>: trabajadores religiosos, traductores militares
              afganos/iraquíes, empleados de organizaciones internacionales y ciertos médicos.
            </p>
          </div>
          <!-- EB-5 -->
          <div class="rounded-xl border border-accent-red/20 bg-accent-red/[0.04] p-4 relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-accent-red to-accent-red/0" />
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-accent-red font-mono font-bold text-lg">EB-5</span>
              <span class="text-[10px] text-accent-red/70 uppercase tracking-wider font-semibold">Inversionistas</span>
            </div>
            <p class="text-xs text-gray-400 leading-relaxed">
              <strong class="text-white">Inversionistas</strong> que crean al menos 10 empleos con una inversión mínima
              de $1.05M (o $800K en áreas de empleo dirigido TEA). Incluye el programa de Centros Regionales.
            </p>
          </div>
        </div>
      </details>

      <!-- Conceptos del Algoritmo -->
      <details class="mb-4 group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-green tracking-wide">Conceptos del Algoritmo</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">MOHHO <span class="text-gray-600 font-normal">(Multi-Objective Harris Hawks Optimization)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Metaheurística poblacional inspirada en la <strong class="text-white">caza cooperativa de los halcones Harris</strong>. Los halcones (soluciones candidatas) persiguen un conejo (mejor solución) alternando fases de exploración y explotación. La variante multi-objetivo mantiene un archivo de soluciones no-dominadas.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Frente de Pareto</span>
            <p class="text-xs text-gray-400 leading-relaxed">Conjunto de soluciones <strong class="text-white">no-dominadas</strong>: ninguna es estrictamente mejor que otra en todos los objetivos simultáneamente. Representa la frontera eficiente del espacio de decisión, donde mejorar un objetivo implica empeorar al menos otro.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Dominancia de Pareto</span>
            <p class="text-xs text-gray-400 leading-relaxed">Una solución <strong class="text-white">A domina a B</strong> (A &#8826; B) si y solo si A es mejor o igual en <em>todos</em> los objetivos y estrictamente mejor en <em>al menos uno</em>. Formalmente: &#8704;i: f&#7522;(A) &#8804; f&#7522;(B) &#8743; &#8707;j: f&#11388;(A) &lt; f&#11388;(B).</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Hipervolumen (HV)</span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Volumen del espacio objetivo</strong> cubierto por el frente de Pareto, delimitado por un punto de referencia. Es la métrica estándar de calidad de un frente: mayor HV indica mejor convergencia y diversidad simultáneamente. Es la única métrica Pareto-compatible.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Punto de referencia (r)</span>
            <p class="text-xs text-gray-400 leading-relaxed">Punto en el espacio objetivo que es <strong class="text-white">peor que todas las soluciones</strong> del frente en todos los objetivos. Se usa como límite superior para el cálculo del hipervolumen. Su elección afecta el valor absoluto del HV pero no el ranking relativo entre frentes.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Knee point <span class="text-gray-600 font-normal">(punto rodilla)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Solución del frente de Pareto con el <strong class="text-white">mejor balance entre objetivos</strong>. Se identifica como el punto con máxima distancia perpendicular a la línea que conecta los extremos del frente. Representa el compromiso más eficiente.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">SPV <span class="text-gray-600 font-normal">(Smallest Position Value)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Método de decodificación que convierte un <strong class="text-white">vector continuo [0,1]&#xB9;&#x2070;&#x2075;</strong> en una permutación. Para cada solución, los 105 valores reales se ordenan de menor a mayor y su posición define la prioridad de asignación de cada grupo país-categoría.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Exploración vs Explotación</span>
            <p class="text-xs text-gray-400 leading-relaxed">Dilema fundamental en metaheurísticas. <strong class="text-white">Exploración</strong>: buscar ampliamente en nuevas regiones del espacio de soluciones (diversidad). <strong class="text-white">Explotación</strong>: refinar soluciones prometedoras en zonas conocidas (convergencia). HHO transiciona gradualmente de exploración a explotación.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Energía de escape (E)</span>
            <p class="text-xs text-gray-400 leading-relaxed">Parámetro que <strong class="text-white">decrece linealmente de 2 a 0</strong> con las iteraciones, modelando la energía del conejo para escapar. Cuando |E| &#8805; 1 se prioriza exploración global; cuando |E| &lt; 1 se activan estrategias de explotación intensiva.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Vuelo de Lévy</span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Caminata aleatoria</strong> con distribución de pasos de cola pesada: la mayoría de pasos son cortos, pero ocasionalmente se producen saltos largos. Permite a los halcones escapar de óptimos locales y descubrir regiones inexploradas del espacio de búsqueda.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-green font-semibold text-sm">Archivo externo</span>
            <p class="text-xs text-gray-400 leading-relaxed">Repositorio que almacena las <strong class="text-white">soluciones no-dominadas</strong> encontradas durante la optimización. Se actualiza cada iteración: nuevas soluciones no-dominadas entran y las dominadas se eliminan. Su tamaño se controla mediante mecanismos de crowding distance.</p>
          </div>
        </div>
      </details>

      <!-- Conceptos del Problema de Visas -->
      <details class="mb-4 group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-blue tracking-wide">Conceptos del Problema de Visas</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">FIFO <span class="text-gray-600 font-normal">(First In, First Out)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Sistema de asignación actual donde las visas se otorgan estrictamente por <strong class="text-white">orden de llegada</strong> de la petición aprobada (fecha de prioridad). No optimiza ningún criterio de equidad ni eficiencia global; simplemente atiende la cola cronológicamente.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Per-country cap <span class="text-gray-600 font-normal">(tope por país)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Restricción legal que limita a cada país al <strong class="text-white">7% del total anual</strong> de visas EB (25,620 de 140,000). Su objetivo es evitar que un solo país acapare todas las visas, pero genera esperas extremas para países con alta demanda como India y China.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Spillover <span class="text-gray-600 font-normal">(cascada de reasignación)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Mecanismo legal donde las <strong class="text-white">visas no utilizadas</strong> de categorías inferiores se reasignan hacia arriba: EB-4/5 &#8594; EB-1 &#8594; EB-2 &#8594; EB-3. Permite que visas sin demanda suficiente en una categoría beneficien a categorías con mayor backlog.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Backlog <span class="text-gray-600 font-normal">(acumulación)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Número total de <strong class="text-white">peticiones aprobadas que esperan visa</strong>. Cuando la demanda supera la oferta anual, se genera un backlog creciente. Para India EB-3 el backlog actual implica esperas superiores a 10 años.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">f&#8321; <span class="text-gray-600 font-normal">(carga de espera)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Primer objetivo a minimizar.</strong> Suma ponderada de los años de espera de las personas que NO reciben visa en la asignación propuesta. Pondera por el tiempo de espera de cada grupo: quienes llevan más tiempo esperando pesan más.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">f&#8322; <span class="text-gray-600 font-normal">(disparidad entre países)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Segundo objetivo a minimizar.</strong> Mide la brecha máxima de tiempo de espera promedio entre cualquier par de países. Captura la inequidad del sistema: un valor bajo indica que todos los países experimentan esperas similares.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">f&#8323; <span class="text-gray-600 font-normal">(desperdicio de visas)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed"><strong class="text-white">Tercer objetivo a minimizar.</strong> Cantidad de visas del total de 140,000 que quedan sin asignar por la interacción entre topes por país y demanda por categoría. Bajo el sistema FIFO actual, se desperdician miles de visas cada año.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-blue font-semibold text-sm">Visa Bulletin</span>
            <p class="text-xs text-gray-400 leading-relaxed">Publicación mensual del <strong class="text-white">Departamento de Estado</strong> de EE.UU. que indica las fechas de prioridad actuales para cada categoría y país. Define quiénes pueden avanzar en el proceso de visa basándose en cuándo fue aprobada su petición.</p>
          </div>
        </div>
      </details>

      <!-- Estadística -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer py-2 px-1 rounded-lg hover:bg-white/[0.03] transition-colors">
          <span class="text-sm font-semibold text-accent-red tracking-wide">Estadística y Métricas</span>
        </summary>
        <div class="space-y-3 mt-3 pl-5">
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">&#963; <span class="text-gray-600 font-normal">(sigma / desviación estándar)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Mide la <strong class="text-white">dispersión</strong> de un conjunto de resultados respecto a su media. En este proyecto, se usa para evaluar la variabilidad del hipervolumen entre las 30 corridas independientes. Menor &#963; indica resultados más reproducibles.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">CV <span class="text-gray-600 font-normal">(coeficiente de variación)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Definido como <strong class="text-white">&#963;/&#956; &#215; 100</strong>, expresa la desviación estándar como porcentaje de la media. Permite comparar la consistencia de métricas con distintas escalas. Un CV bajo (&lt;5%) indica alta consistencia del algoritmo entre corridas.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">IQR <span class="text-gray-600 font-normal">(rango intercuartílico)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Diferencia entre el <strong class="text-white">tercer cuartil (Q3) y el primer cuartil (Q1)</strong>: el rango que contiene el 50% central de los datos. Es robusto frente a valores atípicos, a diferencia del rango total. Se usa en los box plots de convergencia.</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <span class="text-accent-red font-semibold text-sm">Mediana <span class="text-gray-600 font-normal">(percentil 50)</span></span>
            <p class="text-xs text-gray-400 leading-relaxed">Valor que divide los datos ordenados exactamente a la mitad: <strong class="text-white">50% por arriba, 50% por abajo</strong>. Más robusta que la media frente a valores extremos. Reportada junto con la media para caracterizar distribuciones potencialmente asimétricas.</p>
          </div>
        </div>
      </details>
    </section>
  </div>
</template>
