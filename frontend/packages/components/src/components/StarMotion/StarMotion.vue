<template>
  <canvas ref="canvasRef" class="star-motion" :width="width" :height="height" />
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'

interface Star {
  x: number
  y: number
  speed: number
  size: number
  opacity: number
  currentOpacity: number
  init: (firstRun?: boolean) => void
  update: () => void
  draw: () => void
}

const width = 800
const height = 600
const canvasRef = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
const stars: Star[] = []
const starCount = 400
let animationId: number | null = null

class StarImpl implements Star {
  x = 0
  y = 0
  speed = 0
  size = 0
  opacity = 0
  currentOpacity = 0

  constructor() {
    this.init(true)
  }

  init(firstRun = false) {
    this.x = Math.random() * width
    this.y = firstRun ? Math.random() * height : height + Math.random() * 20

    const depth = Math.random()
    this.speed = depth * 0.5 + 0.3
    this.size = depth * 1.2 + 0.5
    this.opacity = depth * 0.6 + 0.6
    this.currentOpacity = this.opacity
  }

  update() {
    this.y -= this.speed

    const fadeZone = height * 0.2
    this.currentOpacity = this.opacity
    if (this.y < fadeZone) {
      this.currentOpacity = this.opacity * (this.y / fadeZone)
    }

    if (this.y < -10) {
      this.init(false)
    }
  }

  draw() {
    if (!ctx) return
    ctx.fillStyle = `rgba(255, 255, 255, ${this.currentOpacity})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

function animate() {
  if (!ctx) return

  ctx.clearRect(0, 0, width, height)

  stars.forEach(star => {
    star.update()
    star.draw()
  })

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  if (!canvasRef.value) return
  ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  for (let i = 0; i < starCount; i++) {
    stars.push(new StarImpl())
  }

  animate()
})

onUnmounted(() => {
  animationId && cancelAnimationFrame(animationId)
})
</script>
