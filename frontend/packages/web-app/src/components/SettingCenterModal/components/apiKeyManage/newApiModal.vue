<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import { createAPI } from '@/api/setting'
import { clipboardManager } from '@/platform'
import type { FormRules } from '@/types/common'

const emit = defineEmits(['refresh'])

interface FormState {
  keyName: string
}

const modal = NiceModal.useModal()
const { t } = useTranslation()

const apiStr = ref('')
const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  keyName: '',
})
const rules: FormRules = {
  keyName: [
    { required: true, message: t('settingCenter.apiKeyManage.enterApiKeyName'), trigger: 'change' },
    {
      max: 20,
      message: t('donotExceedCharacters', { num: 20 }),
      trigger: 'change',
    },
  ],
}

function handleCancel() {
  modal.hide()
  apiStr.value && emit('refresh')
}

async function handleRightBtnClick() {
  if (apiStr.value) {
    clipboardManager.writeClipboardText(apiStr.value)
    message.success(t('copySuccess'))
    return
  }
  await formRef.value?.validate()
  const data = await createAPI({ name: formState.keyName })
  apiStr.value = data.api_key
}
</script>

<template>
  <a-modal
    :open="modal.visible"
    class="newApiModal"
    :z-index="101"
    :width="400"
    :mask-closable="false"
    :title="$t('settingCenter.apiKeyManage.createApiKeyTitle')"
    :after-close="modal.remove"
    @cancel="handleCancel"
  >
    <a-form ref="formRef" :model="formState" :rules="rules" autocomplete="off" layout="vertical" class="mt-[16px]">
      <a-form-item :label="$t('settingCenter.apiKeyManage.name')" name="keyName">
        <a-input v-if="!apiStr" v-model:value="formState.keyName" :placeholder="$t('settingCenter.apiKeyManage.enterApiKeyName')" />
        <div v-else>
          <a-input v-model:value="apiStr" readonly />
          <div class="info mt-[8px] py-[8px] px-[12px] rounded-[12px] bg-[rgba(0,0,0,0.04)] dark:bg-[rgba(255,255,255,0.04)]">
            {{ $t('settingCenter.apiKeyManage.apiKeyInfo') }}
          </div>
        </div>
      </a-form-item>
    </a-form>
    <template #footer>
      <a-button @click="handleCancel">
        {{ apiStr ? $t('settingCenter.apiKeyManage.close') : $t('common.cancel') }}
      </a-button>
      <a-button type="primary" @click="handleRightBtnClick">
        {{ apiStr ? $t('settingCenter.apiKeyManage.copy') : $t('settingCenter.apiKeyManage.create') }}
      </a-button>
    </template>
  </a-modal>
</template>

<style lang="scss" scoped>
.newApiModal {
  .info {
    font-size: 14px;
    line-height: 22px;
    margin-bottom: 12px;
  }
}
</style>
