import Socket from './ws'

export const RpaCvPicker = new Socket('cv_picker/picker', {
  noInitCreat: true,
  port: 8003,
  isReconnect: false,
  timeout: 1000 * 10, // 10s
})
