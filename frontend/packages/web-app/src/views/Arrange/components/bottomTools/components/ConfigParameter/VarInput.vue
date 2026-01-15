<template>
  <input
    :value="modelValue"
    class="px-[12px] py-[5px] outline-none bg-transparent"
    @input="handleInput"
    @compositionstart="isComposing = true"
    @compositionend="handleCompositionEnd"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const modelValue = defineModel<string>('value')
const isComposing = ref(false)

function handleInput(event: Event) {
  if (isComposing.value) return

  const target = event.target as HTMLInputElement
  const filteredValue = target.value.replace(/[^a-zA-Z0-9_]/g, '')

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