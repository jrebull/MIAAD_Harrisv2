interface Scenario {
  id: string
  name: string
  icon: string
  description: string
  objective: string
}

const scenarios: Scenario[] = [
  { id: 'humanitario', name: 'Humanitario', icon: 'heart', description: 'Min espera (f₁)', objective: 'min_f1' },
  { id: 'equilibrio', name: 'Equilibrio', icon: 'scale', description: 'Balance (knee)', objective: 'knee' },
  { id: 'equidad', name: 'Equidad', icon: 'handshake', description: 'Min brecha (f₂)', objective: 'min_f2' },
  { id: 'max_utilizacion', name: 'Máx. Utilización', icon: 'zap', description: 'Min desperdicio (f₃)', objective: 'min_f3' },
  { id: 'fifo', name: 'FIFO', icon: 'list', description: 'Sistema actual', objective: 'baseline' },
]

export const useScenario = () => {
  const scenario = useState<string>('scenario', () => 'equilibrio')
  const selectedRun = useState<number>('selectedRun', () => 0)

  const currentScenario = computed(() =>
    scenarios.find(s => s.id === scenario.value) || scenarios[1]
  )

  function setScenario(id: string) {
    scenario.value = id
  }

  return {
    scenario,
    scenarios,
    currentScenario,
    selectedRun,
    setScenario,
  }
}
