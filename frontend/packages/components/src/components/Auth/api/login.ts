import { http } from './http'
import { LoginFormData, RegisterFormData, TenantItem } from '../interface'
import { clearUserInfo } from '../utils/remember'
import { message } from 'ant-design-vue'

// 查询登录状态
export const loginStatus = async () => {
  const { data } = await http.get('/rpa-auth/login-status')
  return data
}

// 获取 token
export const getToken = async () => {
  const { data } = await http.get('/rpa-auth/token')
  return data
}

// 退出登录
export const logout = async () => {
  const { data } = await http.post('/rpa-auth/logout')
  clearUserInfo()
  return data
}

// 检查是否是历史用户
export const isHistory = async (params: LoginFormData) => {
  const { data } = await http.get('/rpa-auth/user/history', params)
  return data
}

// 预认证
export const preAuthenticate = async (params: LoginFormData) => {
  const { data } = await http.post('/rpa-auth/pre-authenticate', params)
  return data
}

// 发送验证码
export const sendCaptcha = async (phone: string, isRegister: boolean = true) => {
  if (!isRegister) {
    const registered = await checkRegistered({ phone });
    if (!registered) {
      message.warning('当前手机号未注册');
      return Promise.reject();
    }
  }
  const { data } = await http.postparams('/rpa-auth/verification-code/send', { phone });
  return data;
}

// 获取租户列表
export const tenantList = async (tempToken?: string) => {
  const { data } = await http.get<TenantItem[]>('/rpa-auth/tenant/list', { tempToken })
  return data
}

// 正式登录
export const login = async (params: { tempToken: string, tenantId: string, platform: string }) => {
  const { data } = await http.postparams('/rpa-auth/login', params)
  return data
}

// 注册
export const register = async (params: RegisterFormData) => {
  const { data } = await http.post('/rpa-auth/register', params)
  return data
}

// 检查是否已注册
export const checkRegistered = async ({ phone } : { phone: string }) => {
  const { data } = await http.get('/rpa-auth/user/exist', { phone })
  return data
}

// 设置密码
interface SetPasswordData extends LoginFormData {
  tempToken: string
}
export const setPassword = async (params: SetPasswordData) => {
  const { data } = await http.post('/rpa-auth/password/set', params)
  return data
}

// 切换租户
export const switchTenant = async (params: { tenantId: string }) => {
  const { data } = await http.postparams('/rpa-auth/tenant/switch', params)
  return data
}

// 获取用户信息
export const userInfo = async () => {
  const { data } = await http.get('/rpa-auth/user/info')
  return data
}

// 修改密码
export const modifyPassword = async (params: LoginFormData) => {
  const { data } = await http.post('/rpa-auth/user/password/modify', params)
  return data
}
