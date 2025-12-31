<script setup lang="ts">
import { computed } from 'vue'

import type { AsyncAction, AuthType, Edition, InviteInfo, LoginFormData } from '../../interface'
import DynamicForm from '../Base/DynamicForm.vue'
import FormLayout from '../Base/FormLayout.vue'

import { useModifyPassword } from './hooks/useModifyPassword'

const { running, title, inviteInfo } = defineProps({
  title: {
    type: String,
    default: '修改密码',
  },
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
  submit: [data: LoginFormData]
  switchToLogin: []
}>()

const loading = computed(() => running === 'SET_PASSWORD')

const { formRef, formData, config, handleEvents } = useModifyPassword(inviteInfo, emit as any)
</script>

<template>
  <FormLayout
    wrap-class="auth-modify-password h-full relative"
    :title="title || '修改密码'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      v-model="formData"
      :loading="loading"
      :config="config"
      :handle-events="handleEvents"
      class="auth-modify-form"
    />
  </FormLayout>
</template>
