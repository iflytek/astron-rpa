import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { FetchEventSourceInit } from '@microsoft/fetch-event-source'

/**
 * SSE 流式接口
 * @param url 接口地址
 * @param params 参数
 * @param options 请求配置
 * @param sCB 成功回调
 * @param eCB 失败回调
 * @returns
 */
export function sseRequest(
  url: string,
  params: Record<string, any>,
  options: FetchEventSourceInit,
  sCB: FetchEventSourceInit['onmessage'],
  eCB?: FetchEventSourceInit['onerror'],
) {
  const controller = new AbortController()

  fetchEventSource(url, {
    method: 'POST',
    signal: controller.signal,
    mode: 'cors',
    // mode: 'no-cors',
    headers: {
      'Content-Type': 'application/json',
      'Accept': '*/*',
    },
    body: JSON.stringify(params),
    onopen: async (res) => {
      console.log('sse open', res)
    },
    ...options || {},
    onmessage(msg) {
      console.log('sse msg', msg)
      sCB(msg)
    },
    onerror(err) {
      // 必须抛出错误才会停止
      console.log('sse error', err)
      eCB?.(err)
      throw err
    },
  })

  return controller
};
