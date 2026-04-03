<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import { rename, renameCheck } from '@/api/project'

interface FormState {
  robotId: string | number
  newName: string
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
  newName: props.robotName,
})

async function handleOk() {
  await formRef.value.validate()

  confirmLoading.value = true

  try {
    await renameCheck(formState)
    await rename(formState)
    modal.hide()
    message.success(t('common.renameSuccess'))
    emit('refresh', formState.newName)
  }
  catch (error) {
    console.error(error)
  }

  confirmLoading.value = false
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('rename')"
    :confirm-loading="confirmLoading"
    :width="400"
    @ok="handleOk"
  >
    <a-form
      ref="formRef"
      :model="formState"
      autocomplete="off"
      layout="vertical"
    >
      <a-form-item
        :label="$t('name')"
        name="newName"
        :rules="[{ required: true, message: t('common.enterPlaceholder', { name: t('name') }) }]"
      >
        <a-input v-model:value="formState.newName" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
