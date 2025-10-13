import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { windowManager } from '@/platform'
import { setUrlQueryField } from '@/utils/common'

import { casdoorLoginUrl, casdoorLoginStatus, casdoorSignin, casdoorSignout } from './authApi'
import type { IAuthService } from './types'

export class CasdoorAuthService implements IAuthService {  
  private async isLoggedIn(): Promise<boolean> {
    const res = await casdoorLoginStatus()
    return !!res
  }

  private async signin(code: string, state: string) {
    try {
      const response: any = await casdoorSignin({code, state})
      localStorage.setItem('userInfo', JSON.stringify(response.data.data))
      useRoutePush({ name: DESIGNER })
    }
    catch (error) {
      console.error('Casdoor登录失败:', error)
    }
  }

  private async redirectToLogin(): Promise<void> {
    try {
      const res = await casdoorLoginUrl()
      let loginUrl = res.data.data
      if (loginUrl) {
        if (windowManager) {
          await windowManager.restoreLoginWindow()
          await windowManager.showDecorations()
        }
        const redirectUrl = location.origin + '/'
        loginUrl = setUrlQueryField('redirect_uri', redirectUrl, loginUrl)
        window.location.href = loginUrl
        return
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
      this.signin(code, state)
      return
    }
    this.redirectToLogin()
  }

  async getUserName(): Promise<string> {
    const userInfo = localStorage.getItem('userInfo')
    return Promise.resolve(JSON.parse(userInfo||'{}')?.displayName || '--')
  }

  async logout(): Promise<void> {
    try {
      await casdoorSignout()
      window.location.href = '/'
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
    this.login()
  }

  checkHttpResponse(response: any): boolean {
    const isExpired = response?.data.code === '900001'
    if (isExpired) {
      this.redirectToLogin()
    }
    return isExpired
  }
}
