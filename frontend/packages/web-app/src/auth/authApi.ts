import axios from 'axios'

import sentry from '@/plugins/sentry'

import { getBaseURL } from '@/api/http/env'

import type { UapUserInfo } from './types'

export async function casdoorLoginStatus() {
  try {
    const res: any = await axios.get(`${getBaseURL()}/robot/user/login-check`)
    return !(res.data.code === '900001')
  } catch {
    return false
  }
}

export async function casdoorLoginUrl() {
  return axios.get(`${getBaseURL()}/robot/user/redirect-url`)
}

export async function casdoorSignin(params: {code: string | null, state: string | null}) {
  return axios.post(`${getBaseURL()}/robot/user/sign/in?code=${params.code}&state=${params.state}`)
}

export async function casdoorSignout() {
  return axios.post(`${getBaseURL()}/robot/user/sign/out`)
}

export async function uapLoginStatus() {
  return axios.get(`${getBaseURL()}/robot/login-status`)
}

export async function uapLogout() {
  return axios.post(`${getBaseURL()}/robot/logout`)
}

export async function uapUserInfo() {
  const res = await axios.get<UapUserInfo>(`${getBaseURL()}/robot/user/info`)
  if (res.data) {
    sentry.setUser({
      id: res.data.id,
      email: res.data.email,
      username: res.data.loginName,
    })
  }
  return res
}
