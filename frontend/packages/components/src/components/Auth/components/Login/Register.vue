<script setup lang="ts">
import { ref, computed } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import ConsultForm from '../Base/Consult/ConsultForm.vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, RegisterFormData, ConsultFormData, InviteInfo } from '../../interface.ts'
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
  submit: [data: RegisterFormData | ConsultFormData, mode: RegisterMode]
  switchToLogin: []
}>()

const personal = useRegisterForm({ inviteInfo, edition, authType }, emit as any)
const consultRef = ref<InstanceType<typeof ConsultForm> | null>(null)

const currentMode = ref('REGISTER')

const headerTitle = computed(() => {
  if(edition === 'saas' && authType === 'uap') {
    return { 
      title: currentMode.value === 'REGISTER' ? '注册讯飞账号' : '咨询',
      actionText: currentMode.value === 'REGISTER' ? '咨询' : '注册讯飞账号'
    }
  }
  if(edition === 'saas' && authType === 'casdoor') {
    return { title: '注册讯飞账号', actionText: '' }
  }
  return { title: '', actionText: '' }
})

const personalLoading = computed(() => running === 'REGISTER')
const enterpriseLoading = computed(() => running === 'CONSULT')

const changeMode = () => {
  const next: RegisterMode = currentMode.value === 'REGISTER' ? 'CONSULT' : 'REGISTER'
  next === 'CONSULT' ? personal.resetForm() : consultRef.value?.resetForm()
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
      class="auth-register-form"
      v-if="currentMode === 'REGISTER' && personal.config"
      :loading="personalLoading"
      :ref="personal.formRef"
      :config="personal.config"
      v-model="personal.formData"
      :handleEvents="personal.handleEvents"
    />

    <ConsultForm
      v-if="currentMode === 'CONSULT'"
      ref="consultRef"
      :loading="enterpriseLoading"
      @submit="(data) => emit('submit', data, 'CONSULT')"
    />
  </FormLayout>
</template>