<script setup lang="ts">
import { computed, PropType } from 'vue'
import type { LoginFormData, AsyncAction } from '../../interface'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useForgotPassword } from './hooks/useForgotPassword'

const { running, sendCaptcha } = defineProps({
  running: { type: String as () => AsyncAction, default: 'IDLE' },
  sendCaptcha: {
    type: Function as PropType<(phone: string) => Promise<void>>,
    default: (phone: string) => Promise.resolve()
  }
})

const emit = defineEmits<{
  submit: [data: LoginFormData]
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
      :send-captcha="sendCaptcha"
      v-model="formData"
      :handleEvents="handleEvents"
      class="auth-forgot-password-form"
    />
  </FormLayout>
</template>
