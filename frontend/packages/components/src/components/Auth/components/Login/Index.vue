<script setup lang="ts">
import Login from './Login.vue'
import Register from './Register.vue'
import ForgotPassword from './ForgotPassword.vue'
import SetPassword from './SetPassword.vue'
import TenantSelect from './TenantSelect.vue'
import type { InviteInfo } from '../../interface'

import { useAuthFlow } from './hooks/useAuthFlow'

const props = defineProps({
  baseUrl: { type: String },
  inviteInfo: { type: Object as () => InviteInfo, default: () => null },
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
  switchMode,
} = useAuthFlow(props, emits)
</script>

<template>
  <div class="auth-container-content h-[540px]">
    <Login
      v-if="currentFormMode === 'login'"
      :invite-info="inviteInfo"
      :running="running"
      @submit="preLogin"
      @switch-to-register="() => switchMode('register')"
      @forget-password="() => switchMode('forgotPassword')"
    />

    <Register
      v-else-if="currentFormMode === 'register'"
      :running="running"
      :invite-info="inviteInfo"
      @submit="handleRegister"
      @switch-to-login="() => switchMode('login')"
    />

    <ForgotPassword
      v-else-if="['forgotPasswordWithSysUpgrade', 'forgotPassword' ].includes(currentFormMode)"
      :running="running"
      :title="currentFormMode === 'forgotPasswordWithSysUpgrade' ? '系统已升级，请重新设置密码' : ''"
      @submit="handleForgotPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <SetPassword
      v-else-if="['setPasswordWithSysUpgrade', 'setPassword' ].includes(currentFormMode)"
      :title="currentFormMode === 'setPasswordWithSysUpgrade' ? '系统已升级，请重新设置密码' : ''"
      :running="running"
      :invite-info="inviteInfo"
      @submit="handleSetPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <TenantSelect
      v-else-if="currentFormMode === 'tenantSelect'"
      :invite-info="inviteInfo"
      :running="running"
      :tenants="tenants"
      @submit="handleChooseTenant"
      @switch-to-login="() => switchMode('login')"
    />
  </div>
</template>
