<script setup lang="ts">
import { computed } from 'vue'
import { isArray } from 'lodash-es'

import type { FormItemProps } from './index'

const props = defineProps<FormItemProps>()

const isMultiple = computed(() => props.item.formType.params?.multiple)

const selectValue = computed(() => {
  if (isMultiple.value && isArray(props.item.value)) {
    return props.item.value
  }

  if (isArray(props.item.value)) {
    return props.item.value[0]
  }

  return props.item.value as string
})
</script>

<template>
  <a-select
    :value="selectValue"
    :mode="isMultiple ? 'multiple' : undefined"
    placeholder="请选择"
    class="bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] rounded-[8px]"
    style="width: 100%;"
  >
    <a-select-option v-for="(op, index) in props.item.options" :key="index" :value="op?.label ? op.value : op.rId">
      <template v-if="op?.label">
        {{ op.label }}
      </template>
      <template v-else>
        <span v-for="(it, idx) in op.value.value" :key="idx">
          <hr v-if="it.type === 'var'" class="dialog-tag-input-hr" :data-name="it.value">
          <span v-else>{{ it.value }}</span>
        </span>
      </template>
    </a-select-option>
  </a-select>
</template>

<style lang="scss" scoped>
:deep(.ant-select-selector) {
  font-size: 12px;
  background-color: inherit !important;
  color: inherit;
}

:deep(.ant-select-dropdown .ant-select-item) {
  font-size: 12px;
}
</style>
