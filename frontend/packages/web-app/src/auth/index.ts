import { CasdoorAuthService } from './casdoor.auth'
import type { AuthType, IAuthService } from './types'
import { UapAuthService } from './uap.auth'

const ENV = import.meta.env

const AUTH_TYPE = ENV.VITE_AUTH_TYPE || 'casdoor'
export class AuthServiceFactory {
  private static instance: AuthServiceFactory
  private currentAuthType: AuthType = AUTH_TYPE
  private auths: Map<AuthType, IAuthService>

  private constructor() {
    this.auths = new Map()
    this.init()
    this.setAuthType(AUTH_TYPE)
  }

  init(): void {
    this.auths.set('casdoor', new CasdoorAuthService())
    this.auths.set('uap', new UapAuthService())
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

  getAuth(): IAuthService {
    const service = this.auths.get(this.currentAuthType)
    if (!service) {
      throw new Error(`未找到认证服务: ${this.currentAuthType}`)
    }
    return service
  }
}

export default AuthServiceFactory.getInstance()
