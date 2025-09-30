import { getUrlPath, getUrlQueryField, replaceUrlDomain, setUrlQueryField } from '@/utils/common'

import { getRootBaseURL } from '@/api/http/env'
import { DESIGNER } from '@/constants/menu'
import { windowManager } from '@/platform'

import { uapLoginStatus, uapLogout, uapUserInfo } from './authApi'
import type { IAuthService } from './types'

export class UapAuthService implements IAuthService {
  private async isLoggedIn(): Promise<boolean> {
    const res = await uapLoginStatus()
    return !!res.data
  }

  private async redirectToLogin(url: string): Promise<void> {
    try {
      const redirectUrl = location.hash === '#/' ? `${location.href}${DESIGNER}` : location.href
      let uapUrl = setUrlQueryField('redirect', redirectUrl, url)
      const service = getUrlQueryField('service', uapUrl)
      let newService = ''
      if (url.includes('/logout')) {
        newService = getUrlPath(location.href)
      }
      else {
        newService = replaceUrlDomain(service, getRootBaseURL())
      }
      uapUrl = setUrlQueryField('service', newService, uapUrl)
      if (windowManager) {
        await windowManager.restoreLoginWindow()
        await windowManager.showDecorations()
      }
      location.href = uapUrl
    }
    catch (error) {
      console.error('UAP登录跳转失败:', error)
      throw error
    }
  }

  async login(): Promise<void> {
    await uapUserInfo()
  }

  async checkLogin(callback: () => void): Promise<void> {
    const isLogin = await this.isLoggedIn()
    if (isLogin) {
      callback && callback()
      return
    }
    this.login()
  }

  async getUserName(): Promise<string> {
    try {
      const res = await uapUserInfo()
      return res.data?.loginName || '--'
    }
    catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }

  async logout(): Promise<void> {
    await uapLogout()
  }

  checkHttpResponse(response: any): boolean {
    const isExpired = response?.data.ret === 302
    if (isExpired) {
      this.redirectToLogin(response.data.redirectUrl)
    }
    return isExpired
  }

  getHttpAuthHeader(): Record<string, string> | null {
    return null
  }
}
