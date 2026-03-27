interface SimulationState {
  running: boolean
  iteration: number
  maxIter: number
  archiveSize: number
  hv: number
  hvHistory: number[]
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
}

export const useSimulation = () => {
  const { wsUrl } = useApi()

  const state = useState<SimulationState>('simulation', () => ({
    running: false,
    iteration: 0,
    maxIter: 0,
    archiveSize: 0,
    hv: 0,
    hvHistory: [],
    paretoFront: [],
  }))

  let ws: WebSocket | null = null

  function start(popSize: number = 30, maxIter: number = 100, seed: number = 42) {
    stop()

    state.value = {
      running: true,
      iteration: 0,
      maxIter,
      archiveSize: 0,
      hv: 0,
      hvHistory: [],
      paretoFront: [],
    }

    ws = new WebSocket(wsUrl('/ws/simulation'))

    ws.onopen = () => {
      ws?.send(JSON.stringify({ pop_size: popSize, max_iter: maxIter, seed }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'iteration') {
        state.value.iteration = data.iteration
        state.value.maxIter = data.max_iter
        state.value.archiveSize = data.archive_size
        state.value.hv = data.hv
        state.value.hvHistory.push(data.hv)
        state.value.paretoFront = data.pareto_front
      } else if (data.type === 'complete') {
        state.value.running = false
      } else if (data.type === 'error') {
        state.value.running = false
        console.error('Simulation error:', data.message)
      }
    }

    ws.onerror = () => {
      state.value.running = false
    }

    ws.onclose = () => {
      state.value.running = false
    }
  }

  function stop() {
    if (ws) {
      ws.close()
      ws = null
    }
    state.value.running = false
  }

  const progress = computed(() => {
    if (state.value.maxIter === 0) return 0
    return Math.round((state.value.iteration / state.value.maxIter) * 100)
  })

  return {
    state,
    start,
    stop,
    progress,
  }
}
