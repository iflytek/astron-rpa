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

// 判断 icon 是否是新应用头像格式 (如 avatar-internet-1 或 avatar-industry-construction-1)
// 格式：avatar-{type1}-{type2?}-...-{number}，可以有多个类型部分
const isNewRobotAvatar = computed(() => {
  if (!props.icon)
    return false
  return /^avatar-[a-z]+(?:-[a-z]+)*-\d+$/.test(props.icon)
})

// 新应用头像不显示背景色
const backgroundColor = computed(() => {
  if (isNewRobotAvatar.value) {
    return 'transparent'
  }
  return props.color || DEFAULT_COLOR
})
</script>

<template>
  <div
    v-if="robotName"
    :style="{ width: `${sizeStyle.size}px`, height: `${sizeStyle.size}px`, borderRadius: `${sizeStyle.radius}px`, background: backgroundColor }"
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
