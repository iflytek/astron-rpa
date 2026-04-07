<script setup lang="ts">
import { computed } from 'vue';
import { isArray } from 'lodash-es'

import { PY_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import type { FormItemProps } from './index'

const iconStyle = { fontSize: '16px', color: 'inherit' }

const props = defineProps<FormItemProps>()

const isExpr = computed(() => {
  if (isArray(props.item.value)) {
    return props.item.value.some(item => item.type === PY_IN_TYPE)
  }
  return false
})

const handleClick = () => {}
</script>

<template>
  <rpa-hint-icon
    @click="handleClick"
    :title="isExpr ? 'python模式' : '普通模式'"
    :name="isExpr ? 'create-python-process' : 'change-python-btn'"
    :style="iconStyle"
  />
</template>
