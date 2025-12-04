<script setup lang="ts">
import { computed } from 'vue'
import type { LoginFormData, AsyncAction } from '../../interface'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useForgotPassword } from './hooks/useForgotPassword'

const { running } = defineProps({
  running: { type: String as () => AsyncAction, default: 'IDLE' },
})

const emit = defineEmits<{
  submit: [data: LoginFormData]
  sendCaptcha: [phone: string]
  switchToLogin: []
}>()

const loading = computed(() => running === 'SET_PASSWORD')

const { formRef, formData, config, handleEvents } = useForgotPassword(emit as any)
</script>

<template>
  <FormLayout
    :wrap-class="'auth-forgot-password h-full relative'"
    title="找回密码"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      :loading="loading"
      :config="config"
      v-model="formData"
      :handleEvents="handleEvents"
      class="auth-forgot-password-form"
    />
  </FormLayout>
</template>
