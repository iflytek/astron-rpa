<script setup lang="ts">
import { isArray, isEmpty } from 'lodash-es'
import { computed, watch } from 'vue'

import { OTHER_IN_TYPE } from '@/constants/atom'
import AtomConfig from '@/views/Arrange/components/atomForm/AtomConfig.vue'

const props = defineProps<{
  varValue: string | unknown
  varType?: string
  formType?: string
  size?: 'default' | 'small'
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:varValue', value: string): void
  (e: 'blur'): void
  (e: 'model-change', model: string): void
}>()

const instanceId = `var-value-${Date.now()}-${Math.random().toString(36).slice(2)}`

// 由 String 转换成 Array
function convertVarValueToArray(varValue: unknown): RPA.AtomFormItemResult[] {
  if (isArray(varValue) && !isEmpty(varValue)) {
    return varValue
  }
  if (typeof varValue === 'string') {
    try {
      const parsed = JSON.parse(varValue)
      return isArray(parsed) ? parsed : [{ type: OTHER_IN_TYPE, value: varValue }]
    }
    catch {
      return [{ type: OTHER_IN_TYPE, value: varValue }]
    }
  }
  return [{ type: OTHER_IN_TYPE, value: '' }]
}

// 由 Array 转换成 String
function convertArrayToVarValue(value: RPA.AtomFormItemResult[]): string {
  if (!isArray(value) || value.length === 0) {
    return ''
  }
  return JSON.stringify(value)
}

function syncVarValue(value: RPA.AtomFormItemResult[]) {
  emit('update:varValue', convertArrayToVarValue(value))
}

function handleBlur(event: FocusEvent) {
  const currentTarget = event.currentTarget as HTMLElement
  const relatedTarget = event.relatedTarget as HTMLElement | null

  // 焦点移到了容器外则触发 blur 事件
  if (!currentTarget.contains(relatedTarget)) {
    emit('blur')
  }
}

// 创建 formItem，使用 Proxy 拦截变化
const formItem = computed(() => {
  const baseItem: RPA.AtomDisplayItem = {
    types: props.varType || 'Any',
    name: instanceId,
    key: instanceId,
    title: '',
    value: convertVarValueToArray(props.varValue),
    formType: {
      type: props.formType || 'INPUT_PYTHON',
    },
    noInput: props.disabled, // 禁用编辑
  } as RPA.AtomDisplayItem

  return new Proxy(baseItem, {
    set(target, prop, value) {
      target[prop as keyof typeof target] = value

      if (prop === 'value' && !props.disabled) {
        syncVarValue(value as RPA.AtomFormItemResult[])
      }

      return true
    },
  })
})

// 模式切换
watch(
  () => formItem.value?.value[0]?.type,
  (newVal) => {
    emit('model-change', newVal)
  },
)
</script>

<template>
  <div @focusout="handleBlur">
    <AtomConfig :form-item="formItem" :size="size" />
  </div>
</template>
