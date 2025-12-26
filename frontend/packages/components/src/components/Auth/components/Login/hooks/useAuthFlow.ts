import { ref, watch, defineExpose } from 'vue'
import { setBaseUrl } from '../../../api/http'
import {
  loginStatus,
  preAuthenticate,
  login,
  register,
  setPassword,
  tenantList,
  isHistory,
  modifyPassword
} from '../../../api/login'
import type {
  LoginFormData,
  LoginMode,
  RegisterFormData,
  RegisterMode,
  TenantItem,
  AuthFormMode,
  AsyncAction,
} from '../../../interface'
import { getRememberUser, saveRememberUser, clearRememberUser, saveSelectedTenant, getSelectedTenant, saveUserInfo } from '../../../utils/remember'
import { message } from 'ant-design-vue'
import type { Platform, Edition, AuthType, InviteInfo } from '../../../interface'
export interface UseAuthFlowOptions {
  baseUrl?: string
  inviteInfo?: InviteInfo
  authType?: AuthType
  edition?: Edition
}

export function useAuthFlow(opts: UseAuthFlowOptions = {}, emits: {(e: 'finish'): void}) {
  const platform = ref<Platform>('admin')
  const currentFormMode = ref<AuthFormMode>('login')
  const tenants = ref<TenantItem[]>([])
  const tempToken = ref<string>('')
  const running = ref<AsyncAction>('IDLE')

  const run = async <T>(action: AsyncAction, task: () => Promise<T>) => {
    running.value = action
    try {
      return await task()
    } finally {
      running.value = 'IDLE'
    }
  }

  watch(
    () => opts.baseUrl,
    (newVal) => {
      newVal && setBaseUrl(newVal)
      platform.value = newVal && newVal.includes('127.0.0.1') ? 'client' : 'admin'
    },
    { immediate: true }
  )

  const checkLoginStatus = async () => {
    try {
      const isLogin = await loginStatus()
      if(isLogin) {
        checkTenant(getSelectedTenant())
      }
    } catch (e) {
      currentFormMode.value = 'login'
    }
  }

  const checkTenant = async (tenantId: string | null) => {
    try {
      const data = await tenantList()
      tenants.value = data
      if(tenantId) {
        const tenantExists = tenants.value.find(t => t.id === tenantId)
        if(tenantExists && !tenantExists.isExpired) {
          emits('finish')
          return
        }
      }
      switchMode('login')
    } catch (e) {
      console.error('获取租户列表失败')
    }
  }
  

  const switchToTenants = async (autoLogin = true) => {
    try {
      const data = await tenantList(tempToken.value)
      tenants.value = data

      if(autoLogin && tenants.value.length === 1) {
        handleLogin(tenants.value[0].id)
        return
      }

      switchMode('tenantSelect')
    } catch (e) {
      console.error('获取租户列表失败')
    }
  }

  const preLogin = async (data: LoginFormData, mode: LoginMode, autoLogin = true) => run(mode, async () => {
    try {
      const params = {...data, loginType: mode}
      if(opts.edition === 'saas') {
        const history = await isHistory({phone: params.phone})
        if(history) {
          if(mode === 'PASSWORD') switchMode('forgotPasswordWithSysUpgrade')
          if(mode === 'CODE'){
            await handleForgotPassword(params)
          }
          return
        }
      }
      const account = params.phone || params.loginName
      mode === 'PASSWORD' && params.remember && account  && params.password ? saveRememberUser(account, params.password, opts.edition, opts.authType) : clearRememberUser()
      delete params.remember
      delete params.agreement
      const token = await preAuthenticate(params)
      tempToken.value = token
      switchToTenants(autoLogin)
    } catch (e) {
      console.error('登录失败')
    }
  })

  const handleLogin = async (tenantId: string) => {
    try {
      const userInfo = await login({ tenantId, tempToken: tempToken.value, platform: platform.value })
      console.log(userInfo)
      saveSelectedTenant(tenantId)
      saveUserInfo(userInfo)
      emits('finish')
    } catch (e) {
      console.error('进入空间失败')
    }
  }

  const handleRegister = async (data: RegisterFormData, mode: RegisterMode) => run(mode, async () => {
    console.log(data, mode)
    try {
      const token = await register(data)
      message.success('注册账号成功')
      tempToken.value = token
      switchMode('setPassword')
    } catch (e) {
      console.log(e)
    }
  })

  const handleForgotPassword = async (data: LoginFormData) => run('FORGOT_PASSWORD', async () =>{
    try {
      const params: LoginFormData = { ...data, loginType: 'CODE' }
      delete params.remember
      delete params.agreement
      const token = await preAuthenticate(params)
      tempToken.value = token
      switchMode(currentFormMode.value === 'forgotPassword' ? 'setPassword' : 'setPasswordWithSysUpgrade')
    } catch (e) {
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
    if(remembered) {
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