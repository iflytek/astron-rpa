import CryptoJS from 'crypto-js'

import type { AuthType, Edition } from '../interface'

const KEY = 'Fh$8bR#mK2p@7vL!wQ9y^U4nE6j*T1&s'

export interface RememberedUser {
  account: string
  password: string
  edition: Edition
  authType: AuthType
}

export function saveSelectedTenant(tenantId: string) {
  localStorage.setItem('tenantId', tenantId)
}

export function getSelectedTenant(): string | null {
  return localStorage.getItem('tenantId')
}

export function saveRememberUser(account: string, pwdPlain: string, edition: Edition = 'saas', authType: AuthType = 'uap') {
  const encrypted = CryptoJS.AES.encrypt(pwdPlain, KEY).toString()
  const val: RememberedUser = { account, password: encrypted, edition, authType }
  localStorage.setItem('user', JSON.stringify(val))
}

export function getRememberUser(): RememberedUser | null {
  const raw = localStorage.getItem('user')
  if (!raw)
    return null
  try {
    const { account, password, edition, authType } = JSON.parse(raw) as RememberedUser
    const decrypted = CryptoJS.AES.decrypt(password, KEY).toString(CryptoJS.enc.Utf8)
    return { account, password: decrypted, edition, authType }
  }
  catch {
    return null
  }
}

export function clearRememberUser() {
  localStorage.removeItem('user')
}

export function saveUserInfo(userInfo: any) {
  const encrypted = CryptoJS.AES.encrypt(JSON.stringify(userInfo), KEY).toString()
  localStorage.setItem('userInfo', encrypted)
}

export function getUserInfo(): any | null {
  const raw = localStorage.getItem('userInfo')
  if (!raw)
    return null
  try {
    const decrypted = CryptoJS.AES.decrypt(raw, KEY).toString(CryptoJS.enc.Utf8)
    return JSON.parse(decrypted)
  }
  catch {
    return null
  }
}

export function clearUserInfo() {
  localStorage.removeItem('userInfo')
}
