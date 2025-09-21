<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
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
    message.success('重命名成功')
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
        label="名称"
        name="newName"
        :rules="[{ required: true, message: '请输入名称' }]"
      >
        <a-input v-model:value="formState.newName" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
