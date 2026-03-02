<!-- @format -->

<script lang="ts" setup>
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { getWeightedLength, getWeightText } from '@/utils/common'

const props = defineProps({
  formOption: {
    type: Object,
  },
})

const formRef = ref()
const { t } = useTranslation()
const rules: Record<string, Rule[]> = {
  pickName: [
    {
      message: t('enterElementName'),
      trigger: 'blur',
      validator: async (_rule, value) => {
        if (!value.replace(/\s+/g, '')) {
          return Promise.reject(new Error(t('enterElementName')))
        }
        else {
          return Promise.resolve()
        }
      },
    },
  ],
}

function validateName() {
  return new Promise((resolve) => {
    formRef.value.validateFields(['pickName']).then((valid) => {
      if (valid) {
        resolve(true)
      }
    })
  })
}

function inputChange(e) {
  const originLength = getWeightedLength(e.target.value)
  if (originLength >= 32) {
    e.target.value = getWeightText(32, e.target.value)
    props.formOption.pickName = e.target.value
    return false
  }
}

defineExpose({
  validateName,
})
</script>

<template>
  <div class="pick-form">
    <a-form
      ref="formRef"
      :key="formOption.pikName"
      class="form-wrapper text-[12px]"
      :rules="rules"
      :model="formOption"
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 14 }"
      label-align="left"
      layout="vertical"
    >
      <a-form-item :label="$t('elementName')" name="pickName">
        <a-input v-model:value="formOption.pickName" autocomplete="off" class="label-form  w-[550px]" :maxlength="32" :placeholder="$t('enterElementName')" @change="inputChange" />
      </a-form-item>
    </a-form>
    <div class="pick-form-checkbox flex flex-row gap-2 mt-8 text-[12px] color-gray-700">
      <div class="mr-2">
        <div class="mb-2 label-form">
          {{ $t("customization") }}
        </div>
        <a-radio-group v-model:value="formOption.editXPathType" size="small">
          <a-radio v-for="item in formOption.customOptions" :key="item.lable" :value="item.value" class="text-[12px]">
            {{ $t(item.label) }}
          </a-radio>
        </a-radio-group>
      </div>
      <div v-if="formOption.pickType === 'web'" class="mr-2">
        <div class="mb-2 label-form">
          {{ $t("matchingMethod") }}
        </div>
        <a-checkbox-group v-model:value="formOption.matchTypes" size="small" class="flex flex-nowrap" :options="formOption.matchOptions">
          <template #label="{ label, value }">
            <span class="text-[12px]">{{ $t(label) }}</span>
            <a-tooltip placement="top" :title="$t(value)">
              <QuestionCircleOutlined class="ml-1" />
            </a-tooltip>
          </template>
        </a-checkbox-group>
      </div>
    </div>
  </div>
</template>

<style scoped>
.label-form {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.ant-form-item {
  margin-bottom: 10px;
}
.ant-form-item:last-child {
  margin-bottom: 0;
}

.ant-btn-sm {
  font-size: 12px;
}

.form-wrapper {
  height: auto;
  font-size: 12px;
}

.font-small {
  font-size: 12px;
}

.check-select {
  height: 28px;
}

:deep(.ant-select-single .ant-select-selector) {
  height: 28px;
  font-size: 12px;
}

:deep(.ant-select-single.ant-select-sm.ant-select-show-arrow .ant-select-selection-item) {
  font-size: 12px;
}
</style>
