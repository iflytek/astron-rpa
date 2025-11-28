<script setup lang="ts">
import { computed } from 'vue'
import { isArray } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

const selectValue = computed(() => {
  if (!isArray(props.item.value)) {
    return props.item.value
  }

  return ""
})

const handleChange = (value: boolean) => {
  props.item.value = value
  emit('update', props.item.key, value)
}
</script>

<template>
  <a-switch
    :checked="selectValue"
    :checked-value="props.item?.options[0].value"
    :un-checked-value="props.item?.options[1].value"
    :checked-children="props.item?.options[0].label"
    :un-checked-children="props.item?.options[1].label"
    @update:checked="handleChange"
  />
</template>
