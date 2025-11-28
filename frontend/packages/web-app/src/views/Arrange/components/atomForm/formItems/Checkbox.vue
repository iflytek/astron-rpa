<script setup lang="ts">
import { computed } from 'vue'
import { isBoolean } from 'lodash-es'
import { InfoCircleOutlined } from '@ant-design/icons-vue'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

const selectValue = computed(() => {
  if (isBoolean(props.item.value)) {
    return props.item.value
  }

  return false
})

const handleChange = (value: boolean) => {
  props.item.value = value
  emit('update', props.item.key, value)
}
</script>

<template>
  <a-checkbox :checked="selectValue" @update:checked="handleChange">
    <div class="text-xs inline-flex items-center gap-1">
      {{ props.item.title }}
      <a-tooltip v-if="props.item.tip" :title="props.item.tip">
        <InfoCircleOutlined />
      </a-tooltip>
    </div>
  </a-checkbox>
</template>
