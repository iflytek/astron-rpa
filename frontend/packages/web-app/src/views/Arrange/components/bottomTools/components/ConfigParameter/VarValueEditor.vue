<script setup lang="ts">
import { has, isArray, isEmpty, isEqual, some } from 'lodash-es'
import { nextTick, ref, watch } from 'vue'

import { OTHER_IN_TYPE, PY_IN_TYPE } from '@/constants/atom'
import AtomConfig from '@/views/Arrange/components/atomForm/AtomConfig.vue'
import { VariableType } from '@/corobot/type';

const props = defineProps<{
  varValue: string | unknown
  varType?: VariableType
  formType?: string
  size?: 'default' | 'small'
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:varValue', value: string): void
  (e: 'blur'): void
  (e: 'changed', value: string): void
}>()

const instanceId = `var-value-${Date.now()}-${Math.random().toString(36).slice(2)}`

function safeParse(str) {
  try {
    return JSON.parse(str)
  } catch {
    return str
  }
}

function convertStringToArray(_varValue: unknown): RPA.AtomFormItemResult[] {
  const varValue = safeParse(_varValue)
  const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))
  return illegal ? [{ type: OTHER_IN_TYPE, value: varValue || '' }] : varValue
}

function convertArrayToString(varValue: RPA.AtomFormItemResult[]): string {
  const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))
  return JSON.stringify(illegal ? [{ type: OTHER_IN_TYPE, value: varValue || '' }] : varValue)
}

function syncVarValue(varValue: RPA.AtomFormItemResult[]) {
  const newVarValue = convertArrayToString(varValue)
  emit('update:varValue', newVarValue)
  return newVarValue
}

function handleBlur(event: FocusEvent) {
  const currentTarget = event.currentTarget as HTMLElement
  const relatedTarget = event.relatedTarget as HTMLElement | null

  // 焦点移到了容器外则触发 blur 事件
  if (!currentTarget.contains(relatedTarget)) {
    emit('blur')
  }
}

const formItem = ref<RPA.AtomDisplayItem>()

let externalChange = false // 标记是否是外部变化导致的 formItem.value.value 变化
watch(() => [props.varValue, props.disabled], () => {
  externalChange = true
  formItem.value = {
    types: props.varType || 'Any',
    name: instanceId,
    key: instanceId,
    title: '',
    value: convertStringToArray(props.varValue),
    formType: {
      type: props.formType || 'INPUT_PYTHON',
    },
    noInput: props.disabled,
  }
  nextTick(() => externalChange = false)
}, { immediate: true })

watch(() => props.varType, (varType) => {
  externalChange = true
  const type = varType === 'Str' ? OTHER_IN_TYPE : PY_IN_TYPE
  const value = isArray(formItem.value.value) ? formItem.value.value.map(i => i.value).join() : formItem.value.value
  const newVarValue = syncVarValue([{ type, value }])
  emit('changed', newVarValue)
  nextTick(() => externalChange = false)
})

watch(() => formItem.value.value, (newVal, oldVal) => {
  if (!externalChange && !isEqual(newVal, oldVal)) {
    const newVarValue = syncVarValue(newVal as RPA.AtomFormItemResult[])
    emit('changed', newVarValue)
  }
})
</script>

<template>
  <div @focusout="handleBlur">
    <AtomConfig
      :form-item="formItem"
      :size="size"
    />
  </div>
</template>
