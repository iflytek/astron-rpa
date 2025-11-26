import Socket from './ws'

export const RpaExecutor = new Socket('scheduler/executor', {
  noInitCreat: true,
  port: 13159,
  isReconnect: false,
})
