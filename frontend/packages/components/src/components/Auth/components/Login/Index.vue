<script setup lang="ts">
import { ref } from 'vue'

import Login from './Login.vue'
import Register from './Register.vue'
import ForgotPassword from './ForgotPassword.vue'
import SetPassword from './SetPassword.vue'
import TenantSelect from './TenantSelect.vue'
import TenantDropdown from './TenantDropdown.vue'
import type { 
  LoginFormData, 
  LoginMode, 
  RegisterFormData, 
  RegisterMode,
  ForgotPasswordFormData,
  SetPasswordFormData,
  TenantItem
} from '../../interface'
import { authFormProps } from '../../interface'
import { loginStatus, login, register, sendCaptcha, forgotPassword, setPassword, chooseTenant } from '../../api/login'
import { message } from 'ant-design-vue'

const props = defineProps(authFormProps())

const emit = defineEmits<{
  login: [data: LoginFormData, mode: LoginMode]
  register: [data: RegisterFormData, mode: RegisterMode]
  sendCaptcha: [phone: string]
  forgotPassword: [data: ForgotPasswordFormData]
  setPassword: [data: SetPasswordFormData]
  chooseTenant: [tenantId: string]
}>()

// 当前界面模式
type AuthFormMode = 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect'
const currentFormMode = ref<AuthFormMode>('login')
const tenants = ref<TenantItem[]>([
  {
    id: '1',
    name: '星辰科技',
    type: 1,
  },
  {
    id: '2', 
    name: '智能自动化部',
    type: 0,
  },
  {
    id: '3',
    name: '产品研发中心',
    type: 0,
  },
  {
    id: '4',
    name: '匡瑞珂的个人空间',
    type: 0,
  }
])

const checkLoginStatus = async () => {
  const status = await loginStatus()
  if (status) {
    currentFormMode.value = 'tenantSelect'
  } else {
    currentFormMode.value = 'login'
  }
}

const handleLogin = async (data: LoginFormData, mode: LoginMode) => {
  emit('login', data, mode)
  // 登录成功后切换到租户选择界面
  handleSwitchMode('tenantSelect')
}

const handleRegister = async (data: RegisterFormData, mode: RegisterMode) => {
  emit('register', data, mode)
}

const handleSwitchMode = (mode: AuthFormMode) => {
  currentFormMode.value = mode
}

const handleForgotPassword = async (data: ForgotPasswordFormData) => {

  emit('forgotPassword', data)
}

const handleSetPassword = async (data: SetPasswordFormData) => {
  emit('setPassword', data)
  await setPassword(data)
  handleSwitchMode('tenantSelect')
}

const chooseTenant = async (tenantId: string) => {
  emit('chooseTenant', tenantId)
}

const handleSendCode = async (phone: string) => {
  await sendCaptcha({ phone })
  message.success('验证码已发送')
  emit('sendCaptcha', phone)
}

// checkLoginStatus()
</script>

<template>
  <div class="auth-container-content h-[540px]">    
    <TenantDropdown
      :tenants="tenants"
      :selected-tenant="tenants[0]"
    />

    <Login
      v-if="currentFormMode === 'login'"
      @submit="handleLogin"
      @switch-to-register="() => handleSwitchMode('register')"
      @forget-password="() => handleSwitchMode('forgotPassword')"
      @send-captcha="handleSendCode"
    >
    </Login>

    <Register
      v-else-if="currentFormMode === 'register'"
      @submit="handleRegister"
      @switch-to-login="() => handleSwitchMode('login')"
      @send-captcha="handleSendCode"
    />

    <ForgotPassword
      v-else-if="currentFormMode === 'forgotPassword'"
      @submit="handleForgotPassword"
      @send-captcha="handleSendCode"
      @switch-to-login="() => handleSwitchMode('login')"
    />

    <SetPassword
      v-else-if="currentFormMode === 'setPassword'"
      @submit="handleSetPassword"
      @switch-to-login="() => handleSwitchMode('login')"
    />

    <TenantSelect
      v-else-if="currentFormMode === 'tenantSelect'"
      :tenants="tenants"
      @submit="chooseTenant"
      @switch-to-login="() => handleSwitchMode('login')"
    />
  </div>
</template>
