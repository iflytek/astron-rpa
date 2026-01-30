<script setup lang="ts">
/**
 * LoadingDots Component
 * SVG implementation of loading dots with opacity animation
 */
interface Props {
  size?: string | number
  color?: string
}

withDefaults(defineProps<Props>(), {
  size: 48,
  color: 'var(--color-primary, #726fff)',
})
</script>

<template>
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    :width="size" 
    :height="size" 
    viewBox="0 0 48 48" 
    fill="none"
  >
    <circle 
      cx="10" cy="24" r="4" 
      transform="rotate(180 10 24)" 
      :fill="color" 
      class="dot dot-1"
    />
    <circle 
      cx="24" cy="24" r="4" 
      transform="rotate(180 24 24)" 
      :fill="color" 
      class="dot dot-2"
    />
    <circle 
      cx="38" cy="24" r="4" 
      transform="rotate(180 38 24)" 
      :fill="color" 
      class="dot dot-3"
    />
  </svg>
</template>

<style scoped>
.dot {
  animation: fade 1.4s infinite ease-in-out both;
}

.dot-1 {
  animation-delay: -0.32s;
}

.dot-2 {
  animation-delay: -0.16s;
}

.dot-3 {
  animation-delay: 0s;
}

@keyframes fade {
  0%, 80%, 100% {
    fill-opacity: 0.35;
  }
  40% {
    fill-opacity: 1;
  }
}
</style>
