<script setup lang="ts">
import { computed } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useModifyPassword } from './hooks/useModifyPassword'
import type { Edition, AuthType, LoginFormData, AsyncAction, InviteInfo } from '../../interface'

const { running, title, inviteInfo } = defineProps({
  title: { 
    type: String, 
    default: '修改密码' 
  },
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
  submit: [data: LoginFormData]
  switchToLogin: []
}>()

const loading = computed(() => running === 'SET_PASSWORD')

const { formRef, formData, config, handleEvents } = useModifyPassword(inviteInfo, emit as any)
</script>

<template>
  <FormLayout
    :wrap-class="'auth-set-password h-full relative'"
    :title="title || '修改密码'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <DynamicForm
      ref="formRef"
      :loading="loading"
      :config="config"
      v-model="formData"
      :handleEvents="handleEvents"
      class="auth-set-password-form"
    />
  </FormLayout>
</template>