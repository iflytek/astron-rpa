<script setup lang="ts">
import Login from './Login.vue'
import Register from './Register.vue'
import ForgotPassword from './ForgotPassword.vue'
import SetPassword from './SetPassword.vue'
import TenantSelect from './TenantSelect.vue'

import { useAuthFlow } from './hooks/useAuthFlow'

const props = defineProps({
  baseUrl: { type: String },
})
const emits = defineEmits(['finish'])

const {
  currentFormMode,
  tenants,
  running,
  preLogin,
  handleRegister,
  handleForgotPassword,
  handleSetPassword,
  handleChooseTenant,
  handleSendCaptcha,
  switchMode,
} = useAuthFlow({
  baseUrl: props.baseUrl,
}, emits)
</script>

<template>
  <div class="auth-container-content h-[540px]">
    <Login
      v-if="currentFormMode === 'login'"
      :running="running"
      @submit="preLogin"
      @switch-to-register="() => switchMode('register')"
      @forget-password="() => switchMode('forgotPassword')"
      @send-captcha="handleSendCaptcha"
    />

    <Register
      v-else-if="currentFormMode === 'register'"
      :running="running"
      @submit="handleRegister"
      @switch-to-login="() => switchMode('login')"
      @send-captcha="handleSendCaptcha"
    />

    <ForgotPassword
      v-else-if="currentFormMode === 'forgotPassword'"
      :running="running"
      @submit="handleForgotPassword"
      @send-captcha="handleSendCaptcha"
      @switch-to-login="() => switchMode('login')"
    />

    <SetPassword
      v-else-if="currentFormMode === 'setPassword'"
      :running="running"
      @submit="handleSetPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <TenantSelect
      v-else-if="currentFormMode === 'tenantSelect'"
      :running="running"
      :tenants="tenants"
      @submit="handleChooseTenant"
      @switch-to-login="() => switchMode('login')"
    />
  </div>
</template>
