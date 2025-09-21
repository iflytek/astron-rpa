<script setup lang="ts">
import { computed } from 'vue'

import { COMPONENT_DEFAULT_ICON, DEFAULT_COLOR } from '@/constants/avatar'

type Size = 'xlarge' | 'large' | 'middle' | 'small'

const props = withDefaults(defineProps<{
  icon?: string
  color?: string
  robotName?: string
  hover?: boolean
  active?: boolean
  size?: Size
}>(), { size: 'middle' })

const sizeMap: Record<Size, { size: number, iconSize: number, fontSize: number, radius: number }> = {
  xlarge: { size: 80, iconSize: 56, fontSize: 32, radius: 18 },
  large: { size: 64, iconSize: 42, fontSize: 26, radius: 16 },
  middle: { size: 46, iconSize: 30, fontSize: 18, radius: 8 },
  small: { size: 24, iconSize: 16, fontSize: 12, radius: 4 },
}

const sizeStyle = computed(() => sizeMap[props.size])
</script>

<template>
  <div
    v-if="robotName"
    :style="{ width: `${sizeStyle.size}px`, height: `${sizeStyle.size}px`, borderRadius: `${sizeStyle.radius}px`, background: color || DEFAULT_COLOR }"
    class="shrink-0 inline-flex justify-center items-center text-[#FFFFFF]"
  >
    <rpa-icon v-if="icon" :name="props.icon" :size="`${sizeStyle.iconSize}px`" />
    <div v-else :style="{ fontSize: `${sizeStyle.fontSize}px` }">
      {{ robotName[0] }}
    </div>
  </div>
  <div
    v-else
    class="inline-flex items-center justify-center bg-[rgba(0,0,0,0.03)] dark:bg-[rgba(255,255,255,0.03)]"
    :class="{ 'cursor-pointer hover:bg-[rgba(93,89,255,0.35)]': props.hover, 'border dark:border-white border-black/[.85]': props.active }"
    :style="{ width: `${sizeStyle.size}px`, height: `${sizeStyle.size}px`, borderRadius: `${sizeStyle.radius}px` }"
  >
    <rpa-icon :name="props.icon || COMPONENT_DEFAULT_ICON" :size="`${sizeStyle.iconSize}px`" />
  </div>
</template>
