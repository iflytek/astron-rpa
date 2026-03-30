<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

interface Props {
  /** 矩阵大小（行列数） */
  size?: number
  /** 方块颜色 */
  color?: string
  /** 方块大小（px） */
  squareSize?: number
  /** 方块间距（px） */
  gap?: number
  /** 最小透明度 */
  minAlpha?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 3,
  color: '#726fff',
  squareSize: 4,
  gap: 2,
  minAlpha: 0.15,
})

const squaresRef = ref<HTMLDivElement[]>([])
let animationId: number | null = null

// 为每个方块生成随机相位和速度
const numSquares = props.size * props.size
const phases = Array.from({ length: numSquares }, () => Math.random() * Math.PI * 2)
const speeds = Array.from({ length: numSquares }, () => 0.04 + Math.random() * 0.06)

function animate() {
  squaresRef.value.forEach((square, index) => {
    if (!square)
      return

    phases[index] += speeds[index]
    const flicker = ((Math.sin(phases[index]) + 1) / 2) ** 3
    const finalOpacity = flicker * (1 - props.minAlpha) + props.minAlpha

    square.style.opacity = String(finalOpacity)
    const shadowSpread = Math.max(4, flicker * 22)
    const shadowOpacity = Math.max(0.05, flicker * 0.35)
    square.style.boxShadow = `0 0 ${shadowSpread}px rgba(190, 158, 255, ${shadowOpacity})`
  })

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  animationId = requestAnimationFrame(animate)
})

onUnmounted(() => {
  if (animationId !== null) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<template>
  <div class="matrix-container">
    <div
      class="matrix-grid"
      :style="{
        gridTemplateColumns: `repeat(${size}, 1fr)`,
        gap: `${gap}px`,
      }"
    >
      <div
        v-for="i in numSquares"
        :key="i"
        ref="squaresRef"
        class="matrix-square"
        :style="{
          width: `${squareSize}px`,
          height: `${squareSize}px`,
          background: color,
          borderRadius: `${squareSize / 4}px`,
        }"
      />
    </div>
  </div>
</template>

<style scoped>
.matrix-container {
  position: relative;
  background: rgba(190, 158, 255, 0.05);
  box-shadow: 0 0 40px rgba(190, 158, 255, 0.1);
  overflow: hidden;
}

.matrix-grid {
  display: grid;
}

.matrix-square {
  position: relative;
}
</style>
