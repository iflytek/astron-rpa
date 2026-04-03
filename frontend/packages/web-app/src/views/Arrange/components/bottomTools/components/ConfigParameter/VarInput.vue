<script setup lang="ts">
import { ref } from 'vue'

const modelValue = defineModel<string>('value')
const isComposing = ref(false)

function handleInput(event: Event) {
  if (isComposing.value)
    return

  const target = event.target as HTMLInputElement
  // 允许字母、数字、下划线和Python变量名允许的中文字符（CJK统一汉字范围）
  // Python 3 支持 Unicode 标识符，包括 CJK 统一汉字 \u4E00-\u9FFF
  const filteredValue = target.value.replace(/[^\w\u4E00-\u9FFF]/g, '')

  if (target.value !== filteredValue) {
    target.value = filteredValue
  }

  if (modelValue.value !== filteredValue) {
    modelValue.value = filteredValue
  }
}

function handleCompositionEnd(event: CompositionEvent) {
  isComposing.value = false
  handleInput(event)
}
</script>

<template>
  <input
    :value="modelValue"
    class="px-[12px] py-[5px] outline-none bg-transparent"
    @input="handleInput"
    @compositionstart="isComposing = true"
    @compositionend="handleCompositionEnd"
  >
</template>
