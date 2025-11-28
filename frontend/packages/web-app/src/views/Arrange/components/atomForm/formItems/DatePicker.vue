<script setup lang="ts">
import { computed } from 'vue'
import { CalendarOutlined } from '@ant-design/icons-vue'
import { isString } from 'lodash-es'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const params = computed(() => props.item.formType.params)

const value = computed(() => {
  if (isString(props.item.value)) {
    return props.item.value
  }

  return null
})

const handleChange = (val: string) => {
  emits('update', props.item.key, val)
}
</script>

<template>
  <a-date-picker
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
  </a-date-picker>
</template>
