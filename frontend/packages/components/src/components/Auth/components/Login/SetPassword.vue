<script setup lang="ts">
import { computed } from 'vue'

import type { AsyncAction, InviteInfo, LoginFormData } from '../../interface'
import DynamicForm from '../Base/DynamicForm.vue'
import FormLayout from '../Base/FormLayout.vue'

import { useSetPassword } from './hooks/useSetPassword'

const { running, title, inviteInfo } = defineProps({
  title: { type: String, default: '设置密码' },
  running: { type: String as () => AsyncAction, default: 'IDLE' },
  inviteInfo: {
    type: Object as () => InviteInfo,
    default: () => null,
  },
})

const emit = defineEmits<{
  submit: [data: LoginFormData]
  switchToLogin: []
}>()

const loading = computed(() => running === 'SET_PASSWORD')

const { formRef, formData, config, handleEvents } = useSetPassword(inviteInfo, emit as any)
</script>

<template>
  <FormLayout
    wrap-class="auth-set-password h-full relative"
    :title="title || '设置密码'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      v-model="formData"
      :loading="loading"
      :config="config"
      :handle-events="handleEvents"
      class="auth-set-password-form"
    />
  </FormLayout>
</template>
