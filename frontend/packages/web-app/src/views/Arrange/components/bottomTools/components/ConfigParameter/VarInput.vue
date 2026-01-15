<template>
  <input ref="feeInputRef" :value="modelValue" @input="handleChange" class="px-[12px] py-[5px] outline-none bg-transparent" />
</template>

<script setup lang="ts">
import { nextTick, useTemplateRef } from 'vue'

const modelValue = defineModel<string>('value')

const feeInputRef = useTemplateRef('feeInputRef')
  
function handleChange(event: InputEvent) {
  const inputValue = (event.target as HTMLInputElement).value
  // 使用正则表达式替换非数字、字母、下划线的字符
  modelValue.value = inputValue.replace(/[^a-zA-Z0-9_]/g, '')

  nextTick(() => {
    const actualValue = feeInputRef.value.value
    if (actualValue !== modelValue.value) {
      feeInputRef.value.value = modelValue.value
    }
  });
}
</script>
