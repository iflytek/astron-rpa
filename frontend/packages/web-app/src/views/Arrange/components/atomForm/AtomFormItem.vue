<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'

import { ProcessModal } from '@/views/Arrange/components/process'

import AtomConfig from './AtomConfig.vue'
import {
  getLimitLengthTip,
  useFormItemLimitLength,
  useFormItemRequired,
} from './hooks/useFormItemSort'

const { atomFormItem } = defineProps<{ atomFormItem: RPA.AtomDisplayItem }>()

// 是否展示 label
const showLabel = computed(() => {
  return atomFormItem.formType?.type !== 'CHECKBOX'
})
</script>

<template>
  <div class="form-container">
    <label
      v-if="showLabel"
      class="form-container-label flex items-center text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]"
    >
      <span v-if="atomFormItem.required" class="form-container-label-required">*</span>
      <span
        v-if="atomFormItem.title"
        class="form-container-label-name text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]"
      >
        {{ atomFormItem.title }}
      </span>
      <a-tooltip v-if="atomFormItem.tip" :title="atomFormItem.tip">
        <rpa-hint-icon name="atom-form-tip" width="16px" height="16px" />
      </a-tooltip>
      <span
        v-if="atomFormItem.title === '选择Python模块'"
        class="form-container-label-name text-primary ml-auto cursor-pointer"
        @click="NiceModal.show(ProcessModal, { type: 'module' })"
      >
        创建Python脚本
      </span>
    </label>
    <AtomConfig :form-item="atomFormItem" class="mt-2" />
    <article
      v-if="useFormItemRequired(atomFormItem)"
      class="form-container-context-required"
    >
      {{ atomFormItem.title }}是必填的
    </article>
    <article
      v-if="atomFormItem.customizeTip"
      class="form-container-context-required"
    >
      {{ atomFormItem.customizeTip }}
    </article>
    <article
      v-if="!useFormItemLimitLength(atomFormItem)"
      class="form-container-context-required"
    >
      {{ atomFormItem.title }}长度{{ getLimitLengthTip(atomFormItem.limitLength) || "超出限制" }}
    </article>
  </div>
</template>

<style lang="scss" scoped>
.form-container {
  & + & {
    margin-top: 10px;
  }

  .form-container-label {
    &-required {
      position: relative;
      top: 3px;
      color: $color-error;
      margin-right: 4px;
    }

    &-name {
      font-size: 12px;
      margin-right: 4px;
    }
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
