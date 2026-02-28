<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import { createCopy } from '@/api/project'

interface FormState {
  robotId: string | number
  robotName: string
}

const props = defineProps<{
  robotId: string | number
  robotName: string
}>()

const emit = defineEmits(['refresh'])

const modal = NiceModal.useModal()
const confirmLoading = ref(false)
const { t } = useTranslation()

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  robotId: props.robotId,
  robotName: `${props.robotName}${t('copySuffix')}`,
})

async function handleOk() {
  formRef.value.validate().then(() => {
    confirmLoading.value = true
    createCopy(formState).then(() => {
      confirmLoading.value = false
      message.success(t('createCopySuccess'))
      emit('refresh')
      modal.hide()
    }).finally(() => {
      confirmLoading.value = false
    })
  })
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('createCopy')"
    :confirm-loading="confirmLoading"
    :width="400"
    @ok="handleOk"
  >
    <a-form ref="formRef" :model="formState" layout="vertical" autocomplete="off">
      <a-form-item
        :label="$t('name')"
        name="robotName"
        required
      >
        <a-input v-model:value="formState.robotName" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
