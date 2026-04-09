<script setup lang="ts">
import { computed } from 'vue';
import { isArray } from 'lodash-es'

import { PY_IN_TYPE, OTHER_IN_TYPE } from '@/constants/atom'
import type { FormItemProps, FormItemEmits } from './index'

const iconStyle = { fontSize: '16px', color: 'inherit' }

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const isExpr = computed(() => {
  if (isArray(props.item.value)) {
    return props.item.value.some(item => item.type === PY_IN_TYPE)
  }
  return false
})

const handleClick = () => {
  const obj = { type: isExpr.value ? OTHER_IN_TYPE : PY_IN_TYPE, value: '' }

  if (isArray(props.item.value)) {
    obj.value = props.item.value.map(item => item.value).join('')
  }

  emits('update', props.item.key, [obj])
}
</script>

<template>
  <rpa-hint-icon
    @click="handleClick"
    :title="isExpr ? $t('atomForm.pythonMode') : $t('atomForm.normalMode')"
    :name="isExpr ? 'create-python-process' : 'change-python-btn'"
    :style="iconStyle"
  />
</template>
