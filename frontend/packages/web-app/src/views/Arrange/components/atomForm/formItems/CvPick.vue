<script setup lang="ts">
import BUS from '@/utils/eventBus'

import { ELEMENT_IN_TYPE } from '@/constants/atom'

import type { FormItemProps, FormItemEmits } from './index'
import CvPickBtn from '../../cvPick/CvPickBtn.vue'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const handleClick = () => {
  BUS.$once('cv-pick-done', (res: any) => {
    console.log('cv-pick-done', res)
    const value = [{ type: ELEMENT_IN_TYPE, value: res.value, data: res.data }]
    emits('update', props.item.key, value)
  })
}
</script>

<template>
  <a-tooltip title="拾取图像" class="rounded-lg panel-bg h-8 w-8 justify-center text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
    <CvPickBtn type="icon" entry="atomFormBtn" @click="handleClick" />
  </a-tooltip>
</template>
