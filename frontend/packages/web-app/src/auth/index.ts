import { CasdoorAuthService } from './casdoorAuth'
import type { IAuthService } from './types'
import { UapAuthService } from './uapAuth'

const AUTH_TYPE = import.meta.env.VITE_AUTH_TYPE || 'casdoor'

export type AuthType = 'casdoor' | 'uap'

export class AuthServiceFactory {
  private static instance: AuthServiceFactory
  private currentAuthType: AuthType = AUTH_TYPE
  private services: Map<AuthType, IAuthService>

  private constructor() {
    this.services = new Map()
    this.services.set('casdoor', new CasdoorAuthService())
    this.services.set('uap', new UapAuthService())
  }

  static getInstance(): AuthServiceFactory {
    if (!AuthServiceFactory.instance) {
      AuthServiceFactory.instance = new AuthServiceFactory()
    }
    return AuthServiceFactory.instance
  }

  setAuthType(type: AuthType): void {
    this.currentAuthType = type
  }

  getAuthType(): AuthType {
    return this.currentAuthType
  }

  getService(): IAuthService {
    const service = this.services.get(this.currentAuthType)
    if (!service) {
      throw new Error(`未找到认证服务: ${this.currentAuthType}`)
    }
    return service
  }
}

// 导出一个全局单例并初始化为 casdoor 认证
const authService = (() => {
  const instance = AuthServiceFactory.getInstance()
  instance.setAuthType(AUTH_TYPE)
  return instance
})()

export default authService
