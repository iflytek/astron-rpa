import { pickBy } from 'lodash-es'

import http from './http'

/**
 * @description: 获取执行器机器人列表数据
 */
export function getRobotLst(data) {
  return http.post('/robot/robot-execute/execute-list', data)
}

/**
 * 检测机器人是否被计划任务引用被返回引用这个机器人的计划任务的数组
 */
export function isRobotInTask(params) {
  return http.get('/robot/robot-execute/delete-robot-res', params)
}

/**
 * @description: 删除机器人
 */
export function deleteRobot(data) {
  return http.post('/robot/robot-execute/delete-robot', data)
}

/**
 * @description: 发布机器人
 */
export function publishRobot<T = any>(data: T) {
  return http.post('/robot/robot-version/publish', data)
}

/**
 * @description: 获取机器人上次发版信息回显
 */
export async function getRobotLastVersion(robotId: string) {
  const res = await http.post('/robot/robot-version/latest-info', { robotId })
  return pickBy(res.data, value => value !== null)
}

/**
 * @description: 获取该机器人是否允许外部调用
 */

export async function getRobotLastIsExternalCall(robotId: string) {
  console.log('robotId', robotId)
  const res = await http.get(`/rpa-openapi/workflows/get/${robotId}`)
  return pickBy(res?.data?.workflow, value => value !== null)
}

/**
 * @description: 保存是否允许外部调用的配置
 */
export function setRobotIsExternalCall(data) {
  return http.post('/rpa-openapi/workflows/upsert', data)
}

/**
 * @description: 获取机器人名称以英文翻译
 */
export function getRobotEnglishName(name: string) {
  console.log('name', name)
  return http.post('/rpa-ai-service/v1/chat/prompt', { prompt_type: 'translate', params: { name } })
}

/**
 * @description: 轮询执行器下机器人更新状态
 */
export function getRobotUpdateStatus(data) {
  return http.post('/robot/robot-execute/execute-update-check', data)
}

/**
 * @description: 更新执行器下机器人
 */
export function updateRobot(data) {
  return http.post('/robot/robot-execute/update/pull', data)
}

/**
 * @description: 机器人重名校验
 */
export function checkRobotName(data: { robotId: string, name: string }) {
  return http.post('/robot/robot-version/same-name', data)
}

/**
 * 我创建的机器人详情
 */
export async function getMyRobotDetail(robotId: string) {
  const res = await http.get('/robot/robot-design/my-robot-detail', { robotId })
  return res.data
}

/**
 * 我获取的机器人详情
 */
export async function getMarketRobotDetail(robotId: string) {
  const res = await http.get('/robot/robot-design/market-robot-detail', { robotId })
  const { myRobotDetailVo, sourceName, versionInfoList } = res.data

  return { ...myRobotDetailVo, sourceName, versionList: versionInfoList }
}

/**
 * @description: 获取机器人详情
 */
export async function getRobotRecordOverview(data: { robotId: string, version: number, deadline: string }) {
  const res = await http.post('/robot/robot-record/detail/overview', data)
  return res.data
}

/**
 * @description: 查询机器人的所有流程数据
 */
export async function getRobotProcessList(robotId: string): Promise<any[]> {
  const res = await http.post('/robot/process/all-data', { robotId })
  return res.data.map(it => ({
    ...it,
    processContent: JSON.parse(it.processContent),
  }))
}

/**
 * 保存机器人自定义配置参数
 */
export async function saveRobotConfigParamValue(data: RPA.CreateConfigParamData[], mode: string, robotId: string) {
  return http.post('/robot/param/saveUserParam', { paramList: data, mode, robotId })
}

/**
 * 执行器机器人详情基本信息
 */
export async function getRobotBasicInfo(robotId: string) {
  const res = await http.get('/robot/robot-execute/robot-detail', { robotId })
  return res.data
}

/**
 * 获取编辑页内组件管理列表
 */
export async function getComponentManageList(robotId: string) {
  const res = await http.post<RPA.ComponentManageItem[]>('/robot/component/editing/manage-list', { robotId, version: 0 })
  return res.data
}

/**
 * 安装组件
 */
export async function installComponent(data: { robotId: string, componentId: string }) {
  const res = await http.post<string>('/robot/component-robot-block/delete', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}

/**
 * 移除组件
 */
export async function removeComponent(data: { robotId: string, componentId: string }) {
  const res = await http.post<string>('/robot/component-robot-block/add', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}

/**
 * 添加组件引用
 */
export async function addComponentUse(data: { componentId: string, robotId: string, robotVersion?: number }) {
  const res = await http.post<boolean>('/robot/component-robot-use/add', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}

/**
 * 删除组件引用
 */
export async function deleteComponentUse(data: { componentId: string, robotId: string, robotVersion?: number }) {
  const res = await http.post<boolean>('/robot/component-robot-use/delete', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}

/**
 * 更新组件引用
 */
export async function updateComponent(data: { robotId: string, componentId: string, componentVersion: number }) {
  const res = await http.post<string>('/robot/component-robot-use/update', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}

/**
 * 获取组件详情
 */
export async function getComponentDetail(data: { robotId: string, componentId: string }) {
  const res = await http.post<RPA.ComponentManageItem>('/robot/component/editing/info', { ...data, mode: 'EDIT_PAGE' })
  return res.data
}
