<script setup>
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { onMounted, reactive, ref } from 'vue'

import { getTaskQueueConfig, updateTaskQueueConfig } from '@/api/task'

const emit = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { t } = useTranslation()
const queueRef = ref(null)
const queueConfig = reactive({
  max_length: 500,
  max_wait_minutes: 0,
  deduplicate: false,
})

const queueRules = {
  max_length: [
    {
      required: true,
      message: t('queueMaxLengthPlaceholder'),
      trigger: 'blur',
    },
  ],
  max_wait_minutes: [
    { required: true, message: t('queueWaitTimePlaceholder'), trigger: 'blur' },
  ],
}

async function okHandle() {
  await queueRef.value.validate()
  await updateTaskQueueConfig(queueConfig)
  emit('ok', queueConfig)
  modal.hide()
}

async function fetchQueueConfig() {
  const res = await getTaskQueueConfig()
  Object.assign(queueConfig, res.data)
}

onMounted(() => fetchQueueConfig())
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="queueConfigModal"
    :width="400"
    :title="t('queueSetting')"
    :mask-closable="false"
    @ok="okHandle"
  >
    <a-form
      ref="queueRef"
      :rules="queueRules"
      :model="queueConfig"
      layout="vertical"
    >
      <a-form-item name="max_length">
        <template #label>
          {{ t("queueMaxLength") }}
          <a-tooltip :title="t('queueMaxLengthTip')">
            <QuestionCircleOutlined class="ml-1" />
          </a-tooltip>
        </template>
        <a-input-number
          v-model:value="queueConfig.max_length"
          :controls="false"
          class="w-full"
          :min="0"
          :max="500"
        />
      </a-form-item>

      <a-form-item name="max_wait_minutes" class="relative">
        <template #label>
          {{ t("queueWaitTime") }}
          <a-tooltip :title="t('queueWaitTimeTip')">
            <QuestionCircleOutlined class="ml-1" />
          </a-tooltip>
        </template>
        <a-input-number
          v-model:value="queueConfig.max_wait_minutes"
          :controls="false"
          class="w-full"
          :min="0"
          :max="99999"
        />
        <div class="unit">
          {{ t("minutes") }}
        </div>
      </a-form-item>

      <div class="form-item flex items-center">
        <a-checkbox
          v-model:checked="queueConfig.deduplicate"
          class="deduplicate"
        >
          {{ t("queueTasksUniq") }}
        </a-checkbox>
        <a-tooltip :title="t('queueTasksUniqTip')">
          <QuestionCircleOutlined class="ml-1" />
        </a-tooltip>
      </div>
    </a-form>
  </a-modal>
</template>

<style lang="scss" scoped>
.queueConfigModal {
  .deduplicate {
    margin-left: 0px;
  }
  .unit {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
  }
}
</style>
