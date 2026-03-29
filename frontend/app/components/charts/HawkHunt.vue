<script setup lang="ts">
/**
 * HawkHunt v5 — Cinematic Tactical Visualization
 *
 * Chevron agents with afterburner exhaust, scanner rings.
 * Target core with radar sweep, shield arcs, holographic brackets.
 * HUD moved to HTML overlay to avoid overlap.
 * Siege zone visualization with danger field.
 */

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  iteration: number
  maxIter: number
  running: boolean
  completed: boolean
  popSize?: number
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animId = 0
let dpr = 1
let fc = 0

// ═══ HUD (reactive for HTML overlay) ═══
const hudProgress = computed(() => props.maxIter > 0 ? props.iteration / props.maxIter : 0)
const hudPhase = computed(() => {
  if (props.completed) return 'COMPLETADO'
  if (hudProgress.value < 0.3) return 'EXPLORACIÓN'
  if (hudProgress.value < 0.65) return 'TRANSICIÓN'
  return 'ASEDIO'
})
const hudEnergy = computed(() => {
  if (props.completed) return '0.00'
  return (2 * (1 - hudProgress.value)).toFixed(2)
})
const hudBorder = computed(() => {
  if (props.completed) return 'border-emerald-500/30'
  if (hudProgress.value < 0.3) return 'border-blue-500/30'
  if (hudProgress.value < 0.65) return 'border-yellow-500/30'
  return 'border-orange-500/30'
})
const hudText = computed(() => {
  if (props.completed) return 'text-emerald-400'
  if (hudProgress.value < 0.3) return 'text-blue-400'
  if (hudProgress.value < 0.65) return 'text-yellow-400'
  return 'text-orange-400'
})
const hudGlow = computed(() => {
  if (props.completed) return 'shadow-[0_0_15px_rgba(52,211,153,0.15)]'
  if (hudProgress.value < 0.3) return 'shadow-[0_0_15px_rgba(96,165,250,0.15)]'
  if (hudProgress.value < 0.65) return 'shadow-[0_0_15px_rgba(250,204,21,0.15)]'
  return 'shadow-[0_0_15px_rgba(251,146,60,0.15)]'
})

// ═══════════════════ TYPES ═══════════════════

interface Star { x: number; y: number; r: number; tw: number; sp: number }

interface Hawk {
  x: number; y: number
  tx: number; ty: number
  vx: number; vy: number
  angle: number
  trail: Array<{ x: number; y: number; age: number }>
  phase: 'explore' | 'transition' | 'siege'
  size: number; wing: number; wingSpd: number
  orbOff: number
  hIdx: number
}

interface Spark {
  x: number; y: number; vx: number; vy: number
  life: number; maxLife: number
  r: number; g: number; b: number; sz: number
}

// ═══════════════════ STATE ═══════════════════

let stars: Star[] = []
let hawks: Hawk[] = []
let sparks: Spark[] = []

let rabbitX = 0.5, rabbitY = 0.5
let rabbitTx = 0.5, rabbitTy = 0.5
let rabbitPulse = 0

let paretoNorm: Array<{ x: number; y: number }> = []
let progress = 0
let dispIter = 0
let finished = false
let completionFc = 0
let resetFlash = 0
let scanY = 0
let prevPhase = 'explore'
let phaseFlash = 0

// ═══════════════════ HELPERS ═══════════════════

function phaseRGB(p: string): [number, number, number] {
  if (p === 'siege') return [255, 120, 40]
  if (p === 'transition') return [255, 200, 60]
  return [80, 160, 255]
}

function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v))
}

// ═══════════════════ INITIALIZATION ═══════════════════

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
  hawks = Array.from({ length: count }, (_, i) => ({
    x: 0.05 + Math.random() * 0.9,
    y: 0.05 + Math.random() * 0.9,
    tx: 0.25 + Math.random() * 0.5,
    ty: 0.25 + Math.random() * 0.5,
    vx: (Math.random() - 0.5) * 0.002,
    vy: (Math.random() - 0.5) * 0.002,
    angle: Math.random() * Math.PI * 2,
    trail: [],
    phase: 'explore' as const,
    size: 24 + Math.random() * 12,
    wing: Math.random() * Math.PI * 2,
    wingSpd: 0.06 + Math.random() * 0.04,
    orbOff: Math.random() * Math.PI * 2,
    hIdx: i,
  }))
  sparks = []
}

function normalize(pts: Array<{ f1: number; f2: number }>) {
  if (!pts.length) return []
  const m = 0.12
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
  rabbitTx = 0.5; rabbitTy = 0.5
  fc = 0; progress = 0; dispIter = 0
  finished = false; completionFc = 0
  resetFlash = 50; prevPhase = 'explore'; phaseFlash = 0
}

// ═══════════════════ CANVAS ═══════════════════

function setupCanvas() {
  const cvs = canvasRef.value
  if (!cvs) return
  dpr = window.devicePixelRatio || 1
  const rect = cvs.getBoundingClientRect()
  const nw = Math.round(rect.width * dpr)
  const nh = Math.round(rect.height * dpr)
  if (nw < 1 || nh < 1) return
  if (cvs.width !== nw || cvs.height !== nh) {
    cvs.width = nw; cvs.height = nh
    const ctx = cvs.getContext('2d')
    if (ctx) ctx.scale(dpr, dpr)
  }
}

// ═══════════════════ WATCHERS ═══════════════════

watch(() => props.running, (r) => {
  if (r) {
    finished = false
    completionFc = 0
    fullReset()
  }
})

watch(() => props.completed, (done) => {
  if (done && !finished) {
    finished = true
    completionFc = fc
    for (let i = 0; i < 80; i++) {
      const a = Math.random() * Math.PI * 2
      const sp = 0.003 + Math.random() * 0.008
      sparks.push({
        x: rabbitX, y: rabbitY,
        vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
        life: 60 + Math.random() * 90, maxLife: 150,
        r: Math.random() > 0.5 ? 255 : 0,
        g: 180 + Math.floor(Math.random() * 75),
        b: Math.random() > 0.5 ? 160 : Math.floor(Math.random() * 60),
        sz: 3 + Math.random() * 4,
      })
    }
  }
})

watch(() => props.popSize, (n) => {
  if (!props.running && !props.completed && dispIter === 0) spawnHawks(n || 20)
})

watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0
  dispIter = props.iteration

  if (paretoNorm.length > 0) {
    rabbitTx = paretoNorm[0].x
    rabbitTy = paretoNorm[0].y
  }

  const phase = progress < 0.3 ? 'explore' : progress < 0.65 ? 'transition' : 'siege'

  // Phase transition flash
  if (phase !== prevPhase) {
    prevPhase = phase
    phaseFlash = 40
  }

  hawks.forEach((h, i) => {
    h.phase = phase
    if (phase !== 'siege') {
      const scatter = phase === 'explore' ? 0.40 : 0.22
      const tgt = paretoNorm[i % Math.max(paretoNorm.length, 1)]
      if (tgt) {
        const ang = (i / hawks.length) * Math.PI * 2
        h.tx = tgt.x + Math.cos(ang) * scatter * 0.4 + (Math.random() - 0.5) * scatter * 0.3
        h.ty = tgt.y + Math.sin(ang) * scatter * 0.4 + (Math.random() - 0.5) * scatter * 0.3
        h.tx = clamp(h.tx, 0.06, 0.94)
        h.ty = clamp(h.ty, 0.06, 0.94)
      }
    }
  })
}, { deep: true })

// ═══════════════════ DRAW — BACKGROUND ═══════════════════

function drawBg(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const hue = 230 - progress * 30
  const g = ctx.createLinearGradient(0, 0, 0, H)
  g.addColorStop(0, `hsl(${hue},40%,4%)`)
  g.addColorStop(0.5, `hsl(${hue - 10},35%,6%)`)
  g.addColorStop(1, `hsl(${hue - 20},30%,3%)`)
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H)

  const t = fc * 0.002
  for (let i = 0; i < 3; i++) {
    const cx = W * (0.3 + 0.4 * Math.sin(t + i * 2.1))
    const cy = H * (0.3 + 0.4 * Math.cos(t * 0.7 + i * 1.7))
    const r = W * (0.15 + 0.1 * Math.sin(t * 0.4 + i))
    const ng = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    ng.addColorStop(0, `hsla(${hue + i * 30 - progress * 60},70%,35%,0.03)`)
    ng.addColorStop(1, 'transparent')
    ctx.fillStyle = ng; ctx.fillRect(0, 0, W, H)
  }

  stars.forEach(s => {
    s.tw += s.sp
    const a = 0.2 + 0.8 * (0.5 + 0.5 * Math.sin(s.tw))
    ctx.beginPath(); ctx.fillStyle = `rgba(200,215,255,${a})`
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2); ctx.fill()
  })

  // Tactical grid
  ctx.strokeStyle = 'rgba(255,255,255,0.018)'; ctx.lineWidth = 0.5
  const gs = 50
  for (let gx = gs; gx < W; gx += gs) {
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke()
  }
  for (let gy = gs; gy < H; gy += gs) {
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke()
  }
  ctx.fillStyle = 'rgba(255,255,255,0.035)'
  for (let gx = gs; gx < W; gx += gs) {
    for (let gy = gs; gy < H; gy += gs) {
      ctx.beginPath(); ctx.arc(gx, gy, 1, 0, Math.PI * 2); ctx.fill()
    }
  }

  // Scanning line
  scanY = (scanY + 0.4) % H
  const slg = ctx.createLinearGradient(0, scanY - 40, 0, scanY + 40)
  slg.addColorStop(0, 'transparent')
  slg.addColorStop(0.5, `rgba(${finished ? '0,229,160' : '80,160,255'},0.025)`)
  slg.addColorStop(1, 'transparent')
  ctx.fillStyle = slg; ctx.fillRect(0, scanY - 40, W, 80)

  // Vignette
  const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) * 0.8)
  vg.addColorStop(0, 'transparent'); vg.addColorStop(1, 'rgba(0,0,0,0.4)')
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H)
}

// ═══════════════════ DRAW — CONNECTIONS ═══════════════════

function drawConstellations(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const maxD = 0.22; ctx.lineWidth = 0.7; let c = 0
  for (let i = 0; i < hawks.length && c < 80; i++) {
    for (let j = i + 1; j < hawks.length && c < 80; j++) {
      const dx = hawks[i].x - hawks[j].x, dy = hawks[i].y - hawks[j].y
      const d = Math.sqrt(dx * dx + dy * dy)
      if (d < maxD) {
        const a = 0.08 * (1 - d / maxD)
        const [r, g, b] = phaseRGB(hawks[i].phase)
        ctx.strokeStyle = `rgba(${r},${g},${b},${a})`
        ctx.beginPath()
        ctx.moveTo(hawks[i].x * W, hawks[i].y * H)
        ctx.lineTo(hawks[j].x * W, hawks[j].y * H)
        ctx.stroke(); c++
      }
    }
  }
}

function drawParetoFront(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (paretoNorm.length < 1) return
  if (paretoNorm.length > 1) {
    const sorted = [...paretoNorm].sort((a, b) => a.x - b.x)
    // Glow line (wider, softer)
    ctx.beginPath(); ctx.strokeStyle = 'rgba(60,130,255,0.12)'; ctx.lineWidth = 8
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'
    ctx.moveTo(sorted[0].x * W, sorted[0].y * H)
    for (let i = 1; i < sorted.length; i++) ctx.lineTo(sorted[i].x * W, sorted[i].y * H)
    ctx.stroke()
    // Core line
    ctx.beginPath(); ctx.strokeStyle = 'rgba(60,130,255,0.45)'; ctx.lineWidth = 2
    ctx.moveTo(sorted[0].x * W, sorted[0].y * H)
    for (let i = 1; i < sorted.length; i++) ctx.lineTo(sorted[i].x * W, sorted[i].y * H)
    ctx.stroke()
  }
  paretoNorm.forEach((p, i) => {
    const pulse = 0.4 + 0.6 * Math.sin(fc * 0.04 + i * 0.3)
    ctx.beginPath(); ctx.fillStyle = `rgba(60,140,255,${pulse * 0.7})`
    ctx.arc(p.x * W, p.y * H, 4, 0, Math.PI * 2); ctx.fill()
  })
}

function drawBeams(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (progress < 0.55 || finished) return
  const int = (progress - 0.55) / 0.45
  hawks.forEach(h => {
    if (h.phase !== 'siege') return
    const dx = rabbitX - h.x, dy = rabbitY - h.y
    const d = Math.sqrt(dx * dx + dy * dy)
    if (d > 0.4) return
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,200,50,${int * 0.15 * (1 - d / 0.4)})`
    ctx.lineWidth = 1; ctx.setLineDash([6, 8])
    ctx.moveTo(h.x * W, h.y * H)
    ctx.lineTo(rabbitX * W, rabbitY * H)
    ctx.stroke(); ctx.setLineDash([])
  })
}

function drawFormationRings(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (!finished && progress < 0.65) return
  const numRings = finished ? 4 : 3
  const baseR = finished ? 0.10 : 0.06
  const spacing = finished ? 0.05 : 0.04
  const alpha = finished ? 0.06 : 0.03 * ((progress - 0.65) / 0.35)

  for (let ring = 0; ring < numRings; ring++) {
    const r = (baseR + ring * spacing) * Math.min(W, H)
    ctx.beginPath()
    ctx.strokeStyle = finished
      ? `rgba(0,229,160,${alpha})`
      : `rgba(255,120,40,${alpha})`
    ctx.lineWidth = 1
    ctx.setLineDash([4, 8])
    ctx.arc(rabbitX * W, rabbitY * H, r, 0, Math.PI * 2)
    ctx.stroke()
    ctx.setLineDash([])
  }
}

// ═══════════════════ DRAW — SIEGE ZONE ═══════════════════

function drawSiegeZone(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (progress < 0.55 || finished) return
  const intensity = (progress - 0.55) / 0.45
  const zoneR = 0.20 * Math.min(W, H)
  const rx = rabbitX * W, ry = rabbitY * H
  const pa = 0.035 * intensity * (0.7 + 0.3 * Math.sin(fc * 0.03))

  const zg = ctx.createRadialGradient(rx, ry, zoneR * 0.2, rx, ry, zoneR)
  zg.addColorStop(0, `rgba(255,100,30,${pa})`)
  zg.addColorStop(1, 'rgba(255,100,30,0)')
  ctx.fillStyle = zg
  ctx.beginPath()
  ctx.arc(rx, ry, zoneR, 0, Math.PI * 2)
  ctx.fill()
}

// ═══════════════════ DRAW — HAWK (v5 Chevron + Afterburner) ═══════════════════
// ALL absolute coordinates — NO save/restore/translate/rotate/ellipse/shadow

function drawHawk(ctx: CanvasRenderingContext2D, h: Hawk, W: number, H: number) {
  const px = h.x * W, py = h.y * H
  const [cr, cg, cb] = phaseRGB(h.phase)
  const s = h.size * 0.5

  // Direction vectors
  const ca = Math.cos(h.angle - Math.PI / 2)
  const sa = Math.sin(h.angle - Math.PI / 2)
  const pa = Math.cos(h.angle)
  const qa = Math.sin(h.angle)

  // Energy trail
  if (h.trail.length > 1) {
    for (let i = 1; i < h.trail.length; i++) {
      const t = h.trail[i], prev = h.trail[i - 1]
      const a = Math.max(0, 1 - t.age / 60) * 0.25
      if (a <= 0) continue
      ctx.beginPath()
      ctx.strokeStyle = finished
        ? `rgba(0,229,160,${a})`
        : `rgba(${cr},${cg},${cb},${a})`
      ctx.lineWidth = (1 - t.age / 60) * 2
      ctx.lineCap = 'round'
      ctx.moveTo(prev.x * W, prev.y * H)
      ctx.lineTo(t.x * W, t.y * H)
      ctx.stroke()
    }
  }

  // Subtle outer glow (reduced from v4)
  const aR = finished ? s * 0.9 : (h.phase === 'siege' ? s * 0.6 : s * 0.8)
  const ap = finished
    ? 0.05 + 0.025 * Math.sin(fc * 0.035 + h.orbOff)
    : 0.03 + 0.015 * Math.sin(fc * 0.06 + h.orbOff)
  ctx.beginPath()
  ctx.fillStyle = finished
    ? `rgba(0,229,160,${ap})`
    : `rgba(${cr},${cg},${cb},${ap})`
  ctx.arc(px, py, aR, 0, Math.PI * 2)
  ctx.fill()

  // Chevron geometry
  const tipX = px + ca * s * 0.9
  const tipY = py + sa * s * 0.9
  const lWingX = px - ca * s * 0.3 + pa * s * 0.5
  const lWingY = py - sa * s * 0.3 + qa * s * 0.5
  const rWingX = px - ca * s * 0.3 - pa * s * 0.5
  const rWingY = py - sa * s * 0.3 - qa * s * 0.5
  const notchX = px - ca * s * 0.1
  const notchY = py - sa * s * 0.1

  // ── Afterburner exhaust (speed-based) ──
  const spd = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
  if (spd > 0.0006) {
    const intensity = Math.min(1, spd / 0.004)
    const burnLen = s * (0.4 + intensity * 1.8)
    const burnW = s * 0.18

    const bTipX = notchX - ca * burnLen
    const bTipY = notchY - sa * burnLen

    ctx.beginPath()
    ctx.moveTo(notchX + pa * burnW, notchY + qa * burnW)
    ctx.lineTo(bTipX, bTipY)
    ctx.lineTo(notchX - pa * burnW, notchY - qa * burnW)
    ctx.closePath()

    const fg = ctx.createLinearGradient(notchX, notchY, bTipX, bTipY)
    if (finished) {
      fg.addColorStop(0, `rgba(200,255,230,${0.45 * intensity})`)
      fg.addColorStop(0.3, `rgba(0,229,160,${0.25 * intensity})`)
      fg.addColorStop(1, 'rgba(0,229,160,0)')
    } else {
      fg.addColorStop(0, `rgba(255,255,255,${0.35 * intensity})`)
      fg.addColorStop(0.25, `rgba(${cr},${cg},${cb},${0.35 * intensity})`)
      fg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`)
    }
    ctx.fillStyle = fg
    ctx.fill()
  }

  // Outer chevron fill + stroke
  ctx.beginPath()
  ctx.moveTo(tipX, tipY)
  ctx.lineTo(lWingX, lWingY)
  ctx.lineTo(notchX, notchY)
  ctx.lineTo(rWingX, rWingY)
  ctx.closePath()

  if (finished) {
    ctx.fillStyle = 'rgba(0,229,160,0.65)'
    ctx.strokeStyle = 'rgba(0,229,160,0.9)'
  } else {
    ctx.fillStyle = `rgba(${cr},${cg},${cb},0.55)`
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.85)`
  }
  ctx.fill()
  ctx.lineWidth = 1.5
  ctx.lineJoin = 'miter'
  ctx.stroke()

  // Inner chevron accent
  const is2 = 0.45
  ctx.beginPath()
  ctx.moveTo(px + ca * s * 0.9 * is2, py + sa * s * 0.9 * is2)
  ctx.lineTo(px - ca * s * 0.3 * is2 + pa * s * 0.5 * is2, py - sa * s * 0.3 * is2 + qa * s * 0.5 * is2)
  ctx.lineTo(px - ca * s * 0.1 * is2, py - sa * s * 0.1 * is2)
  ctx.lineTo(px - ca * s * 0.3 * is2 - pa * s * 0.5 * is2, py - sa * s * 0.3 * is2 - qa * s * 0.5 * is2)
  ctx.closePath()
  ctx.fillStyle = finished ? 'rgba(0,229,160,0.3)' : `rgba(${cr},${cg},${cb},0.25)`
  ctx.fill()

  // Scanner ring (rotating partial arc)
  const scanRot = fc * 0.035 + h.orbOff * 3
  const scanR = s * 0.55
  ctx.beginPath()
  ctx.arc(px, py, scanR, scanRot, scanRot + Math.PI * 0.5)
  ctx.strokeStyle = finished ? 'rgba(0,229,160,0.18)' : `rgba(${cr},${cg},${cb},0.12)`
  ctx.lineWidth = 1
  ctx.stroke()

  // Core dot
  ctx.beginPath()
  ctx.fillStyle = finished
    ? 'rgba(200,255,230,0.95)'
    : `rgba(${Math.min(255, cr + 100)},${Math.min(255, cg + 100)},${Math.min(255, cb + 100)},0.9)`
  ctx.arc(px, py, 2, 0, Math.PI * 2)
  ctx.fill()
}

// ═══════════════════ DRAW — TARGET (v5 Tactical Core) ═══════════════════

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number) {
  const color: [number, number, number] = finished ? [0, 229, 160] : [255, 51, 102]
  const cs = `${color[0]},${color[1]},${color[2]}`

  // Outer glow
  if (finished) {
    const ga = 0.15 + 0.08 * Math.sin(fc * 0.025)
    ctx.beginPath(); ctx.fillStyle = `rgba(255,215,0,${ga * 0.1})`
    ctx.arc(x, y, 100, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(0,229,160,${ga * 0.15})`
    ctx.arc(x, y, 50, 0, Math.PI * 2); ctx.fill()
  } else {
    ctx.beginPath(); ctx.fillStyle = `rgba(${cs},0.035)`
    ctx.arc(x, y, 55, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(${cs},0.07)`
    ctx.arc(x, y, 28, 0, Math.PI * 2); ctx.fill()
  }

  // ── Radar sweep ──
  const sweepAngle = fc * 0.02
  const sweepR = finished ? 75 : 55
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.arc(x, y, sweepR, sweepAngle, sweepAngle + 0.5)
  ctx.closePath()
  const sg = ctx.createRadialGradient(x, y, 0, x, y, sweepR)
  sg.addColorStop(0, `rgba(${cs},0.1)`)
  sg.addColorStop(1, `rgba(${cs},0)`)
  ctx.fillStyle = sg
  ctx.fill()
  // Sweep leading edge
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(
    x + Math.cos(sweepAngle + 0.5) * sweepR,
    y + Math.sin(sweepAngle + 0.5) * sweepR,
  )
  ctx.strokeStyle = `rgba(${cs},0.2)`
  ctx.lineWidth = 1
  ctx.stroke()

  // ── Shield arcs (rotating partial circles) ──
  const shR = finished ? 34 : 26
  const shRot = fc * 0.01
  ctx.lineWidth = 1.5
  ctx.strokeStyle = finished ? 'rgba(0,229,160,0.25)' : `rgba(${cs},0.2)`
  ctx.beginPath(); ctx.arc(x, y, shR, shRot, shRot + Math.PI * 0.7); ctx.stroke()
  ctx.beginPath(); ctx.arc(x, y, shR, shRot + Math.PI, shRot + Math.PI * 1.7); ctx.stroke()
  // Outer shield (slower, larger)
  const shR2 = shR + 8
  const shRot2 = -fc * 0.007
  ctx.strokeStyle = finished ? 'rgba(0,229,160,0.12)' : `rgba(${cs},0.09)`
  ctx.lineWidth = 1
  ctx.beginPath(); ctx.arc(x, y, shR2, shRot2, shRot2 + Math.PI * 0.5); ctx.stroke()
  ctx.beginPath(); ctx.arc(x, y, shR2, shRot2 + Math.PI * 0.8, shRot2 + Math.PI * 1.3); ctx.stroke()
  ctx.beginPath(); ctx.arc(x, y, shR2, shRot2 + Math.PI * 1.6, shRot2 + Math.PI * 2.1); ctx.stroke()

  // Pulse rings
  const rc = finished ? 4 : 3 + Math.floor(progress * 3)
  for (let i = 0; i < rc; i++) {
    const p = (pulse + i / rc) % 1
    const r = 16 + p * 65
    const a = (1 - p) * (finished ? 0.3 : 0.2 + progress * 0.3)
    ctx.beginPath()
    ctx.strokeStyle = finished ? `rgba(255,215,0,${a})` : `rgba(${cs},${a})`
    ctx.lineWidth = 2 * (1 - p)
    ctx.arc(x, y, r, 0, Math.PI * 2)
    ctx.stroke()
  }

  // Targeting brackets (4 corners)
  const bSz = finished ? 28 : 22
  const bLen = 9
  const ba = finished
    ? 0.6 + 0.25 * Math.sin(fc * 0.03)
    : 0.45 + 0.2 * Math.sin(fc * 0.04)
  ctx.strokeStyle = finished ? `rgba(0,229,160,${ba})` : `rgba(${cs},${ba})`
  ctx.lineWidth = 2; ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.moveTo(x - bSz, y - bSz + bLen); ctx.lineTo(x - bSz, y - bSz); ctx.lineTo(x - bSz + bLen, y - bSz)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(x + bSz - bLen, y - bSz); ctx.lineTo(x + bSz, y - bSz); ctx.lineTo(x + bSz, y - bSz + bLen)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(x + bSz, y + bSz - bLen); ctx.lineTo(x + bSz, y + bSz); ctx.lineTo(x + bSz - bLen, y + bSz)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(x - bSz + bLen, y + bSz); ctx.lineTo(x - bSz, y + bSz); ctx.lineTo(x - bSz, y + bSz - bLen)
  ctx.stroke()

  // Crosshair lines
  if (progress > 0.5 || finished) {
    const ci = finished ? 0.3 : ((progress - 0.5) / 0.5) * 0.2
    ctx.strokeStyle = `rgba(${cs},${ci})`
    ctx.lineWidth = 1; ctx.setLineDash([3, 5])
    const cLen = finished ? 55 : 42
    const gap = bSz + 5
    ctx.beginPath(); ctx.moveTo(x - cLen, y); ctx.lineTo(x - gap, y); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(x + gap, y); ctx.lineTo(x + cLen, y); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(x, y - cLen); ctx.lineTo(x, y - gap); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(x, y + gap); ctx.lineTo(x, y + cLen); ctx.stroke()
    ctx.setLineDash([])
  }

  // Rotating diamond core
  const rot = fc * 0.015
  const dSz = finished ? 13 : 9
  ctx.beginPath()
  ctx.moveTo(x + Math.cos(rot) * dSz, y + Math.sin(rot) * dSz)
  ctx.lineTo(x + Math.cos(rot + Math.PI * 0.5) * dSz, y + Math.sin(rot + Math.PI * 0.5) * dSz)
  ctx.lineTo(x + Math.cos(rot + Math.PI) * dSz, y + Math.sin(rot + Math.PI) * dSz)
  ctx.lineTo(x + Math.cos(rot + Math.PI * 1.5) * dSz, y + Math.sin(rot + Math.PI * 1.5) * dSz)
  ctx.closePath()
  ctx.fillStyle = finished ? 'rgba(255,215,0,0.75)' : `rgba(${cs},0.7)`
  ctx.fill()
  ctx.strokeStyle = finished ? 'rgba(255,255,200,0.8)' : 'rgba(255,255,255,0.4)'
  ctx.lineWidth = 1.5
  ctx.stroke()

  // Inner counter-rotating diamond
  const rot2 = -fc * 0.01
  const dSz2 = dSz * 0.55
  ctx.beginPath()
  ctx.moveTo(x + Math.cos(rot2) * dSz2, y + Math.sin(rot2) * dSz2)
  ctx.lineTo(x + Math.cos(rot2 + Math.PI * 0.5) * dSz2, y + Math.sin(rot2 + Math.PI * 0.5) * dSz2)
  ctx.lineTo(x + Math.cos(rot2 + Math.PI) * dSz2, y + Math.sin(rot2 + Math.PI) * dSz2)
  ctx.lineTo(x + Math.cos(rot2 + Math.PI * 1.5) * dSz2, y + Math.sin(rot2 + Math.PI * 1.5) * dSz2)
  ctx.closePath()
  ctx.fillStyle = 'rgba(255,255,255,0.6)'
  ctx.fill()

  // Central dot
  ctx.beginPath()
  ctx.fillStyle = '#fff'
  ctx.arc(x, y, 2.5, 0, Math.PI * 2)
  ctx.fill()

  // Label
  ctx.textAlign = 'center'
  ctx.font = 'bold 10px "JetBrains Mono", monospace'
  if (finished) {
    ctx.fillStyle = `rgba(0,229,160,${0.7 + 0.3 * Math.sin(fc * 0.03)})`
    ctx.fillText('\u25C6 CAPTURADA \u25C6', x, y - bSz - 12)
  } else {
    ctx.fillStyle = `rgba(${cs},${0.5 + 0.2 * Math.sin(fc * 0.04)})`
    ctx.fillText('L\u00cdDER PARETO', x, y - bSz - 12)
  }
}

// ═══════════════════ DRAW — CANVAS LABELS ═══════════════════

function drawLabels(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const M = 32 // axis margin

  // ── Axis lines with arrows ──
  // X axis line + arrow
  ctx.strokeStyle = 'rgba(250,204,21,0.4)'; ctx.lineWidth = 1.2
  ctx.beginPath(); ctx.moveTo(M, H - M); ctx.lineTo(W - 10, H - M); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(W - 10, H - M); ctx.lineTo(W - 17, H - M - 4); ctx.moveTo(W - 10, H - M); ctx.lineTo(W - 17, H - M + 4); ctx.stroke()
  // Y axis line + arrow
  ctx.strokeStyle = 'rgba(0,229,160,0.4)'
  ctx.beginPath(); ctx.moveTo(M, H - M); ctx.lineTo(M, 10); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(M, 10); ctx.lineTo(M - 4, 17); ctx.moveTo(M, 10); ctx.lineTo(M + 4, 17); ctx.stroke()

  // ── X axis label (bottom center) ──
  ctx.textAlign = 'center'
  ctx.font = 'bold 12px Inter, sans-serif'
  ctx.fillStyle = 'rgba(250,204,21,0.75)'
  ctx.fillText('f\u2081 \u2014 Carga de Espera (a\u00f1os promedio)', W / 2, H - 8)

  // ── Y axis label (vertical, centered) ──
  ctx.save()
  ctx.translate(13, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.font = 'bold 12px Inter, sans-serif'
  ctx.fillStyle = 'rgba(0,229,160,0.75)'
  ctx.fillText('f\u2082 \u2014 Disparidad entre Pa\u00edses', 0, 0)
  ctx.restore()

  // ── Bottom-left context (small, non-overlapping) ──
  ctx.textAlign = 'left'
  ctx.font = '9px Inter, sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.25)'
  ctx.fillText('105 grupos \u00b7 140K visas \u00b7 Menor = mejor', M + 6, H - M - 8)
}

// ═══════════════════ MAIN FRAME LOOP ═══════════════════

function frame() {
  const cvs = canvasRef.value
  if (!cvs) { animId = requestAnimationFrame(frame); return }
  const ctx = cvs.getContext('2d')
  if (!ctx) { animId = requestAnimationFrame(frame); return }

  const W = cvs.width / dpr
  const H = cvs.height / dpr
  if (W < 10 || H < 10) { setupCanvas(); animId = requestAnimationFrame(frame); return }

  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
  ctx.setLineDash([])
  ctx.lineCap = 'butt'
  ctx.lineJoin = 'miter'

  try {

  fc++

  if (hawks.length === 0) spawnHawks(props.popSize || 20)

  drawBg(ctx, W, H)

  // Reset flash
  if (resetFlash > 0) {
    resetFlash--
    const a = (resetFlash / 50) * 0.6
    ctx.fillStyle = `rgba(80,160,255,${a})`; ctx.fillRect(0, 0, W, H)
    if (resetFlash > 25) {
      ctx.textAlign = 'center'; ctx.font = 'bold 22px Inter, sans-serif'
      ctx.fillStyle = `rgba(255,255,255,${a * 1.5})`
      ctx.fillText('REINICIANDO...', W / 2, H / 2)
    }
  }

  // Phase transition flash
  if (phaseFlash > 0) {
    phaseFlash--
    const a = (phaseFlash / 40) * 0.25
    const [pr, pg, pb] = phaseRGB(hawks[0]?.phase || 'explore')
    ctx.fillStyle = `rgba(${pr},${pg},${pb},${a})`; ctx.fillRect(0, 0, W, H)
  }

  drawConstellations(ctx, W, H)
  drawParetoFront(ctx, W, H)
  drawSiegeZone(ctx, W, H)
  drawFormationRings(ctx, W, H)
  drawBeams(ctx, W, H)

  ctx.setLineDash([])

  // Sparks
  sparks = sparks.filter(s => s.life > 0)
  sparks.forEach(s => {
    s.x += s.vx; s.y += s.vy
    s.vy += 0.00008; s.vx *= 0.98; s.vy *= 0.98; s.life--
    const a = s.life / s.maxLife
    ctx.beginPath()
    ctx.fillStyle = `rgba(${s.r},${s.g},${s.b},${a * 0.8})`
    ctx.arc(s.x * W, s.y * H, Math.max(0.1, s.sz * a), 0, Math.PI * 2); ctx.fill()
  })

  // Smooth rabbit
  rabbitX += (rabbitTx - rabbitX) * 0.04
  rabbitY += (rabbitTy - rabbitY) * 0.04
  if (!isFinite(rabbitX)) rabbitX = 0.5
  if (!isFinite(rabbitY)) rabbitY = 0.5

  // Hawks physics + draw
  hawks.forEach((h) => {
    if (!isFinite(h.x) || !isFinite(h.y) || !isFinite(h.vx) || !isFinite(h.vy)) {
      h.x = 0.3 + Math.random() * 0.4
      h.y = 0.3 + Math.random() * 0.4
      h.vx = 0; h.vy = 0
    }

    const idx = h.hIdx
    let effTx: number
    let effTy: number

    if (finished || h.phase === 'siege') {
      const numRings = finished ? 4 : 3
      const ring = idx % numRings
      const baseRadius = finished ? 0.10 : 0.06
      const ringSpacing = finished ? 0.05 : 0.04
      const radius = baseRadius + ring * ringSpacing

      const hawksPerRing = Math.ceil(hawks.length / numRings)
      const posInRing = Math.floor(idx / numRings)
      const baseAngle = (posInRing / hawksPerRing) * Math.PI * 2 + ring * 0.6

      const rotSpeed = finished
        ? 0.004 + ring * 0.002
        : 0.007 + ring * 0.003
      const angle = baseAngle + fc * rotSpeed
      const wobble = 0.01 * Math.sin(fc * 0.013 + h.orbOff * 5)

      effTx = rabbitX + Math.cos(angle) * (radius + wobble)
      effTy = rabbitY + Math.sin(angle) * (radius + wobble)
    } else {
      effTx = h.tx
      effTy = h.ty
    }

    effTx = clamp(effTx, 0.04, 0.96)
    effTy = clamp(effTy, 0.04, 0.96)

    const dx = effTx - h.x
    const dy = effTy - h.y

    const accel = finished ? 0.008
      : h.phase === 'explore' ? 0.0006
      : h.phase === 'transition' ? 0.0015
      : 0.006
    const noise = h.phase === 'explore' ? 0.001 : h.phase === 'transition' ? 0.0004 : 0

    h.vx += dx * accel + (Math.random() - 0.5) * noise
    h.vy += dy * accel + (Math.random() - 0.5) * noise

    if (h.phase === 'siege' && !finished && Math.random() < 0.003) {
      const l = Math.pow(Math.max(Math.random(), 0.001), -0.5) * 0.012
      h.vx += (Math.random() - 0.5) * l
      h.vy += (Math.random() - 0.5) * l
    }

    const damping = finished ? 0.92 : 0.95
    h.vx *= damping; h.vy *= damping
    const spd = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    const maxS = finished ? 0.008 : h.phase === 'siege' ? 0.012 : 0.006
    if (spd > maxS) { h.vx *= maxS / spd; h.vy *= maxS / spd }

    h.x += h.vx; h.y += h.vy
    h.x = clamp(h.x, 0.02, 0.98)
    h.y = clamp(h.y, 0.02, 0.98)
    if (h.x <= 0.02 || h.x >= 0.98) h.vx *= -0.5
    if (h.y <= 0.02 || h.y >= 0.98) h.vy *= -0.5

    if (spd > 0.0004) {
      const tgt = Math.atan2(h.vy, h.vx) + Math.PI / 2
      let d2 = tgt - h.angle
      while (d2 > Math.PI) d2 -= Math.PI * 2
      while (d2 < -Math.PI) d2 += Math.PI * 2
      h.angle += d2 * 0.06
    }

    h.wing += h.wingSpd + (h.phase === 'siege' ? 0.05 : 0)

    h.trail.push({ x: h.x, y: h.y, age: 0 })
    h.trail.forEach(t => t.age++)
    h.trail = h.trail.filter(t => t.age < 60)

    if (h.phase === 'siege' && !finished) {
      const dR = Math.sqrt(Math.pow(h.x - rabbitX, 2) + Math.pow(h.y - rabbitY, 2))
      if (dR < 0.15 && Math.random() < 0.06 && sparks.length < 200) {
        const a2 = Math.random() * Math.PI * 2, sp2 = 0.002 + Math.random() * 0.004
        sparks.push({
          x: h.x, y: h.y, vx: Math.cos(a2) * sp2, vy: Math.sin(a2) * sp2,
          life: 30 + Math.random() * 40, maxLife: 70,
          r: 255, g: 180 + Math.floor(Math.random() * 75), b: 0,
          sz: 2.5 + Math.random() * 2.5,
        })
      }
    }

    if (finished && Math.random() < 0.008 && sparks.length < 300) {
      const a2 = Math.random() * Math.PI * 2, sp2 = 0.001 + Math.random() * 0.003
      sparks.push({
        x: h.x, y: h.y, vx: Math.cos(a2) * sp2, vy: Math.sin(a2) * sp2,
        life: 40 + Math.random() * 60, maxLife: 100,
        r: Math.random() > 0.5 ? 0 : 255,
        g: 180 + Math.floor(Math.random() * 75),
        b: Math.random() > 0.5 ? 160 : 0,
        sz: 2 + Math.random() * 3,
      })
    }

    drawHawk(ctx, h, W, H)
  })

  // Target
  rabbitPulse = (rabbitPulse + 0.004) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse)

  // Completion shockwave
  if (finished && completionFc > 0) {
    const el = fc - completionFc
    if (el < 260) {
      const p = el / 260
      const maxR = Math.max(W, H) * 0.75
      ctx.beginPath()
      ctx.strokeStyle = `rgba(0,229,160,${0.5 * (1 - p)})`
      ctx.lineWidth = 5 * (1 - p)
      ctx.arc(rabbitX * W, rabbitY * H, maxR * p, 0, Math.PI * 2); ctx.stroke()
      if (p > 0.10) {
        const p2 = (p - 0.10) / 0.90
        ctx.beginPath()
        ctx.strokeStyle = `rgba(255,215,0,${0.4 * (1 - p2)})`
        ctx.lineWidth = 4 * (1 - p2)
        ctx.arc(rabbitX * W, rabbitY * H, maxR * 0.6 * p2, 0, Math.PI * 2); ctx.stroke()
      }
      if (p > 0.22) {
        const p3 = (p - 0.22) / 0.78
        ctx.beginPath()
        ctx.strokeStyle = `rgba(80,160,255,${0.3 * (1 - p3)})`
        ctx.lineWidth = 3 * (1 - p3)
        ctx.arc(rabbitX * W, rabbitY * H, maxR * 0.4 * p3, 0, Math.PI * 2); ctx.stroke()
      }
    }
  }

  // Canvas labels
  drawLabels(ctx, W, H)

  } catch (e) {
    console.error('HawkHunt frame error:', e)
  }

  animId = requestAnimationFrame(frame)
}

// ═══════════════════ LIFECYCLE ═══════════════════

let resizeHandler: (() => void) | null = null

onMounted(() => {
  setupCanvas(); initStars(200); spawnHawks(props.popSize || 20)
  animId = requestAnimationFrame(frame)
  resizeHandler = () => setupCanvas()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})
</script>

<template>
  <div class="relative">
    <canvas ref="canvasRef" class="w-full h-[660px] rounded-xl" />

    <!-- Legend (top-left) -->
    <div class="absolute top-3 left-3 flex flex-wrap gap-2 text-[10px] text-gray-400/80">
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(80,160,255,0.8)]" /> Exploraci&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_rgba(255,200,60,0.8)]" /> Transici&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-orange-400 shadow-[0_0_6px_rgba(255,120,40,0.8)]" /> Asedio
      </span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,51,102,0.8)]" /> Objetivo
      </span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_6px_rgba(0,100,255,0.8)]" /> Frente Pareto
      </span>
    </div>

    <!-- HUD Panel (bottom-right, HTML overlay) -->
    <div
      v-if="props.iteration > 0 || props.completed"
      class="absolute bottom-4 right-4 bg-black/70 backdrop-blur-md rounded-lg border px-4 py-3 text-right min-w-[180px]"
      :class="[hudBorder, hudGlow]"
    >
      <p class="text-sm font-bold tracking-widest" :class="hudText">{{ hudPhase }}</p>
      <div class="mt-1.5 space-y-0.5 text-[11px] font-mono text-gray-400">
        <p>E(t) = {{ hudEnergy }}</p>
        <p>iter {{ props.iteration }} / {{ props.maxIter }}</p>
        <p>{{ props.paretoFront.length }} Pareto &middot; {{ props.popSize || 20 }} hawks</p>
      </div>
    </div>
  </div>
</template>
