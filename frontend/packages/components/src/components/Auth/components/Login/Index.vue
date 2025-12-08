<script setup lang="ts">
import { ref } from 'vue'

import Login from './Login.vue'
import Register from './Register.vue'
import ForgotPassword from './ForgotPassword.vue'
import SetPassword from './SetPassword.vue'
import TenantSelect from './TenantSelect.vue'
import type { 
  AccountLoginFormData, 
  LoginMode, 
  PhoneLoginFormData, 
  RegisterFormData, 
  RegisterMode,
  ForgotPasswordFormData,
  SetPasswordFormData,
  TenantItem
} from '../../interface'
import { authFormProps } from '../../interface'

const props = defineProps(authFormProps())

const emit = defineEmits<{
  login: [data: AccountLoginFormData | PhoneLoginFormData, mode: LoginMode]
  register: [data: RegisterFormData, mode: RegisterMode]
  modeChange: [mode: 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect']
  loginModeChange: [mode: LoginMode]
  registerModeChange: [mode: RegisterMode]
  sendCode: [phone: string]
  forgotPassword: [data: ForgotPasswordFormData]
  setPassword: [data: SetPasswordFormData]
  tenantSelect: [tenantId: string]
}>()

// 当前界面模式
type AuthFormMode = 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect'
const currentFormMode = ref<AuthFormMode>('login')
const currentLoginMode = ref<LoginMode>(props.loginMode)
const currentRegisterMode = ref<RegisterMode>(props.registerMode)

// 租户数据 - 实际使用时应该从外部传入
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

const handleLogin = async (data: AccountLoginFormData | PhoneLoginFormData, mode: LoginMode) => {
  emit('login', data, mode)
  // 登录成功后切换到租户选择界面
  currentFormMode.value = 'tenantSelect'
  emit('modeChange', 'tenantSelect')
}

const handleRegister = async (data: RegisterFormData, mode: RegisterMode) => {
  emit('register', data, mode)
}

const handleSwitchMode = () => {
  const newMode = currentFormMode.value === 'login' ? 'register' : 'login'
  currentFormMode.value = newMode
  emit('modeChange', newMode)
}

// 切换到忘记密码界面
const handleSwitchToForgotPassword = () => {
  currentFormMode.value = 'forgotPassword'
  emit('modeChange', 'forgotPassword')
}

// 切换到设置密码界面
const handleSwitchToSetPassword = () => {
  currentFormMode.value = 'setPassword'
  emit('modeChange', 'setPassword')
}

// 切换到租户选择界面
const handleSwitchToTenantSelect = () => {
  currentFormMode.value = 'tenantSelect'
  emit('modeChange', 'tenantSelect')
}

// 切换到登录界面
const handleSwitchToLogin = () => {
  currentFormMode.value = 'login'
  emit('modeChange', 'login')
}

// 忘记密码表单提交
const handleForgotPassword = async (data: ForgotPasswordFormData) => {
  emit('forgotPassword', data)
  // 验证通过后切换到设置密码界面
  handleSwitchToSetPassword()
}

// 设置密码表单提交
const handleSetPassword = async (data: SetPasswordFormData) => {
  emit('setPassword', data)
  // 设置成功后切换到租户选择界面
  handleSwitchToTenantSelect()
}

// 租户选择表单提交
const handleTenantSelect = async (tenantId: string) => {
  emit('tenantSelect', tenantId)
}

const handleLoginModeChange = (mode: LoginMode) => {
  currentLoginMode.value = mode
  emit('loginModeChange', mode)
}

const handleRegisterModeChange = (mode: RegisterMode) => {
  currentRegisterMode.value = mode
  emit('registerModeChange', mode)
}

const handleSendCode = async (phone: string) => {
  emit('sendCode', phone)
}
</script>

<template>
  <div class="auth-container-content">    
    <Login
      v-if="currentFormMode === 'login'"
      :mode="currentLoginMode"
      @submit="handleLogin"
      @switch-to-register="handleSwitchMode"
      @forget-password="handleSwitchToForgotPassword"
      @mode-change="handleLoginModeChange"
      @send-code="handleSendCode"
    >
    </Login>

    <Register
      v-else-if="currentFormMode === 'register'"
      :mode="currentRegisterMode"
      @submit="handleRegister"
      @switch-to-login="handleSwitchMode"
      @mode-change="handleRegisterModeChange"
      @send-code="handleSendCode"
    />

    <ForgotPassword
      v-else-if="currentFormMode === 'forgotPassword'"
      @submit="handleForgotPassword"
      @send-code="handleSendCode"
      @switch-to-login="handleSwitchToLogin"
    />

    <SetPassword
      v-else-if="currentFormMode === 'setPassword'"
      @submit="handleSetPassword"
      @switch-to-login="handleSwitchToLogin"
    />

    <TenantSelect
      v-else-if="currentFormMode === 'tenantSelect'"
      :tenants="tenants"
      @submit="handleTenantSelect"
      @switch-to-login="handleSwitchToLogin"
    />
  </div>
</template>
