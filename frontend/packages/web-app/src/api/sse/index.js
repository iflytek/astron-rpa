// export default SSEClient
import { fetchEventSource } from '@microsoft/fetch-event-source'

// SSE post请求
// const controller = new AbortController();
// const signal = controller.signal;

/*
 * url 接口地址
 * params 参数
 * sCB 成功回调
 * eCB 失败回调
*/
export function sseRequest(url, params, options, sCB, eCB) {
  fetchEventSource(url, {
    method: 'POST',
    // signal: signal,
    mode: 'cors',
    // mode: 'no-cors',
    headers: {
      'Content-Type': 'application/json',
      'Accept': '*/*',
    },
    body: JSON.stringify(params),
    responseType: 'text/event-stream',
    ...options,
    onopen(res) {
      console.log('sse open', res)
    },
    onmessage(msg) {
      console.log('sse msg', msg)
      sCB(msg)
    },
    onerror(err) {
      // 必须抛出错误才会停止
      console.log('sse error', err)
      eCB(err)
      throw err
    },
  })
};
