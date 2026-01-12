/**
 * 带超时功能的 Promise 包装器
 * @param promise 要包装的 Promise
 * @param timeout 超时时间（毫秒）
 * @param timeoutMessage 超时时的错误消息，默认为 'Operation timed out'
 * @returns 包装后的 Promise，会在超时时 reject
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeout: number,
  timeoutMessage: string = 'Operation timed out'
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    // 设置超时定时器
    const timeoutId = setTimeout(() => {
      reject(new Error(timeoutMessage))
    }, timeout)

    // 执行原始 Promise
    promise.then(resolve).catch(reject).finally(() => clearTimeout(timeoutId))
  })
}

/**
 * 带超时功能的异步函数包装器
 * @param asyncFn 要包装的异步函数
 * @param timeout 超时时间（毫秒）
 * @param timeoutMessage 超时时的错误消息，默认为 'Operation timed out'
 * @returns 包装后的异步函数
 */
export function createTimeoutWrapper<T extends (...args: any[]) => Promise<any>>(
  asyncFn: T,
  timeout: number,
  timeoutMessage: string = 'Operation timed out'
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  return (...args: Parameters<T>): Promise<ReturnType<T>> => {
    return withTimeout(asyncFn(...args), timeout, timeoutMessage)
  }
}

export interface RetryOptions {
  timeout?: number
  maxRetries?: number
  retryDelay?: number
  timeoutMessage?: string
  shouldRetry?: (error: Error) => boolean
}

/**
 * 带超时和重试功能的 Promise 包装器
 * @param promiseFn 返回 Promise 的函数
 * @param options 配置选项
 * @returns 包装后的 Promise
 */
export function withTimeoutAndRetry<T>(
  promiseFn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    timeout = 5000,
    maxRetries = 3,
    retryDelay = 1000,
    timeoutMessage = 'Operation timed out',
    shouldRetry = (error: Error) => !error.message.includes('timeout')
  } = options

  return new Promise<T>((resolve, reject) => {
    let retries = 0

    const attempt = () => {
      const timeoutPromise = new Promise<T>((_, rejectTimeout) => {
        setTimeout(() => {
          rejectTimeout(new Error(timeoutMessage))
        }, timeout)
      })

      Promise.race([promiseFn(), timeoutPromise])
        .then(resolve)
        .catch((error) => {
          retries++

          if (retries < maxRetries && shouldRetry(error)) {
            setTimeout(attempt, retryDelay)
          } else {
            reject(error)
          }
        })
    }

    attempt()
  })
}
