<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import { createAPI } from '@/api/setting'
import { clipboardManager } from '@/platform'
import type { FormRules } from '@/types/common'
import type { resOption } from '@/views/Home/types'

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
    { required: true, message: '请输入API key的名称', trigger: 'change' },
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

function handleRightBtnClick() {
  if (apiStr.value) {
    clipboardManager.writeClipboardText(apiStr.value)
    message.success('复制成功')
    return
  }
  formRef.value?.validate().then(() => {
    createAPI({ name: formState.keyName }).then((res: resOption) => {
      apiStr.value = res.data.api_key
    })
  })
}
</script>

<template>
  <a-modal
    :open="modal.visible"
    class="newApiModal"
    :z-index="101"
    :width="400"
    :mask-closable="false"
    title="创建 API Key"
    :after-close="modal.remove"
    @cancel="handleCancel"
  >
    <a-form ref="formRef" :model="formState" :rules="rules" autocomplete="off" layout="vertical" class="mt-[16px]">
      <a-form-item label="名称" name="keyName">
        <a-input v-if="!apiStr" v-model:value="formState.keyName" placeholder="请输入API key的名称" />
        <div v-else>
          <a-input v-model:value="apiStr" readonly />
          <div class="info mt-[8px] py-[8px] px-[12px] rounded-[12px] bg-[rgba(0,0,0,0.04)] dark:bg-[rgba(255,255,255,0.04)]">
            请将此API key保存在安全且易于访问的地方。出于安全原因，即将无法通过API keys管理界面再次查看它。如果你丢失了这个key，将需要重新创建。
          </div>
        </div>
      </a-form-item>
    </a-form>
    <template #footer>
      <a-button @click="handleCancel">
        {{ apiStr ? '关闭' : '取消' }}
      </a-button>
      <a-button type="primary" @click="handleRightBtnClick">
        {{ apiStr ? '复制' : '创建' }}
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
