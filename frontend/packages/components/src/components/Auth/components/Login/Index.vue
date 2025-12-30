<script setup lang="ts">
import type { AuthType, Edition, InviteInfo } from '../../interface'

import ForgotPassword from './ForgotPassword.vue'
import { useAuthFlow } from './hooks/useAuthFlow'
import Login from './Login.vue'
import ModifyPassword from './ModifyPassword.vue'
import Register from './Register.vue'
import SetPassword from './SetPassword.vue'
import TenantSelect from './TenantSelect.vue'

const props = defineProps({
  baseUrl: { type: String },
  inviteInfo: { type: Object as () => InviteInfo, default: () => null },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
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
  handleModifyPassword,
  handleChooseTenant,
  switchMode,
  autoPreLogin,
} = useAuthFlow(props, emits)

defineExpose({
  autoPreLogin,
})
</script>

<template>
  <div class="auth-container-content h-[540px]">
    <Login
      v-if="currentFormMode === 'login'"
      :invite-info="inviteInfo"
      :edition="edition"
      :auth-type="authType"
      :running="running"
      @submit="preLogin"
      @switch-to-register="() => switchMode('register')"
      @forget-password="() => switchMode('forgotPassword')"
      @modify-password="() => switchMode('modifyPassword')"
    />

    <Register
      v-else-if="currentFormMode === 'register'"
      :edition="edition"
      :auth-type="authType"
      :running="running"
      :invite-info="inviteInfo"
      @submit="handleRegister"
      @switch-to-login="() => switchMode('login')"
    />

    <ForgotPassword
      v-else-if="['forgotPasswordWithSysUpgrade', 'forgotPassword'].includes(currentFormMode)"
      :running="running"
      :title="currentFormMode === 'forgotPasswordWithSysUpgrade' ? '系统已升级，请重新设置密码' : ''"
      @submit="handleForgotPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <SetPassword
      v-else-if="['setPasswordWithSysUpgrade', 'setPassword'].includes(currentFormMode)"
      :title="currentFormMode === 'setPasswordWithSysUpgrade' ? '系统已升级，请重新设置密码' : ''"
      :running="running"
      :invite-info="inviteInfo"
      @submit="handleSetPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <ModifyPassword
      v-else-if="['modifyPassword'].includes(currentFormMode)"
      :running="running"
      :invite-info="inviteInfo"
      :edition="edition"
      :auth-type="authType"
      @submit="handleModifyPassword"
      @switch-to-login="() => switchMode('login')"
    />

    <TenantSelect
      v-else-if="currentFormMode === 'tenantSelect'"
      :invite-info="inviteInfo"
      :edition="edition"
      :auth-type="authType"
      :running="running"
      :tenants="tenants"
      @submit="handleChooseTenant"
      @switch-to-login="() => switchMode('login')"
    />
  </div>
</template>
