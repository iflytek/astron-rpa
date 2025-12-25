<script setup lang="ts">
import { ref, computed } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData, InviteInfo } from '../../interface.ts'
import { Edition, AuthType, AsyncAction } from '../../interface.ts'

const { running, inviteInfo, edition, authType } = defineProps({
  running: { 
    type: String as () => AsyncAction, 
    default: 'IDLE' 
  },
  inviteInfo: { 
    type: Object as () => InviteInfo, 
    default: () => null 
  },
  edition: { 
    type: String as () => Edition, 
    default: 'saas' 
  },
  authType: { 
    type: String as () => AuthType, 
    default: 'uap' 
  },
})

const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  switchToLogin: []
}>()

const personal = useRegisterForm('PERSONAL', { inviteInfo, edition, authType }, emit as any)
const enterprise = useRegisterForm('ENTERPRISE', { inviteInfo, edition, authType }, emit as any)

const currentMode = ref<RegisterMode>('PERSONAL')

const headerTitle = computed(() => {
  if(edition === 'saas' && authType === 'uap') {
    return { 
      title: currentMode.value === 'PERSONAL' ? '注册讯飞账号' : '咨询企业版',
      actionText: currentMode.value === 'PERSONAL' ? '咨询企业版' : '注册讯飞账号'
    }
  }
  if(edition === 'saas' && authType === 'casdoor') {
    return { title: '注册讯飞账号', actionText: '' }
  }
  return { title: '', actionText: '' }
})

const personalLoading = computed(() => running === 'PERSONAL')
const enterpriseLoading = computed(() => running === 'ENTERPRISE')

const changeMode = () => {
  const next: RegisterMode = currentMode.value === 'PERSONAL' ? 'ENTERPRISE' : 'PERSONAL'
  next === 'ENTERPRISE' ? personal.resetForm() : enterprise.resetForm()
  currentMode.value = next
}

</script>

<template>
  <FormLayout
    :wrap-class="'auth-register h-full'"
    :title="headerTitle.title"
    :action-text="headerTitle.actionText"
    @action="changeMode"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      class="auth-register-personal-form"
      v-if="currentMode === 'PERSONAL' && personal.config"
      :loading="personalLoading"
      :ref="personal.formRef"
      :config="personal.config"
      v-model="personal.formData"
      :handleEvents="personal.handleEvents"
    />

    <DynamicForm
      class="auth-register-enterprise-form"
      v-if="currentMode === 'ENTERPRISE' && enterprise.config"
      :loading="enterpriseLoading"
      :ref="enterprise.formRef"
      :config="enterprise.config"
      v-model="enterprise.formData"
      :handleEvents="enterprise.handleEvents"
    />
  </FormLayout>
</template>