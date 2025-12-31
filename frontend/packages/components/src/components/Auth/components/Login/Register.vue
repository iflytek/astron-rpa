<script setup lang="ts">
import { computed, ref } from 'vue'

import type { AsyncAction, AuthType, ConsultFormData, Edition, InviteInfo, RegisterFormData, RegisterMode } from '../../interface.ts'
import ConsultForm from '../Base/Consult/ConsultForm.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import FormLayout from '../Base/FormLayout.vue'

import { useRegisterForm } from './hooks/useRegisterForm.ts'

const { running, inviteInfo, edition, authType } = defineProps({
  running: {
    type: String as () => AsyncAction,
    default: 'IDLE',
  },
  inviteInfo: {
    type: Object as () => InviteInfo,
    default: () => null,
  },
  edition: {
    type: String as () => Edition,
    default: 'saas',
  },
  authType: {
    type: String as () => AuthType,
    default: 'uap',
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
  if (edition === 'saas' && authType === 'uap') {
    return {
      title: currentMode.value === 'REGISTER' ? '注册讯飞账号' : '咨询',
      actionText: currentMode.value === 'REGISTER' ? '咨询' : '注册讯飞账号',
    }
  }
  if (edition === 'saas' && authType === 'casdoor') {
    return { title: '注册讯飞账号', actionText: '' }
  }
  return { title: '', actionText: '' }
})

const personalLoading = computed(() => running === 'REGISTER')
const enterpriseLoading = computed(() => running === 'CONSULT')

function changeMode() {
  const next: RegisterMode = currentMode.value === 'REGISTER' ? 'CONSULT' : 'REGISTER'
  next === 'CONSULT' ? personal.resetForm() : consultRef.value?.resetForm()
  currentMode.value = next
}
</script>

<template>
  <FormLayout
    wrap-class="auth-register h-full"
    :title="headerTitle.title"
    :action-text="headerTitle.actionText"
    show-back
    @action="changeMode"
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      v-if="currentMode === 'REGISTER' && personal.config"
      :ref="personal.formRef"
      v-model="personal.formData"
      class="auth-register-form"
      :loading="personalLoading"
      :config="personal.config"
      :handle-events="personal.handleEvents"
    />

    <ConsultForm
      v-if="currentMode === 'CONSULT'"
      ref="consultRef"
      :loading="enterpriseLoading"
      @submit="(data) => emit('submit', data, 'CONSULT')"
    />
  </FormLayout>
</template>
