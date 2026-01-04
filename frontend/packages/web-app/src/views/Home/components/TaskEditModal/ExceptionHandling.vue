<script lang="ts" setup>
import { useTheme } from '@rpa/components'
import { InputNumber } from 'ant-design-vue'
import { computed, h, nextTick } from 'vue'

import type { Task } from '@/types/schedule'

const exceptional = defineModel<Task['exceptional']>('exceptional')
const retryTimes = defineModel<number>('retryTimes')

const { colorTheme } = useTheme()

const options = computed(() => {
  const genNumber = (type: Task['exceptional']) => {
    const times = retryTimes.value ?? 0
    return h('span', { class: 'text-primary' }, exceptional.value === type ? times : 0)
  }

  const genNumberInput = (type: Task['exceptional']) => {
    return h(InputNumber, {
      size: 'small',
      min: 0,
      max: 99,
      class: ['input-number', colorTheme.value],
      placeholder: '0 (不重试)',
      value: exceptional.value === type ? retryTimes.value : undefined,
      onChange: (value: number) => { retryTimes.value = value },
      onMousedown: (e: MouseEvent) => {
        e.stopPropagation()
        exceptional.value = type
        // 使用 nextTick 确保 DOM 更新后再聚焦
        nextTick(() => {
          const inputNumberEl = (e.target as HTMLElement).closest('.ant-input-number')
          const input = inputNumberEl?.querySelector('input') as HTMLInputElement
          input?.focus()
        })
      },
      onClick: (e: MouseEvent) => {
        e.stopPropagation()
      },
    })
  }

  return [
    {
      value: 'stop',
      label: '中止任务',
    },
    {
      value: 'jump',
      label: '跳过异常应用，继续执行任务',
    },
    {
      value: 'retry_stop',
      label: h('div', { class: 'flex items-center gap-2' }, ['重试', genNumber('retry_stop'), '次异常应用后，中止任务']),
      render: h('div', { class: 'flex items-center gap-2' }, ['重试', genNumberInput('retry_stop'), '次异常应用后，中止任务']),
    },
    {
      value: 'retry_jump',
      label: h('div', { class: 'flex items-center gap-2' }, ['重试', genNumber('retry_jump'), '次异常应用后，跳过并继续任务']),
      render: h('div', { class: 'flex items-center gap-2' }, ['重试', genNumberInput('retry_jump'), '次异常应用后，跳过并继续任务']),
    },
  ]
})
</script>

<template>
  <a-select
    v-model:value="exceptional" :dropdown-match-select-width="false" option-label-prop="label"
    :options="options"
  >
    <template #option="{ label, render }">
      <component :is="render" v-if="render" />
      <span v-else>{{ label }}</span>
    </template>
  </a-select>
</template>

<style lang="scss" scoped>
.input-number {
  border: 1px solid #d9d9d9;
}

.dark.input-number {
  border: 1px solid #424242;
}

:deep(.ant-input-number-focused) {
  border-color: var(--color-primary);
}
</style>
