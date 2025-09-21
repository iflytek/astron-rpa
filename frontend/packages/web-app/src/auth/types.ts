export interface AuthUser {
  id: string
  name: string
  email?: string
  token?: string
}

export interface LoginResponse {
  user: AuthUser
  token: string
}

export interface IAuthService {
  login: (url?: string) => Promise<void>
  logout: () => Promise<void>
  getUserName: () => Promise<string>
  checkLogin: (callback: () => void) => Promise<void>
}

export interface CasdoorUserInfo {
  id: string
  name: string
  displayName: string
  phone: string
  email: string
}
