import { http } from './http'
import { LoginFormData, PersonalRegisterFormData, SetPasswordFormData } from '../interface'

// 查询登录状态
export const loginStatus = async () => {
  const { data } = await http.get('/login-status')
  return data
}

// 获取 token
export const getToken = async () => {
  const { data } = await http.get('/token')
  return data
}

// 退出登录
export const logout = async () => {
  const { data } = await http.post('/logout')
  return data
}

// 预认证
export const preAuthenticate = async () => {
  const { data } = await http.post<LoginFormData>('/pre-authenticate', { user: 'tom', pwd: '123' })
  return data
}

// 发送验证码
export const sendCaptcha = async ({ phone } : { phone: string }) => {
  const { data } = await http.post<LoginFormData>('/verification-code/send', { phone })
  return data
}

// 获取租户列表
export const tenantList = async () => {
  const { data } = await http.get<{ tempToken: string }>('/tenant/list', { user: 'tom', pwd: '123' })
  return data
}

// 正式登录
export const login = async () => {
  const { data } = await http.post<{ tempToken: string, tenantId: string }>('/login', { user: 'tom', pwd: '123' })
  return data
}

// 注册
export const register = async () => {
  const { data } = await http.post<PersonalRegisterFormData>('/register', { user: 'tom', pwd: '123' })
  return data
}

// 检查是否已注册
export const checkRegistered = async ({ phone } : { phone: string }) => {
  const { data } = await http.post<{phone: string}>('/user/exist', { phone })
  return data
}

// 设置密码
export const setPassword = async (params: SetPasswordFormData) => {
  const { data } = await http.post('/password/set', params)
  return data
}
