import { message } from 'ant-design-vue'
import axios from 'axios'
import type { AxiosRequestConfig } from 'axios'

let BASE_URL = localStorage.getItem('authBaseUrl') || import.meta.env.VITE_API_BASE_URL || '/api'
export function setBaseUrl(url?: string) {
  BASE_URL = url || import.meta.env.VITE_API_BASE_URL || '/api'
  localStorage.setItem('authBaseUrl', BASE_URL || '')
}

const SUCCESS_CODE = '000000'
export interface ResponseData<T = any> {
  code?: string
  data: T
  message?: string
  msg?: string
}

export async function request<T = any, P = any>(
  config: AxiosRequestConfig<P> & { url: string },
): Promise<ResponseData<T>> {
  try {
    const { data: res } = await axios<ResponseData<T>>({
      baseURL: BASE_URL,
      timeout: 20000,
      withCredentials: false,
      headers: { 'Content-Type': 'application/json;charset=UTF-8' },
      ...config,
      data: config.data && JSON.parse(JSON.stringify(config.data)),
    })

    if (res.code === SUCCESS_CODE)
      return res

    if (res.code !== SUCCESS_CODE) {
      message.error(res.message || res.msg || '服务异常')
    }
    return Promise.reject(res)
  }
  catch (err: any) {
    const msg = err.response
      ? `${err.response.status} ${err.response.statusText}`
      : err.message || '服务异常'
    message.error(msg)
    return Promise.reject(err)
  }
}

export const http = {
  get: <T = any>(url: string, params?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'GET', url, params, ...config }),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'POST', url, data, ...config }),

  postparams: <T = any>(url: string, params?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'POST', url, params, ...config }),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'PUT', url, data, ...config }),

  del: <T = any>(url: string, params?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'DELETE', url, params, ...config }),
}

export default request
