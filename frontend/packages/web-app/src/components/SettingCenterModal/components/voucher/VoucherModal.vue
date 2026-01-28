<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { reactive, ref } from 'vue'

import { checkCredentialExists, createCredential } from '@/api/engine'

interface FormState {
  name: string
  password: string
}

const emit = defineEmits(['refresh'])

const modal = NiceModal.useModal()

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({ name: '', password: '' })

async function validateVoucherName(_rule: Rule, value: string) {
  if (!value) {
    return Promise.resolve()
  }
  const exists = await checkCredentialExists(value)
  if (exists) {
    return Promise.reject(new Error('凭证名称已存在'))
  }
  return Promise.resolve()
}

async function handleOk() {
  await formRef.value?.validate()
  await createCredential(formState)
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
    :title="$t('settingCenter.voucherManage.createVoucher')"
    @ok="handleOk"
  >
    <a-form
      ref="formRef"
      :model="formState"
      autocomplete="off"
      layout="vertical"
      class="mt-[16px]"
    >
      <a-form-item
        :label="$t('voucherName')"
        name="name"
        :rules="[
          { required: true, trigger: 'change' },
          { validator: validateVoucherName, trigger: 'blur' },
        ]"
      >
        <a-input
          v-model:value="formState.name"
          :placeholder="
            $t('common.enterPlaceholder', { name: $t('voucherName') })
          "
        />
      </a-form-item>
      <a-form-item :label="$t('password')" name="password" required>
        <a-input
          v-model:value="formState.password"
          type="password"
          :placeholder="$t('common.enterPlaceholder', { name: $t('password') })"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
