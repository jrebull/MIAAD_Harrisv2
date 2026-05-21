import { reactive } from 'vue'
import type { Fitness } from '~/composables/useOptimizer'

// Verified FIFO baseline (matches the original Streamlit app and summary.json).
// Used as a fallback so the UI shows correct numbers even if /api/summary is
// unreachable; replaced with the live API value as soon as it loads.
const fifo = reactive<Fitness>({ f1: 7.2138, f2: 12.6377, f3: 17540 })
let loaded = false
let inflight: Promise<Fitness> | null = null

export const useFifoBaseline = () => {
  const { fetchSummary } = useOptimizer()

  async function ensureFifo(): Promise<Fitness> {
    if (loaded) return fifo
    if (inflight) return inflight
    inflight = (async () => {
      try {
        const s = await fetchSummary()
        if (s?.baseline) {
          fifo.f1 = s.baseline.f1
          fifo.f2 = s.baseline.f2
          fifo.f3 = s.baseline.f3
          loaded = true
        }
      } catch {
        // Keep the verified fallback constants on failure.
      } finally {
        inflight = null
      }
      return fifo
    })()
    return inflight
  }

  return { fifo, ensureFifo }
}
