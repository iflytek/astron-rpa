<script setup lang="ts">import type { ForgotPasswordFormData } from '../../interface'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useForgotPassword } from './hooks/useForgotPassword'

const emit = defineEmits<{
  submit: [data: ForgotPasswordFormData]
  sendCaptcha: [phone: string]
  switchToLogin: []
}>()

const { formRef, formData, config, emitEvent } = useForgotPassword(emit as any)
</script>

<template>
  <FormLayout
    :wrap-class="'auth-forgot-password h-full relative'"
    title="忘记密码"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      :config="config"
      v-model="formData"
      :emitEvent="emitEvent"
      class="auth-forgot-password-form"
    />
  </FormLayout>
</template>
