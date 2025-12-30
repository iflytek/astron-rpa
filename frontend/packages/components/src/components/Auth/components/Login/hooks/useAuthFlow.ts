import { message } from 'ant-design-vue'
import { ref, watch } from 'vue'

import { setBaseUrl } from '../../../api/http'
import {
  isHistory,
  login,
  loginStatus,
  modifyPassword,
  preAuthenticate,
  register,
  setPassword,
  submitConsult,
  tenantList,
} from '../../../api/login'
import type {
  AsyncAction,
  AuthFormMode,
  AuthType,
  ConsultFormData,
  Edition,
  InviteInfo,
  LoginFormData,
  LoginMode,
  Platform,
  RegisterFormData,
  RegisterMode,
  TenantItem,
} from '../../../interface'
import { clearRememberUser, getRememberUser, getSelectedTenant, saveRememberUser, saveSelectedTenant, saveUserInfo } from '../../../utils/remember'

export interface UseAuthFlowOptions {
  baseUrl?: string
  inviteInfo?: InviteInfo
  authType?: AuthType
  edition?: Edition
}

export function useAuthFlow(opts: UseAuthFlowOptions = {}, emits: { (e: 'finish'): void }) {
  const platform = ref<Platform>('admin')
  const currentFormMode = ref<AuthFormMode>('login')
  const tenants = ref<TenantItem[]>([])
  const tempToken = ref<string>('')
  const running = ref<AsyncAction>('IDLE')

  const run = async <T>(action: AsyncAction, task: () => Promise<T>) => {
    running.value = action
    try {
      return await task()
    }
    finally {
      running.value = 'IDLE'
    }
  }

  watch(
    () => opts.baseUrl,
    (newVal) => {
      newVal && setBaseUrl(newVal)
      platform.value = newVal && newVal.includes('127.0.0.1') ? 'client' : 'admin'
    },
    { immediate: true },
  )

  const checkLoginStatus = async () => {
    try {
      const isLogin = await loginStatus()
      if (isLogin) {
        checkTenant(getSelectedTenant())
      }
    }
    catch (e) {
      console.log(e)
      currentFormMode.value = 'login'
    }
  }

  const checkTenant = async (tenantId: string | null) => {
    try {
      const data = await tenantList()
      tenants.value = data
      if (tenantId) {
        const tenantExists = tenants.value.find(t => t.id === tenantId)
        if (tenantExists && !tenantExists.isExpired) {
          emits('finish')
          return
        }
      }
      switchMode('login')
    }
    catch (e) {
      console.error('获取租户列表失败', e)
    }
  }

  const switchToTenants = async (autoLogin = true) => {
    try {
      const data = await tenantList(tempToken.value)
      tenants.value = data

      if (autoLogin && tenants.value.length === 1 && tenants.value[0]?.id) {
        handleLogin(tenants.value[0].id)
        return
      }

      switchMode('tenantSelect')
    }
    catch (e) {
      console.error('获取租户列表失败', e)
    }
  }

  const preLogin = async (data: LoginFormData, mode: LoginMode, autoLogin = true) => run(mode, async () => {
    try {
      const params = { ...data, loginType: mode }
      if (opts.edition === 'saas') {
        const history = await isHistory({ phone: params.phone })
        if (history) {
          if (mode === 'PASSWORD')
            switchMode('forgotPasswordWithSysUpgrade')
          if (mode === 'CODE') {
            await handleForgotPassword(params)
          }
          return
        }
      }
      const account = params.phone || params.loginName
      mode === 'PASSWORD' && params.remember && account && params.password ? saveRememberUser(account, params.password, opts.edition, opts.authType) : clearRememberUser()
      delete params.remember
      delete params.agreement
      const token = await preAuthenticate({ ...params, platform: platform.value })
      tempToken.value = token
      switchToTenants(autoLogin)
    }
    catch (e) {
      console.error('登录失败', e)
    }
  })

  const handleLogin = async (tenantId: string) => {
    try {
      const userInfo = await login({ tenantId, tempToken: tempToken.value })
      console.log(userInfo)
      saveSelectedTenant(tenantId)
      saveUserInfo(userInfo)
      emits('finish')
    }
    catch (e) {
      console.error('进入空间失败', e)
    }
  }

  const handleRegister = async (data: RegisterFormData | ConsultFormData, mode: RegisterMode) => run(mode, async () => {
    try {
      if (mode === 'REGISTER') {
        const token = await register(data as RegisterFormData)
        message.success('注册账号成功')
        tempToken.value = token
        if (!Object.prototype.hasOwnProperty.call(data, 'password'))
          switchMode('setPassword')
        else switchToTenants()
        return
      }
      await submitConsult(data as ConsultFormData)
      message.success('提交成功')
      switchMode('login')
    }
    catch (e) {
      console.log(e)
    }
  })

  const handleForgotPassword = async (data: LoginFormData) => run('FORGOT_PASSWORD', async () => {
    try {
      const params: LoginFormData = { ...data, loginType: 'CODE' }
      delete params.remember
      delete params.agreement
      const token = await preAuthenticate({ ...params, platform: platform.value })
      tempToken.value = token
      switchMode(currentFormMode.value === 'forgotPassword' ? 'setPassword' : 'setPasswordWithSysUpgrade')
    }
    catch (e) {
      console.log(e)
    }
  })

  const handleSetPassword = async (data: LoginFormData) => run('SET_PASSWORD', async () => {
    await setPassword({ ...data, tempToken: tempToken.value })
    message.success('密码设置成功')
    switchToTenants()
  })

  const handleModifyPassword = async (data: LoginFormData) => run('MODIFY_PASSWORD', async () => {
    await modifyPassword(data)
    message.success('密码修改成功')
    switchToTenants()
  })

  const handleChooseTenant = async (tenantId: string) => {
    await handleLogin(tenantId)
  }

  const switchMode = (mode: AuthFormMode) => (currentFormMode.value = mode)

  const autoPreLogin = () => {
    const remembered = getRememberUser()
    if (remembered) {
      const accountKey = opts.authType === 'uap' ? 'phone' : 'loginName'
      const params = {
        [accountKey]: remembered.account,
        password: remembered.password,
        remember: true,
      }

      preLogin(params, 'PASSWORD', false)
    }
  }
  !opts.inviteInfo && checkLoginStatus()

  return {
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
  }
}
