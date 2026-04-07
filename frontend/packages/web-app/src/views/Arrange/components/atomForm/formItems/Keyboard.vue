<script setup lang="ts">
import { ref } from 'vue'

import ShortCutInput from '@/components/ShortcutInput/Index.vue'
import type { ShortcutItemMap } from '@/components/ShortcutInput/types'
import { OTHER_IN_TYPE } from '@/constants/atom'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

function initkeyboard() {
  const valueArr = Array.isArray(props.item?.value) ? props.item.value : []
  const firstValue = (valueArr[0] || {}) as { value?: string }

  const value = firstValue.value ? firstValue.value.replace(/\s*\+\s*/g, ',') : ''
  const text = firstValue.value ?? ''
  
  return{
    id: props.item.id || '',
    name: props.item.name || '',
    value,
    text: text || '点击设置按键',
  }
}

const keyObj = ref<ShortcutItemMap>(initkeyboard())
const keyboardTextList = ref<string[]>([keyObj.value.text])

function handleChange(val) {
  const { text, value: keyVal } = val
  keyboardTextList.value = [text]

  const newValue = keyVal ? [{ type: OTHER_IN_TYPE, value: text }] : []
  emits('update', props.item.key, newValue)
}
</script>

<template>
  <ShortCutInput v-model="keyObj" :keyboard-text-list="keyboardTextList" @change="handleChange" />
</template>
