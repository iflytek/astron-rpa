<script setup lang="ts">
import InviteFormLayout from '../Base/InviteFormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { usePhoneLogin } from './hooks/usePhoneLogin'
import type {
  LoginMode,
} from '../../interface'
import { enterpriseInviteProps } from '../../interface'

const props = defineProps(enterpriseInviteProps())
const emit = defineEmits<{
  submit: [data: any, mode: LoginMode]
  sendCode: [phone: string]
  switchToRegister: []
}>()

const phone = usePhoneLogin(emit as any)
</script>

<template>
  <InviteFormLayout
    :wrap-class="'auth-invite h-full'"
    :type="'enterprise'"
    :username="props.inviteInfo.userName"
    :targetName="props.inviteInfo.enterpriseName"
    :show-agreement="true"
  >
    <DynamicForm
      :ref="phone.formRef"
      :config="phone.config"
      v-model="phone.formData"
      :emitEvent="phone.emitEvent"
      class="auth-invite-form"
    />
  </InviteFormLayout>
</template>