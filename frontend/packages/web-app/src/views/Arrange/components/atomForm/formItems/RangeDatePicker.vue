<script setup lang="ts">
import { computed } from 'vue'
import { CalendarOutlined } from '@ant-design/icons-vue'
import { isArray } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const params = computed(() => props.item.formType.params)

const handleChange = (dates: [string, string]) => {
  emits('update', props.item.key, dates)
}

const value = computed(() => {
  const itemValue = props.item.value
  if (isArray(itemValue) && itemValue.every((val) => typeof val === 'string')) {
    return itemValue as unknown as [string, string]
  }

  return undefined
});
</script>

<template>
  <a-range-picker
    value-format="YYYY-MM-DD HH:mm:ss"
    :show-time="params?.format?.split(' ')[1] ? { format: params?.format?.split(' ')[1] } : false"
    :format="params?.format || 'YYYY-MM-DD'"
    :style="{ width: '100%' }"
    :value="value"
    @update:value="handleChange"
  >
    <template #suffixIcon>
      <CalendarOutlined class="text-black dark:text-white opacity-45" />
    </template>
  </a-range-picker>
</template>
