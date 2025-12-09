import { ref, watch, type Ref } from 'vue'
import { setBaseUrl } from '../../../api/http'
import {
  loginStatus,
  preAuthenticate,
  login,
  register,
  sendCaptcha,
  setPassword,
  tenantList,
  isNewUser,
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
import { saveRememberUser, clearRememberUser, saveSelectedTenant, getSelectedTenant, saveUserInfo } from '../../../utils/remember'
import { message } from 'ant-design-vue'

export interface UseAuthFlowOptions {
  baseUrl?: string
}

export function useAuthFlow(opts: UseAuthFlowOptions = {}, emits: {(e: 'finish'): void}) {
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
    (newVal) => newVal && setBaseUrl(newVal),
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
        if(tenantExists) {
          emits('finish')
          return
        }
      }
      switchMode('login')
    } catch (e) {
      console.error('获取租户列表失败')
    }
  }
  

  const switchToTenants = async () => {
    try {
      const data = await tenantList(tempToken.value)
      tenants.value = data

      if(tenants.value.length === 1) {
        handleLogin(tenants.value[0].id)
        return
      }

      switchMode('tenantSelect')
    } catch (e) {
      console.error('获取租户列表失败')
    }
  }

  const preLogin = async (data: LoginFormData, mode: LoginMode) => run(mode, async () => {
    try {
      const params = {...data, loginType: mode}
      const isNew = await isNewUser(params)
      if(!isNew){
        switchMode('forgotPasswordWithSysUpgrade')
        return
      }
      mode === 'PASSWORD' && params.remember && params.phone && params.password ? saveRememberUser(params.phone, params.password) : clearRememberUser()
      delete params.remember
      delete params.agreement
      const token = await preAuthenticate(params)
      tempToken.value = token
      switchToTenants()
    } catch (e) {
      console.error('登录失败')
    }
  })

  const handleLogin = async (tenantId: string) => {
    try {
      const userInfo = await login({ tenantId, tempToken: tempToken.value })
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

  const handleChooseTenant = async (tenantId: string) => {
    await handleLogin(tenantId)
  }

  const handleSendCaptcha = (phone: string) => {
    return sendCaptcha(phone, currentFormMode.value)
  }

  const switchMode = (mode: AuthFormMode) => (currentFormMode.value = mode)

  checkLoginStatus()

  return {
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
  }
}