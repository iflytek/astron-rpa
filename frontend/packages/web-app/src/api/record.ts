import type { ITableResponse } from '@/types/normalTable'

import http from './http'

/**
 * @description: 获取应用执行记录列表数据
 */
export async function getExecuteLst(data) {
  const res = await http.post<ITableResponse>('/api/robot/robot-record/list', data)
  return res.data || { records: [], total: 0 }
}

export function delExecute(data: { recordIds: string[] }) {
  return http.post('/api/robot/robot-record/delete-robot-execute-records', data)
}

export function delTaskExecute(data: { taskExecuteIdList: string[] }) {
  return http.post('/api/robot/task-execute/batch-delete', data)
}

/**
 * @description: 获取特定版本应用执行记录列表数据
 */
export function getlogs(data) {
  return http.post('/api/robot/robot-record/log', data)
}
