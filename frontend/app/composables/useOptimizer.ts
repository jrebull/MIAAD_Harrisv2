export interface Fitness {
  f1: number
  f2: number
  f3: number
}

export interface AllocationRow {
  country: string
  flag: string
  categories: Record<string, number>
  total: number
}

export interface AllocationData {
  scenario: string
  fitness: Fitness
  visas_used: number
  utilization: number
  rows: AllocationRow[]
  matrix: number[][]
}

export interface ParetoPoint {
  f1: number
  f2: number
  f3: number
  visas_used: number
}

export interface ParetoData {
  points: ParetoPoint[]
  baseline: ParetoPoint | null
  count: number
}

export interface SummaryData {
  num_runs: number
  pop_size: number
  max_iter: number
  archive_size: number
  combined_pareto_size: number
  baseline: Fitness
  hv_stats: { mean: number; std: number; min: number; max: number }
  best_f1: number[]
  best_f2: number[]
  best_f3: number[]
}

export interface GroupInfo {
  index: number
  country: string
  category: string
  n: number
  d: number
  w: number
  source: string
}

export interface GroupsData {
  groups: GroupInfo[]
  countries: string[]
  categories: string[]
  cats_desc: Record<string, string>
  flags: Record<string, string>
  total_demand: number
  total_visas: number
}

export interface ConvergenceData {
  iterations: number[]
  hv_mean: number[]
  hv_std: number[]
}

export interface RunHV {
  run: number
  seed: number
  hv_final: number
  num_pareto: number
}

export interface RunsHVData {
  runs: RunHV[]
}

export interface ParetoRunData {
  run: number
  seed: number
  num_pareto: number
  hv_final: number
  points: ParetoPoint[]
}

export interface ImpactRow {
  country: string
  flag: string
  fifo_visas: number
  scenario_visas: number
  delta: number
  max_wait: number
}

export interface ImpactData {
  scenario: string
  rows: ImpactRow[]
}

export const useOptimizer = () => {
  const { get, post } = useApi()
  const { scenario } = useScenario()

  const allocation = useState<AllocationData | null>('allocation', () => null)
  const loading = useState<boolean>('optimizerLoading', () => false)

  async function fetchAllocation(): Promise<AllocationData> {
    loading.value = true
    try {
      const data = await get<AllocationData>(`/api/allocation/${scenario.value}`)
      allocation.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchPareto(): Promise<ParetoData> {
    return await get<ParetoData>('/api/pareto')
  }

  async function fetchSummary(): Promise<SummaryData> {
    return await get<SummaryData>('/api/summary')
  }

  async function fetchGroups(): Promise<GroupsData> {
    return await get<GroupsData>('/api/groups')
  }

  async function fetchConvergence(): Promise<ConvergenceData> {
    return await get<ConvergenceData>('/api/convergence')
  }

  async function fetchRunsHV(): Promise<RunsHVData> {
    return await get<RunsHVData>('/api/convergence/runs')
  }

  async function fetchParetoRun(runIdx: number): Promise<ParetoRunData> {
    return await get<ParetoRunData>(`/api/pareto/run/${runIdx}`)
  }

  async function fetchImpact(sc?: string): Promise<ImpactData> {
    return await get<ImpactData>(`/api/impact/${sc || scenario.value}`)
  }

  return {
    allocation,
    loading,
    fetchAllocation,
    fetchPareto,
    fetchSummary,
    fetchGroups,
    fetchConvergence,
    fetchRunsHV,
    fetchParetoRun,
    fetchImpact,
  }
}
