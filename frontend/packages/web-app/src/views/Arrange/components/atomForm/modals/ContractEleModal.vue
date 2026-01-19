<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
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
    { required: true, message: '请输入要素名称' },
    { validator: checkDuplicateTaskName, trigger: 'blur' },
  ],
}

async function checkDuplicateTaskName(_rule, value) {
  if (!value)
    return Promise.resolve()
  const idx = props.customData.findIndex(item => item.name === value)
  if (idx > -1 && (!props.isEdit || (props.isEdit && formState.key !== props.customData[idx].key))) {
    return Promise.reject(new Error('要素名称重复，请重新输入名称'))
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
    :title="`${props.isEdit ? '编辑' : '添加'}自定义要素`"
    centered
    @ok="handleOk"
  >
    <a-form ref="formRef" :rules="rules" layout="vertical" :model="formState" autocomplete="off">
      <a-form-item label="要素名称" name="name">
        <a-input v-model:value="formState.name" placeholder="例如：合同期限" />
      </a-form-item>
      <a-form-item label="要素描述">
        <a-textarea v-model:value="formState.desc" placeholder="描述该要素的含义" />
      </a-form-item>
      <a-form-item label="要素示例">
        <a-input v-model:value="formState.example" placeholder="例如：自2023年1月1日起至2025年1月1日" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
