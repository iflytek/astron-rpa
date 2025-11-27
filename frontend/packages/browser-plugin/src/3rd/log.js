export const log = {
  info: (...args) => {
    console.log('[info]', ...args)
  },
  warn: (...args) => {
    console.warn('[warn]', ...args)
  },
  error: (...args) => {
    console.error('[error]', ...args)
  },
  time: (label) => {
    console.time(label)
  },
  timeEnd: (label) => {
    console.timeEnd(label)
  }
}