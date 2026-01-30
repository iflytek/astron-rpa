import http from './http'

// 启动服务
export function startPickServices(data) {
  return http.post('/scheduler/picker/start', data)
}

// 停止服务
export function stopPickServices(data) {
  return http.post('/scheduler/picker/stop', data)
}

// 切换为调度模式
export function startSchedulingMode() {
  return http.post('/scheduler/terminal/start', {})
}

// 退出调度模式
export function endSchedulingMode() {
  return http.post('/scheduler/terminal/end', {})
}

// 调度模式-中止当前任务
export function stopSchedulingTask() {
  return http.post('/scheduler/executor/stop_list', {})
}

// 查询客户端状态 busy/free
export function getTermianlStatus() {
  return http.post('/scheduler/executor/status', {})
}
