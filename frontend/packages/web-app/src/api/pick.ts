import Socket from './ws'

export const RpaPicker = new Socket('picker/picker', {
  noInitCreat: true,
  port: 13159,
  isReconnect: false,
  timeout: 1000 * 10, // 10s
})
