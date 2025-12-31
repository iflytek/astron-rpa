<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{
  starCount?: number
  movementFactor?: number
}>(), {
  starCount: 300,
  movementFactor: 0.08,
})

const canvasEl = ref<HTMLCanvasElement>()
let ctx: CanvasRenderingContext2D
let width = 0
let height = 0
let stars: Star[] = []
let rafId = 0

let mouseX = 0
let mouseY = 0
let targetX = 0
let targetY = 0

class Star {
  x = 0
  y = 0
  depth = 0
  size = 0
  opacity = 0

  constructor() {
    this.reset()
  }

  reset() {
    this.x = Math.random() * width
    this.y = Math.random() * height
    this.depth = Math.random() * 0.9 + 0.1
    this.size = (Math.random() * 1.5 + 0.5) * this.depth
    this.opacity = (Math.random() * 0.5 + 0.3) * this.depth
  }

  draw(offsetX: number, offsetY: number) {
    const moveX = offsetX * this.depth
    const moveY = offsetY * this.depth
    ctx.beginPath()
    ctx.arc(this.x + moveX, this.y + moveY, this.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`
    ctx.fill()
  }
}

function resize() {
  width = window.innerWidth
  height = window.innerHeight
  canvasEl.value!.width = width
  canvasEl.value!.height = height
  initStars()
}

function initStars() {
  stars = []
  for (let i = 0; i < props.starCount; i++) stars.push(new Star())
}

function animate() {
  ctx.clearRect(0, 0, width, height)
  targetX += (mouseX - targetX) * 0.05
  targetY += (mouseY - targetY) * 0.05
  const offsetX = (targetX - width / 2) * props.movementFactor
  const offsetY = (targetY - height / 2) * props.movementFactor

  stars.forEach(star => star.draw(-offsetX, -offsetY))
  rafId = requestAnimationFrame(animate)
}

function onMouseMove(e: MouseEvent) {
  mouseX = e.clientX
  mouseY = e.clientY
}
const onResize = () => resize()

onMounted(() => {
  ctx = canvasEl.value!.getContext('2d')!
  resize()
  mouseX = width / 2
  mouseY = height / 2
  targetX = mouseX
  targetY = mouseY
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', onResize)
  animate()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <div class="w-full h-full pointer-events-none fixed top-0 left-0 z-0">
    <div class="bottom-glow" />
    <canvas
      ref="canvasEl"
      class="star-canvas block absolute top-0 left-0"
    />
  </div>
</template>

<style lang="scss" scoped>
.bottom-glow {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 120vw;
  height: 40vh;
  z-index: 2;
  background: radial-gradient(
    ellipse at bottom,
    rgba(200, 180, 255, 0.4) 0%,
    rgba(114, 111, 255, 0.4) 30%,
    rgba(50, 20, 100, 0.2) 60%,
    transparent 80%
  );
  filter: blur(40px);
  mix-blend-mode: screen;
  animation: glow-breathe 6s ease-in-out infinite;
}
@keyframes glow-breathe {
  0% {
    opacity: 0.6;
    transform: translateX(-85%) scale(0.8);
  }

  25% {
    opacity: 1;
    transform: translateX(-50%) scale(1.2);
  }

  50% {
    opacity: 0.6;
    transform: translateX(-15%) scale(0.8);
  }

  75% {
    opacity: 1;
    transform: translateX(-50%) scale(1.2);
  }

  100% {
    opacity: 0.6;
    transform: translateX(-85%) scale(0.8);
  }
}
</style>
