import Sdk from 'casdoor-js-sdk'

import { getRootBaseURL } from '@/api/http/env'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { windowManager } from '@/platform'

import { casdoorSignin, setCasdoorRpaLocalAuth } from './authApi'
import type { CasdoorConfig, CasdoorUserInfo, IAuthService } from './types'

const ENV = import.meta.env

export class CasdoorAuthService implements IAuthService {
  private readonly backendServerUrl: string
  private readonly casdoorSDK: InstanceType<typeof Sdk>
  private readonly config: CasdoorConfig

  constructor() {
    this.config = {
      serverUrl: ENV.VITE_CASDOOR_SERVER_URL,
      clientId: ENV.VITE_CASDOOR_CLIENT_ID,
      appName: ENV.VITE_CASDOOR_APP_NAME,
      organizationName: ENV.VITE_CASDOOR_ORG,
      redirectPath: '/',
      scope: 'read',
      backendServerUrl: ENV.VITE_CASDOOR_BACKEND_SERVER_URL || getRootBaseURL(),
      signinPath: ENV.VITE_CASDOOR_SIGNIN_PATH,
    }
    // 检查必填字段
    if (!this.config.serverUrl || !this.config.clientId || !this.config.appName || !this.config.organizationName) {
      throw new Error('CasdoorConfig 缺少必填字段')
    }
    this.setCasdoorState()
    this.backendServerUrl = this.config.backendServerUrl
    this.casdoorSDK = new Sdk(this.config as Required<CasdoorConfig>)
  }

  /**
   * state在服务端用于区分不同的应用，即state就是appName
   * 存储位置：
   * sessionStorage的casdoor-state字段
   * 使用位置：casdoor-js-sdk中会使用
   * 1.sdk的getSigninUrl方法会读取casdoor-state字段用于拼接signinUrl
   * 2.sdk的signin方法中，使用casdoor-state字段作为参数换取token
   */
  private setCasdoorState(): void {
    sessionStorage.setItem('casdoor-state', this.config.appName)
  }

  private getToken(): string | null {
    return localStorage.getItem('accessToken')
  }

  private setToken(token: string): void {
    localStorage.setItem('accessToken', token ? `Bearer ${token}` : '')
  }

  private isLoggedIn(): boolean {
    const token = this.getToken()
    return !!token
  }

  private async setLocalAuth() {
    try {
      await setCasdoorRpaLocalAuth({ authorization: `${this.getToken()}` })
    }
    catch {}
  }

  private async handleCallback() {
    try {
      // 登录成功，获取token
      // sdk的signin方法header头部credentials: "include",服务端配置为*，会导致跨域规则问题
      // const response: any = await this.casdoorSDK.signin(this.serverUrl)
      const response: any = await casdoorSignin(this.backendServerUrl, this.config.signinPath)
      const accessToken = response.data.data
      this.setToken(accessToken)
      await this.setLocalAuth()
      useRoutePush({ name: DESIGNER })
    }
    catch (error) {
      console.error('Casdoor登录失败:', error)
    }
  }

  private async redirectToLogin(): Promise<void> {
    try {
      const signinUrl = this.casdoorSDK.getSigninUrl()
      if (signinUrl) {
        if (windowManager) {
          await windowManager.restoreLoginWindow()
          await windowManager.showDecorations()
        }
        window.location.href = signinUrl
      }
    }
    catch {
      // console.error('casdoorRedirectUrl:', error)
    }
  }

  async login(): Promise<void> {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')

    if (code && state) {
      await this.handleCallback()
    }
    else {
      await this.redirectToLogin()
    }
  }

  async getUserName(): Promise<string> {
    try {
      let token = this.getToken()
      token = token.replace('Bearer ', '')
      const res = await this.casdoorSDK.parseAccessToken(token) as { payload: CasdoorUserInfo }
      return res.payload.displayName || '--'
    }
    catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }

  async logout(): Promise<void> {
    try {
      // casdoorSDK 没有 logout 方法，直接清理本地 token及本地路由组件token
      localStorage.removeItem('accessToken')
      await this.setLocalAuth()
      window.location.href = '/'
    }
    catch (error) {
      console.error('Casdoor登出失败:', error)
    }
  }

  async checkLogin(callback: () => void) {
    if (this.isLoggedIn()) {
      await this.setLocalAuth()
      callback && callback()
      return
    }
    await this.login()
  }

  getHttpAuthHeader(): Record<string, string> | null {
    const token = this.getToken()
    return token ? { Authorization: token } : null
  }

  checkHttpResponse(response: any): boolean {
    const isExpired = response?.data.code === '800000'
    if (isExpired) {
      this.redirectToLogin()
    }
    return isExpired
  }
}
