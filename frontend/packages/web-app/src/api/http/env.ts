import { isBase64Image } from '@/utils/common'
import { storage } from '@/utils/storage'
import { message } from 'ant-design-vue'

import GlobalModal from '@/components/GlobalModal/index.ts'

const DEFAULT_PORT = 13159
const DEFAULT_HOST = import.meta.env.VITE_SERVICE_HOST ?? "localhost"

/**
 * 获取接口基础URL
 * @returns baseURL
 */
export function getBaseURL(): string {
  const port = Number(storage.get('route_port')) || DEFAULT_PORT
  return `http://${DEFAULT_HOST}:${port}/api`
}

/**
 * 获取接口根路径
 * @returns
 */
export function getRootBaseURL(): string {
  return new URL(getBaseURL()).origin
}

export function getImageURL(str: string): string {
  if (isBase64Image(str))
    return str
  return `${getRootBaseURL()}${str}`
}

/**
 * 登录失效
 */
export function unauthorize(response) {
  if(response.config.toast === false) {
    message.error(response.data.message || response.data.msg || '登录失效，请重新登录')
  }
  const code = response.data.code || response.data.ret
  location.href = '/boot.html?code=' + code
}

let isUnauthorized = null
export function unauthorizeModal(code?: string | number) {
  if (isUnauthorized) return

  let message = '登录失效，请重新登录'
  if(code === '900001') {
    message = '账号已在其他地方登录，请重新登录'
  } else if(code === '900005') {
    message = '空间已到期，请重新登录'
  }

  isUnauthorized = GlobalModal.error({
    title: '登录失效',
    content: message,
    keyboard: false,
    maskClosable: false,
    onOk: () => {
      isUnauthorized = null
    },
  })
}

let isExpired = null
export function expiredModal(tenantType?: string | number) {
  if (isExpired) return

  isExpired = GlobalModal.error({
    title: '空间到期',
    content: `您的${tenantType === 'enterprise' ? '企业' : '专业版'}空间已到期，请联系管理人员续费办理`,
    keyboard: false,
    maskClosable: false,
    okTxt: '我知道了',
    onOk: () => {
      isExpired = null
    },
  })
}
