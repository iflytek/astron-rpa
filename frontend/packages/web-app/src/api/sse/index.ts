import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { FetchEventSourceInit } from '@microsoft/fetch-event-source'
import { isFunction } from 'lodash-es'

import { getBaseURL } from '../http/env'

/**
 * SSE 流式接口
 * @param url 接口地址
 * @param params 参数
 * @param options 请求配置
 * @param sCB 成功回调
 * @param eCB 失败回调
 * @returns
 */
function SSERequest(
  url: string,
  params: Record<string, any>,
  options: FetchEventSourceInit,
  sCB: FetchEventSourceInit['onmessage'],
  eCB?: FetchEventSourceInit['onerror'],
  cCB?: FetchEventSourceInit['onclose'],
) {
  const controller = new AbortController()
  const baseURL = getBaseURL()
  const finalUrl = new URL(url, baseURL).href

  fetchEventSource(finalUrl, {
    signal: controller.signal,
    mode: 'cors',
    // mode: 'no-cors',
    headers: {
      'Content-Type': 'application/json',
      'Accept': '*/*',
    },
    onopen: async (res) => {
      console.log('sse open', res)
    },
    ...(options || {}),
    ...(options?.method === 'GET' ? {} : { body: JSON.stringify(params) }),
    onmessage(msg) {
      console.log('sse msg', msg)
      sCB(msg)
    },
    onerror(err) {
      // 必须抛出错误才会停止
      console.log('sse error', err)
      isFunction(eCB) && eCB(err)
      throw err
    },
    onclose() {
      console.log('sse close')
      isFunction(cCB) && cCB()
    },
  })

  return controller
};

function get(url: string, callback: FetchEventSourceInit['onmessage'], errorCallback?: FetchEventSourceInit['onerror'], options?: FetchEventSourceInit, closeCallback?: FetchEventSourceInit['onclose']) {
  return SSERequest(url, null, { method: 'GET', ...options }, callback, errorCallback, closeCallback)
}

function post(url: string, data: Record<string, any>, callback: FetchEventSourceInit['onmessage'], errorCallback?: FetchEventSourceInit['onerror'], options?: FetchEventSourceInit, closeCallback?: FetchEventSourceInit['onclose']) {
  return SSERequest(url, data, { method: 'POST', ...options }, callback, errorCallback, closeCallback)
}

export const sseRequest = { get, post }
