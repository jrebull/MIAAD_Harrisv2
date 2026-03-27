interface IterationSnapshot {
  iteration: number
  archiveSize: number
  hv: number
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
}

interface SimulationState {
  running: boolean
  iteration: number
  maxIter: number
  archiveSize: number
  hv: number
  hvHistory: number[]
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  history: IterationSnapshot[]
  completed: boolean
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
    history: [],
    completed: false,
  }))

  let ws: WebSocket | null = null

  function start(popSize: number = 30, maxIter: number = 100, seed: number = 42) {
    // Close existing connection — null handlers first to prevent stale
    // onclose from setting running=false after we reset state
    if (ws) {
      ws.onopen = null
      ws.onmessage = null
      ws.onerror = null
      ws.onclose = null
      ws.close()
      ws = null
    }

    // Full reset of state
    state.value = {
      running: true,
      iteration: 0,
      maxIter,
      archiveSize: 0,
      hv: 0,
      hvHistory: [],
      paretoFront: [],
      history: [],
      completed: false,
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
        state.value.hvHistory = [...state.value.hvHistory, data.hv]
        state.value.paretoFront = data.pareto_front

        // Store snapshot for scrubber replay
        state.value.history = [...state.value.history, {
          iteration: data.iteration,
          archiveSize: data.archive_size,
          hv: data.hv,
          paretoFront: data.pareto_front,
        }]
      } else if (data.type === 'complete') {
        state.value.running = false
        state.value.completed = true
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

  // Scrub to a specific iteration in history
  function seekTo(historyIdx: number) {
    const snap = state.value.history[historyIdx]
    if (!snap) return
    state.value.iteration = snap.iteration
    state.value.archiveSize = snap.archiveSize
    state.value.hv = snap.hv
    state.value.paretoFront = snap.paretoFront
  }

  const progress = computed(() => {
    if (state.value.maxIter === 0) return 0
    return Math.round((state.value.iteration / state.value.maxIter) * 100)
  })

  return {
    state,
    start,
    stop,
    seekTo,
    progress,
  }
}
