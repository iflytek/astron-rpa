<script setup lang="ts">
import { computed } from 'vue'

import { DEFAULT_COLOR } from '@/constants/avatar'

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

const containerStyle = computed(() => ({
  width: `${sizeStyle.value.size}px`,
  height: `${sizeStyle.value.size}px`,
  borderRadius: `${sizeStyle.value.radius}px`,
  background: backgroundColor.value,
  color: props.icon?.includes('comp') ? '#000000' : '#FFFFFF'
}))
</script>

<template>
  <div
    :style="containerStyle"
    class="shrink-0 inline-flex justify-center items-center"
  >
    <rpa-icon v-if="icon" :name="props.icon" :size="`${sizeStyle.iconSize}px`" />
    <div v-else :style="{ fontSize: `${sizeStyle.fontSize}px` }">
      {{ robotName?.[0] }}
    </div>
  </div>
</template>
