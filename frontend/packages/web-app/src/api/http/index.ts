import { message } from 'ant-design-vue'
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosRequestHeaders,
  AxiosResponse,
} from 'axios'
import axios, { AxiosHeaders } from 'axios'
import { isNil } from 'lodash-es'

import { promiseWithResolvers } from '@/utils/common'

import { ERROR_CODES, SUCCESS_CODES, UN_AUTHORIZED_CODES } from '@/constants'

import { getBaseURL, unauthorize } from './env'

export type { AxiosProgressEvent } from 'axios'

export interface RequestConfig<T = any, P = any> extends AxiosRequestConfig<P> {
  toast?: boolean
  loading?: boolean
  mock?: (params: P) => Promise<ResponseData<T>> | ResponseData<T>
}

interface InternalRequestConfig<T = any, P = any> extends RequestConfig<T, P> {
  headers: AxiosRequestHeaders
}

interface ResponseData<T = any> {
  code?: string
  data: T
  message?: string
  msg?: string
  imageType?: string
  success?: boolean
  ret?: number // 添加 ret 属性, UAP
  redirectUrl?: string // 添加 redirectUrl 属性, UAP
}

interface Response<T = any, D = any> extends AxiosResponse<ResponseData<T>, D> {
  config: InternalRequestConfig<T, D>
}

class HttpClient {
  private HTTP_READY_KEY = 'httpReady'
  private instance: AxiosInstance

  // 阻塞所有的 http 请求，只有在 readyPromise 被 resolve 时才会发送请求
  private readyPromise = promiseWithResolvers<void>()

  // 允许外部调用的方法，用于在引擎加载完成后，将 readyPromise 标记为已完成
  public resolveReadyPromise() {
    // 将已完成的标识存储到 session storage 中
    sessionStorage.setItem(this.HTTP_READY_KEY, 'true')
    this.readyPromise.resolve()
  }

  constructor() {
    // 检查 session storage 中是否已经存在 httpReady 标识
    const isReady = sessionStorage.getItem(this.HTTP_READY_KEY) === 'true'
    if (isReady) {
      // 如果已经存在 httpReady 标识，则将 readyPromise 标记为已完成
      this.readyPromise.resolve()
    }

    this.init()
  }

  public init() {
    this.instance = axios.create({
      baseURL: getBaseURL(),
      headers: {
        'Content-Type': 'application/json;charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
      },
      timeout: 20000,
      withCredentials: false,
      responseType: 'json',
    })

    this.instance.interceptors.request.use((config: InternalRequestConfig) => {
      if (config.mock) {
        // 替换 adapter，直接返回自定义响应
        config.adapter = async () => {
          return Promise.resolve({
            data: await Promise.resolve(config.mock(config)),
            status: 200,
            statusText: 'OK',
            headers: new AxiosHeaders({ 'content-type': 'application/json' }),
            config, // 包含原始的请求配置
          })
        }
      }

      // 在这里可以添加请求拦截器的逻辑，例如添加请求头、处理请求参数等
      if (config.loading) {
        // TODO: 添加全局 loading
      }

      return config
    })

    this.instance.interceptors.response.use(
      (response: Response) => {
        // 在这里可以添加响应拦截器的逻辑，例如处理响应数据、处理错误等
        if (response.config.loading) {
          // 关闭loading
        }

        if (response.config.responseType === 'blob') {
          response.data = { code: '0000', data: response.data }

          // TODO: 这里直接返回是否必要
          return response
        }

        // toast 默认开启，可以通过 config.toast 来控制是否显示
        if (!SUCCESS_CODES.includes(response.data.code) && response.config.toast !== false) {
          message.error(response.data.message || response.data.msg)
        }

        if (UN_AUTHORIZED_CODES.includes(response.data.code) || response.data.ret === 302) {
          unauthorize(response)
        }

        if (response.headers.token) {
          sessionStorage.setItem('tokenValue', response.headers.token)
        }

        if (response.headers['content-type'].search('image') > -1) {
          response.data = {
            data: response.data,
            imageType: response.headers['content-type'],
          }
        }

        if (ERROR_CODES.includes(response.data.code)) {
          return Promise.reject(response)
        }

        return response
      },
      (error) => {
        // 在这里可以处理请求错误，例如显示错误提示、跳转到错误页面等
        if (error.config.toast !== false) {
          if (error.response) {
            const msg = error.response?.status === 403 ? '无权限，请联系管理员！' : `${error.response.status} ${error.response.statusText}`
            message.error(msg)
          }
          else {
            message.error(error.message)
          }
        }
        return Promise.reject(error)
      },
    )
  }

  private request<T = any, P = any>(config: RequestConfig<T, P>) {
    // eslint-disable-next-line no-async-promise-executor
    return new Promise<ResponseData<T>>(async (resolve, reject) => {
      try {
        // 在发送请求之前，需要等待引擎加载完成
        await this.readyPromise.promise

        const res = await this.instance.request<ResponseData<T>>(config)

        const isSuccess = SUCCESS_CODES.includes(res?.data.code)
        isSuccess ? resolve(res?.data) : reject(res?.data)
      }
      catch (error) {
        return reject(error)
      }
    })
  }

  public get<T = any, P = any>(url: string, params?: P, config?: RequestConfig<T, P>) {
    return this.request<T, P>({ method: 'get', url, params, ...config })
  }

  public delete<T = any, P = any>(url: string, params?: P, config?: RequestConfig<T, P>) {
    return this.request<T, P>({ method: 'delete', url, params, ...config })
  }

  public put<T = any, P = any>(url: string, data?: P, config?: RequestConfig<T, P>) {
    return this.request<T, P>({ method: 'put', url, data, ...config })
  }

  public post<T = any, P = Record<string, any>>(
    url: string,
    data?: P,
    config?: RequestConfig<T, P>,
  ) {
    const dataConfig = !isNil(data)
      ? { data: Object.fromEntries(Object.entries(data).map(([key, value]) => [key, value ?? ''])) as P }
      : {}

    return this.request<T, P>({
      method: 'post',
      url,
      ...dataConfig,
      ...config,
    })
  }

  public getBlob(url: string, params?: any, config?: RequestConfig) {
    return this.request({
      method: 'get',
      url,
      params,
      responseType: 'blob',
      ...config,
    })
  }

  public getStream(url: string, data?: any, config?: RequestConfig) {
    return this.request({
      method: 'get',
      url,
      data,
      responseType: 'blob',
      ...config,
    })
  }

  public postStream(url: string, data?: any, config?: RequestConfig) {
    return this.request({
      method: 'post',
      url,
      data,
      responseType: 'blob',
      ...config,
    })
  }

  public postForm<T = any, P = any>(
    url: string,
    data: P,
    config?: RequestConfig<T, URLSearchParams>,
  ) {
    const formData = new URLSearchParams()
    Object.keys(data).forEach((key) => {
      formData.append(key, (data as any)[key] ?? '')
    })

    return this.request<T, URLSearchParams>({
      method: 'post',
      url,
      data: formData,
      ...config,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...config?.headers,
      },
    })
  }

  public postFormData<T = any, P = Record<string, any>>(
    url: string,
    data: P,
    config?: RequestConfig<T, P>,
  ) {
    const formDataConfig: RequestConfig<T, P> = {
      method: 'post',
      url,
      data,
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    }

    return this.request<T, P>(formDataConfig)
  }

  public postBlob(url: string, data?: any, config?: RequestConfig) {
    return this.request({
      method: 'post',
      url,
      data,
      responseType: 'blob',
      ...config,
    })
  }
}

export default new HttpClient()
