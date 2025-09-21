<script setup lang="ts">
import { ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import type { FormRules } from '@/types/common'

interface FormState {
  imgName: string
}

const { name } = defineProps<{ name: string }>()
const emit = defineEmits(['confirm'])

const modal = NiceModal.useModal()
const { t } = useTranslation()
const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  imgName: name || '',
})
const rules: FormRules = {
  groupName: [
    { required: true, message: '请输入分组名称', trigger: 'change' },
    {
      max: 20,
      message: t('donotExceedCharacters', { num: 20 }),
      trigger: 'change',
    },
  ],
}

async function handleOk() {
  formRef.value.validate().then((valid) => {
    if (valid) {
      emit('confirm', formState.imgName)
      modal.hide()
    }
  })
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :ok-text="t('confirm')"
    :cancel-text="t('cancel')"
    title="图像名称"
    :width="500"
    @ok="handleOk"
  >
    <span class="rename">
      <ExclamationCircleOutlined style="color: #ffc107; margin-right: 3px" />
      上传图像名称与图像库中的图像名称重复，请重新命名
    </span>
    <a-form
      ref="formRef"
      :model="formState"
      :rules="rules"
      :label-col="{ span: 4 }"
      :wrapper-col="{ span: 20 }"
      autocomplete="off"
    >
      <a-form-item
        name="name"
        label="名称"
        class="!mb-0"
        style="margin-bottom: 10px"
      >
        <a-input
          v-model:value="formState.imgName"
          placeholder="请输入图像名称"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
