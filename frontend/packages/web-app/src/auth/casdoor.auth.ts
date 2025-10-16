import { setUrlQueryField } from '@/utils/common'

import { windowManager } from '@/platform'

import { casdoorLoginStatus, casdoorLoginUrl, casdoorSignin, casdoorSignout } from './authApi'
import type { IAuthService } from './types'

export class CasdoorAuthService implements IAuthService {
  private async isLoggedIn(): Promise<boolean> {
    const res = await casdoorLoginStatus()
    return !!res
  }

  private async signin(code: string, state: string) {
    try {
      const response: any = await casdoorSignin({ code, state })
      localStorage.setItem('userInfo', JSON.stringify(response.data.data))
      location.replace(`/`)
    }
    catch (error) {
      console.error('Casdoor登录失败:', error)
    }
  }

  private async redirectToLogin(): Promise<void> {
    try {
      const res = await casdoorLoginUrl()
      let loginUrl = res.data.data
      const redirectUrl = `${location.origin}/boot.html`
      loginUrl = setUrlQueryField('redirect_uri', redirectUrl, loginUrl)
      if (loginUrl) {
        if (windowManager) {
          await windowManager.restoreLoginWindow()
          await windowManager.showDecorations()
        }
        window.location.href = loginUrl
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
      await this.signin(code, state)
      return
    }
    this.redirectToLogin()
  }

  async getUserName(): Promise<string> {
    const userInfo = localStorage.getItem('userInfo')
    return Promise.resolve(JSON.parse(userInfo || '{}')?.displayName || '--')
  }

  async logout(): Promise<void> {
    try {
      const res = await casdoorSignout()
      let logoutUrl = res.data.data.logoutUrl
      const redirectUrl = `${location.origin}/boot.html`
      logoutUrl = setUrlQueryField('post_logout_redirect_uri', redirectUrl, logoutUrl)
      window.location.href = logoutUrl
    }
    catch (error) {
      console.error('Casdoor登出失败:', error)
    }
  }

  async checkLogin(callback: () => void) {
    const isLogin = await this.isLoggedIn()
    if (isLogin) {
      callback && callback()
      return
    }
    await this.login()
  }

  checkHttpResponse(response: any): boolean {
    const isExpired = response?.data.code === '900001'
    if (isExpired) {
      this.redirectToLogin()
    }
    return isExpired
  }
}
