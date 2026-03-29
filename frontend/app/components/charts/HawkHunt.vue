<script setup lang="ts">
/**
 * Cinematic Harris Hawks Optimization — v3 complete redesign.
 *
 * KEY FIX: During siege and finished states, hawks orbit in concentric
 * ring formations around the rabbit.  Each hawk has a unique ring/slot,
 * guaranteeing they are ALWAYS individually visible — never piling up.
 *
 * State management: `completed` prop drives finished state explicitly,
 * not derived from `running` transitions (which caused race conditions).
 *
 * Rabbit uses smooth interpolation, not instant jumps.
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

let rabbitX = 0.5, rabbitY = 0.5     // current (smoothed) position
let rabbitTx = 0.5, rabbitTy = 0.5   // target position
let rabbitPulse = 0

let paretoNorm: Array<{ x: number; y: number }> = []
let progress = 0
let dispIter = 0
let finished = false
let completionFc = 0
let resetFlash = 0

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
  resetFlash = 50
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

// Simulation starts → full reset
watch(() => props.running, (r) => {
  if (r) {
    finished = false
    completionFc = 0
    fullReset()
  }
})

// Simulation completes → celebration
watch(() => props.completed, (done) => {
  if (done && !finished) {
    finished = true
    completionFc = fc
    // Burst of celebratory sparks from rabbit
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

// Process each pareto update — set targets for explore/transition
watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0
  dispIter = props.iteration

  // Smooth rabbit target (leader = first pareto solution)
  if (paretoNorm.length > 0) {
    rabbitTx = paretoNorm[0].x
    rabbitTy = paretoNorm[0].y
  }

  // Set phase & targets for NON-siege modes
  // Siege/finished targets are computed per-frame (formation orbits)
  const phase = progress < 0.3 ? 'explore' : progress < 0.65 ? 'transition' : 'siege'
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
  g.addColorStop(0, `hsl(${hue},40%,5%)`)
  g.addColorStop(0.5, `hsl(${hue - 10},35%,7%)`)
  g.addColorStop(1, `hsl(${hue - 20},30%,4%)`)
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H)

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

  stars.forEach(s => {
    s.tw += s.sp
    const a = 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(s.tw))
    ctx.beginPath(); ctx.fillStyle = `rgba(200,215,255,${a})`
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2); ctx.fill()
  })

  ctx.strokeStyle = 'rgba(255,255,255,0.015)'; ctx.lineWidth = 0.5
  for (let i = 1; i < 20; i++) {
    const gx = (i / 20) * W, gy = (i / 20) * H
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke()
  }

  const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) * 0.8)
  vg.addColorStop(0, 'transparent'); vg.addColorStop(1, 'rgba(0,0,0,0.35)')
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
    ctx.beginPath(); ctx.strokeStyle = 'rgba(60,130,255,0.35)'; ctx.lineWidth = 2.5
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
    ctx.strokeStyle = `rgba(255,200,50,${int * 0.2 * (1 - d / 0.4)})`
    ctx.lineWidth = 1.5; ctx.setLineDash([6, 8])
    ctx.moveTo(h.x * W, h.y * H)
    ctx.lineTo(rabbitX * W, rabbitY * H)
    ctx.stroke(); ctx.setLineDash([])
  })
}

// Draw formation ring guides (subtle circles showing the orbit rings)
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

// ═══════════════════ DRAW — HAWK ═══════════════════
// NO ctx.save/restore/translate/rotate/ellipse/shadow — absolute coords only.
// This prevents canvas state corruption that was making hawks invisible.

function drawHawk(ctx: CanvasRenderingContext2D, h: Hawk, W: number, H: number) {
  const px = h.x * W, py = h.y * H
  const [cr, cg, cb] = phaseRGB(h.phase)
  const s = h.size
  const flap = Math.sin(h.wing)

  // Heading direction vectors
  const ca = Math.cos(h.angle - Math.PI / 2)  // forward x
  const sa = Math.sin(h.angle - Math.PI / 2)  // forward y
  const pa = Math.cos(h.angle)                 // perpendicular x
  const qa = Math.sin(h.angle)                 // perpendicular y

  // Trail
  if (h.trail.length > 1) {
    for (let i = 1; i < h.trail.length; i++) {
      const t = h.trail[i], prev = h.trail[i - 1]
      const a = Math.max(0, 1 - t.age / 60) * 0.45
      if (a <= 0) continue
      ctx.beginPath()
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${a})`
      ctx.lineWidth = (1 - t.age / 60) * 4
      ctx.lineCap = 'round'
      ctx.moveTo(prev.x * W, prev.y * H)
      ctx.lineTo(t.x * W, t.y * H)
      ctx.stroke()
    }
  }

  // Aura glow (simple concentric fills — no createRadialGradient)
  const aR = finished ? s * 1.8 : (h.phase === 'siege' ? s * 1.0 : s * 1.5)
  const ap = finished
    ? 0.10 + 0.05 * Math.sin(fc * 0.035 + h.orbOff)
    : 0.06 + 0.04 * Math.sin(fc * 0.06 + h.orbOff)
  if (finished) {
    ctx.beginPath(); ctx.fillStyle = `rgba(0,229,160,${ap * 0.3})`
    ctx.arc(px, py, aR, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(0,229,160,${ap * 0.6})`
    ctx.arc(px, py, aR * 0.5, 0, Math.PI * 2); ctx.fill()
  } else {
    ctx.beginPath(); ctx.fillStyle = `rgba(${cr},${cg},${cb},${ap * 0.3})`
    ctx.arc(px, py, aR, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(${cr},${cg},${cb},${ap * 0.7})`
    ctx.arc(px, py, aR * 0.5, 0, Math.PI * 2); ctx.fill()
  }

  // Wing length and flap offset
  const wLen = s * 1.2
  const flapAmt = flap * s * 0.4

  // Wings (two lines + fill triangles from body center)
  ctx.lineWidth = 3; ctx.lineCap = 'round'
  for (const side of [-1, 1]) {
    // Wingtip position: perpendicular from body + forward flap
    const wx = px + side * pa * wLen + ca * flapAmt * side * 0.3
    const wy = py + side * qa * wLen + sa * flapAmt * side * 0.3

    // Wing stroke
    ctx.beginPath()
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.9)`
    ctx.moveTo(px, py)
    ctx.lineTo(wx, wy)
    ctx.stroke()

    // Wing fill (triangle: body → wingtip → tail)
    const tailX = px - ca * s * 0.4
    const tailY = py - sa * s * 0.4
    ctx.beginPath()
    ctx.fillStyle = `rgba(${cr},${cg},${cb},0.18)`
    ctx.moveTo(px, py)
    ctx.lineTo(wx, wy)
    ctx.lineTo(tailX, tailY)
    ctx.closePath()
    ctx.fill()

    // Feather lines along the wing
    for (let f = 0; f < 3; f++) {
      const t = 0.4 + f * 0.2
      const fx = px + (wx - px) * t
      const fy = py + (wy - py) * t
      ctx.beginPath()
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.3)`
      ctx.lineWidth = 1
      ctx.moveTo(fx, fy)
      ctx.lineTo(fx - ca * s * 0.15, fy - sa * s * 0.15)
      ctx.stroke()
    }
  }

  // Body (circle at center)
  ctx.beginPath()
  ctx.fillStyle = `rgba(${cr},${cg},${cb},0.95)`
  ctx.arc(px, py, s * 0.35, 0, Math.PI * 2)
  ctx.fill()

  // Body highlight
  ctx.beginPath()
  ctx.fillStyle = 'rgba(255,255,255,0.15)'
  ctx.arc(px - pa * s * 0.08, py - qa * s * 0.08, s * 0.18, 0, Math.PI * 2)
  ctx.fill()

  // Head (forward from body)
  const hx = px + ca * s * 0.55
  const hy = py + sa * s * 0.55
  ctx.beginPath()
  ctx.fillStyle = `rgba(${Math.min(255, cr + 50)},${Math.min(255, cg + 50)},${Math.min(255, cb + 50)},1)`
  ctx.arc(hx, hy, s * 0.25, 0, Math.PI * 2)
  ctx.fill()

  // Eye
  const ex = hx + pa * s * 0.08
  const ey = hy + qa * s * 0.08
  ctx.beginPath(); ctx.fillStyle = '#fff'
  ctx.arc(ex, ey, s * 0.10, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.fillStyle = '#111'
  ctx.arc(ex + pa * 0.5, ey + qa * 0.5, s * 0.05, 0, Math.PI * 2); ctx.fill()

  // Beak (triangle forward from head)
  const bx = hx + ca * s * 0.35
  const by = hy + sa * s * 0.35
  ctx.beginPath()
  ctx.fillStyle = '#777'
  ctx.moveTo(hx + ca * s * 0.2 + pa * s * 0.06, hy + sa * s * 0.2 + qa * s * 0.06)
  ctx.lineTo(bx, by)
  ctx.lineTo(hx + ca * s * 0.2 - pa * s * 0.06, hy + sa * s * 0.2 - qa * s * 0.06)
  ctx.closePath()
  ctx.fill()

  // Tail (lines behind body)
  const tailCx = px - ca * s * 0.5
  const tailCy = py - sa * s * 0.5
  ctx.lineWidth = 2; ctx.lineCap = 'round'
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.5)`
  for (let t = -2; t <= 2; t++) {
    const tx = tailCx + pa * t * s * 0.08
    const ty = tailCy + qa * t * s * 0.08
    const endX = tx - ca * s * 0.5 + pa * t * s * 0.12
    const endY = ty - sa * s * 0.5 + qa * t * s * 0.12
    ctx.beginPath()
    ctx.moveTo(tx, ty)
    ctx.lineTo(endX, endY)
    ctx.stroke()
  }
}

// ═══════════════════ DRAW — RABBIT ═══════════════════

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number) {
  // ALL absolute coordinates — NO save/restore/translate/ellipse/shadow

  if (finished) {
    // Triumphant golden glow — concentric fills (no createRadialGradient)
    const ga = 0.20 + 0.10 * Math.sin(fc * 0.025)
    ctx.beginPath(); ctx.fillStyle = `rgba(255,215,0,${ga * 0.15})`
    ctx.arc(x, y, 130, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(0,229,160,${ga * 0.25})`
    ctx.arc(x, y, 60, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.fillStyle = `rgba(255,215,0,${ga * 0.4})`
    ctx.arc(x, y, 25, 0, Math.PI * 2); ctx.fill()
    for (let i = 0; i < 4; i++) {
      const p = (pulse * 0.35 + i / 4) % 1
      const r = 30 + p * 100
      ctx.beginPath()
      ctx.strokeStyle = `rgba(255,215,0,${0.45 * (1 - p)})`
      ctx.lineWidth = 3.5 * (1 - p)
      ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke()
    }
  } else {
    if (progress > 0.55) {
      const ca = (progress - 0.55) / 0.45 * 0.35
      ctx.strokeStyle = `rgba(255,51,102,${ca})`; ctx.lineWidth = 1; ctx.setLineDash([5, 5])
      ctx.beginPath(); ctx.moveTo(x - 60, y); ctx.lineTo(x - 24, y); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(x + 24, y); ctx.lineTo(x + 60, y); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(x, y - 60); ctx.lineTo(x, y - 36); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(x, y + 30); ctx.lineTo(x, y + 60); ctx.stroke()
      ctx.beginPath(); ctx.arc(x, y, 48, 0, Math.PI * 2); ctx.stroke()
      ctx.setLineDash([])
    }
    const rc = 3 + Math.floor(progress * 4)
    for (let i = 0; i < rc; i++) {
      const p = (pulse + i / rc) % 1, r = 22 + p * 80
      ctx.beginPath()
      ctx.strokeStyle = `rgba(255,51,102,${0.5 * (1 - p) * (0.3 + progress * 0.7)})`
      ctx.lineWidth = 4 * (1 - p)
      ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke()
    }
  }

  // Glow (concentric fills — no createRadialGradient)
  const glR = finished ? 80 : 55
  ctx.beginPath()
  ctx.fillStyle = finished ? 'rgba(255,215,0,0.08)' : 'rgba(255,51,102,0.06)'
  ctx.arc(x, y + 5, glR, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath()
  ctx.fillStyle = finished ? 'rgba(255,215,0,0.18)' : 'rgba(255,51,102,0.15)'
  ctx.arc(x, y + 5, glR * 0.4, 0, Math.PI * 2); ctx.fill()

  // Body (arc instead of ellipse — average radius 20)
  ctx.fillStyle = finished ? '#FFD700' : '#FF3366'
  ctx.beginPath(); ctx.arc(x, y + 5, 20, 0, Math.PI * 2); ctx.fill()

  // Head
  ctx.fillStyle = finished ? '#FFE040' : '#FF4477'
  ctx.beginPath(); ctx.arc(x, y - 16, 14, 0, Math.PI * 2); ctx.fill()

  // Ears (two overlapping circles per ear instead of ellipse)
  for (const side of [-1, 1]) {
    const earX = x + side * 8
    ctx.fillStyle = finished ? '#FFD700' : '#FF3366'
    ctx.beginPath(); ctx.arc(earX, y - 34, 7, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.arc(earX, y - 44, 6, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = finished ? '#FFED80' : '#FF88AA'
    ctx.beginPath(); ctx.arc(earX, y - 35, 5, 0, Math.PI * 2); ctx.fill()
    ctx.beginPath(); ctx.arc(earX, y - 43, 4, 0, Math.PI * 2); ctx.fill()
  }

  // Eyes
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x + side * 5.5, y - 16, 5, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#220011'; ctx.beginPath(); ctx.arc(x + side * 5.5, y - 16, 2.5, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.beginPath(); ctx.arc(x + side * 6.5, y - 17.5, 1.3, 0, Math.PI * 2); ctx.fill()
  }

  // Nose
  ctx.fillStyle = finished ? '#FFE080' : '#FFaacc'
  ctx.beginPath(); ctx.arc(x, y - 9, 2.8, 0, Math.PI * 2); ctx.fill()

  // Whiskers
  ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.lineWidth = 0.8
  for (const side of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(x + side * 6, y - 9); ctx.lineTo(x + side * 24, y - 13); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(x + side * 6, y - 8); ctx.lineTo(x + side * 22, y - 4); ctx.stroke()
  }

  // Tail
  ctx.fillStyle = finished ? '#FFED80' : '#FFccdd'
  ctx.beginPath(); ctx.arc(x, y + 24, 8, 0, Math.PI * 2); ctx.fill()

  // Label
  ctx.textAlign = 'center'
  if (finished) {
    ctx.fillStyle = `rgba(0,229,160,${0.7 + 0.3 * Math.sin(fc * 0.03)})`
    ctx.font = 'bold 15px Inter, sans-serif'
    ctx.fillText('\u2605 CAPTURADA \u2605', x, y - 68)
  } else {
    ctx.fillStyle = `rgba(255,51,102,${0.5 + 0.2 * Math.sin(fc * 0.04)})`
    ctx.font = 'bold 12px Inter, sans-serif'
    ctx.fillText('PRESA', x, y - 60)
  }
}

// ═══════════════════ DRAW — HUD ═══════════════════

function drawHUD(ctx: CanvasRenderingContext2D, W: number, H: number) {
  // ALL absolute coordinates — NO save/restore/translate/rotate/roundRect
  if (dispIter <= 0 && !finished) return

  const label = finished ? 'COMPLETADO' : progress < 0.3 ? 'EXPLORACI\u00d3N' : progress < 0.65 ? 'TRANSICI\u00d3N' : 'ASEDIO'
  const [pr, pg, pb] = finished ? [0, 229, 160] : progress < 0.3 ? [80, 160, 255] : progress < 0.65 ? [255, 200, 60] : [255, 120, 40]
  const E = finished ? '0.00' : (2 * (1 - progress)).toFixed(2)

  // Manual rounded rectangle (replaces roundRect which may not exist in all browsers)
  const bx = W - 200, by = 8, bw = 188, bh = 86, br = 10
  ctx.fillStyle = 'rgba(0,0,0,0.6)'
  ctx.beginPath()
  ctx.moveTo(bx + br, by)
  ctx.lineTo(bx + bw - br, by)
  ctx.arcTo(bx + bw, by, bx + bw, by + br, br)
  ctx.lineTo(bx + bw, by + bh - br)
  ctx.arcTo(bx + bw, by + bh, bx + bw - br, by + bh, br)
  ctx.lineTo(bx + br, by + bh)
  ctx.arcTo(bx, by + bh, bx, by + bh - br, br)
  ctx.lineTo(bx, by + br)
  ctx.arcTo(bx, by, bx + br, by, br)
  ctx.closePath()
  ctx.fill()

  ctx.strokeStyle = `rgba(${pr},${pg},${pb},0.4)`; ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(bx + br, by)
  ctx.lineTo(bx + bw - br, by)
  ctx.arcTo(bx + bw, by, bx + bw, by + br, br)
  ctx.lineTo(bx + bw, by + bh - br)
  ctx.arcTo(bx + bw, by + bh, bx + bw - br, by + bh, br)
  ctx.lineTo(bx + br, by + bh)
  ctx.arcTo(bx, by + bh, bx, by + bh - br, br)
  ctx.lineTo(bx, by + br)
  ctx.arcTo(bx, by, bx + br, by, br)
  ctx.closePath()
  ctx.stroke()

  ctx.textAlign = 'right'
  ctx.fillStyle = `rgba(${pr},${pg},${pb},0.95)`
  ctx.font = 'bold 14px Inter, sans-serif'
  ctx.fillText(label, W - 22, 30)
  ctx.fillStyle = 'rgba(255,255,255,0.5)'
  ctx.font = '11px "JetBrains Mono", monospace'
  ctx.fillText(`E(t) = ${E}`, W - 22, 48)
  ctx.fillText(`iter ${dispIter} / ${props.maxIter}`, W - 22, 63)
  ctx.fillText(`${paretoNorm.length} Pareto \u00b7 ${hawks.length} hawks`, W - 22, 78)
  ctx.fillText(`${finished ? 'completado' : (hawks[0]?.phase || '...')}`, W - 22, 90)

  // Axis labels — horizontal only (NO rotate/translate)
  ctx.textAlign = 'center'
  ctx.fillStyle = 'rgba(255,255,255,0.15)'; ctx.font = '11px Inter, sans-serif'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 10)
  // Vertical axis: draw without rotation
  ctx.textAlign = 'left'
  ctx.fillText('f\u2082', 6, H / 2)

  if (finished) {
    const ba = 0.6 + 0.2 * Math.sin(fc * 0.025)
    ctx.textAlign = 'center'
    ctx.font = 'bold 20px Inter, sans-serif'
    ctx.fillStyle = `rgba(0,229,160,${ba})`
    ctx.fillText('OPTIMIZACI\u00d3N COMPLETADA', W / 2, H - 40)
    ctx.font = '13px Inter, sans-serif'
    ctx.fillStyle = 'rgba(255,255,255,0.4)'
    ctx.fillText(`${paretoNorm.length} soluciones Pareto \u00b7 ${hawks.length} halcones`, W / 2, H - 18)
  }
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

  // ── Defensive state reset — prevent leaks from ANY source ──
  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
  ctx.setLineDash([])
  ctx.lineCap = 'butt'
  ctx.lineJoin = 'miter'

  try {

  fc++

  // Safety: always have hawks
  if (hawks.length === 0) spawnHawks(props.popSize || 20)

  // ── Background ──
  drawBg(ctx, W, H)

  // ── Reset flash ──
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

  // ── Connections & Pareto ──
  drawConstellations(ctx, W, H)
  drawParetoFront(ctx, W, H)
  drawFormationRings(ctx, W, H)
  drawBeams(ctx, W, H)

  // ── Reset line dash after beams/rings (extra safety) ──
  ctx.setLineDash([])

  // ── Sparks ──
  sparks = sparks.filter(s => s.life > 0)
  sparks.forEach(s => {
    s.x += s.vx; s.y += s.vy
    s.vy += 0.00008; s.vx *= 0.98; s.vy *= 0.98; s.life--
    const a = s.life / s.maxLife
    ctx.beginPath()
    ctx.fillStyle = `rgba(${s.r},${s.g},${s.b},${a * 0.8})`
    ctx.arc(s.x * W, s.y * H, Math.max(0.1, s.sz * a), 0, Math.PI * 2); ctx.fill()
  })

  // ── Smooth rabbit (with NaN guard) ──
  rabbitX += (rabbitTx - rabbitX) * 0.04
  rabbitY += (rabbitTy - rabbitY) * 0.04
  if (!isFinite(rabbitX)) rabbitX = 0.5
  if (!isFinite(rabbitY)) rabbitY = 0.5

  // ── Hawks physics + draw ──
  hawks.forEach((h) => {
    // NaN guard — reset corrupt hawk
    if (!isFinite(h.x) || !isFinite(h.y) || !isFinite(h.vx) || !isFinite(h.vy)) {
      h.x = 0.3 + Math.random() * 0.4
      h.y = 0.3 + Math.random() * 0.4
      h.vx = 0; h.vy = 0
    }

    const idx = h.hIdx
    let effTx: number
    let effTy: number

    if (finished || h.phase === 'siege') {
      // Formation orbits — concentric rings around rabbit
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

    // Lévy flight in siege — SAFE: clamp base to prevent Infinity
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

    // Sparks — siege combat
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

    // Sparks — celebration
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

  // ── Rabbit (always on top of hawks) ──
  rabbitPulse = (rabbitPulse + 0.004) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse)

  // ── Completion shockwave (triple ring) ──
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

  // ── HUD ──
  drawHUD(ctx, W, H)

  } catch (e) {
    // Never let the animation loop die — log and continue
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
    <canvas ref="canvasRef" class="w-full h-[600px] rounded-xl" />
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
        <span class="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,51,102,0.8)]" /> Presa
      </span>
      <span class="flex items-center gap-1.5 bg-black/50 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_6px_rgba(0,100,255,0.8)]" /> Frente Pareto
      </span>
    </div>
  </div>
</template>
