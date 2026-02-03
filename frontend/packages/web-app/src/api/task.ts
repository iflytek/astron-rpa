import type { Task } from '@/types/schedule'
import type { ITableResponse } from '@/types/normalTable'

import http from './http'

/**
 * @description: 获取计划任务列表数据
 */
export async function getScheduleLst(data) {
  const res = await http.post<ITableResponse>('/api/robot/triggerTask/page/list', data)
  return res.data || { records: [], total: 0 }
}

/**
 * @description: cron表达式校验
 */
export function checkCronExpression(data) {
  return http.post('/api/robot/task/corn/check', data, { toast: false })
}

/**
 * @description: 获取计划任务执行记录列表数据
 */
export async function getTaskExecuteLst(data) {
  const res = await http.post<ITableResponse>('/api/robot/task-execute/list', data)
  return res.data || { records: [], total: 0 }
}

/**
 * @description: 倒计时的计划任务取消
 */
export function taskCancel(data) {
  return http.post('/scheduler/crontab/cancel', data)
}

// 手动触发
export function manualTrigger(data: { task_id: string }) {
  return http.post('/trigger/task/run', data)
}

// taskNotify 通知触发器更新
export function taskNotify(params = { event: 'normal' }) {
  return http.post('/trigger/task/notify', params, { toast: false })
}

// 获取计划任务未来执行时间
export function taskFutureTime(data: { task_id: string, times: number }) {
  return http.post('/trigger/task/future', data,)
}

// /task/future_with_no_create
export function taskFutureTimeNoCreate(data: { frequency_flag: string, times: number }) {
  return http.post('/trigger/task/future_with_no_create', data, { toast: false })
}

// 重命名校验
export async function isNameCopy(data: { name: string }) {
  const res = await http.get('/api/robot/triggerTask/isNameCopy', data)
  return res.data
}

// 应用列表
export function getRobotList(data: { name: string }) {
  return http.get('/api/robot/triggerTask/robotExe/list', data)
}

// 新增计划任务
export async function insertTask(data: Task) {
  const res = await http.post('/api/robot/triggerTask/insert', data)
  taskNotify()
  return res
}

// 获取单个计划任务接口
export function getTaskInfo(data: { taskId: string }) {
  return http.get('/api/robot/triggerTask/get', data)
}

// 删除单个计划任务接口
export async function deleteTask(data: { taskId: string }) {
  const res = await http.get('/api/robot/triggerTask/delete', data)
  taskNotify()
  return res
}
// 更新计划任务接口
export async function updateTask(data: Task) {
  const res = await http.post('/api/robot/triggerTask/update', data)
  taskNotify()
  return res
}
// 启用/禁用 计划任务
export async function enableTask(data: { taskId: string, enable: number }) {
  const res = await http.get('/api/robot/triggerTask/enable', data)
  taskNotify()
  return res
}

// 获取计划任务队列状态
export function getTaskQueueList(data) {
  return http.get('/trigger/task/queue/status', data)
}

// 移除计划任务队列
export function removeTaskQueue(data: { unique_id: string[] }) {
  return http.post('/trigger/task/queue/remove', data)
}

// 更新计划任务队列配置
export function updateTaskQueueConfig(data: { max_length: number, max_wait_minutes: number, deduplicate: boolean }) {
  return http.post('/trigger/task/queue/config', data)
}

// 获取计划任务队列配置
export function getTaskQueueConfig() {
  return http.get('/trigger/task/queue/config', {})
}
