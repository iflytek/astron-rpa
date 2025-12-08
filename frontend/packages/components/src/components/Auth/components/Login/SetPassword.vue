<script setup lang="ts">
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useSetPassword } from './hooks/useSetPassword'
import type { SetPasswordFormData } from '../../interface'

const emit = defineEmits<{
  submit: [data: SetPasswordFormData]
  switchToLogin: []
}>()

const { formRef, formData, config, emitEvent } = useSetPassword(emit as any)
</script>

<template>
  <FormLayout
    :wrap-class="'auth-set-password h-full relative'"
    title="设置密码"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      :config="config"
      v-model="formData"
      :emitEvent="emitEvent"
      class="auth-set-password-form"
    />
  </FormLayout>
</template>