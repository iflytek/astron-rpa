<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'

import { ProcessModal } from '@/views/Arrange/components/process'

import AtomConfig from './AtomConfig.vue'
import { useFormStore } from './hooks/useFormStore'

const { atomFormItem } = defineProps<{ atomFormItem: RPA.AtomDisplayItem }>()
const emit = defineEmits<{ (e: 'update', key: string, value: any): void }>()

const { formValues } = useFormStore()

// 是否展示 label
const showLabel = computed(() => {
  return atomFormItem.formType?.type !== 'CHECKBOX'
})

function handleUpdate(key: string, value: any) {
  emit('update', key, value)
}
</script>

<template>
  <div class="form-container">
    <label
      v-if="showLabel"
      class="form-container-label flex items-center gap-1 text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]"
    >
      <span v-if="atomFormItem.required" class="text-error">*</span>
      <span
        v-if="atomFormItem.title"
        class="text-xs leading-[22px] text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]"
      >
        {{ atomFormItem.title }}
      </span>
      <span v-if="atomFormItem.subTitle" class="text-[10px] leading-4">
        {{ atomFormItem.subTitle }}
      </span>
      <a-tooltip v-if="atomFormItem.tip" :title="atomFormItem.tip">
        <rpa-hint-icon name="atom-form-tip" width="16px" height="16px" />
      </a-tooltip>
      <span
        v-if="atomFormItem.title === '选择Python模块'"
        class="text-xs text-primary ml-auto cursor-pointer"
        @click="NiceModal.show(ProcessModal, { type: 'module' })"
      >
        创建Python脚本
      </span>
    </label>
    <AtomConfig :form-item="atomFormItem" :form-values="formValues" class="mt-2" @update="handleUpdate" />
    <article
      v-for="value in atomFormItem.errors"
      :key="value"
      class="form-container-context-required"
    >
      {{ value }}
    </article>
  </div>
</template>

<style lang="scss" scoped>
.form-container {
  & + & {
    margin-top: 12px;
  }

  .form-container-context-required {
    color: $color-error;
    margin: 4px 0px;
  }
}

:deep(.atom-options_item) {
  margin: 0 !important;
  padding: 4px 0 !important;
}
</style>
