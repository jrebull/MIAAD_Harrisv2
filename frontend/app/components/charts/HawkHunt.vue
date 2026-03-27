<script setup lang="ts">
/**
 * Animated Harris Hawks hunting visualization.
 * Hawks (agents) converge on the rabbit (prey/leader) in the f₁–f₂ objective space.
 * Pareto front solutions glow as hawks discover them.
 */

const props = defineProps<{
  paretoFront: Array<{ f1: number; f2: number; f3: number }>
  iteration: number
  maxIter: number
  running: boolean
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
let animId = 0

// Hawks state — synthetic positions that converge toward pareto front
interface Hawk {
  x: number; y: number       // current position
  tx: number; ty: number     // target position
  vx: number; vy: number     // velocity
  trail: Array<{ x: number; y: number; age: number }>
  phase: 'explore' | 'siege'
  size: number
  wingAngle: number
  wingSpeed: number
}

interface Rabbit {
  x: number; y: number
  pulsePhase: number
}

const hawks = ref<Hawk[]>([])
const rabbit = ref<Rabbit>({ x: 0.5, y: 0.5, pulsePhase: 0 })
const particles = ref<Array<{ x: number; y: number; vx: number; vy: number; life: number; color: string }>>([])

// Normalize pareto points to [0,1] canvas space
function normalizePoints(pts: Array<{ f1: number; f2: number }>) {
  if (pts.length === 0) return []
  const f1s = pts.map(p => p.f1)
  const f2s = pts.map(p => p.f2)
  const f1min = Math.min(...f1s), f1max = Math.max(...f1s)
  const f2min = Math.min(...f2s), f2max = Math.max(...f2s)
  const f1range = f1max - f1min || 1
  const f2range = f2max - f2min || 1
  return pts.map(p => ({
    x: 0.08 + 0.84 * (p.f1 - f1min) / f1range,
    y: 0.08 + 0.84 * (p.f2 - f2min) / f2range,
  }))
}

// Initialize hawks
function initHawks(count: number) {
  const h: Hawk[] = []
  for (let i = 0; i < count; i++) {
    h.push({
      x: 0.1 + Math.random() * 0.8,
      y: 0.1 + Math.random() * 0.8,
      tx: 0.5, ty: 0.5,
      vx: (Math.random() - 0.5) * 0.01,
      vy: (Math.random() - 0.5) * 0.01,
      trail: [],
      phase: 'explore',
      size: 5 + Math.random() * 3,
      wingAngle: Math.random() * Math.PI * 2,
      wingSpeed: 0.15 + Math.random() * 0.1,
    })
  }
  hawks.value = h
}

watch(() => props.running, (running) => {
  if (running) {
    initHawks(Math.min(40, props.maxIter > 0 ? 30 : 20))
    particles.value = []
  }
})

// Update hawks when Pareto front changes
watch(() => props.paretoFront, (front) => {
  if (!front || front.length === 0) return
  const norm = normalizePoints(front)

  // Rabbit = first point (best f1)
  rabbit.value.x = norm[0].x
  rabbit.value.y = norm[0].y

  // Assign targets from Pareto front
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0
  hawks.value.forEach((h, i) => {
    const target = norm[i % norm.length]
    h.tx = target.x + (Math.random() - 0.5) * 0.1 * (1 - progress)
    h.ty = target.y + (Math.random() - 0.5) * 0.1 * (1 - progress)
    h.phase = progress > 0.5 ? 'siege' : 'explore'
  })
}, { deep: true })

function drawHawk(ctx: CanvasRenderingContext2D, x: number, y: number, size: number, wingAngle: number, phase: string) {
  ctx.save()
  ctx.translate(x, y)

  // Wing flap animation
  const flap = Math.sin(wingAngle) * 0.4

  // Body
  ctx.beginPath()
  ctx.fillStyle = phase === 'siege' ? '#FFD600' : 'rgba(96,165,250,0.9)'
  ctx.shadowColor = phase === 'siege' ? '#FFD600' : '#60a5fa'
  ctx.shadowBlur = 8

  // Left wing
  ctx.moveTo(0, -size * 0.3)
  ctx.quadraticCurveTo(-size * 1.2, -size * flap, -size * 0.3, size * 0.2)

  // Body bottom
  ctx.lineTo(0, size * 0.4)

  // Right wing
  ctx.lineTo(size * 0.3, size * 0.2)
  ctx.quadraticCurveTo(size * 1.2, -size * flap, 0, -size * 0.3)

  ctx.fill()

  // Head dot
  ctx.beginPath()
  ctx.fillStyle = '#fff'
  ctx.shadowBlur = 0
  ctx.arc(0, -size * 0.15, size * 0.15, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

function drawRabbit(ctx: CanvasRenderingContext2D, x: number, y: number, pulsePhase: number) {
  ctx.save()
  ctx.translate(x, y)

  // Pulse rings
  for (let i = 0; i < 3; i++) {
    const phase = (pulsePhase + i * 0.33) % 1
    const r = 8 + phase * 30
    ctx.beginPath()
    ctx.strokeStyle = `rgba(255,51,102,${0.4 * (1 - phase)})`
    ctx.lineWidth = 2 * (1 - phase)
    ctx.arc(0, 0, r, 0, Math.PI * 2)
    ctx.stroke()
  }

  // Rabbit body
  ctx.beginPath()
  ctx.fillStyle = '#FF3366'
  ctx.shadowColor = '#FF3366'
  ctx.shadowBlur = 15
  ctx.arc(0, 2, 7, 0, Math.PI * 2)
  ctx.fill()

  // Ears
  ctx.shadowBlur = 0
  ctx.beginPath()
  ctx.fillStyle = '#FF3366'
  ctx.ellipse(-3, -8, 2.5, 6, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(3, -8, 2.5, 6, 0.2, 0, Math.PI * 2)
  ctx.fill()

  // Inner ears
  ctx.beginPath()
  ctx.fillStyle = '#FF6690'
  ctx.ellipse(-3, -7, 1.5, 4, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(3, -7, 1.5, 4, 0.2, 0, Math.PI * 2)
  ctx.fill()

  // Eyes
  ctx.fillStyle = '#fff'
  ctx.beginPath()
  ctx.arc(-2.5, 1, 1.5, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.arc(2.5, 1, 1.5, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#111'
  ctx.beginPath()
  ctx.arc(-2.5, 1, 0.8, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.arc(2.5, 1, 0.8, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

function animate() {
  const cvs = canvas.value
  if (!cvs) return
  const ctx = cvs.getContext('2d')
  if (!ctx) return

  const W = cvs.width
  const H = cvs.height
  const progress = props.maxIter > 0 ? props.iteration / props.maxIter : 0

  // Clear with fade trail
  ctx.fillStyle = 'rgba(8,8,24,0.15)'
  ctx.fillRect(0, 0, W, H)

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.03)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const x = (i / 10) * W
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
    const y = (i / 10) * H
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
  }

  // Axis labels
  ctx.fillStyle = 'rgba(255,255,255,0.25)'
  ctx.font = '11px Inter, sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('f\u2081 \u2014 Carga de espera', W / 2, H - 6)
  ctx.save()
  ctx.translate(14, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('f\u2082 \u2014 Disparidad', 0, 0)
  ctx.restore()

  // Pareto front glow dots
  if (props.paretoFront.length > 0) {
    const norm = normalizePoints(props.paretoFront)
    norm.forEach(p => {
      const px = p.x * W
      const py = p.y * H
      ctx.beginPath()
      ctx.fillStyle = 'rgba(0,60,166,0.6)'
      ctx.shadowColor = '#003CA6'
      ctx.shadowBlur = 12
      ctx.arc(px, py, 3, 0, Math.PI * 2)
      ctx.fill()
      ctx.shadowBlur = 0
    })
  }

  // Update and draw particles
  particles.value = particles.value.filter(p => p.life > 0)
  particles.value.forEach(p => {
    p.x += p.vx
    p.y += p.vy
    p.life -= 0.02
    p.vy += 0.0002 // gravity
    ctx.beginPath()
    ctx.fillStyle = p.color.replace(')', `,${p.life})`)
    ctx.arc(p.x * W, p.y * H, 1.5 * p.life, 0, Math.PI * 2)
    ctx.fill()
  })

  // Update and draw hawks
  hawks.value.forEach(h => {
    // Physics
    const speed = h.phase === 'siege' ? 0.008 : 0.004
    const dx = h.tx - h.x
    const dy = h.ty - h.y
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (h.phase === 'explore') {
      // Random exploration with drift toward target
      h.vx += (dx * 0.002 + (Math.random() - 0.5) * 0.003)
      h.vy += (dy * 0.002 + (Math.random() - 0.5) * 0.003)
    } else {
      // Siege: converge more aggressively
      h.vx += dx * speed * 0.5
      h.vy += dy * speed * 0.5
      // Lévy-like occasional jump
      if (Math.random() < 0.005) {
        h.vx += (Math.random() - 0.5) * 0.05
        h.vy += (Math.random() - 0.5) * 0.05
      }
    }

    // Damping
    h.vx *= 0.95
    h.vy *= 0.95

    // Clamp velocity
    const maxV = 0.015
    const v = Math.sqrt(h.vx * h.vx + h.vy * h.vy)
    if (v > maxV) { h.vx *= maxV / v; h.vy *= maxV / v }

    h.x += h.vx
    h.y += h.vy

    // Bounce off edges
    if (h.x < 0.05 || h.x > 0.95) h.vx *= -0.8
    if (h.y < 0.05 || h.y > 0.95) h.vy *= -0.8
    h.x = Math.max(0.05, Math.min(0.95, h.x))
    h.y = Math.max(0.05, Math.min(0.95, h.y))

    // Wing animation
    h.wingAngle += h.wingSpeed

    // Trail
    h.trail.push({ x: h.x, y: h.y, age: 1.0 })
    if (h.trail.length > 20) h.trail.shift()
    h.trail.forEach(t => { t.age -= 0.04 })

    // Draw trail
    if (h.trail.length > 1) {
      for (let i = 1; i < h.trail.length; i++) {
        const t = h.trail[i]
        if (t.age <= 0) continue
        ctx.beginPath()
        ctx.strokeStyle = h.phase === 'siege'
          ? `rgba(255,214,0,${t.age * 0.3})`
          : `rgba(96,165,250,${t.age * 0.2})`
        ctx.lineWidth = t.age * 1.5
        ctx.moveTo(h.trail[i - 1].x * W, h.trail[i - 1].y * H)
        ctx.lineTo(t.x * W, t.y * H)
        ctx.stroke()
      }
    }

    // Spawn particles near rabbit
    if (h.phase === 'siege' && dist < 0.15 && Math.random() < 0.1) {
      particles.value.push({
        x: h.x, y: h.y,
        vx: (Math.random() - 0.5) * 0.005,
        vy: (Math.random() - 0.5) * 0.005,
        life: 0.8,
        color: 'rgba(255,214,0',
      })
    }

    drawHawk(ctx, h.x * W, h.y * H, h.size, h.wingAngle, h.phase)
  })

  // Draw rabbit (prey)
  rabbit.value.pulsePhase = (rabbit.value.pulsePhase + 0.008) % 1
  drawRabbit(ctx, rabbit.value.x * W, rabbit.value.y * H, rabbit.value.pulsePhase)

  // Phase label
  ctx.fillStyle = 'rgba(255,255,255,0.5)'
  ctx.font = 'bold 11px Inter, sans-serif'
  ctx.textAlign = 'right'
  const phaseText = progress < 0.3 ? 'EXPLORACIÓN' : progress < 0.7 ? 'TRANSICIÓN' : 'SIEGE'
  const energyText = `E = ${(2 * (1 - progress)).toFixed(2)}`
  ctx.fillText(phaseText, W - 12, 20)
  ctx.font = '10px monospace'
  ctx.fillStyle = 'rgba(255,255,255,0.3)'
  ctx.fillText(energyText, W - 12, 34)

  animId = requestAnimationFrame(animate)
}

onMounted(() => {
  const cvs = canvas.value
  if (cvs) {
    const rect = cvs.getBoundingClientRect()
    cvs.width = rect.width * 2
    cvs.height = rect.height * 2
    const ctx = cvs.getContext('2d')
    if (ctx) {
      ctx.scale(2, 2)
      cvs.width = rect.width * 2
      cvs.height = rect.height * 2
      ctx.scale(2, 2)
    }
  }
  animId = requestAnimationFrame(animate)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
})

// Handle resize
function handleResize() {
  const cvs = canvas.value
  if (!cvs) return
  const rect = cvs.getBoundingClientRect()
  cvs.width = rect.width * 2
  cvs.height = rect.height * 2
  const ctx = cvs.getContext('2d')
  if (ctx) ctx.scale(2, 2)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="relative">
    <canvas
      ref="canvas"
      class="w-full h-[480px] rounded-xl bg-[#08081a]"
    />
    <!-- Legend overlay -->
    <div class="absolute top-3 left-3 flex gap-4 text-[10px]">
      <span class="flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-blue-400" /> Halcones (exploración)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-accent-yellow" /> Halcones (siege)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-accent-red" /> Conejo (presa)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-primary" /> Frente Pareto
      </span>
    </div>
  </div>
</template>
