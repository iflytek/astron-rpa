import Socket from './ws'

export const RpaHighlight = new Socket('', {
  url: 'ws://localhost:8080',
  noInitCreat: true,
  port: 8080,
  isReconnect: true,
  timeout: 1000 * 10, // 10s
})