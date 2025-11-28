<script setup lang="ts">
import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

function handleChange(value: any) {
  props.item.value = value
  emit('update', props.item.key, value)
}
</script>

<template>
  <a-radio-group
    :value="props.item.value"
    :options="props.item.options"
    @update:value="handleChange"
  />
</template>

<style lang="scss" scoped>
:deep(.ant-radio-wrapper) {
  font-size: 12px;
}
</style>
