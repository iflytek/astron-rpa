import { message } from 'ant-design-vue'

import type { ConsultFormData, LoginFormData, RegisterFormData, TenantItem } from '../interface'
import { clearUserInfo } from '../utils/remember'

import { http } from './http'

interface PreAuthenticateData extends LoginFormData {
  platform: string
}

interface SetPasswordData extends LoginFormData {
  tempToken: string
}

// 查询登录状态
export async function loginStatus() {
  const { data } = await http.get('/rpa-auth/login-status')
  return data
}

// 获取 token
export async function getToken() {
  const { data } = await http.get('/rpa-auth/token')
  return data
}

// 退出登录
export async function logout() {
  const { data } = await http.post('/rpa-auth/logout')
  clearUserInfo()
  return data
}

// 检查是否是历史用户
export async function isHistory(params: LoginFormData) {
  const { data } = await http.get('/rpa-auth/user/history', params)
  return data
}

// 预认
export async function preAuthenticate(params: PreAuthenticateData) {
  const { data } = await http.post('/rpa-auth/pre-authenticate', params)
  return data
}

// 发送验证码
export async function sendCaptcha(phone: string, isRegister: boolean = true) {
  if (!isRegister) {
    const registered = await checkRegistered({ phone })
    if (!registered) {
      message.warning('当前手机号未注册')
      return Promise.reject(new Error('当前手机号未注册'))
    }
  }
  const { data } = await http.postparams('/rpa-auth/verification-code/send', { phone })
  return data
}

// 获取租户列表
export async function tenantList(tempToken?: string) {
  const { data } = await http.get<TenantItem[]>('/rpa-auth/tenant/list', { tempToken })
  return data
}

// 正式登录
export async function login(params: { tempToken: string, tenantId: string }) {
  const { data } = await http.postparams('/rpa-auth/login', params)
  return data
}

// 注册
export async function register(params: RegisterFormData) {
  const { data } = await http.post('/rpa-auth/register', params)
  return data
}

// 检查是否已注册
export async function checkRegistered({ phone }: { phone: string }) {
  const { data } = await http.get('/rpa-auth/user/exist', { phone })
  return data
}

// 设置密码
export async function setPassword(params: SetPasswordData) {
  const { data } = await http.post('/rpa-auth/password/set', params)
  return data
}

// 切换租户
export async function switchTenant(params: { tenantId: string }) {
  const { data } = await http.postparams('/rpa-auth/tenant/switch', params)
  return data
}

// 获取用户信息
export async function userInfo() {
  const { data } = await http.get('/rpa-auth/user/info')
  return data
}

// 修改密码
export async function modifyPassword(params: LoginFormData) {
  const { data } = await http.post('/rpa-auth/password/change', params)
  return data
}

// 提交咨询
export async function submitConsult(params: ConsultFormData) {
  const { data } = await http.post('/robot/feedback/consult/submit', params)
  return data
}

// 提交续费
export async function submitRenewal(params: ConsultFormData) {
  const { data } = await http.post('/robot/feedback/renewal/submit', params)
  return data
}
