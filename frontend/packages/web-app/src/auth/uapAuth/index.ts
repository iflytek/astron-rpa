import { uapLoginStatus, uapLogout, uapUserInfo } from '@/api/login/uap'

import type { IAuthService } from '../types'

export class UapAuthService implements IAuthService {
  async logout(): Promise<void> {
    await uapLogout()
  }

  async login(): Promise<void> {
    // 未登录时，通过调用获取用户信息接口，跳转到登录页面
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

  private async isLoggedIn(): Promise<boolean> {
    const res = await uapLoginStatus()
    return !!res.data
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
}
