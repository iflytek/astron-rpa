<script setup lang="ts">
import { computed } from 'vue'

import type { AsyncAction, LoginFormData } from '../../interface'
import DynamicForm from '../Base/DynamicForm.vue'
import FormLayout from '../Base/FormLayout.vue'

import { useForgotPassword } from './hooks/useForgotPassword'

const { title, running } = defineProps({
  title: { type: String, default: '找回密码' },
  running: { type: String as () => AsyncAction, default: 'IDLE' },
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
    wrap-class="auth-forgot-password h-full relative"
    :title="title || '找回密码'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      v-model="formData"
      :loading="loading"
      :config="config"
      :handle-events="handleEvents"
      class="auth-forgot-password-form"
    />
  </FormLayout>
</template>
