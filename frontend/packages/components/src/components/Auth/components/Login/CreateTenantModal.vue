<script setup lang="ts">
import { ref } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import { Modal } from 'ant-design-vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData } from '../../interface.ts'
import { registerProps } from '../../interface.ts'
 
const props = defineProps({
  ...registerProps(),
  showModal: true as any,
})

const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  sendCaptcha: [phone: string]
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
  <Modal
    :open="showModal"
    centered
    title="创建新工作空间"
    class="tenant-modal"
    :z-index="19"
    :footer="null"
  >
    <FormLayout :wrap-class="'auth-set-password h-full relative'">
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
  </Modal>
</template>
