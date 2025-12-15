import http from './http'

/**
 * @description: 获取应用执行记录列表数据
 */
export function getExecuteLst(data) {
  return http.post('/robot/robot-record/list', data)
}

export function delExecute(data: { recordIds: string[] }) {
  return http.post('/robot/robot-record/delete-robot-execute-records', data)
}

/**
 * @description: 获取应用执行记录列表数据
 */
export function getTaskExecuteLst(data) {
  return http.post('/robot/task-execute/list', data)
}

export function delTaskExecute(data: { taskExecuteIdList: string[] }) {
  return http.post('/robot/task-execute/batch-delete', data)
}

/**
 * @description: 获取特定版本应用执行记录列表数据
 */
export function getlogs(data) {
  return http.post('/robot/robot-record/log', data)
}
