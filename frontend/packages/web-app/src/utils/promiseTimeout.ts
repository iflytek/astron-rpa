class TimeoutError extends Error {
  constructor() {
    super('TimeoutError')
  }
}

/**
 * 设置 promise 超时
 * @param promise 需要设置超时的 promise
 * @param timeoutMillis 超时时间
 * @returns Promise<T>
 */
export function promiseTimeout<T>(promise: Promise<T>, timeoutMillis: number, params?: { default?: T }): Promise<T> {
  const error = new TimeoutError()

  let timeout: ReturnType<typeof setTimeout>

  return Promise.race([
    promise,
    new Promise<T>((resolve, reject) => {
      const defaultResult = params?.default
      timeout = setTimeout(() => defaultResult ? resolve(defaultResult) : reject(error), timeoutMillis)
    }),
  ]).then((v) => {
    clearTimeout(timeout)
    return v
  }, (err) => {
    clearTimeout(timeout)
    throw err
  })
}
