<script setup lang="ts">
/**
 * Cinematic Harris Hawks Optimization — obra de arte edition.
 * Deep space with nebula, constellation mesh, orbital siege, shooting stars,
 * completion shockwave, large detailed hawks & rabbit.
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
let frameCount = 0
let completionPulse = 0

// ======================== TYPES ========================

interface Star { x: number; y: number; r: number; twinkle: number; speed: number }
interface ShootingStar { x: number; y: number; vx: number; vy: number; life: number; maxLife: number }

interface Hawk {
  x: number; y: number; tx: number; ty: number; vx: number; vy: number
  angle: number; trail: Array<{ x: number; y: number; age: number }>
  phase: 'explore' | 'transition' | 'siege'
  size: number; wing: number; wingSpeed: number; orbitOffset: number
}

interface Spark {
  x: number; y: number; vx: number; vy: number
  life: number; maxLife: number; r: number; g: number; b: number; size: number
}

// ======================== STATE ========================

let stars: Star[] = []
let shootingStars: ShootingStar[] = []
let hawks: Hawk[] = []
let sparks: Spark[] = []
let rabbitX = 0.5, rabbitY = 0.5, rabbitPulse = 0
let paretoNorm: Array<{ x: number; y: number }> = []

// ======================== HELPERS ========================

function phaseRGB(phase: string): [number, number, number] {
  if (phase === 'siege') return [255, 180, 30]
  if (phase === 'transition') return [220, 180, 80]
  return [100, 170, 255]
}

// ======================== INITIALIZATION ========================

function initStars(n: number) {
  stars = Array.from({ length: n }, () => ({
    x: Math.random(), y: Math.random(),
    r: 0.3 + Math.random() * 1.4,
    twinkle: Math.random() * Math.PI * 2,
    speed: 0.008 + Math.random() * 0.025,
  }))
}

function spawnHawks(n: number) {
  const count = Math.max(n || 20, 5)
  hawks = Array.from({ length: count }, () => ({
    x: 0.05 + Math.random() * 0.9,
    y: 0.05 + Math.random() * 0.9,
    tx: 0.25 + Math.random() * 0.5,
    ty: 0.25 + Math.random() * 0.5,
    vx: (Math.random() - 0.5) * 0.003,
    vy: (Math.random() - 0.5) * 0.003,
    angle: Math.random() * Math.PI * 2,
    trail: [],
    phase: 'explore' as const,
    size: 24 + Math.random() * 14,
    wing: Math.random() * Math.PI * 2,
    wingSpeed: 0.07 + Math.random() * 0.04,
    orbitOffset: Math.random() * Math.PI * 2,
  }))
  sparks = []
  shootingStars = []
}

function normalize(pts: Array<{ f1: number; f2: number }>) {
  if (pts.length === 0) return []
  const m = 0.1
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2)
  const f1min = Math.min(...f1s), f1max = Math.max(...f1s)
  const f2min = Math.min(...f2s), f2max = Math.max(...f2s)
  const f1r = Math.max(f1max - f1min, 0.001)
  const f2r = Math.max(f2max - f2min, 0.001)
  return pts.map(p => ({
    x: m + (1 - 2 * m) * (p.f1 - f1min) / f1r,
    y: m + (1 - 2 * m) * (p.f2 - f2min) / f2r,
  }))
}

function fullReset() {
  const cvs = canvasRef.value
  if (cvs) {
    const ctx = cvs.getContext('2d')
    if (ctx) {
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.clearRect(0, 0, cvs.width, cvs.height)
      setupCanvas()
    }
  }
  spawnHawks(props.popSize || 20)
  paretoNorm = []
  rabbitX = 0.5; rabbitY = 0.5
  frameCount = 0
  completionPulse = 0
  finished = false
}

// ======================== DERIVED STATE ========================

/** True once the simulation finishes (not running but has data) */
let finished = false

// ======================== WATCHERS ========================

watch(() => props.running, (isRunning) => {
  if (isRunning) {
    finished = false
    fullReset()
  } else if (props.iteration > 0) {
    finished = true
    completionPulse = 160
    // Expand hawks into a wider victory orbit so they stay clearly visible
    hawks.forEach(h => {
      h.phase = 'siege'
    })
  }
})

watch(() => props.popSize, (n) => {
  if (!props.running && !props.iteration) spawnHawks(n || 20)
})

watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  rabbitX = paretoNorm[0].x
  rabbitY = paretoNorm[0].y

  const scatter = Math.max(0.2 * (1 - progress), 0.03)
  hawks.forEach((h, i) => {
    const tgt = paretoNorm[i % paretoNorm.length]
    h.tx = tgt.x + (Math.random() - 0.5) * scatter
    h.ty = tgt.y + (Math.random() - 0.5) * scatter
    h.phase = progress < 0.3 ? 'explore' : progress < 0.65 ? 'transition' : 'siege'
  })
}, { deep: true })

// ======================== DRAWING — BACKGROUND ========================

function drawNebula(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  const hue = 220 - progress * 180
  const t = frameCount * 0.003
  for (let i = 0; i < 4; i++) {
    const cx = W * (0.25 + 0.5 * Math.sin(t + i * 1.8))
    const cy = H * (0.25 + 0.5 * Math.cos(t * 0.7 + i * 1.5))
    const r = W * (0.18 + 0.12 * Math.sin(t * 0.5 + i * 0.9))
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    grad.addColorStop(0, `hsla(${hue + i * 25},80%,40%,0.05)`)
    grad.addColorStop(0.6, `hsla(${hue + i * 25},60%,20%,0.02)`)
    grad.addColorStop(1, 'transparent')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)
  }
}

function drawStarfield(ctx: CanvasRenderingContext2D, W: number, H: number) {
  stars.forEach(s => {
    s.twinkle += s.speed
    const alpha = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(s.twinkle))
    ctx.beginPath()
    ctx.fillStyle = `rgba(200,215,255,${alpha})`
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2)
    ctx.fill()
  })
}

function updateShootingStars(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (shootingStars.length < 4 && Math.random() < 0.003) {
    const angle = -Math.PI / 4 + (Math.random() - 0.5) * 0.5
    const speed = 0.01 + Math.random() * 0.015
    shootingStars.push({
      x: Math.random() * 0.8 + 0.1, y: Math.random() * 0.25,
      vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
      life: 40 + Math.random() * 25, maxLife: 65,
    })
  }
  shootingStars = shootingStars.filter(s => s.life > 0)
  shootingStars.forEach(s => {
    s.x += s.vx; s.y += s.vy; s.life--
    const alpha = s.life / s.maxLife
    const spd = Math.sqrt(s.vx * s.vx + s.vy * s.vy)
    const tailLen = Math.min(4 / Math.max(spd, 0.001), 300)
    ctx.beginPath()
    ctx.strokeStyle = `rgba(210,225,255,${alpha * 0.8})`
    ctx.lineWidth = 2.5 * alpha
    ctx.lineCap = 'round'
    ctx.moveTo(s.x * W, s.y * H)
    ctx.lineTo((s.x - s.vx * tailLen) * W, (s.y - s.vy * tailLen) * H)
    ctx.stroke()
  })
}

function drawGrid(ctx: CanvasRenderingContext2D, W: number, H: number) {
  ctx.strokeStyle = 'rgba(255,255,255,0.02)'
  ctx.lineWidth = 0.5
  for (let i = 1; i < 20; i++) {
    const gx = (i / 20) * W, gy = (i / 20) * H
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke()
  }
}

function drawVignette(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const grad = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.max(W, H) * 0.78)
  grad.addColorStop(0, 'transparent')
  grad.addColorStop(1, 'rgba(0,0,0,0.3)')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, W, H)
}

// ======================== DRAWING — CONNECTIONS ========================

function drawConstellations(ctx: CanvasRenderingContext2D, W: number, H: number) {
  const maxD = 0.18
  ctx.lineWidth = 0.6
  let count = 0
  for (let i = 0; i < hawks.length && count < 80; i++) {
    for (let j = i + 1; j < hawks.length && count < 80; j++) {
      const dx = hawks[i].x - hawks[j].x
      const dy = hawks[i].y - hawks[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < maxD) {
        const alpha = 0.07 * (1 - dist / maxD)
        const [r, g, b] = phaseRGB(hawks[i].phase)
        ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`
        ctx.beginPath()
        ctx.moveTo(hawks[i].x * W, hawks[i].y * H)
        ctx.lineTo(hawks[j].x * W, hawks[j].y * H)
        ctx.stroke()
        count++
      }
    }
  }
}

function drawParetoFront(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (paretoNorm.length < 1) return

  if (paretoNorm.length === 1) {
    ctx.beginPath()
    ctx.fillStyle = 'rgba(0,100,255,0.6)'
    ctx.shadowColor = '#0066ff'; ctx.shadowBlur = 15
    ctx.arc(paretoNorm[0].x * W, paretoNorm[0].y * H, 5, 0, Math.PI * 2)
    ctx.fill(); ctx.shadowBlur = 0
    return
  }

  const sorted = [...paretoNorm].sort((a, b) => a.x - b.x)
  ctx.beginPath()
  ctx.strokeStyle = 'rgba(0,100,255,0.3)'
  ctx.lineWidth = 2.5
  ctx.shadowColor = '#0066ff'; ctx.shadowBlur = 18
  ctx.moveTo(sorted[0].x * W, sorted[0].y * H)
  for (let i = 1; i < sorted.length; i++) {
    ctx.lineTo(sorted[i].x * W, sorted[i].y * H)
  }
  ctx.stroke()
  ctx.shadowBlur = 0

  sorted.forEach((p, i) => {
    const pulse = 0.5 + 0.5 * Math.sin(frameCount * 0.04 + i * 0.4)
    ctx.beginPath()
    ctx.fillStyle = `rgba(60,140,255,${pulse})`
    ctx.arc(p.x * W, p.y * H, 4, 0, Math.PI * 2)
    ctx.fill()
  })
}

function drawEnergyBeams(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  if (progress < 0.6) return
  const intensity = (progress - 0.6) / 0.4
  hawks.forEach(h => {
    if (h.phase !== 'siege') return
    const dx = rabbitX - h.x, dy = rabbitY - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist > 0.35) return
    const alpha = intensity * 0.18 * (1 - dist / 0.35)
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,200,50,${alpha})`
    ctx.lineWidth = 1.5
    ctx.setLineDash([5, 7])
    ctx.moveTo(h.x * W, h.y * H)
    ctx.lineTo(rabbitX * W, rabbitY * H)
    ctx.stroke()
    ctx.setLineDash([])
  })
}

// ======================== DRAWING — HAWK ========================

function drawHawk(ctx: CanvasRenderingContext2D, h: Hawk, W: number, H: number, isFinished: boolean) {
  const px = h.x * W, py = h.y * H

  // Energy trail
  if (h.trail.length > 1) {
    for (let i = 1; i < h.trail.length; i++) {
      const t = h.trail[i], prev = h.trail[i - 1]
      const alpha = Math.max(0, 1 - t.age / 45) * 0.45
      if (alpha <= 0) continue
      const w = (1 - t.age / 45) * 4
      const [r, g, b] = phaseRGB(h.phase)
      ctx.beginPath()
      ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`
      ctx.lineWidth = w; ctx.lineCap = 'round'
      ctx.moveTo(prev.x * W, prev.y * H)
      ctx.lineTo(t.x * W, t.y * H)
      ctx.stroke()
    }
  }

  ctx.save()
  ctx.translate(px, py)
  ctx.rotate(h.angle)

  const s = h.size
  const flap = Math.sin(h.wing)
  const wingSpan = s * 2.2
  const bodyLen = s * 1.2
  const [cr, cg, cb] = phaseRGB(h.phase)

  // Siege/victory aura
  if (h.phase === 'siege') {
    const auraR = isFinished ? s * 2.2 : s * 1.8
    const ap = isFinished
      ? 0.12 + 0.06 * Math.sin(frameCount * 0.04 + h.orbitOffset)
      : 0.08 + 0.06 * Math.sin(frameCount * 0.06 + h.orbitOffset)
    const ag = ctx.createRadialGradient(0, 0, s * 0.3, 0, 0, auraR)
    if (isFinished) {
      ag.addColorStop(0, `rgba(0,229,160,${ap})`)
      ag.addColorStop(0.6, `rgba(${cr},${cg},${cb},${ap * 0.4})`)
    } else {
      ag.addColorStop(0, `rgba(${cr},${cg},${cb},${ap})`)
    }
    ag.addColorStop(1, 'transparent')
    ctx.fillStyle = ag
    ctx.beginPath(); ctx.arc(0, 0, auraR, 0, Math.PI * 2); ctx.fill()
  }

  ctx.shadowColor = `rgb(${cr},${cg},${cb})`
  ctx.shadowBlur = h.phase === 'siege' ? 28 : 16

  // Wings (both sides)
  ctx.lineWidth = 3.5; ctx.lineCap = 'round'
  for (const side of [-1, 1]) {
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.9)`
    ctx.beginPath()
    ctx.moveTo(0, 0)
    ctx.bezierCurveTo(
      side * wingSpan * 0.3, -wingSpan * 0.4 * flap,
      side * wingSpan * 0.5, -wingSpan * 0.35 * flap,
      side * wingSpan * 0.55, -wingSpan * 0.08 * flap,
    )
    ctx.stroke()

    ctx.beginPath()
    ctx.fillStyle = `rgba(${cr},${cg},${cb},0.14)`
    ctx.moveTo(0, 0)
    ctx.bezierCurveTo(
      side * wingSpan * 0.3, -wingSpan * 0.4 * flap,
      side * wingSpan * 0.5, -wingSpan * 0.35 * flap,
      side * wingSpan * 0.55, -wingSpan * 0.08 * flap,
    )
    ctx.lineTo(side * wingSpan * 0.15, bodyLen * 0.2)
    ctx.closePath(); ctx.fill()
  }

  // Secondary feathers
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.35)`
  ctx.lineWidth = 1.5
  for (const side of [-1, 1]) {
    for (let f = 0; f < 4; f++) {
      const fx = side * wingSpan * (0.33 + f * 0.06)
      const fy = -wingSpan * (0.28 - f * 0.05) * flap
      ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(fx + side * s * 0.12, fy + s * 0.18); ctx.stroke()
    }
  }

  ctx.shadowBlur = 0

  // Body
  ctx.beginPath(); ctx.fillStyle = `rgba(${cr},${cg},${cb},0.95)`
  ctx.ellipse(0, 0, s * 0.35, bodyLen * 0.5, 0, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = 'rgba(255,255,255,0.16)'
  ctx.ellipse(-s * 0.1, -bodyLen * 0.15, s * 0.14, bodyLen * 0.2, -0.2, 0, Math.PI * 2); ctx.fill()

  // Head
  ctx.beginPath()
  ctx.fillStyle = `rgba(${Math.min(255, cr + 40)},${Math.min(255, cg + 40)},${Math.min(255, cb + 40)},1)`
  ctx.arc(0, -bodyLen * 0.48, s * 0.27, 0, Math.PI * 2); ctx.fill()

  // Eye
  ctx.beginPath(); ctx.fillStyle = '#fff'
  ctx.arc(s * 0.08, -bodyLen * 0.5, s * 0.12, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = '#000'
  ctx.arc(s * 0.09, -bodyLen * 0.5, s * 0.06, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = 'rgba(255,255,255,0.85)'
  ctx.arc(s * 0.11, -bodyLen * 0.52, s * 0.025, 0, Math.PI * 2); ctx.fill()

  // Beak
  ctx.beginPath(); ctx.fillStyle = '#555'
  ctx.moveTo(s * 0.1, -bodyLen * 0.62)
  ctx.lineTo(s * 0.25, -bodyLen * 0.68)
  ctx.lineTo(s * 0.1, -bodyLen * 0.55)
  ctx.closePath(); ctx.fill()

  // Tail feathers
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.5)`
  ctx.lineWidth = 2.5
  for (let t = -2; t <= 2; t++) {
    ctx.beginPath()
    ctx.moveTo(t * s * 0.1, bodyLen * 0.4)
    ctx.quadraticCurveTo(t * s * 0.15, bodyLen * 0.65, t * s * 0.22, bodyLen * 0.85)
    ctx.stroke()
  }

  ctx.restore()
}

// ======================== DRAWING — RABBIT ========================

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number, progress: number, isFinished: boolean) {
  ctx.save()
  ctx.translate(x, y)

  // After completion: golden victory aura instead of danger crosshair
  if (isFinished) {
    const ga = 0.15 + 0.08 * Math.sin(frameCount * 0.025)
    const victoryGlow = ctx.createRadialGradient(0, 0, 10, 0, 0, 90)
    victoryGlow.addColorStop(0, `rgba(255,200,50,${ga})`)
    victoryGlow.addColorStop(0.5, `rgba(0,229,160,${ga * 0.4})`)
    victoryGlow.addColorStop(1, 'transparent')
    ctx.fillStyle = victoryGlow
    ctx.beginPath(); ctx.arc(0, 0, 90, 0, Math.PI * 2); ctx.fill()

    // Victory rings (golden, slower)
    for (let i = 0; i < 3; i++) {
      const p = (pulse * 0.5 + i / 3) % 1
      const r = 25 + p * 65
      ctx.beginPath()
      ctx.strokeStyle = `rgba(255,200,50,${0.4 * (1 - p)})`
      ctx.lineWidth = 3 * (1 - p)
      ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke()
    }
  } else {
    // Target crosshair during siege
    if (progress > 0.55) {
      const ca = (progress - 0.55) / 0.45 * 0.3
      ctx.strokeStyle = `rgba(255,51,102,${ca})`
      ctx.lineWidth = 1
      ctx.setLineDash([5, 5])
      ctx.beginPath(); ctx.moveTo(-55, 0); ctx.lineTo(-22, 0); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(22, 0); ctx.lineTo(55, 0); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(0, -55); ctx.lineTo(0, -35); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(0, 28); ctx.lineTo(0, 55); ctx.stroke()
      ctx.beginPath(); ctx.arc(0, 0, 45, 0, Math.PI * 2); ctx.stroke()
      ctx.setLineDash([])
    }

    // Danger rings
    const ringCount = 3 + Math.floor(progress * 4)
    for (let i = 0; i < ringCount; i++) {
      const p = (pulse + i / ringCount) % 1
      const r = 20 + p * 75
      ctx.beginPath()
      ctx.strokeStyle = `rgba(255,51,102,${0.5 * (1 - p) * (0.4 + progress * 0.6)})`
      ctx.lineWidth = 4 * (1 - p)
      ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke()
    }
  }

  // Ground glow — bigger after completion
  const glowR = isFinished ? 70 : 50
  const gg = ctx.createRadialGradient(0, 5, 0, 0, 5, glowR)
  gg.addColorStop(0, isFinished ? 'rgba(255,200,50,0.35)' : 'rgba(255,51,102,0.3)')
  gg.addColorStop(1, 'transparent')
  ctx.fillStyle = gg
  ctx.beginPath(); ctx.arc(0, 5, glowR, 0, Math.PI * 2); ctx.fill()

  // Body
  ctx.shadowColor = '#FF3366'; ctx.shadowBlur = 30
  ctx.fillStyle = '#FF3366'
  ctx.beginPath(); ctx.ellipse(0, 5, 16, 20, 0, 0, Math.PI * 2); ctx.fill()

  // Head
  ctx.shadowBlur = 0
  ctx.fillStyle = '#FF4477'
  ctx.beginPath(); ctx.arc(0, -14, 13, 0, Math.PI * 2); ctx.fill()

  // Ears
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#FF3366'
    ctx.beginPath(); ctx.ellipse(side * 7, -34, 5, 14, side * 0.15, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#FF88AA'
    ctx.beginPath(); ctx.ellipse(side * 7, -33, 3, 10, side * 0.15, 0, Math.PI * 2); ctx.fill()
  }

  // Eyes
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#fff'
    ctx.beginPath(); ctx.arc(side * 5, -14, 4.5, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#220011'
    ctx.beginPath(); ctx.arc(side * 5, -14, 2.2, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = 'rgba(255,255,255,0.75)'
    ctx.beginPath(); ctx.arc(side * 6, -15.5, 1.2, 0, Math.PI * 2); ctx.fill()
  }

  // Nose + whiskers
  ctx.fillStyle = '#FFaacc'
  ctx.beginPath(); ctx.arc(0, -8, 2.5, 0, Math.PI * 2); ctx.fill()
  ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.lineWidth = 0.8
  for (const side of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(side * 5, -8); ctx.lineTo(side * 22, -12); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(side * 5, -7); ctx.lineTo(side * 20, -3); ctx.stroke()
  }

  // Fluffy tail
  ctx.fillStyle = '#FFccdd'
  ctx.beginPath(); ctx.arc(0, 22, 7, 0, Math.PI * 2); ctx.fill()

  // Label
  ctx.textAlign = 'center'
  if (isFinished) {
    ctx.fillStyle = `rgba(0,229,160,${0.6 + 0.3 * Math.sin(frameCount * 0.03)})`
    ctx.font = 'bold 13px Inter, sans-serif'
    ctx.fillText('★ CAPTURADA ★', 0, -60)
  } else {
    ctx.fillStyle = `rgba(255,51,102,${0.4 + 0.2 * Math.sin(frameCount * 0.04)})`
    ctx.font = 'bold 11px Inter, sans-serif'
    ctx.fillText('PRESA', 0, -55)
  }

  ctx.restore()
}

// ======================== DRAWING — HUD ========================

function drawHUD(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  if (props.iteration <= 0) return

  const label = progress < 0.3 ? 'EXPLORACI\u00d3N' : progress < 0.65 ? 'TRANSICI\u00d3N' : 'SIEGE'
  const [pr, pg, pb] = progress < 0.3 ? [100, 170, 255] : progress < 0.65 ? [220, 180, 80] : [255, 80, 80]
  const E = (2 * (1 - progress)).toFixed(2)

  ctx.fillStyle = 'rgba(0,0,0,0.55)'
  ctx.beginPath(); ctx.roundRect(W - 185, 8, 173, 82, 10); ctx.fill()
  ctx.strokeStyle = `rgba(${pr},${pg},${pb},0.4)`; ctx.lineWidth = 1
  ctx.beginPath(); ctx.roundRect(W - 185, 8, 173, 82, 10); ctx.stroke()

  ctx.textAlign = 'right'
  ctx.fillStyle = `rgba(${pr},${pg},${pb},0.95)`
  ctx.font = 'bold 14px Inter, sans-serif'
  ctx.fillText(label, W - 22, 30)

  ctx.fillStyle = 'rgba(255,255,255,0.45)'
  ctx.font = '11px "JetBrains Mono", monospace'
  ctx.fillText(`E(t) = ${E}`, W - 22, 48)
  ctx.fillText(`iter ${props.iteration} / ${props.maxIter}`, W - 22, 63)
  ctx.fillText(`${paretoNorm.length} Pareto \u00b7 ${hawks.length} hawks`, W - 22, 78)

  // Axis labels
  ctx.textAlign = 'center'
  ctx.fillStyle = 'rgba(255,255,255,0.15)'
  ctx.font = '11px Inter, sans-serif'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 10)
  ctx.save()
  ctx.translate(14, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('f\u2082 \u2014 Disparidad', 0, 0)
  ctx.restore()
}

// ======================== MAIN LOOP ========================

function frame() {
  const cvs = canvasRef.value
  if (!cvs) { animId = requestAnimationFrame(frame); return }
  const ctx = cvs.getContext('2d')
  if (!ctx) { animId = requestAnimationFrame(frame); return }

  frameCount++
  const W = cvs.width / dpr
  const H = cvs.height / dpr
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  // Background
  ctx.fillStyle = '#06061a'
  ctx.fillRect(0, 0, W, H)
  drawNebula(ctx, W, H, progress)
  drawStarfield(ctx, W, H)
  updateShootingStars(ctx, W, H)
  drawGrid(ctx, W, H)
  drawVignette(ctx, W, H)

  // Connections
  drawConstellations(ctx, W, H)
  drawParetoFront(ctx, W, H)
  drawEnergyBeams(ctx, W, H, progress)

  // Sparks
  sparks = sparks.filter(s => s.life > 0)
  sparks.forEach(s => {
    s.x += s.vx; s.y += s.vy
    s.vy += 0.00012; s.vx *= 0.97; s.vy *= 0.97
    s.life--
    const alpha = s.life / s.maxLife
    ctx.beginPath()
    ctx.fillStyle = `rgba(${s.r},${s.g},${s.b},${alpha * 0.8})`
    ctx.arc(s.x * W, s.y * H, s.size * alpha, 0, Math.PI * 2)
    ctx.fill()
  })

  // Hawks — physics + draw
  hawks.forEach((h, idx) => {
    let effTx = h.tx, effTy = h.ty

    // Orbital motion keeps siege hawks circling — never static
    if (h.phase === 'siege') {
      // After completion, use a much wider orbit so hawks stay clearly visible
      const baseR = finished ? 0.09 : 0.045
      const ampR = finished ? 0.035 : 0.02
      const orbitR = baseR + ampR * Math.sin(frameCount * 0.008 + h.orbitOffset * 3)
      const orbitSpeed = finished ? 0.012 : 0.02
      const orbitA = frameCount * orbitSpeed + h.orbitOffset + idx * 0.4
      effTx = h.tx + Math.cos(orbitA) * orbitR
      effTy = h.ty + Math.sin(orbitA) * orbitR
    }

    const dx = effTx - h.x, dy = effTy - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (h.phase === 'explore') {
      h.vx += dx * 0.0012 + (Math.random() - 0.5) * 0.002
      h.vy += dy * 0.0012 + (Math.random() - 0.5) * 0.002
    } else if (h.phase === 'transition') {
      h.vx += dx * 0.004 + (Math.random() - 0.5) * 0.001
      h.vy += dy * 0.004 + (Math.random() - 0.5) * 0.001
    } else {
      h.vx += dx * 0.008
      h.vy += dy * 0.008
      if (Math.random() < 0.005) {
        const levy = Math.pow(Math.random(), -0.5) * 0.02
        h.vx += (Math.random() - 0.5) * levy
        h.vy += (Math.random() - 0.5) * levy
      }
    }

    h.vx *= 0.93; h.vy *= 0.93
    const speed = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    const maxSpd = h.phase === 'siege' ? 0.014 : 0.009
    if (speed > maxSpd) { h.vx *= maxSpd / speed; h.vy *= maxSpd / speed }

    h.x += h.vx; h.y += h.vy
    h.x = Math.max(0.02, Math.min(0.98, h.x))
    h.y = Math.max(0.02, Math.min(0.98, h.y))
    if (h.x <= 0.02 || h.x >= 0.98) h.vx *= -0.5
    if (h.y <= 0.02 || h.y >= 0.98) h.vy *= -0.5

    // Smooth heading
    if (speed > 0.0006) {
      const tgt = Math.atan2(h.vy, h.vx) + Math.PI / 2
      let diff = tgt - h.angle
      while (diff > Math.PI) diff -= Math.PI * 2
      while (diff < -Math.PI) diff += Math.PI * 2
      h.angle += diff * 0.1
    }

    h.wing += h.wingSpeed + (h.phase === 'siege' ? 0.08 : 0)

    // Trail
    h.trail.push({ x: h.x, y: h.y, age: 0 })
    h.trail.forEach(t => t.age++)
    h.trail = h.trail.filter(t => t.age < 45)

    // Sparks near rabbit during siege
    if (h.phase === 'siege' && dist < 0.12 && Math.random() < 0.12 && sparks.length < 300) {
      const a = Math.random() * Math.PI * 2
      const sp = 0.002 + Math.random() * 0.005
      sparks.push({
        x: h.x, y: h.y,
        vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
        life: 25 + Math.random() * 35, maxLife: 60,
        r: 255, g: 180 + Math.floor(Math.random() * 75), b: 0,
        size: 2.5 + Math.random() * 2.5,
      })
    }

    drawHawk(ctx, h, W, H, finished)
  })

  // Rabbit — always on top
  rabbitPulse = (rabbitPulse + 0.005) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse, progress, finished)

  // Completion shockwave
  if (completionPulse > 0) {
    completionPulse--
    const p = 1 - completionPulse / 160
    const maxR = Math.max(W, H) * 0.6
    ctx.beginPath()
    ctx.strokeStyle = `rgba(0,229,160,${0.5 * (1 - p)})`
    ctx.lineWidth = 4 * (1 - p)
    ctx.arc(rabbitX * W, rabbitY * H, maxR * p, 0, Math.PI * 2)
    ctx.stroke()
    if (p > 0.1) {
      const p2 = (p - 0.1) / 0.9
      ctx.beginPath()
      ctx.strokeStyle = `rgba(255,200,50,${0.4 * (1 - p2)})`
      ctx.lineWidth = 3 * (1 - p2)
      ctx.arc(rabbitX * W, rabbitY * H, maxR * 0.7 * p2, 0, Math.PI * 2)
      ctx.stroke()
    }
  }

  // Persistent "COMPLETADO" banner after simulation ends
  if (finished && completionPulse <= 0) {
    const bannerAlpha = 0.6 + 0.15 * Math.sin(frameCount * 0.03)
    ctx.textAlign = 'center'
    ctx.font = 'bold 16px Inter, sans-serif'
    ctx.fillStyle = `rgba(0,229,160,${bannerAlpha})`
    ctx.fillText('OPTIMIZACIÓN COMPLETADA', W / 2, H - 32)
    ctx.font = '11px Inter, sans-serif'
    ctx.fillStyle = 'rgba(255,255,255,0.3)'
    ctx.fillText(`${paretoNorm.length} soluciones Pareto · ${hawks.length} halcones`, W / 2, H - 14)
  }

  drawHUD(ctx, W, H, progress)

  animId = requestAnimationFrame(frame)
}

// ======================== SETUP & LIFECYCLE ========================

function setupCanvas() {
  const cvs = canvasRef.value
  if (!cvs) return
  dpr = window.devicePixelRatio || 1
  const rect = cvs.getBoundingClientRect()
  cvs.width = rect.width * dpr
  cvs.height = rect.height * dpr
  const ctx = cvs.getContext('2d')
  if (ctx) ctx.scale(dpr, dpr)
}

let resizeHandler: (() => void) | null = null

onMounted(() => {
  setupCanvas()
  initStars(200)
  spawnHawks(props.popSize || 20)
  animId = requestAnimationFrame(frame)
  resizeHandler = () => { setupCanvas(); initStars(200) }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})
</script>

<template>
  <div class="relative">
    <canvas
      ref="canvasRef"
      class="w-full h-[600px] rounded-xl"
    />
    <div class="absolute top-3 left-3 flex flex-wrap gap-2 text-[10px] text-gray-400/80">
      <span class="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(96,165,250,0.8)]" />
        Exploraci&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_rgba(220,180,80,0.8)]" />
        Transici&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-red-400 shadow-[0_0_6px_rgba(255,80,80,0.8)]" />
        Siege
      </span>
      <span class="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,51,102,0.8)]" />
        Presa
      </span>
      <span class="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_6px_rgba(0,100,255,0.8)]" />
        Frente Pareto
      </span>
    </div>
  </div>
</template>
