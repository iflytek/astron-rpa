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

  return ''
})

const handleChange = (val: string) => {
  emits('update', props.item.key, val)
}
</script>

<template>
   <a-input-password
    :value="selectValue"
    :style="{ width: '100%' }"
    @update:value="handleChange"
  />
</template>
