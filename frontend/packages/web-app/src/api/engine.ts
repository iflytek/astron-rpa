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
export function startSchedulingMode(data) {
  return http.post('/scheduler/terminal/start', data)
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

/**
 * @description: 获取凭证列表
 * @returns 凭证列表
 */
export async function getCredentialList() {
  const res = await http.get<{ name: string }[]>('/scheduler/credential/list')
  return res.data || []
}

/**
 * @description: 创建凭证
 * @param data 凭证信息
 * @returns 
 */
export async function createCredential(data: { name: string, password: string }) {
  return http.post('/scheduler/credential/create', data)
}

/**
 * @description: 删除凭证
 * @param data 凭证信息
 * @returns 
 */
export async function deleteCredential(name: string) {
  return http.post('/scheduler/credential/delete', { name })
}

/**
 * @description: 检查凭证是否存在
 * @param name 凭证名称
 * @returns 是否存在
 */
export async function checkCredentialExists(name: string) {
  const res = await http.get<{ exists: boolean }>('/scheduler/credential/exists', { name })
  return !!res?.data?.exists
}
