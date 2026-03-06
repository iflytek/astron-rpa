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
        v-if="atomFormItem.title === $t('common.selectPythonModule')"
        class="text-xs text-primary ml-auto cursor-pointer"
        @click="NiceModal.show(ProcessModal, { type: 'module' })"
      >
        {{ $t('common.createPythonScript') }}
      </span>
    </label>
    <AtomConfig :form-item="atomFormItem" class="mt-2" />
    <article
      v-if="useFormItemRequired(atomFormItem)"
      class="form-container-context-required"
    >
      {{ $t('common.fieldIsRequired', { field: atomFormItem.title }) }}
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
      {{ atomFormItem.title }}{{ $t('common.length') }}{{ getLimitLengthTip(atomFormItem.limitLength) || $t('common.exceedLimit') }}
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
