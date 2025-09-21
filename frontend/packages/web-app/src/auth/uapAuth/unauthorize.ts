import { getUrlPath, getUrlQueryField, replaceUrlDomain, setUrlQueryField } from '@/utils/common'

import { getRootBaseURL } from '@/api/http/env'
import { DESIGNER } from '@/constants/menu'
import { windowManager } from '@/platform'

async function redirectToLogin(url: string): Promise<void> {
  try {
    // 如果是根路径，跳转到 designer 页面（必须是 hash 路由模式）
    const redirectUrl = location.hash === '#/' ? `${location.href}${DESIGNER}` : location.href
    let uapUrl = setUrlQueryField('redirect', redirectUrl, url)
    const service = getUrlQueryField('service', uapUrl)

    let newService = ''
    // 如果是退出登录，service要替换为当前前端页面的路径
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

function checkHttpResponse(response: any): boolean {
  // 处理UAP返回302时，重定向到登录页面
  const isExpired = response?.data.ret === 302
  if (isExpired) {
    redirectToLogin(response.data.redirectUrl)
  }
  return isExpired
}

function getHttpAuthHeader(): Record<string, string> | null {
  return null
}

export { checkHttpResponse, getHttpAuthHeader, redirectToLogin }
