<script setup lang="ts">
/**
 * Cinematic Harris Hawks Optimization — obra de arte.
 *
 * The backend sends one iteration every ~0.4s (server-side pacing).
 * This component processes each update immediately and lets hawks
 * glide smoothly toward their targets over many frames.
 */

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  iteration: number
  maxIter: number
  running: boolean
  popSize?: number
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animId = 0
let dpr = 1
let fc = 0  // frame counter

// ======================== TYPES ========================

interface Star { x: number; y: number; r: number; tw: number; sp: number }
interface Hawk {
  x: number; y: number
  tx: number; ty: number
  vx: number; vy: number
  angle: number
  trail: Array<{ x: number; y: number; age: number }>
  phase: 'explore' | 'transition' | 'siege'
  size: number; wing: number; wingSpd: number; orbOff: number
}
interface Spark {
  x: number; y: number; vx: number; vy: number
  life: number; maxLife: number; r: number; g: number; b: number; sz: number
}

// ======================== STATE ========================

let stars: Star[] = []
let hawks: Hawk[] = []
let sparks: Spark[] = []
let rabbitX = 0.5, rabbitY = 0.5, rabbitPulse = 0
let paretoNorm: Array<{ x: number; y: number }> = []
let progress = 0
let dispIter = 0
let finished = false
let completionFc = 0
let resetFlash = 0

// ======================== HELPERS ========================

function phaseRGB(p: string): [number, number, number] {
  if (p === 'siege') return [255, 120, 40]
  if (p === 'transition') return [255, 200, 60]
  return [80, 160, 255]
}

// ======================== INITIALIZATION ========================

function initStars(n: number) {
  stars = Array.from({ length: n }, () => ({
    x: Math.random(), y: Math.random(),
    r: 0.3 + Math.random() * 1.6,
    tw: Math.random() * Math.PI * 2,
    sp: 0.008 + Math.random() * 0.025,
  }))
}

function spawnHawks(n: number) {
  const count = Math.max(n || 20, 5)
  hawks = Array.from({ length: count }, () => ({
    x: 0.05 + Math.random() * 0.9,
    y: 0.05 + Math.random() * 0.9,
    tx: 0.25 + Math.random() * 0.5,
    ty: 0.25 + Math.random() * 0.5,
    vx: (Math.random() - 0.5) * 0.002,
    vy: (Math.random() - 0.5) * 0.002,
    angle: Math.random() * Math.PI * 2,
    trail: [],
    phase: 'explore' as const,
    size: 28 + Math.random() * 16,
    wing: Math.random() * Math.PI * 2,
    wingSpd: 0.06 + Math.random() * 0.04,
    orbOff: Math.random() * Math.PI * 2,
  }))
  sparks = []
}

function normalize(pts: Array<{ f1: number; f2: number }>) {
  if (!pts.length) return []
  const m = 0.1
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2)
  const f1min = Math.min(...f1s), f1max = Math.max(...f1s)
  const f2min = Math.min(...f2s), f2max = Math.max(...f2s)
  return pts.map(p => ({
    x: m + (1 - 2 * m) * (p.f1 - f1min) / Math.max(f1max - f1min, 0.001),
    y: m + (1 - 2 * m) * (p.f2 - f2min) / Math.max(f2max - f2min, 0.001),
  }))
}

function fullReset() {
  spawnHawks(props.popSize || 20)
  paretoNorm = []
  rabbitX = 0.5; rabbitY = 0.5
  fc = 0; progress = 0; dispIter = 0
  finished = false; completionFc = 0
  resetFlash = 45
}

// ======================== CANVAS ========================

function setupCanvas() {
  const cvs = canvasRef.value
  if (!cvs) return
  dpr = window.devicePixelRatio || 1
  const rect = cvs.getBoundingClientRect()
  const nw = Math.round(rect.width * dpr)
  const nh = Math.round(rect.height * dpr)
  if (cvs.width !== nw || cvs.height !== nh) {
    cvs.width = nw; cvs.height = nh
    const ctx = cvs.getContext('2d')
    if (ctx) ctx.scale(dpr, dpr)
  }
}

// ======================== WATCHERS ========================

watch(() => props.running, (r) => {
  if (r) { finished = false; fullReset() }
  else if (props.iteration > 0) { finished = true; completionFc = fc }
})

watch(() => props.popSize, (n) => {
  if (!props.running && !props.iteration) spawnHawks(n || 20)
})

// Process each pareto update directly (backend is already paced)
watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0
  dispIter = props.iteration

  if (paretoNorm.length > 0) {
    rabbitX = paretoNorm[0].x; rabbitY = paretoNorm[0].y
  }

  // Scatter stays meaningful even late — hawks should never pile up
  const scatter = Math.max(0.22 * (1 - progress * 0.6), 0.14)
  hawks.forEach((h, i) => {
    // Distribute hawks across pareto solutions evenly
    const tgt = paretoNorm[i % Math.max(paretoNorm.length, 1)]
    if (tgt) {
      // Add per-hawk angular offset so they don't all land on the same spot
      const ang = (i / hawks.length) * Math.PI * 2
      const dist = scatter * (0.4 + 0.6 * ((i * 7 + 3) % hawks.length) / hawks.length)
      h.tx = tgt.x + Math.cos(ang) * dist * 0.5 + (Math.random() - 0.5) * scatter * 0.3
      h.ty = tgt.y + Math.sin(ang) * dist * 0.5 + (Math.random() - 0.5) * scatter * 0.3
    }
    h.phase = progress < 0.3 ? 'explore' : progress < 0.65 ? 'transition' : 'siege'
  })
}, { deep: true })

// ======================== DRAWING — BACKGROUND ========================

function drawBg(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const hue = 230 - progress * 30
  const g = ctx.createLinearGradient(0, 0, 0, H)
  g.addColorStop(0, `hsl(${hue},40%,5%)`); g.addColorStop(0.5, `hsl(${hue - 10},35%,7%)`); g.addColorStop(1, `hsl(${hue - 20},30%,4%)`)
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H)

  // Nebula
  const t = fc * 0.002
  for (let i = 0; i < 3; i++) {
    const cx = W * (0.3 + 0.4 * Math.sin(t + i * 2.1))
    const cy = H * (0.3 + 0.4 * Math.cos(t * 0.7 + i * 1.7))
    const r = W * (0.15 + 0.1 * Math.sin(t * 0.4 + i))
    const ng = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    ng.addColorStop(0, `hsla(${hue + i * 30 - progress * 60},70%,35%,0.04)`)
    ng.addColorStop(1, 'transparent')
    ctx.fillStyle = ng; ctx.fillRect(0, 0, W, H)
  }

  // Stars
  stars.forEach(s => { s.tw += s.sp; const a = 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(s.tw)); ctx.beginPath(); ctx.fillStyle = `rgba(200,215,255,${a})`; ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2); ctx.fill() })

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.015)'; ctx.lineWidth = 0.5
  for (let i = 1; i < 20; i++) { const gx = (i / 20) * W, gy = (i / 20) * H; ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke() }

  // Vignette
  const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) * 0.8)
  vg.addColorStop(0, 'transparent'); vg.addColorStop(1, 'rgba(0,0,0,0.35)')
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H)
}

// ======================== DRAWING — CONNECTIONS ========================

function drawConstellations(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const maxD = 0.2; ctx.lineWidth = 0.7; let c = 0
  for (let i = 0; i < hawks.length && c < 80; i++) {
    for (let j = i + 1; j < hawks.length && c < 80; j++) {
      const dx = hawks[i].x - hawks[j].x, dy = hawks[i].y - hawks[j].y
      const d = Math.sqrt(dx * dx + dy * dy)
      if (d < maxD) { const a = 0.08 * (1 - d / maxD); const [r, g, b] = phaseRGB(hawks[i].phase); ctx.strokeStyle = `rgba(${r},${g},${b},${a})`; ctx.beginPath(); ctx.moveTo(hawks[i].x * W, hawks[i].y * H); ctx.lineTo(hawks[j].x * W, hawks[j].y * H); ctx.stroke(); c++ }
    }
  }
}

function drawParetoFront(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (paretoNorm.length < 1) return
  if (paretoNorm.length > 1) {
    const sorted = [...paretoNorm].sort((a, b) => a.x - b.x)
    ctx.beginPath(); ctx.strokeStyle = 'rgba(60,130,255,0.35)'; ctx.lineWidth = 2.5
    ctx.shadowColor = '#0066ff'; ctx.shadowBlur = 16
    ctx.moveTo(sorted[0].x * W, sorted[0].y * H)
    for (let i = 1; i < sorted.length; i++) ctx.lineTo(sorted[i].x * W, sorted[i].y * H)
    ctx.stroke(); ctx.shadowBlur = 0
  }
  paretoNorm.forEach((p, i) => { const pulse = 0.4 + 0.6 * Math.sin(fc * 0.04 + i * 0.3); ctx.beginPath(); ctx.fillStyle = `rgba(60,140,255,${pulse * 0.7})`; ctx.arc(p.x * W, p.y * H, 4, 0, Math.PI * 2); ctx.fill() })
}

function drawBeams(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (progress < 0.55) return
  const int = (progress - 0.55) / 0.45
  hawks.forEach(h => {
    if (h.phase !== 'siege') return
    const dx = rabbitX - h.x, dy = rabbitY - h.y, d = Math.sqrt(dx * dx + dy * dy)
    if (d > 0.4) return
    ctx.beginPath(); ctx.strokeStyle = `rgba(255,200,50,${int * 0.2 * (1 - d / 0.4)})`; ctx.lineWidth = 1.5; ctx.setLineDash([6, 8])
    ctx.moveTo(h.x * W, h.y * H); ctx.lineTo(rabbitX * W, rabbitY * H); ctx.stroke(); ctx.setLineDash([])
  })
}

// ======================== DRAWING — HAWK ========================

function drawHawk(ctx: CanvasRenderingContext2D, h: Hawk, W: number, H: number) {
  const px = h.x * W, py = h.y * H
  const [cr, cg, cb] = phaseRGB(h.phase)

  // Trail
  if (h.trail.length > 1) {
    for (let i = 1; i < h.trail.length; i++) {
      const t = h.trail[i], prev = h.trail[i - 1]
      const a = Math.max(0, 1 - t.age / 60) * 0.5
      if (a <= 0) continue
      ctx.beginPath(); ctx.strokeStyle = `rgba(${cr},${cg},${cb},${a})`; ctx.lineWidth = (1 - t.age / 60) * 5; ctx.lineCap = 'round'
      ctx.moveTo(prev.x * W, prev.y * H); ctx.lineTo(t.x * W, t.y * H); ctx.stroke()
    }
  }

  ctx.save(); ctx.translate(px, py); ctx.rotate(h.angle)

  const s = h.size, flap = Math.sin(h.wing), wSpan = s * 2.4, bLen = s * 1.3

  // Aura
  const aR = finished ? s * 2.5 : s * 2
  const ap = finished ? 0.14 + 0.06 * Math.sin(fc * 0.035 + h.orbOff) : 0.08 + 0.05 * Math.sin(fc * 0.06 + h.orbOff)
  const ag = ctx.createRadialGradient(0, 0, s * 0.2, 0, 0, aR)
  if (finished) { ag.addColorStop(0, `rgba(0,229,160,${ap})`); ag.addColorStop(0.5, `rgba(${cr},${cg},${cb},${ap * 0.3})`) }
  else { ag.addColorStop(0, `rgba(${cr},${cg},${cb},${ap})`) }
  ag.addColorStop(1, 'transparent')
  ctx.fillStyle = ag; ctx.beginPath(); ctx.arc(0, 0, aR, 0, Math.PI * 2); ctx.fill()

  ctx.shadowColor = `rgb(${cr},${cg},${cb})`; ctx.shadowBlur = h.phase === 'siege' ? 30 : 18; ctx.lineWidth = 3.5; ctx.lineCap = 'round'

  // Wings
  for (const side of [-1, 1]) {
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.9)`; ctx.beginPath(); ctx.moveTo(0, 0)
    ctx.bezierCurveTo(side * wSpan * 0.3, -wSpan * 0.4 * flap, side * wSpan * 0.5, -wSpan * 0.35 * flap, side * wSpan * 0.55, -wSpan * 0.08 * flap); ctx.stroke()
    ctx.beginPath(); ctx.fillStyle = `rgba(${cr},${cg},${cb},0.15)`; ctx.moveTo(0, 0)
    ctx.bezierCurveTo(side * wSpan * 0.3, -wSpan * 0.4 * flap, side * wSpan * 0.5, -wSpan * 0.35 * flap, side * wSpan * 0.55, -wSpan * 0.08 * flap)
    ctx.lineTo(side * wSpan * 0.15, bLen * 0.2); ctx.closePath(); ctx.fill()
  }

  // Feathers
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.35)`; ctx.lineWidth = 1.5
  for (const side of [-1, 1]) { for (let f = 0; f < 4; f++) { const fx = side * wSpan * (0.33 + f * 0.06), fy = -wSpan * (0.28 - f * 0.05) * flap; ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(fx + side * s * 0.12, fy + s * 0.18); ctx.stroke() } }

  ctx.shadowBlur = 0

  // Body
  ctx.beginPath(); ctx.fillStyle = `rgba(${cr},${cg},${cb},0.95)`; ctx.ellipse(0, 0, s * 0.38, bLen * 0.5, 0, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = 'rgba(255,255,255,0.16)'; ctx.ellipse(-s * 0.1, -bLen * 0.15, s * 0.14, bLen * 0.2, -0.2, 0, Math.PI * 2); ctx.fill()

  // Head
  ctx.beginPath(); ctx.fillStyle = `rgba(${Math.min(255, cr + 40)},${Math.min(255, cg + 40)},${Math.min(255, cb + 40)},1)`
  ctx.arc(0, -bLen * 0.48, s * 0.28, 0, Math.PI * 2); ctx.fill()

  // Eye
  ctx.beginPath(); ctx.fillStyle = '#fff'; ctx.arc(s * 0.08, -bLen * 0.5, s * 0.13, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = '#000'; ctx.arc(s * 0.09, -bLen * 0.5, s * 0.065, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.arc(s * 0.11, -bLen * 0.52, s * 0.025, 0, Math.PI * 2); ctx.fill()

  // Beak
  ctx.beginPath(); ctx.fillStyle = '#666'; ctx.moveTo(s * 0.1, -bLen * 0.62); ctx.lineTo(s * 0.26, -bLen * 0.68); ctx.lineTo(s * 0.1, -bLen * 0.55); ctx.closePath(); ctx.fill()

  // Tail
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.5)`; ctx.lineWidth = 2.5
  for (let t = -2; t <= 2; t++) { ctx.beginPath(); ctx.moveTo(t * s * 0.1, bLen * 0.4); ctx.quadraticCurveTo(t * s * 0.15, bLen * 0.65, t * s * 0.22, bLen * 0.85); ctx.stroke() }

  ctx.restore()
}

// ======================== DRAWING — RABBIT ========================

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number) {
  ctx.save(); ctx.translate(x, y)

  if (finished) {
    const ga = 0.18 + 0.08 * Math.sin(fc * 0.025)
    const vg = ctx.createRadialGradient(0, 0, 8, 0, 0, 100); vg.addColorStop(0, `rgba(255,215,0,${ga})`); vg.addColorStop(0.4, `rgba(0,229,160,${ga * 0.5})`); vg.addColorStop(1, 'transparent')
    ctx.fillStyle = vg; ctx.beginPath(); ctx.arc(0, 0, 100, 0, Math.PI * 2); ctx.fill()
    for (let i = 0; i < 3; i++) { const p = (pulse * 0.4 + i / 3) % 1, r = 28 + p * 70; ctx.beginPath(); ctx.strokeStyle = `rgba(255,215,0,${0.4 * (1 - p)})`; ctx.lineWidth = 3 * (1 - p); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke() }
  } else {
    if (progress > 0.55) { const ca = (progress - 0.55) / 0.45 * 0.35; ctx.strokeStyle = `rgba(255,51,102,${ca})`; ctx.lineWidth = 1; ctx.setLineDash([5, 5]); ctx.beginPath(); ctx.moveTo(-60, 0); ctx.lineTo(-24, 0); ctx.stroke(); ctx.beginPath(); ctx.moveTo(24, 0); ctx.lineTo(60, 0); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, -60); ctx.lineTo(0, -36); ctx.stroke(); ctx.beginPath(); ctx.moveTo(0, 30); ctx.lineTo(0, 60); ctx.stroke(); ctx.beginPath(); ctx.arc(0, 0, 48, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]) }
    const rc = 3 + Math.floor(progress * 4)
    for (let i = 0; i < rc; i++) { const p = (pulse + i / rc) % 1, r = 22 + p * 80; ctx.beginPath(); ctx.strokeStyle = `rgba(255,51,102,${0.5 * (1 - p) * (0.3 + progress * 0.7)})`; ctx.lineWidth = 4 * (1 - p); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke() }
  }

  const glR = finished ? 75 : 55; const glC = finished ? 'rgba(255,215,0,0.3)' : 'rgba(255,51,102,0.3)'; const gg = ctx.createRadialGradient(0, 5, 0, 0, 5, glR); gg.addColorStop(0, glC); gg.addColorStop(1, 'transparent'); ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(0, 5, glR, 0, Math.PI * 2); ctx.fill()

  ctx.shadowColor = finished ? '#FFD700' : '#FF3366'; ctx.shadowBlur = finished ? 40 : 30
  ctx.fillStyle = finished ? '#FFD700' : '#FF3366'; ctx.beginPath(); ctx.ellipse(0, 5, 18, 22, 0, 0, Math.PI * 2); ctx.fill()
  ctx.shadowBlur = 0; ctx.fillStyle = finished ? '#FFE040' : '#FF4477'; ctx.beginPath(); ctx.arc(0, -16, 14, 0, Math.PI * 2); ctx.fill()

  for (const side of [-1, 1]) { ctx.fillStyle = finished ? '#FFD700' : '#FF3366'; ctx.beginPath(); ctx.ellipse(side * 8, -38, 5.5, 15, side * 0.15, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = finished ? '#FFED80' : '#FF88AA'; ctx.beginPath(); ctx.ellipse(side * 8, -37, 3.5, 11, side * 0.15, 0, Math.PI * 2); ctx.fill() }
  for (const side of [-1, 1]) { ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(side * 5.5, -16, 5, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#220011'; ctx.beginPath(); ctx.arc(side * 5.5, -16, 2.5, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.beginPath(); ctx.arc(side * 6.5, -17.5, 1.3, 0, Math.PI * 2); ctx.fill() }
  ctx.fillStyle = finished ? '#FFE080' : '#FFaacc'; ctx.beginPath(); ctx.arc(0, -9, 2.8, 0, Math.PI * 2); ctx.fill()
  ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.lineWidth = 0.8; for (const side of [-1, 1]) { ctx.beginPath(); ctx.moveTo(side * 6, -9); ctx.lineTo(side * 24, -13); ctx.stroke(); ctx.beginPath(); ctx.moveTo(side * 6, -8); ctx.lineTo(side * 22, -4); ctx.stroke() }
  ctx.fillStyle = finished ? '#FFED80' : '#FFccdd'; ctx.beginPath(); ctx.arc(0, 24, 8, 0, Math.PI * 2); ctx.fill()

  ctx.textAlign = 'center'
  if (finished) { ctx.fillStyle = `rgba(0,229,160,${0.6 + 0.3 * Math.sin(fc * 0.03)})`; ctx.font = 'bold 14px Inter, sans-serif'; ctx.fillText('\u2605 CAPTURADA \u2605', 0, -65) }
  else { ctx.fillStyle = `rgba(255,51,102,${0.5 + 0.2 * Math.sin(fc * 0.04)})`; ctx.font = 'bold 12px Inter, sans-serif'; ctx.fillText('PRESA', 0, -60) }
  ctx.restore()
}

// ======================== DRAWING — HUD ========================

function drawHUD(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (dispIter <= 0 && !finished) return

  const label = finished ? 'COMPLETADO' : progress < 0.3 ? 'EXPLORACI\u00d3N' : progress < 0.65 ? 'TRANSICI\u00d3N' : 'ASEDIO'
  const [pr, pg, pb] = finished ? [0, 229, 160] : progress < 0.3 ? [80, 160, 255] : progress < 0.65 ? [255, 200, 60] : [255, 120, 40]
  const E = finished ? '0.00' : (2 * (1 - progress)).toFixed(2)

  ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.beginPath(); ctx.roundRect(W - 195, 8, 183, 82, 10); ctx.fill()
  ctx.strokeStyle = `rgba(${pr},${pg},${pb},0.4)`; ctx.lineWidth = 1; ctx.beginPath(); ctx.roundRect(W - 195, 8, 183, 82, 10); ctx.stroke()

  ctx.textAlign = 'right'; ctx.fillStyle = `rgba(${pr},${pg},${pb},0.95)`; ctx.font = 'bold 14px Inter, sans-serif'; ctx.fillText(label, W - 22, 30)
  ctx.fillStyle = 'rgba(255,255,255,0.5)'; ctx.font = '11px "JetBrains Mono", monospace'
  ctx.fillText(`E(t) = ${E}`, W - 22, 48); ctx.fillText(`iter ${dispIter} / ${props.maxIter}`, W - 22, 63); ctx.fillText(`${paretoNorm.length} Pareto \u00b7 ${hawks.length} hawks`, W - 22, 78)

  ctx.textAlign = 'center'; ctx.fillStyle = 'rgba(255,255,255,0.15)'; ctx.font = '11px Inter, sans-serif'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 10)
  ctx.save(); ctx.translate(14, H / 2); ctx.rotate(-Math.PI / 2); ctx.fillText('f\u2082 \u2014 Disparidad', 0, 0); ctx.restore()

  if (finished) {
    const ba = 0.6 + 0.2 * Math.sin(fc * 0.025); ctx.textAlign = 'center'
    ctx.font = 'bold 18px Inter, sans-serif'; ctx.fillStyle = `rgba(0,229,160,${ba})`; ctx.fillText('OPTIMIZACI\u00d3N COMPLETADA', W / 2, H - 38)
    ctx.font = '12px Inter, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillText(`${paretoNorm.length} soluciones Pareto \u00b7 ${hawks.length} halcones`, W / 2, H - 18)
  }
}

// ======================== MAIN LOOP ========================

function frame() {
  const cvs = canvasRef.value
  if (!cvs) { animId = requestAnimationFrame(frame); return }
  const ctx = cvs.getContext('2d')
  if (!ctx) { animId = requestAnimationFrame(frame); return }

  fc++
  const W = cvs.width / dpr, H = cvs.height / dpr
  if (hawks.length === 0) spawnHawks(props.popSize || 20)

  // ---- Background ----
  drawBg(ctx, W, H)

  // ---- Reset flash ----
  if (resetFlash > 0) {
    resetFlash--; const a = (resetFlash / 45) * 0.65
    ctx.fillStyle = `rgba(80,160,255,${a})`; ctx.fillRect(0, 0, W, H)
    if (resetFlash > 20) { ctx.textAlign = 'center'; ctx.font = 'bold 22px Inter, sans-serif'; ctx.fillStyle = `rgba(255,255,255,${a * 1.5})`; ctx.fillText('REINICIANDO...', W / 2, H / 2) }
  }

  // ---- Connections ----
  drawConstellations(ctx, W, H); drawParetoFront(ctx, W, H); drawBeams(ctx, W, H)

  // ---- Sparks ----
  sparks = sparks.filter(s => s.life > 0)
  sparks.forEach(s => { s.x += s.vx; s.y += s.vy; s.vy += 0.0001; s.vx *= 0.97; s.vy *= 0.97; s.life--; const a = s.life / s.maxLife; ctx.beginPath(); ctx.fillStyle = `rgba(${s.r},${s.g},${s.b},${a * 0.8})`; ctx.arc(s.x * W, s.y * H, s.sz * a, 0, Math.PI * 2); ctx.fill() })

  // ---- Hawks physics + draw ----
  hawks.forEach((h, idx) => {
    let effTx = h.tx, effTy = h.ty

    if (h.phase === 'siege' || finished) {
      // Per-hawk orbit radius — spread them out so they don't overlap
      const layer = idx % 5
      const bR = finished ? (0.06 + layer * 0.025) : (0.035 + layer * 0.015)
      const aR = finished ? 0.03 : 0.015
      const oR = bR + aR * Math.sin(fc * 0.007 + h.orbOff * 3)
      const oA = fc * (finished ? 0.008 + layer * 0.003 : 0.012 + layer * 0.004) + h.orbOff + idx * 0.45
      effTx = h.tx + Math.cos(oA) * oR; effTy = h.ty + Math.sin(oA) * oR
    }

    const dx = effTx - h.x, dy = effTy - h.y

    // Very slow, deliberate motion
    const accel = h.phase === 'explore' ? 0.0006 : h.phase === 'transition' ? 0.0015 : 0.004
    const noise = h.phase === 'explore' ? 0.001 : h.phase === 'transition' ? 0.0004 : 0
    h.vx += dx * accel + (Math.random() - 0.5) * noise
    h.vy += dy * accel + (Math.random() - 0.5) * noise

    if (h.phase === 'siege' && !finished && Math.random() < 0.004) { const l = Math.pow(Math.random(), -0.5) * 0.015; h.vx += (Math.random() - 0.5) * l; h.vy += (Math.random() - 0.5) * l }

    // Heavy damping = slow, cinematic gliding
    h.vx *= 0.95; h.vy *= 0.95
    const spd = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    const maxS = finished ? 0.006 : h.phase === 'siege' ? 0.01 : 0.006
    if (spd > maxS) { h.vx *= maxS / spd; h.vy *= maxS / spd }

    h.x += h.vx; h.y += h.vy
    h.x = Math.max(0.02, Math.min(0.98, h.x)); h.y = Math.max(0.02, Math.min(0.98, h.y))
    if (h.x <= 0.02 || h.x >= 0.98) h.vx *= -0.5
    if (h.y <= 0.02 || h.y >= 0.98) h.vy *= -0.5

    if (spd > 0.0004) { const tgt = Math.atan2(h.vy, h.vx) + Math.PI / 2; let d2 = tgt - h.angle; while (d2 > Math.PI) d2 -= Math.PI * 2; while (d2 < -Math.PI) d2 += Math.PI * 2; h.angle += d2 * 0.06 }

    h.wing += h.wingSpd + (h.phase === 'siege' ? 0.05 : 0)

    h.trail.push({ x: h.x, y: h.y, age: 0 }); h.trail.forEach(t => t.age++); h.trail = h.trail.filter(t => t.age < 60)

    // Sparks
    if (h.phase === 'siege' && !finished) {
      const dR = Math.sqrt(Math.pow(h.x - rabbitX, 2) + Math.pow(h.y - rabbitY, 2))
      if (dR < 0.15 && Math.random() < 0.08 && sparks.length < 200) { const a2 = Math.random() * Math.PI * 2, sp2 = 0.002 + Math.random() * 0.004; sparks.push({ x: h.x, y: h.y, vx: Math.cos(a2) * sp2, vy: Math.sin(a2) * sp2, life: 30 + Math.random() * 40, maxLife: 70, r: 255, g: 180 + Math.floor(Math.random() * 75), b: 0, sz: 2.5 + Math.random() * 2.5 }) }
    }

    drawHawk(ctx, h, W, H)
  })

  // ---- Rabbit (always on top) ----
  rabbitPulse = (rabbitPulse + 0.004) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse)

  // ---- Completion shockwave ----
  if (finished && completionFc > 0) {
    const el = fc - completionFc
    if (el < 180) {
      const p = el / 180, maxR = Math.max(W, H) * 0.65
      ctx.beginPath(); ctx.strokeStyle = `rgba(0,229,160,${0.5 * (1 - p)})`; ctx.lineWidth = 5 * (1 - p); ctx.arc(rabbitX * W, rabbitY * H, maxR * p, 0, Math.PI * 2); ctx.stroke()
      if (p > 0.15) { const p2 = (p - 0.15) / 0.85; ctx.beginPath(); ctx.strokeStyle = `rgba(255,215,0,${0.4 * (1 - p2)})`; ctx.lineWidth = 4 * (1 - p2); ctx.arc(rabbitX * W, rabbitY * H, maxR * 0.65 * p2, 0, Math.PI * 2); ctx.stroke() }
    }
  }

  drawHUD(ctx, W, H)
  animId = requestAnimationFrame(frame)
}

// ======================== LIFECYCLE ========================

let resizeHandler: (() => void) | null = null

onMounted(() => {
  setupCanvas(); initStars(200); spawnHawks(props.popSize || 20)
  animId = requestAnimationFrame(frame)
  resizeHandler = () => setupCanvas()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => { cancelAnimationFrame(animId); if (resizeHandler) window.removeEventListener('resize', resizeHandler) })
</script>

<template>
  <div class="relative">
    <canvas ref="canvasRef" class="w-full h-[600px] rounded-xl" />
    <div class="absolute top-3 left-3 flex flex-wrap gap-2 text-[10px] text-gray-400/80">
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm"><span class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(80,160,255,0.8)]" /> Exploraci&oacute;n</span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm"><span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_rgba(255,200,60,0.8)]" /> Transici&oacute;n</span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm"><span class="w-2 h-2 rounded-full bg-orange-400 shadow-[0_0_6px_rgba(255,120,40,0.8)]" /> Asedio</span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm"><span class="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,51,102,0.8)]" /> Presa</span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm"><span class="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_6px_rgba(0,100,255,0.8)]" /> Frente Pareto</span>
    </div>
  </div>
</template>
