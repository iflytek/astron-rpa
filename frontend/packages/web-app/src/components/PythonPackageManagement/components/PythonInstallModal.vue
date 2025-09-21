<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { useInstallPython } from '../hooks/useInstallPython'
import { useManagePython } from '../hooks/useManagePython'

const modal = NiceModal.useModal()
const { t } = useTranslation()
const { pacakgeOption, pacakgeConfig, rules } = useInstallPython()
const { installPackage } = useManagePython()

const ruleFormRef = ref<FormInstance>(null)

function handleOkConfirm() {
  ruleFormRef.value.validate().then(() => {
    installPackage(pacakgeOption.value)
  })
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="t('newPythonPackage')"
    :ok-text="t('install')"
    :cancel-text="t('cancel')"
    @ok="handleOkConfirm"
  >
    <div
      class="h-8 rounded-md mb-4 mt-4 pl-3 text-[12px] bg-[rgba(255,251,230,1)] dark:bg-[rgba(43,33,17,1)]
      text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.65)] flex items-center"
    >
      <rpa-icon name="python-install-warn" class="mr-1" />
      {{ $t('installPyPackageInfo') }}
    </div>
    <a-form
      ref="ruleFormRef"
      layout="vertical"
      :rules="rules"
      :model="pacakgeOption"
    >
      <a-form-item
        v-for="(item, index) in pacakgeConfig"
        :key="index"
        :name="item.key"
        :label="item.label"
        class="mb-4"
      >
        <a-input
          v-if="item.type === 'input'"
          v-model:value="pacakgeOption[item.key]"
          :placeholder="item.placeholder"
        />
        <a-textarea
          v-if="item.type === 'textarea'"
          v-model:value="pacakgeOption[item.key]"
          :placeholder="item.placeholder"
          :rows="4"
        />
        <a-select
          v-if="item.type === 'select'"
          v-model:value="pacakgeOption[item.key]"
          style="width: 100%"
          :dropdown-style="{ fontSize: '12px' }"
          :placeholder="item.placeholder"
        >
          <a-select-option
            v-for="option in item.options"
            :key="option.value"
            :value="option.value"
          >
            {{ option.value }}
          </a-select-option>
        </a-select>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<style lang="scss" scoped>
.pythonDependence-modal {
  .ant-modal {
    width: 400px !important;

    .ant-modal-body {
      padding-bottom: 0;
    }
  }
}
:deep(.ant-input),
:deep(.ant-form-item-explain-error),
:deep(.ant-select-selection-item),
:deep(.ant-form-item-label > label) {
  font-size: 12px;
}
</style>
