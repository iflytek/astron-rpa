<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { computed, reactive, ref } from 'vue'

import { createAgentAPI, updateAgentApi } from '@/api/setting'

interface FormState {
  name: string
  api_key: string
  api_secret: string
  app_id: string
}

export interface AgentData extends FormState {
  id: number
}

const props = defineProps<{ data?: AgentData }>()

const emit = defineEmits(['refresh'])

function initFormState(): FormState {
  return {
    name: '',
    api_key: '',
    api_secret: '',
    app_id: '',
  }
}

const modal = NiceModal.useModal()

const isUpdate = computed(() => props.data !== undefined)

const formRef = ref<FormInstance>()
const formState = reactive<FormState>(props.data ?? initFormState())

async function handleOk() {
  await formRef.value?.validate()
  await (isUpdate.value ? updateAgentApi(formState) : createAgentAPI(formState))
  modal.hide()
  emit('refresh')
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="starAgentModal"
    :width="400"
    :mask-closable="false"
    :title="isUpdate ? '更新星辰Agent配置' : '创建星辰Agent配置'"
    @ok="handleOk"
  >
    <a-form ref="formRef" :model="formState" autocomplete="off" layout="vertical" class="mt-[16px]">
      <a-form-item label="名称" name="name" required>
        <a-input v-model:value="formState.name" />
      </a-form-item>
      <a-form-item label="App ID" name="app_id" required>
        <a-input v-model:value="formState.app_id" />
      </a-form-item>
      <a-form-item label="Api Key" name="api_key" required>
        <a-input v-model:value="formState.api_key" />
      </a-form-item>
      <a-form-item label="Api Secret" name="api_secret" required>
        <a-input v-model:value="formState.api_secret" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<style lang="scss" scoped>
.starAgentModal {
  .info {
    font-size: 14px;
    line-height: 22px;
    margin-bottom: 12px;
  }
}
</style>
