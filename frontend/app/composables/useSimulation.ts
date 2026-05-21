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

// Cinematic base interval (ms per iteration) at 1x speed, adaptive to length.
function baseInterval(maxIter: number): number {
  if (maxIter <= 100) return 360
  if (maxIter <= 200) return 240
  return 130
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

  // Playback controls — the server streams as fast as it can; the client
  // paces the animation, so speed / pause are fully client-side.
  const speed = useState<number>('simSpeed', () => 1)   // 0.5 | 1 | 2
  const paused = useState<boolean>('simPaused', () => false)

  let ws: WebSocket | null = null
  let buffer: IterationSnapshot[] = []   // raw incoming frames (non-reactive)
  let cursor = 0                          // next frame index to display
  let serverDone = false
  let baseMs = 360
  let playbackTimer: ReturnType<typeof setTimeout> | null = null

  function applySnapshot(snap: IterationSnapshot) {
    state.value.iteration = snap.iteration
    state.value.archiveSize = snap.archiveSize
    state.value.hv = snap.hv
    state.value.hvHistory = [...state.value.hvHistory, snap.hv]
    state.value.paretoFront = snap.paretoFront
    state.value.history = [...state.value.history, snap]
  }

  function scheduleNext() {
    if (playbackTimer) clearTimeout(playbackTimer)
    const delay = paused.value ? 120 : Math.max(40, baseMs / speed.value)
    playbackTimer = setTimeout(playbackTick, delay)
  }

  function playbackTick() {
    if (paused.value) { scheduleNext(); return }

    if (cursor < buffer.length) {
      applySnapshot(buffer[cursor])
      cursor++
      scheduleNext()
    } else if (serverDone) {
      // Played every buffered frame and the server is finished.
      state.value.running = false
      if (state.value.iteration > 0) state.value.completed = true
      playbackTimer = null
    } else {
      // Waiting for more frames to arrive.
      scheduleNext()
    }
  }

  function clearPlayback() {
    if (playbackTimer) { clearTimeout(playbackTimer); playbackTimer = null }
  }

  function closeSocket() {
    if (ws) {
      ws.onopen = null
      ws.onmessage = null
      ws.onerror = null
      ws.onclose = null
      ws.close()
      ws = null
    }
  }

  function start(popSize: number = 30, maxIter: number = 100, seed: number = 42) {
    closeSocket()
    clearPlayback()

    buffer = []
    cursor = 0
    serverDone = false
    baseMs = baseInterval(maxIter)
    paused.value = false

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
        buffer.push({
          iteration: data.iteration,
          archiveSize: data.archive_size,
          hv: data.hv,
          paretoFront: data.pareto_front,
        })
      } else if (data.type === 'complete') {
        serverDone = true
      } else if (data.type === 'error') {
        serverDone = true
        console.error('Simulation error:', data.message)
      }
    }

    // A dropped/failed connection still lets playback drain whatever arrived.
    ws.onerror = () => { serverDone = true }
    ws.onclose = () => { serverDone = true }

    scheduleNext()
  }

  function stop() {
    closeSocket()
    clearPlayback()
    state.value.running = false
  }

  // Scrub to a specific iteration in history (used after the run completes).
  function seekTo(historyIdx: number) {
    const snap = state.value.history[historyIdx]
    if (!snap) return
    state.value.iteration = snap.iteration
    state.value.archiveSize = snap.archiveSize
    state.value.hv = snap.hv
    state.value.paretoFront = snap.paretoFront
  }

  function setSpeed(s: number) {
    speed.value = s
    if (paused.value) paused.value = false
    scheduleNext()
  }

  function togglePause() {
    paused.value = !paused.value
    scheduleNext()
  }

  const progress = computed(() => {
    if (state.value.maxIter === 0) return 0
    return Math.round((state.value.iteration / state.value.maxIter) * 100)
  })

  return {
    state,
    speed,
    paused,
    start,
    stop,
    seekTo,
    setSpeed,
    togglePause,
    progress,
  }
}
