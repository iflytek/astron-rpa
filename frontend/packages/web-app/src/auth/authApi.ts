import axios from 'axios'

import sentry from '@/plugins/sentry'

import { getBaseURL, getRootBaseURL } from '@/api/http/env'

import type { UapUserInfo } from './types'

const baseUrl = getBaseURL()
const rootBaseUrl = getRootBaseURL()

export async function casdoorSignin(serverUrl: string, signinPath?: string, code?: string | null, state?: string | null) {
  if (!code || !state) {
    const params = new URLSearchParams(window.location.search)
    code = params.get('code')
    state = params.get('state')
  }
  return axios.post(`${serverUrl}${signinPath || '/api/signin'}?code=${code}&state=${state}`)
}

export function setCasdoorRpaLocalAuth(data: { authorization: string }) {
  return axios.post(`${rootBaseUrl}/rpa-local-route/set-auth`, data)
}

export async function uapLoginStatus() {
  return axios.get(`${baseUrl}/robot/login-status`)
}

export async function uapLogout() {
  return axios.post(`${baseUrl}/robot/logout`)
}

export async function uapUserInfo() {
  const res = await axios.get<UapUserInfo>(`${baseUrl}/robot/user/info`)
  if (res.data) {
    sentry.setUser({
      id: res.data.id,
      email: res.data.email,
      username: res.data.loginName,
    })
  }
  return res
}
