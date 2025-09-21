import sentry from '@/plugins/sentry'

import http from '../http'

export interface UapUserInfo {
  id: string
  name: string
  loginName: string
  email: string
}

/**
 * 查询用户UAP登录状态
 */
export function uapLoginStatus() {
  return http.get('/robot/login-status', {}, { toast: false })
}

/**
 * @description: UAP登出
 */
export function uapLogout() {
  return http.post('/robot/logout')
}

/**
 * 查询 UAP 用户信息，判断登录状态
 * 1. 用户已登录，正常返回用户信息
 * 2. 用户未登录，会返回 302 状态码，重定向到 UAP 登录页面
 */
export async function uapUserInfo() {
  const res = await http.get<UapUserInfo>('/robot/user/info', {}, { toast: false })

  if (res.data) {
    sentry.setUser({
      id: res.data.id,
      email: res.data.email,
      username: res.data.loginName,
    })
  }

  return res
}
