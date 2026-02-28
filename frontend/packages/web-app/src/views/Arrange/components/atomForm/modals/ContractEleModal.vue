<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { nanoid } from 'nanoid'
import { reactive, ref } from 'vue'

import type { FormRules } from '@/types/common'

const props = defineProps<{
  isEdit: boolean
  record?: FormState
  customData: Array<FormState>
}>()

const emits = defineEmits(['ok'])

interface FormState {
  key: string
  name: string
  desc: string
  example: string
}

const { t } = useTranslation()
const modal = NiceModal.useModal()
const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  key: props.record?.key || nanoid(),
  name: props.record?.name || '',
  desc: props.record?.desc || '',
  example: props.record?.example || '',
})

const rules: FormRules = {
  name: [
    { required: true, message: t('contractEle.enterName') },
    { validator: checkDuplicateTaskName, trigger: 'blur' },
  ],
}

async function checkDuplicateTaskName(_rule, value) {
  if (!value)
    return Promise.resolve()
  const idx = props.customData.findIndex(item => item.name === value)
  if (idx > -1 && (!props.isEdit || (props.isEdit && formState.key !== props.customData[idx].key))) {
    return Promise.reject(new Error(t('contractEle.duplicateName')))
  }
  return Promise.resolve()
}

function handleOk() {
  formRef.value.validate().then(() => {
    emits('ok', formState)
    modal.hide()
  })
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :width="500"
    :title="props.isEdit ? t('contractEle.editCustomElement') : t('contractEle.addCustomElement')"
    centered
    @ok="handleOk"
  >
    <a-form ref="formRef" :rules="rules" layout="vertical" :model="formState" autocomplete="off">
      <a-form-item :label="$t('contractEle.elementName')" name="name">
        <a-input v-model:value="formState.name" :placeholder="$t('contractEle.namePlaceholder')" />
      </a-form-item>
      <a-form-item :label="$t('contractEle.elementDesc')">
        <a-textarea v-model:value="formState.desc" :placeholder="$t('contractEle.descPlaceholder')" />
      </a-form-item>
      <a-form-item :label="$t('contractEle.elementExample')">
        <a-input v-model:value="formState.example" :placeholder="$t('contractEle.examplePlaceholder')" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
