import Socket from './ws'

export const RpaExecutor = new Socket('scheduler/executor', {
  noInitCreat: true,
  port: 8003,
  isReconnect: false,
})
