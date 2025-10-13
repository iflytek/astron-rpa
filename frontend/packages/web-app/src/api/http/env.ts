import { storage } from '@/utils/storage'

import GlobalModal from '@/components/GlobalModal/index.ts'

const DEFAULT_PORT = 13159

/**
 * 获取接口基础URL
 * @returns baseURL
 */
export function getBaseURL(): string {
  const port = Number(storage.get('route_port')) || DEFAULT_PORT
  return `http://127.0.0.1:${port}/api`
}

/**
 * 获取接口根路径
 * @returns
 */
export function getRootBaseURL(): string {
  return new URL(getBaseURL()).origin
}

let isUnauthorized = null

/**
 * 登录失效
 */
export function unauthorize() {
  if (isUnauthorized || location.pathname === '/') {
    return
  }

  isUnauthorized = GlobalModal.error({
    title: '登录失效',
    content: '登录失效，请重新登录',
    keyboard: false,
    maskClosable: false,
    onOk: () => {
      sessionStorage.removeItem('tokenValue')
      location.href = '/'
      isUnauthorized = null
    },
  })
}
