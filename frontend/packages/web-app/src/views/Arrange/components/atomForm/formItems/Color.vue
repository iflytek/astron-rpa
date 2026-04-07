/** 使用场景：「设置单元格格式-背景颜色」 */
<script setup lang="ts">
import { ColorPicker, hex2rgb, rgb2hex } from '@rpa/components'
import { computed } from 'vue'
import { theme } from 'ant-design-vue'
import { isArray } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

const { token } = theme.useToken()

// 将颜色值转换为 HEX 格式（ColorPicker 使用 HEX）
const colorValue = computed<string>(() => {
  const value = props.item.value

  let valueText = isArray(value) ? value.map(it => it.value).join('') : value.toString()

  // 如果是 RGB 格式 "123,21,11"，转换为 HEX
  if (valueText.includes(',') && !valueText.includes('#')) {
    const [r, g, b] = valueText.split(',').map(v => Number.parseInt(v.trim()))
    valueText = rgb2hex({ r, g, b }, true)
  }

  return valueText || token.value.colorPrimary
})

// 处理颜色变化
function handleColorChange(hex: string) {
  // 如果清空颜色，直接设置为空字符串
  if (!hex) {
    props.item.value = ''
    emit('update', props.item.key, '')
    return
  }

  // ColorPicker 返回的是 HEX 格式，但需要转换为 RGB 格式存储
  // 根据原有逻辑，存储为 RGB 格式 "r,g,b"
  const rgb = hex2rgb(hex)
  const rgbString = `${rgb.r},${rgb.g},${rgb.b}`
  props.item.value = rgbString

  emit('update', props.item.key, rgbString)
}

// 确认颜色选择
function handleColorConfirm(hex: string) {
  handleColorChange(hex)
}
</script>

<template>
  <ColorPicker :model-value="colorValue" @confirm="handleColorConfirm" />
</template>
