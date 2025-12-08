<script setup lang="ts">
import { ref } from 'vue'
import InviteFormLayout from '../Base/InviteFormLayout.vue'

import Login from './Login.vue'
import Register from './Register.vue'

import { marketInviteProps } from '../../interface'
import type { 
  AccountLoginFormData, 
  LoginMode, 
  PhoneLoginFormData, 
  RegisterFormData, 
  RegisterMode,
} from '../../interface'

const props = defineProps(marketInviteProps())

const emit = defineEmits<{
  login: [data: AccountLoginFormData | PhoneLoginFormData, mode: LoginMode]
  register: [data: RegisterFormData, mode: RegisterMode]
  modeChange: [mode: 'login' | 'register' ]
  loginModeChange: [mode: LoginMode]
  registerModeChange: [mode: RegisterMode]
  sendCode: [phone: string]
}>()

// 当前界面模式
type AuthFormMode = 'login' | 'register'  
const currentFormMode = ref<AuthFormMode>('login')

const handleLogin = async (data: AccountLoginFormData | PhoneLoginFormData, mode: LoginMode) => {
  emit('login', data, mode)
}

const handleRegister = async (data: RegisterFormData, mode: RegisterMode) => {
  emit('register', data, mode)
}

const handleSwitchMode = () => {
  const newMode = currentFormMode.value === 'login' ? 'register' : 'login'
  currentFormMode.value = newMode
  emit('modeChange', newMode)
}
 
const handleSendCode = async (phone: string) => {
  emit('sendCode', phone)
}

</script>

<template>
  <InviteFormLayout
    :wrap-class="'auth-invite h-full'"
    :username="props.inviteInfo.userName"
    :targetName="props.inviteInfo.marketName"
  >
    <Login
      v-if="currentFormMode === 'login'"
      @submit="handleLogin"
      @switch-to-register="handleSwitchMode"
      @send-code="handleSendCode"
    >
    </Login>
    
    <Register
      v-else-if="currentFormMode === 'register'"
      @submit="handleRegister"
      @switch-to-login="handleSwitchMode"
      @send-code="handleSendCode"
    />
  </InviteFormLayout>
 </template>
