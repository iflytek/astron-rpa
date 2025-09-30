export type AuthType = 'casdoor' | 'uap'

export interface IAuthService {
  login: (url?: string) => Promise<void>
  logout: () => Promise<void>
  getUserName: () => Promise<string>
  checkLogin: (callback: () => void) => Promise<void>
  getHttpAuthHeader: () => Record<string, string> | null
  checkHttpResponse: (response: any) => boolean
}

export interface CasdoorConfig {
  serverUrl?: string
  clientId?: string
  appName?: string
  organizationName?: string
  redirectPath?: string
  scope?: string
  signinPath?: string
  backendServerUrl?: string
}

export interface CasdoorUserInfo {
  id: string
  name: string
  displayName: string
  phone: string
  email: string
}

export interface UapUserInfo {
  id: string
  name: string
  loginName: string
  email: string
}
