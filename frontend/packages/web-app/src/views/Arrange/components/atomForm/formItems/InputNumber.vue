<script setup lang="ts">
import { computed } from 'vue'
import { isString, isNumber } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const selectValue = computed(() => {
  if (isString(props.item.value) || isNumber(props.item.value)) {
    return props.item.value
  }

  return 0
})

const handleChange = (val: number) => {
  emits('update', props.item.key, val)
}
</script>

<template>
  <a-input-number
    :value="selectValue"
    :min="props.item.min"
    :max="props.item.max"
    :step="props.item?.step || 1"
    :style="{ width: '100%' }"
    @update:value="handleChange"
  />
</template>
