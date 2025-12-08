<script setup lang="ts">
import { ref } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData } from '../../interface.ts'
import { registerProps } from '../../interface.ts'
 
const props = defineProps(registerProps())
const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  switchToLogin: []
  sendCode: [phone: string]
}>()

const personal = useRegisterForm('personal', emit as any)
const enterprise = useRegisterForm('enterprise', emit as any)

const currentMode = ref<RegisterMode>('personal')

const changeMode = () => {
  const next: RegisterMode = currentMode.value === 'personal' ? 'enterprise' : 'personal'
  next === 'enterprise' ? personal.resetForm() : enterprise.resetForm()
  console.log('dddd')
  currentMode.value = next
}

</script>

<template>
  <FormLayout
    :wrap-class="'auth-register h-full'"
    :title="currentMode === 'personal' ? '注册个人版' : '申请开通企业版'"
    :action-text="currentMode === 'personal' ? '申请开通企业版' : '注册个人版'"
    @action="changeMode"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      v-if="currentMode === 'personal'"
      :ref="personal.formRef"
      :config="personal.config"
      v-model="personal.formData"
      :emitEvent="personal.emitEvent"
      class="auth-register-personal-form"
    />

    <DynamicForm
      v-if="currentMode === 'enterprise'"
      :ref="enterprise.formRef"
      :config="enterprise.config"
      v-model="enterprise.formData"
      :emitEvent="enterprise.emitEvent"
      class="auth-register-enterprise-form"
    />
  </FormLayout>
</template>