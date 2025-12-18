<script setup lang="ts">
import { ref, computed } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData, InviteInfo } from '../../interface.ts'
import { AsyncAction } from '../../interface.ts'
 
const { running, inviteInfo } = defineProps({
  running: { type: String as () => AsyncAction, default: 'IDLE' },
  inviteInfo: { 
    type: Object as () => InviteInfo, 
    default: () => null 
  },
})

const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  switchToLogin: []
}>()

const personal = useRegisterForm('PERSONAL', inviteInfo, emit as any)
const enterprise = useRegisterForm('ENTERPRISE', inviteInfo, emit as any)

const currentMode = ref<RegisterMode>('PERSONAL')

const personalLoading = computed(() => running === 'PERSONAL')
const enterpriseLoading = computed(() => running === 'ENTERPRISE')

const changeMode = () => {
  const next: RegisterMode = currentMode.value === 'PERSONAL' ? 'ENTERPRISE' : 'PERSONAL'
  next === 'ENTERPRISE' ? personal.resetForm() : enterprise.resetForm()
  currentMode.value = next
}

</script>

<template>
  <!--TODO 企业版 :title="currentMode === 'PERSONAL' ? '注册讯飞账号' : '咨询企业版'" -->
  <!--TODO 企业版 :action-text="currentMode === 'PERSONAL' ? '咨询企业版' : '注册讯飞账号'" -->
  <FormLayout
    :wrap-class="'auth-register h-full'"
    :title="'注册讯飞账号'"
    @action="changeMode"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      class="auth-register-personal-form"
      v-if="currentMode === 'PERSONAL'"
      :loading="personalLoading"
      :ref="personal.formRef"
      :config="personal.config"
      v-model="personal.formData"
      :handleEvents="personal.handleEvents"
    />

    <DynamicForm
      class="auth-register-enterprise-form"
      v-if="currentMode === 'ENTERPRISE'"
      :loading="enterpriseLoading"
      :ref="enterprise.formRef"
      :config="enterprise.config"
      v-model="enterprise.formData"
      :handleEvents="enterprise.handleEvents"
    />
  </FormLayout>
</template>