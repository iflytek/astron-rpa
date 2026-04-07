<script setup lang="ts">
import { computed } from 'vue'
import { isArray } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

const selectValue = computed(() => {
  if (isArray(props.item.value)) {
    return props.item.value as unknown as string[]
  }

  return []
})

const handleChange = (value: string[]) => {
  // TODO: 这里的类型转换不合理
  props.item.value = value as unknown as string
  emit('update', props.item.key, value)
}
</script>

<template>
  <a-checkbox-group
    :value="selectValue"
    :options="props.item.options"
    @update:value="handleChange"
  />
</template>
