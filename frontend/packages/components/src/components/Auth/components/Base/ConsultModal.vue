<script setup lang="ts">
import { ref, watch } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import { Modal } from 'ant-design-vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from '../Login/hooks/useRegisterForm.ts'
import type { RegisterMode, RegisterFormData } from '../../interface.ts'

const { consultTitle, consultEdition, consultType } = defineProps<{
  consultTitle?: string
  consultEdition?: 'professional' | 'enterprise'
  consultType?: 'consult' | 'renewal'
}>()

const emit = defineEmits<{
  submit: [data: RegisterFormData, mode: RegisterMode]
}>()

const visible = ref(false)

const consult = useRegisterForm('ENTERPRISE', { consultEdition, consultType }, emit as any)
const setConsultFormData = () => {
  const result = useRegisterForm('ENTERPRISE', { consultEdition, consultType }, emit as any)
  consult.formRef = result.formRef
  consult.formData = result.formData
  consult.handleEvents = result.handleEvents
  consult.config = result.config
}

watch(() => consultTitle, () => {
  console.log('consultTitle changed', consultTitle)
})
const showModal = () => {
  setConsultFormData()
  visible.value = true
}
const closeModal = () => {
  visible.value = false
}

defineExpose({
  showModal,
  closeModal,
})
</script>

<template>
  <Modal
    :open="visible"
    centered
    class="tenant-modal"
    :width="400"
    :z-index="1099"
    :footer="null"
    @cancel="closeModal"
  >
    <FormLayout :wrap-class="'auth-set-password w-full !h-[460px] relative !px-[16px] !py-[20px] !bg-[transparent]'">
      <template #header>
        <div class="text-[18px] text-[#000000D9] mb-[24px] font-[600] text-center dark:text-[#FFFFFF]">{{ consultTitle || (consultType === 'renewal' ? '续费' : '咨询') }}</div>
      </template>
      <DynamicForm
        v-if="consult && consult?.config"
        :ref="consult.formRef"
        :config="consult.config"
        v-model="consult.formData"
        :handleEvents="consult.handleEvents"
        class="auth-register-enterprise-form"
      />
    </FormLayout>
  </Modal>
</template>