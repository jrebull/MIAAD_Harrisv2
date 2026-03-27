<script setup lang="ts">
/**
 * Canvas animation: Harris Hawks hunting a rabbit in f₁–f₂ objective space.
 * Hawks start scattered (exploration), then swoop toward the prey (siege).
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

interface Hawk {
  x: number; y: number
  tx: number; ty: number
  vx: number; vy: number
  angle: number           // flight heading
  trail: Array<[number, number, number]>  // [x, y, opacity]
  phase: 'explore' | 'siege'
  size: number
  wing: number            // wing phase
  wingSpeed: number
}

interface Particle {
  x: number; y: number
  vx: number; vy: number
  life: number
  r: number; g: number; b: number
}

let hawkList: Hawk[] = []
let particleList: Particle[] = []
let rabbitX = 0.5, rabbitY = 0.5, rabbitPulse = 0
let paretoNorm: Array<{ x: number; y: number }> = []

function normalize(pts: Array<{ f1: number; f2: number }>) {
  if (pts.length === 0) return []
  const margin = 0.1
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
  hawkList = []
  for (let i = 0; i < n; i++) {
    hawkList.push({
      x: 0.15 + Math.random() * 0.7,
      y: 0.15 + Math.random() * 0.7,
      tx: 0.5, ty: 0.5,
      vx: (Math.random() - 0.5) * 0.008,
      vy: (Math.random() - 0.5) * 0.008,
      angle: Math.random() * Math.PI * 2,
      trail: [],
      phase: 'explore',
      size: 8 + Math.random() * 4,
      wing: Math.random() * Math.PI * 2,
      wingSpeed: 0.12 + Math.random() * 0.08,
    })
  }
  particleList = []
}

watch(() => props.running, (r) => { if (r) spawnHawks(30) })

watch(() => props.paretoFront, (front) => {
  if (!front?.length) return
  paretoNorm = normalize(front)
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  // Rabbit = best f₁ (first sorted)
  rabbitX = paretoNorm[0].x
  rabbitY = paretoNorm[0].y

  hawkList.forEach((h, i) => {
    const tgt = paretoNorm[i % paretoNorm.length]
    const scatter = 0.12 * (1 - progress)
    h.tx = tgt.x + (Math.random() - 0.5) * scatter
    h.ty = tgt.y + (Math.random() - 0.5) * scatter
    h.phase = progress > 0.45 ? 'siege' : 'explore'
  })
}, { deep: true })

// ---- Drawing helpers ----

function drawBird(ctx: CanvasRenderingContext2D, x: number, y: number, size: number, angle: number, wingPhase: number, siege: boolean) {
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(angle)

  const flap = Math.sin(wingPhase)
  const wingSpan = size * 1.6
  const bodyLen = size * 0.9

  // Glow
  const color = siege ? [255, 214, 0] : [96, 165, 250]
  ctx.shadowColor = `rgb(${color[0]},${color[1]},${color[2]})`
  ctx.shadowBlur = siege ? 14 : 8

  // Wings (two curved arcs)
  ctx.beginPath()
  ctx.strokeStyle = `rgba(${color[0]},${color[1]},${color[2]},0.9)`
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  // Left wing
  ctx.moveTo(0, 0)
  ctx.quadraticCurveTo(-wingSpan * 0.5, -wingSpan * 0.4 * flap, -wingSpan * 0.5, -wingSpan * 0.15 * flap)
  ctx.stroke()
  // Right wing
  ctx.beginPath()
  ctx.moveTo(0, 0)
  ctx.quadraticCurveTo(wingSpan * 0.5, -wingSpan * 0.4 * flap, wingSpan * 0.5, -wingSpan * 0.15 * flap)
  ctx.stroke()

  // Body (tapered)
  ctx.shadowBlur = 0
  ctx.beginPath()
  ctx.fillStyle = `rgba(${color[0]},${color[1]},${color[2]},0.95)`
  ctx.ellipse(0, 0, size * 0.25, bodyLen * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()

  // Head
  ctx.beginPath()
  ctx.fillStyle = '#fff'
  ctx.arc(0, -bodyLen * 0.45, size * 0.18, 0, Math.PI * 2)
  ctx.fill()

  // Tail feathers
  ctx.beginPath()
  ctx.strokeStyle = `rgba(${color[0]},${color[1]},${color[2]},0.5)`
  ctx.lineWidth = 1.5
  ctx.moveTo(-size * 0.12, bodyLen * 0.4)
  ctx.lineTo(-size * 0.2, bodyLen * 0.65)
  ctx.moveTo(0, bodyLen * 0.45)
  ctx.lineTo(0, bodyLen * 0.7)
  ctx.moveTo(size * 0.12, bodyLen * 0.4)
  ctx.lineTo(size * 0.2, bodyLen * 0.65)
  ctx.stroke()

  ctx.restore()
}

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulse: number) {
  ctx.save()
  ctx.translate(x, y)

  // Danger pulse rings
  for (let i = 0; i < 3; i++) {
    const p = (pulse + i * 0.33) % 1
    const r = 10 + p * 35
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,51,102,${0.35 * (1 - p)})`
    ctx.lineWidth = 2.5 * (1 - p)
    ctx.arc(0, 0, r, 0, Math.PI * 2)
    ctx.stroke()
  }

  // Shadow
  ctx.beginPath()
  ctx.fillStyle = 'rgba(255,51,102,0.15)'
  ctx.arc(0, 3, 12, 0, Math.PI * 2)
  ctx.fill()

  // Body
  ctx.shadowColor = '#FF3366'
  ctx.shadowBlur = 18
  ctx.beginPath()
  ctx.fillStyle = '#FF3366'
  ctx.ellipse(0, 3, 8, 9, 0, 0, Math.PI * 2)
  ctx.fill()

  // Head
  ctx.shadowBlur = 0
  ctx.beginPath()
  ctx.fillStyle = '#FF4477'
  ctx.arc(0, -6, 6, 0, Math.PI * 2)
  ctx.fill()

  // Ears
  ctx.fillStyle = '#FF3366'
  ctx.beginPath()
  ctx.ellipse(-3.5, -15, 2.8, 7, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(3.5, -15, 2.8, 7, 0.15, 0, Math.PI * 2)
  ctx.fill()
  // Inner ears
  ctx.fillStyle = '#FF88AA'
  ctx.beginPath()
  ctx.ellipse(-3.5, -14, 1.6, 4.5, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(3.5, -14, 1.6, 4.5, 0.15, 0, Math.PI * 2)
  ctx.fill()

  // Eyes
  ctx.fillStyle = '#fff'
  ctx.beginPath(); ctx.arc(-2.5, -6.5, 2, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(2.5, -6.5, 2, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = '#220011'
  ctx.beginPath(); ctx.arc(-2.5, -6.5, 1, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(2.5, -6.5, 1, 0, Math.PI * 2); ctx.fill()

  // Nose
  ctx.fillStyle = '#FFaacc'
  ctx.beginPath(); ctx.arc(0, -4, 1.2, 0, Math.PI * 2); ctx.fill()

  // Whiskers
  ctx.strokeStyle = 'rgba(255,255,255,0.3)'
  ctx.lineWidth = 0.5
  ctx.beginPath(); ctx.moveTo(-3, -4); ctx.lineTo(-10, -6); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(-3, -3.5); ctx.lineTo(-9, -2); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(3, -4); ctx.lineTo(10, -6); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(3, -3.5); ctx.lineTo(9, -2); ctx.stroke()

  ctx.restore()
}

function frame() {
  const cvs = canvasRef.value
  if (!cvs) { animId = requestAnimationFrame(frame); return }
  const ctx = cvs.getContext('2d')
  if (!ctx) { animId = requestAnimationFrame(frame); return }

  const W = cvs.width / dpr
  const H = cvs.height / dpr
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  // Fade clear
  ctx.fillStyle = 'rgba(8,8,24,0.2)'
  ctx.fillRect(0, 0, W, H)

  // Subtle grid
  ctx.strokeStyle = 'rgba(255,255,255,0.025)'
  ctx.lineWidth = 0.5
  for (let i = 1; i < 12; i++) {
    const gx = (i / 12) * W, gy = (i / 12) * H
    ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke()
  }

  // Axis labels
  ctx.fillStyle = 'rgba(255,255,255,0.2)'
  ctx.font = '11px Inter, sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 8)
  ctx.save()
  ctx.translate(16, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('f\u2082 \u2014 Disparidad', 0, 0)
  ctx.restore()

  // Pareto front dots
  paretoNorm.forEach(p => {
    ctx.beginPath()
    ctx.fillStyle = 'rgba(0,60,166,0.5)'
    ctx.shadowColor = '#003CA6'
    ctx.shadowBlur = 10
    ctx.arc(p.x * W, p.y * H, 3.5, 0, Math.PI * 2)
    ctx.fill()
    ctx.shadowBlur = 0
  })

  // Particles
  particleList = particleList.filter(p => p.life > 0)
  particleList.forEach(p => {
    p.x += p.vx; p.y += p.vy
    p.life -= 0.015
    p.vy += 0.00015
    ctx.beginPath()
    ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${p.life * 0.7})`
    ctx.arc(p.x * W, p.y * H, 2 * p.life, 0, Math.PI * 2)
    ctx.fill()
  })

  // Update hawks
  hawkList.forEach(h => {
    const dx = h.tx - h.x, dy = h.ty - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (h.phase === 'explore') {
      h.vx += dx * 0.0015 + (Math.random() - 0.5) * 0.003
      h.vy += dy * 0.0015 + (Math.random() - 0.5) * 0.003
    } else {
      h.vx += dx * 0.006
      h.vy += dy * 0.006
      // Lévy jumps
      if (Math.random() < 0.004) {
        const levy = Math.pow(Math.random(), -0.5) * 0.02
        h.vx += (Math.random() - 0.5) * levy
        h.vy += (Math.random() - 0.5) * levy
      }
    }

    h.vx *= 0.94; h.vy *= 0.94
    const speed = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    const maxS = 0.012
    if (speed > maxS) { h.vx *= maxS / speed; h.vy *= maxS / speed }

    h.x += h.vx; h.y += h.vy
    if (h.x < 0.06 || h.x > 0.94) h.vx *= -0.7
    if (h.y < 0.06 || h.y > 0.94) h.vy *= -0.7
    h.x = Math.max(0.06, Math.min(0.94, h.x))
    h.y = Math.max(0.06, Math.min(0.94, h.y))

    // Heading angle (smooth)
    if (speed > 0.001) {
      const targetAngle = Math.atan2(h.vy, h.vx) + Math.PI / 2 // bird faces "up" in its local coords
      let diff = targetAngle - h.angle
      while (diff > Math.PI) diff -= Math.PI * 2
      while (diff < -Math.PI) diff += Math.PI * 2
      h.angle += diff * 0.1
    }

    h.wing += h.wingSpeed
    // Faster flapping in siege
    if (h.phase === 'siege') h.wing += 0.04

    // Trail
    h.trail.push([h.x, h.y, 1.0])
    if (h.trail.length > 25) h.trail.shift()

    // Draw trail
    for (let i = 1; i < h.trail.length; i++) {
      h.trail[i][2] -= 0.035
      const t = h.trail[i], prev = h.trail[i - 1]
      if (t[2] <= 0) continue
      const [cr, cg, cb] = h.phase === 'siege' ? [255, 214, 0] : [96, 165, 250]
      ctx.beginPath()
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${t[2] * 0.25})`
      ctx.lineWidth = t[2] * 2
      ctx.moveTo(prev[0] * W, prev[1] * H)
      ctx.lineTo(t[0] * W, t[1] * H)
      ctx.stroke()
    }

    // Particles near rabbit
    if (h.phase === 'siege' && dist < 0.12 && Math.random() < 0.08) {
      particleList.push({
        x: h.x, y: h.y,
        vx: (Math.random() - 0.5) * 0.004,
        vy: (Math.random() - 0.5) * 0.004,
        life: 0.9,
        r: 255, g: 214, b: 0,
      })
    }

    drawBird(ctx, h.x * W, h.y * H, h.size, h.angle, h.wing, h.phase === 'siege')
  })

  // Rabbit
  rabbitPulse = (rabbitPulse + 0.006) % 1
  drawRabbit(ctx, rabbitX * W, rabbitY * H, rabbitPulse)

  // HUD
  if (props.iteration > 0) {
    ctx.textAlign = 'right'
    const phaseLabel = progress < 0.3 ? 'EXPLORACIÓN' : progress < 0.7 ? 'TRANSICIÓN' : 'SIEGE'
    const E = (2 * (1 - progress)).toFixed(2)
    ctx.fillStyle = 'rgba(255,255,255,0.45)'
    ctx.font = 'bold 12px Inter, sans-serif'
    ctx.fillText(phaseLabel, W - 14, 22)
    ctx.fillStyle = 'rgba(255,255,255,0.25)'
    ctx.font = '11px monospace'
    ctx.fillText(`E(t) = ${E}`, W - 14, 38)
    ctx.fillText(`iter ${props.iteration}/${props.maxIter}`, W - 14, 52)
  }

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
  // Start with idle hawks even before simulation
  spawnHawks(20)
  animId = requestAnimationFrame(frame)
  window.addEventListener('resize', setupCanvas)
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
      class="w-full h-[500px] rounded-xl bg-[#08081a]"
    />
    <div class="absolute top-3 left-3 flex gap-4 text-[10px] text-gray-400">
      <span class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(96,165,250,0.6)]" />
        Halcones (exploración)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-full bg-accent-yellow shadow-[0_0_6px_rgba(255,214,0,0.6)]" />
        Halcones (siege)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-full bg-accent-red shadow-[0_0_6px_rgba(255,51,102,0.6)]" />
        Conejo (presa)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_6px_rgba(0,60,166,0.6)]" />
        Frente Pareto
      </span>
    </div>
  </div>
</template>
