import * as casdoorUnAuth from '@/auth/casdoorAuth/unauthorize'
import * as uapUnAuth from '@/auth/uapAuth/unauthorize'

const AUTH_TYPE = import.meta.env.VITE_AUTH_TYPE || 'casdoor'

const unauthorizeMap = {
  casdoor: casdoorUnAuth,
  uap: uapUnAuth,
} as const

export const checkHttpResponse = unauthorizeMap[AUTH_TYPE].checkHttpResponse
export const getHttpAuthHeader = unauthorizeMap[AUTH_TYPE].getHttpAuthHeader
