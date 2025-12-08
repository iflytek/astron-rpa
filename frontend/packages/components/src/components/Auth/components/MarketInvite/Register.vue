<script setup lang="ts">
import InviteFormLayout from '../Base/InviteFormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData } from '../../interface.ts'
import { registerProps } from '../../interface.ts'
 
const props = defineProps(registerProps())
const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  switchToLogin: []
  sendCaptcha: [phone: string]
}>()

const personal = useRegisterForm('personal', emit as any)

</script>

<template>
  <InviteFormLayout :wrap-class="'auth-register h-full !w-full !p-0'">
    <DynamicForm
      :ref="personal.formRef"
      :config="personal.config"
      v-model="personal.formData"
      :emitEvent="personal.emitEvent"
      class="auth-register-personal-form"
    />
  </InviteFormLayout>
</template>