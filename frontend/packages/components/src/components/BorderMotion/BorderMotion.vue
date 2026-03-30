<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

interface Props {
  /** 层数 */
  layerCount?: number
  /** 方块大小（px） */
  squareSize?: number
  /** 方块间距（px） */
  gap?: number
  /** 方块颜色 */
  color?: string
  /** 最小透明度比例 */
  minAlphaRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  layerCount: 4,
  squareSize: 3,
  gap: 2,
  color: '#726fff',
  minAlphaRatio: 0.25,
})

const canvasRef = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let squares: Array<{
  x: number
  y: number
  maxAlpha: number
  phase: number
  speed: number
}> = []
let animationId: number | null = null
let width = 0
let height = 0

function init() {
  if (!canvasRef.value || !canvasRef.value.parentElement)
    return

  const dpr = window.devicePixelRatio || 1
  const container = canvasRef.value.parentElement
  width = container.clientWidth
  height = container.clientHeight
  canvasRef.value.width = width * dpr
  canvasRef.value.height = height * dpr
  canvasRef.value.style.width = `${width}px`
  canvasRef.value.style.height = `${height}px`

  ctx = canvasRef.value.getContext('2d')
  if (!ctx)
    return

  ctx.scale(dpr, dpr)

  squares = []
  const step = props.squareSize + props.gap
  let currentOffset = 0

  for (let l = 0; l < props.layerCount; l++) {
    const layerMaxAlpha = 0.7 ** l
    const cols = Math.floor((width - currentOffset * 2) / step)
    const rows = Math.floor((height - currentOffset * 2) / step)

    const addSquare = (x: number, y: number) => {
      squares.push({
        x,
        y,
        maxAlpha: layerMaxAlpha,
        phase: Math.random() * Math.PI * 2,
        speed: 0.04 + Math.random() * 0.06,
      })
    }

    for (let i = 0; i < cols; i++) {
      addSquare(currentOffset + i * step, currentOffset)
      addSquare(currentOffset + i * step, height - currentOffset - props.squareSize)
    }
    for (let i = 1; i < rows - 1; i++) {
      addSquare(currentOffset, currentOffset + i * step)
      addSquare(width - currentOffset - props.squareSize, currentOffset + i * step)
    }
    currentOffset += step
  }
}

function animate() {
  if (!ctx)
    return

  ctx.clearRect(0, 0, width, height)

  for (const s of squares) {
    s.phase += s.speed
    const flicker = ((Math.sin(s.phase) + 1) / 2) ** 3
    const alphaRatio = flicker * (1 - props.minAlphaRatio) + props.minAlphaRatio
    ctx.globalAlpha = s.maxAlpha * alphaRatio
    ctx.fillStyle = props.color

    const sizeBoost = flicker * 0.4
    ctx.fillRect(
      s.x - sizeBoost / 2,
      s.y - sizeBoost / 2,
      props.squareSize + sizeBoost,
      props.squareSize + sizeBoost,
    )
  }

  animationId = requestAnimationFrame(animate)
}

function handleResize() {
  init()
}

onMounted(() => {
  init()
  animate()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId !== null)
    cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="border-motion">
    <div class="glow-overlay" />
    <canvas ref="canvasRef" class="border-canvas" />
  </div>
</template>

<style scoped>
.border-motion {
  position: relative;
  width: 100%;
  height: 100%;
}

.glow-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  box-shadow: inset 0 0 60px rgba(190, 158, 255, 0.05);
}

.border-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
</style>
