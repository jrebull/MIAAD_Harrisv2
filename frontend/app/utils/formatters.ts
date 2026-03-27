export function formatNumber(n: number): string {
  return n.toLocaleString('es-MX')
}

export function formatDecimal(n: number, decimals: number = 3): string {
  return n.toFixed(decimals)
}

export function formatPercent(n: number): string {
  return `${n.toFixed(1)}%`
}

export function formatDelta(n: number): string {
  const sign = n > 0 ? '+' : ''
  return `${sign}${n.toLocaleString('es-MX')}`
}
