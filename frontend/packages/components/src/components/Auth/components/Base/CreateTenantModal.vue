<script setup lang="ts">
import { ref } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import { Modal } from 'ant-design-vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from '../Login/hooks/useRegisterForm.ts'
import type { RegisterMode, RegisterFormData } from '../../interface.ts'

const visible = ref(false)

const emit = defineEmits<{
  submit: [data: RegisterFormData, mode: RegisterMode]
}>()

const enterprise = useRegisterForm('ENTERPRISE', null, emit as any)

const showModal = () => {
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
        <div class="text-[18px] text-[#000000D9] mb-[24px] font-[600] text-center dark:text-[#FFFFFF]">申请创建新的工作空间</div>
      </template>
      <DynamicForm
        :ref="enterprise.formRef"
        :config="enterprise.config"
        v-model="enterprise.formData"
        :handleEvents="enterprise.handleEvents"
        class="auth-register-enterprise-form"
      />
    </FormLayout>
  </Modal>
</template>