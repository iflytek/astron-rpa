<script setup lang="ts">
import { isNil } from 'lodash-es'

import BUS from '@/utils/eventBus'

import type { FormItemProps, FormItemEmits } from './index'
import useFormPick from '../hooks/useFormPick'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const handleClick = () => {
  BUS.$once('pick-done', (res: { data: { x: number, y: number } }) => {
    const { data: { x, y } } = res

    if (!isNil(x) && !isNil(y)) {
      emits('update', 'position_x', x)
      emits('update', 'position_y', y)
    }
  })
  
  useFormPick('POINT')
}
</script>

<template>
  <a-button type="primary" block @click="handleClick">
    获取坐标位置
  </a-button>
</template>
