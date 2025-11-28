<script setup lang="ts">
import { computed } from 'vue';
import { isString } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const isDisabled = computed(() => props.item.noInput)

const value = computed(() => {
  if (isString(props.item.value)) {
    return props.item.value
  }

  return props.item.value.toString()
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emits('update', props.item.key, target.value)
}
</script>

<template>
  <a-input class="rounded-lg text-xs h-8 text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]" :value="value" @input="handleInput" :readonly="isDisabled" />
</template>
