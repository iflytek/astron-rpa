import sentry from '@/plugins/sentry'

import http from '../http'
import { getRootBaseURL } from '../http/env'

export interface CasdoorUserInfo {
  id: string
  name: string
  displayName: string
  phone: string
  email: string
}

/**
 * 通过code和state， 换取token
 */
export function casdoorSignin(data: { code: string, state: string }) {
  return http.post('/robot/user/api/signin', null, {
    params: data,
  })
}

export function setRpaLocalAuth(data: { authorization: string }) {
  return http.post('/rpa-local-route/set-auth', data, { baseURL: getRootBaseURL(), toast: false })
}

// export function casdoorRedirectUrl() {
//   return http.get('/robot/user/api/redirect-url')
// }

export async function casdoorUserinfo() {
  const res = await http.get<CasdoorUserInfo>('/robot/user/api/userinfo')

  if (res.data) {
    sentry.setUser({
      id: res.data.id,
      email: res.data.email,
      username: res.data.displayName,
      phone: res.data.phone,
    })
  }

  return res
}

export function casdoorLogout() {
  return http.get('/robot/api/logout', null)
}
