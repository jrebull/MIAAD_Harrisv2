<script setup lang="ts">
/**
 * Cinematic Harris Hawks Optimization animation.
 * Starfield + nebula background, large glowing hawks with energy trails,
 * a pulsing prey with danger rings, connecting energy beams during siege,
 * and particle explosions on convergence.
 */

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  iteration: number
  maxIter: number
  running: boolean
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animId = 0
let dpr = 1
let frameCount = 0

// ---- Stars ----
interface Star { x: number; y: number; r: number; twinkle: number; speed: number }
let stars: Star[] = []

function initStars(n: number) {
  stars = []
  for (let i = 0; i < n; i++) {
    stars.push({
      x: Math.random(), y: Math.random(),
      r: 0.3 + Math.random() * 1.2,
      twinkle: Math.random() * Math.PI * 2,
      speed: 0.01 + Math.random() * 0.03,
    })
  }
}

// ---- Hawks ----
interface Hawk {
  x: number; y: number
  tx: number; ty: number
  vx: number; vy: number
  angle: number
  trail: Array<{ x: number; y: number; age: number }>
  phase: 'explore' | 'transition' | 'siege'
  size: number
  wing: number
  wingSpeed: number
  hue: number
  energy: number
}

interface Spark {
  x: number; y: number; vx: number; vy: number
  life: number; maxLife: number
  r: number; g: number; b: number
  size: number
}

let hawks: Hawk[] = []
let sparks: Spark[] = []
let rabbitX = 0.5, rabbitY = 0.5, rabbitPulse = 0
let paretoNorm: Array<{ x: number; y: number }> = []
let nebulaHue = 220

function normalize(pts: Array<{ f1: number; f2: number }>) {
  if (pts.length === 0) return []
  const margin = 0.08
  const f1s = pts.map(p => p.f1), f2s = pts.map(p => p.f2)
  const f1min = Math.min(...f1s), f1max = Math.max(...f1s)
  const f2min = Math.min(...f2s), f2max = Math.max(...f2s)
  const f1r = f1max - f1min || 1, f2r = f2max - f2min || 1
  return pts.map(p => ({
    x: margin + (1 - 2 * margin) * (p.f1 - f1min) / f1r,
    y: margin + (1 - 2 * margin) * (p.f2 - f2min) / f2r,
  }))
}

function spawnHawks(n: number) {
  hawks = []
  for (let i = 0; i < n; i++) {
    hawks.push({
      x: 0.05 + Math.random() * 0.9,
      y: 0.05 + Math.random() * 0.9,
      tx: 0.5, ty: 0.5,
      vx: (Math.random() - 0.5) * 0.004,
      vy: (Math.random() - 0.5) * 0.004,
      angle: Math.random() * Math.PI * 2,
      trail: [],
      phase: 'explore',
      size: 16 + Math.random() * 8,
      wing: Math.random() * Math.PI * 2,
      wingSpeed: 0.08 + Math.random() * 0.05,
      hue: 200 + Math.random() * 40,
      energy: 0.5 + Math.random() * 0.5,
    })
  }
  sparks = []
  paretoNorm = []
  rabbitX = 0.5
  rabbitY = 0.5
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
  spawnHawks(30)
  frameCount = 0
}

watch(() => props.running, (r) => { if (r) fullReset() })

watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  rabbitX = paretoNorm[0].x
  rabbitY = paretoNorm[0].y

  hawks.forEach((h, i) => {
    const tgt = paretoNorm[i % paretoNorm.length]
    const scatter = 0.18 * (1 - progress)
    h.tx = tgt.x + (Math.random() - 0.5) * scatter
    h.ty = tgt.y + (Math.random() - 0.5) * scatter
    h.phase = progress < 0.3 ? 'explore' : progress < 0.65 ? 'transition' : 'siege'
    h.energy = 1 - progress * 0.7
  })
}, { deep: true })

// ---- Drawing ----

function drawStarfield(ctx: CanvasRenderingContext2D, W: number, H: number) {
  stars.forEach(s => {
    s.twinkle += s.speed
    const alpha = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(s.twinkle))
    ctx.beginPath()
    ctx.fillStyle = `rgba(200,210,255,${alpha})`
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2)
    ctx.fill()
  })
}

function drawNebula(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  // Shifts from deep blue (exploration) to amber (siege)
  nebulaHue = 220 - progress * 180
  const t = frameCount * 0.003

  for (let i = 0; i < 3; i++) {
    const cx = W * (0.3 + 0.4 * Math.sin(t + i * 2.1))
    const cy = H * (0.3 + 0.4 * Math.cos(t * 0.7 + i * 1.3))
    const r = W * (0.2 + 0.1 * Math.sin(t * 0.5 + i))

    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    grad.addColorStop(0, `hsla(${nebulaHue + i * 30},80%,40%,0.04)`)
    grad.addColorStop(0.5, `hsla(${nebulaHue + i * 30},60%,20%,0.02)`)
    grad.addColorStop(1, 'transparent')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)
  }
}

function drawGrid(ctx: CanvasRenderingContext2D, W: number, H: number) {
  ctx.strokeStyle = 'rgba(255,255,255,0.018)'
  ctx.lineWidth = 0.5
  for (let i = 1; i < 16; i++) {
    const gx = (i / 16) * W, gy = (i / 16) * H
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke()
  }
}

function drawParetoFront(ctx: CanvasRenderingContext2D, W: number, H: number) {
  if (paretoNorm.length < 2) {
    paretoNorm.forEach(p => {
      ctx.beginPath()
      ctx.fillStyle = 'rgba(0,100,255,0.6)'
      ctx.shadowColor = '#0066ff'
      ctx.shadowBlur = 12
      ctx.arc(p.x * W, p.y * H, 4, 0, Math.PI * 2)
      ctx.fill()
      ctx.shadowBlur = 0
    })
    return
  }

  // Draw connected front line with glow
  ctx.beginPath()
  ctx.strokeStyle = 'rgba(0,100,255,0.3)'
  ctx.lineWidth = 2
  ctx.shadowColor = '#0066ff'
  ctx.shadowBlur = 15
  const sorted = [...paretoNorm].sort((a, b) => a.x - b.x)
  ctx.moveTo(sorted[0].x * W, sorted[0].y * H)
  for (let i = 1; i < sorted.length; i++) {
    ctx.lineTo(sorted[i].x * W, sorted[i].y * H)
  }
  ctx.stroke()
  ctx.shadowBlur = 0

  // Dots on front
  sorted.forEach((p, i) => {
    const pulse = 0.6 + 0.4 * Math.sin(frameCount * 0.04 + i * 0.5)
    ctx.beginPath()
    ctx.fillStyle = `rgba(60,140,255,${pulse})`
    ctx.arc(p.x * W, p.y * H, 3.5, 0, Math.PI * 2)
    ctx.fill()
  })
}

function drawHawk(ctx: CanvasRenderingContext2D, h: Hawk, W: number, H: number) {
  const px = h.x * W, py = h.y * H

  // Trail - glowing ribbon
  if (h.trail.length > 1) {
    for (let i = 1; i < h.trail.length; i++) {
      const t = h.trail[i], prev = h.trail[i - 1]
      const alpha = Math.max(0, 1 - t.age / 50) * 0.4
      if (alpha <= 0) continue
      const w = (1 - t.age / 50) * 3
      const [r, g, b] = h.phase === 'siege' ? [255, 200, 0] : h.phase === 'transition' ? [200, 180, 100] : [100, 160, 255]
      ctx.beginPath()
      ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`
      ctx.lineWidth = w
      ctx.lineCap = 'round'
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
  const wingSpan = s * 2.0
  const bodyLen = s * 1.1

  // Color based on phase
  let cr: number, cg: number, cb: number
  if (h.phase === 'siege') { cr = 255; cg = 200; cb = 20 }
  else if (h.phase === 'transition') { cr = 220; cg = 180; cb = 80 }
  else { cr = 100; cg = 170; cb = 255 }

  // Outer glow
  ctx.shadowColor = `rgb(${cr},${cg},${cb})`
  ctx.shadowBlur = h.phase === 'siege' ? 25 : 14

  // Wings - sweeping curves with secondary feathers
  ctx.lineWidth = 3
  ctx.lineCap = 'round'
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.9)`

  // Left wing
  ctx.beginPath()
  ctx.moveTo(0, 0)
  ctx.bezierCurveTo(
    -wingSpan * 0.3, -wingSpan * 0.35 * flap,
    -wingSpan * 0.5, -wingSpan * 0.3 * flap,
    -wingSpan * 0.55, -wingSpan * 0.1 * flap
  )
  ctx.stroke()
  // Wing fill
  ctx.beginPath()
  ctx.fillStyle = `rgba(${cr},${cg},${cb},0.12)`
  ctx.moveTo(0, 0)
  ctx.bezierCurveTo(
    -wingSpan * 0.3, -wingSpan * 0.35 * flap,
    -wingSpan * 0.5, -wingSpan * 0.3 * flap,
    -wingSpan * 0.55, -wingSpan * 0.1 * flap
  )
  ctx.lineTo(-wingSpan * 0.15, bodyLen * 0.2)
  ctx.closePath()
  ctx.fill()

  // Right wing
  ctx.beginPath()
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.9)`
  ctx.moveTo(0, 0)
  ctx.bezierCurveTo(
    wingSpan * 0.3, -wingSpan * 0.35 * flap,
    wingSpan * 0.5, -wingSpan * 0.3 * flap,
    wingSpan * 0.55, -wingSpan * 0.1 * flap
  )
  ctx.stroke()
  ctx.beginPath()
  ctx.fillStyle = `rgba(${cr},${cg},${cb},0.12)`
  ctx.moveTo(0, 0)
  ctx.bezierCurveTo(
    wingSpan * 0.3, -wingSpan * 0.35 * flap,
    wingSpan * 0.5, -wingSpan * 0.3 * flap,
    wingSpan * 0.55, -wingSpan * 0.1 * flap
  )
  ctx.lineTo(wingSpan * 0.15, bodyLen * 0.2)
  ctx.closePath()
  ctx.fill()

  // Secondary feathers (small lines at wing tips)
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.35)`
  ctx.lineWidth = 1.5
  for (let f = 0; f < 3; f++) {
    const fx = -wingSpan * (0.35 + f * 0.07)
    const fy = -wingSpan * (0.25 - f * 0.05) * flap
    ctx.beginPath()
    ctx.moveTo(fx, fy)
    ctx.lineTo(fx - s * 0.15, fy + s * 0.2)
    ctx.stroke()
  }
  for (let f = 0; f < 3; f++) {
    const fx = wingSpan * (0.35 + f * 0.07)
    const fy = -wingSpan * (0.25 - f * 0.05) * flap
    ctx.beginPath()
    ctx.moveTo(fx, fy)
    ctx.lineTo(fx + s * 0.15, fy + s * 0.2)
    ctx.stroke()
  }

  ctx.shadowBlur = 0

  // Body
  ctx.beginPath()
  ctx.fillStyle = `rgba(${cr},${cg},${cb},0.95)`
  ctx.ellipse(0, 0, s * 0.3, bodyLen * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()
  // Body highlight
  ctx.beginPath()
  ctx.fillStyle = `rgba(255,255,255,0.15)`
  ctx.ellipse(-s * 0.08, -bodyLen * 0.15, s * 0.12, bodyLen * 0.2, -0.2, 0, Math.PI * 2)
  ctx.fill()

  // Head
  ctx.beginPath()
  ctx.fillStyle = `rgba(${Math.min(255, cr + 40)},${Math.min(255, cg + 40)},${Math.min(255, cb + 40)},1)`
  ctx.arc(0, -bodyLen * 0.48, s * 0.24, 0, Math.PI * 2)
  ctx.fill()

  // Eye
  ctx.beginPath()
  ctx.fillStyle = '#fff'
  ctx.arc(s * 0.06, -bodyLen * 0.5, s * 0.1, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.fillStyle = '#000'
  ctx.arc(s * 0.07, -bodyLen * 0.5, s * 0.05, 0, Math.PI * 2)
  ctx.fill()
  // Eye glint
  ctx.beginPath()
  ctx.fillStyle = 'rgba(255,255,255,0.8)'
  ctx.arc(s * 0.09, -bodyLen * 0.52, s * 0.02, 0, Math.PI * 2)
  ctx.fill()

  // Beak
  ctx.beginPath()
  ctx.fillStyle = '#444'
  ctx.moveTo(s * 0.08, -bodyLen * 0.6)
  ctx.lineTo(s * 0.2, -bodyLen * 0.65)
  ctx.lineTo(s * 0.08, -bodyLen * 0.55)
  ctx.closePath()
  ctx.fill()

  // Tail feathers
  ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.5)`
  ctx.lineWidth = 2
  for (let t = -2; t <= 2; t++) {
    ctx.beginPath()
    ctx.moveTo(t * s * 0.08, bodyLen * 0.4)
    ctx.quadraticCurveTo(t * s * 0.12, bodyLen * 0.6, t * s * 0.18, bodyLen * 0.8)
    ctx.stroke()
  }

  ctx.restore()
}

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number, progress: number) {
  ctx.save()
  ctx.translate(x, y)

  // Danger rings — more intense as progress increases
  const ringCount = 3 + Math.floor(progress * 3)
  for (let i = 0; i < ringCount; i++) {
    const p = (pulse + i / ringCount) % 1
    const r = 14 + p * 55
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,51,102,${0.5 * (1 - p) * (0.5 + progress * 0.5)})`
    ctx.lineWidth = 3.5 * (1 - p)
    ctx.arc(0, 0, r, 0, Math.PI * 2)
    ctx.stroke()
  }

  // Ground glow
  ctx.beginPath()
  const glowGrad = ctx.createRadialGradient(0, 4, 0, 0, 4, 30)
  glowGrad.addColorStop(0, 'rgba(255,51,102,0.25)')
  glowGrad.addColorStop(1, 'transparent')
  ctx.fillStyle = glowGrad
  ctx.arc(0, 4, 30, 0, Math.PI * 2)
  ctx.fill()

  // Body
  ctx.shadowColor = '#FF3366'
  ctx.shadowBlur = 25
  ctx.beginPath()
  ctx.fillStyle = '#FF3366'
  ctx.ellipse(0, 4, 11, 14, 0, 0, Math.PI * 2)
  ctx.fill()

  // Head
  ctx.shadowBlur = 0
  ctx.beginPath()
  ctx.fillStyle = '#FF4477'
  ctx.arc(0, -10, 9, 0, Math.PI * 2)
  ctx.fill()

  // Ears
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#FF3366'
    ctx.beginPath()
    ctx.ellipse(side * 5, -24, 3.5, 10, side * 0.15, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = '#FF88AA'
    ctx.beginPath()
    ctx.ellipse(side * 5, -23, 2, 7, side * 0.15, 0, Math.PI * 2)
    ctx.fill()
  }

  // Eyes
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#fff'
    ctx.beginPath(); ctx.arc(side * 3.5, -10.5, 3, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#220011'
    ctx.beginPath(); ctx.arc(side * 3.5, -10.5, 1.5, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = 'rgba(255,255,255,0.7)'
    ctx.beginPath(); ctx.arc(side * 4.2, -11.5, 0.8, 0, Math.PI * 2); ctx.fill()
  }

  // Nose + whiskers
  ctx.fillStyle = '#FFaacc'
  ctx.beginPath(); ctx.arc(0, -6, 1.8, 0, Math.PI * 2); ctx.fill()
  ctx.strokeStyle = 'rgba(255,255,255,0.3)'
  ctx.lineWidth = 0.7
  for (const side of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(side * 4, -6); ctx.lineTo(side * 16, -9); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(side * 4, -5); ctx.lineTo(side * 15, -3); ctx.stroke()
  }

  // Fluffy tail
  ctx.fillStyle = '#FFccdd'
  ctx.beginPath(); ctx.arc(0, 16, 5, 0, Math.PI * 2); ctx.fill()

  ctx.restore()
}

function drawEnergyBeams(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  if (progress < 0.6) return
  const intensity = (progress - 0.6) / 0.4 // 0 to 1

  hawks.forEach(h => {
    if (h.phase !== 'siege') return
    const dx = rabbitX - h.x, dy = rabbitY - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist > 0.3) return

    const alpha = intensity * 0.15 * (1 - dist / 0.3)
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,200,50,${alpha})`
    ctx.lineWidth = 1.5
    ctx.setLineDash([4, 6])
    ctx.moveTo(h.x * W, h.y * H)
    ctx.lineTo(rabbitX * W, rabbitY * H)
    ctx.stroke()
    ctx.setLineDash([])
  })
}

function drawHUD(ctx: CanvasRenderingContext2D, W: number, H: number, progress: number) {
  if (props.iteration <= 0) return

  const phaseLabel = progress < 0.3 ? 'EXPLORACI\u00d3N' : progress < 0.65 ? 'TRANSICI\u00d3N' : 'SIEGE'
  const phaseColors = progress < 0.3 ? [100, 170, 255] : progress < 0.65 ? [220, 180, 80] : [255, 80, 80]
  const E = (2 * (1 - progress)).toFixed(2)

  // HUD panel
  ctx.fillStyle = 'rgba(0,0,0,0.5)'
  ctx.beginPath()
  ctx.roundRect(W - 175, 8, 163, 74, 10)
  ctx.fill()
  ctx.strokeStyle = `rgba(${phaseColors[0]},${phaseColors[1]},${phaseColors[2]},0.3)`
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.roundRect(W - 175, 8, 163, 74, 10)
  ctx.stroke()

  ctx.textAlign = 'right'
  ctx.fillStyle = `rgba(${phaseColors[0]},${phaseColors[1]},${phaseColors[2]},0.9)`
  ctx.font = 'bold 14px Inter, sans-serif'
  ctx.fillText(phaseLabel, W - 20, 30)

  ctx.fillStyle = 'rgba(255,255,255,0.4)'
  ctx.font = '11px "JetBrains Mono", monospace'
  ctx.fillText(`E(t) = ${E}`, W - 20, 48)
  ctx.fillText(`iter ${props.iteration} / ${props.maxIter}`, W - 20, 63)
  ctx.fillText(`${paretoNorm.length} Pareto`, W - 20, 76)

  // Axis labels
  ctx.textAlign = 'center'
  ctx.fillStyle = 'rgba(255,255,255,0.18)'
  ctx.font = '11px Inter, sans-serif'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 10)
  ctx.save()
  ctx.translate(14, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('f\u2082 \u2014 Disparidad', 0, 0)
  ctx.restore()
}

// ---- Main loop ----

function frame() {
  const cvs = canvasRef.value
  if (!cvs) { animId = requestAnimationFrame(frame); return }
  const ctx = cvs.getContext('2d')
  if (!ctx) { animId = requestAnimationFrame(frame); return }

  frameCount++
  const W = cvs.width / dpr
  const H = cvs.height / dpr
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  // Solid clear + nebula
  ctx.fillStyle = '#06061a'
  ctx.fillRect(0, 0, W, H)

  drawNebula(ctx, W, H, progress)
  drawStarfield(ctx, W, H)
  drawGrid(ctx, W, H)
  drawParetoFront(ctx, W, H)
  drawEnergyBeams(ctx, W, H, progress)

  // Update sparks
  sparks = sparks.filter(s => s.life > 0)
  sparks.forEach(s => {
    s.x += s.vx; s.y += s.vy
    s.vy += 0.0001
    s.vx *= 0.98; s.vy *= 0.98
    s.life -= 1
    const alpha = s.life / s.maxLife
    ctx.beginPath()
    ctx.fillStyle = `rgba(${s.r},${s.g},${s.b},${alpha * 0.8})`
    ctx.arc(s.x * W, s.y * H, s.size * alpha, 0, Math.PI * 2)
    ctx.fill()
  })

  // Update hawks
  hawks.forEach(h => {
    const dx = h.tx - h.x, dy = h.ty - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (h.phase === 'explore') {
      h.vx += dx * 0.001 + (Math.random() - 0.5) * 0.002
      h.vy += dy * 0.001 + (Math.random() - 0.5) * 0.002
    } else if (h.phase === 'transition') {
      h.vx += dx * 0.003 + (Math.random() - 0.5) * 0.001
      h.vy += dy * 0.003 + (Math.random() - 0.5) * 0.001
    } else {
      h.vx += dx * 0.006
      h.vy += dy * 0.006
      if (Math.random() < 0.006) {
        const levy = Math.pow(Math.random(), -0.5) * 0.025
        h.vx += (Math.random() - 0.5) * levy
        h.vy += (Math.random() - 0.5) * levy
      }
    }

    h.vx *= 0.94; h.vy *= 0.94
    const speed = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    const maxS = h.phase === 'siege' ? 0.012 : 0.008
    if (speed > maxS) { h.vx *= maxS / speed; h.vy *= maxS / speed }

    h.x += h.vx; h.y += h.vy
    h.x = Math.max(0.03, Math.min(0.97, h.x))
    h.y = Math.max(0.03, Math.min(0.97, h.y))
    if (h.x <= 0.03 || h.x >= 0.97) h.vx *= -0.6
    if (h.y <= 0.03 || h.y >= 0.97) h.vy *= -0.6

    // Smooth heading
    if (speed > 0.0008) {
      const target = Math.atan2(h.vy, h.vx) + Math.PI / 2
      let diff = target - h.angle
      while (diff > Math.PI) diff -= Math.PI * 2
      while (diff < -Math.PI) diff += Math.PI * 2
      h.angle += diff * 0.12
    }

    h.wing += h.wingSpeed + (h.phase === 'siege' ? 0.06 : 0)

    // Trail
    h.trail.push({ x: h.x, y: h.y, age: 0 })
    h.trail.forEach(t => t.age++)
    h.trail = h.trail.filter(t => t.age < 50)

    // Sparks near rabbit
    if (h.phase === 'siege' && dist < 0.1 && Math.random() < 0.15) {
      const angle = Math.random() * Math.PI * 2
      const spd = 0.002 + Math.random() * 0.004
      sparks.push({
        x: h.x, y: h.y,
        vx: Math.cos(angle) * spd,
        vy: Math.sin(angle) * spd,
        life: 30 + Math.random() * 30,
        maxLife: 60,
        r: 255, g: 200 + Math.floor(Math.random() * 55), b: 0,
        size: 2 + Math.random() * 2,
      })
    }

    drawHawk(ctx, h, W, H)
  })

  // Rabbit
  rabbitPulse = (rabbitPulse + 0.004) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse, progress)

  drawHUD(ctx, W, H, progress)

  animId = requestAnimationFrame(frame)
}

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

onMounted(() => {
  setupCanvas()
  initStars(180)
  spawnHawks(20)
  animId = requestAnimationFrame(frame)
  window.addEventListener('resize', () => { setupCanvas(); initStars(180) })
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', setupCanvas)
})
</script>

<template>
  <div class="relative">
    <canvas
      ref="canvasRef"
      class="w-full h-[600px] rounded-xl"
    />
    <div class="absolute top-3 left-3 flex flex-wrap gap-3 text-[10px] text-gray-400/80">
      <span class="flex items-center gap-1.5 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(96,165,250,0.8)]" />
        Exploraci&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_rgba(220,180,80,0.8)]" />
        Transici&oacute;n
      </span>
      <span class="flex items-center gap-1.5 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-red-400 shadow-[0_0_6px_rgba(255,80,80,0.8)]" />
        Siege
      </span>
      <span class="flex items-center gap-1.5 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_6px_rgba(255,51,102,0.8)]" />
        Presa
      </span>
      <span class="flex items-center gap-1.5 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
        <span class="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_6px_rgba(0,100,255,0.8)]" />
        Frente Pareto
      </span>
    </div>
  </div>
</template>
