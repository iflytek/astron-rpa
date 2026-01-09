import http from './http'

// 新建工程
export function createProject(data) {
  return http.post('/robot/robot-design/create', data, { toast: true })
}

// 新建工程-数量校验
export function checkProjectNum() {
  return http.get('/robot/quota/check-designer', { toast: true })
}

/**
 * 检测应用是否被计划任务引用被返回引用这个应用的计划任务的数组
 */
export function isInTask(params) {
  return http.get('/robot/robot-design/delete-robot-res', params)
}

// 删除工程
export function delectProject(data) {
  return http.post('/robot/robot-design/delete-robot', data)
}

/**
 * @description: 获取设计器列表页列表数据
 */
export async function getDesignList(data) {
  const res = await http.post('/robot/robot-design/design-list', data)
  return res.data
}

/**
 * 分享至市场
 */
export function shareRobotToMarket(data) {
  return http.post('/robot/market-resource/share', data)
}

/**
 * 获取版本列表
 */
export async function getVersionLst<T>(params) {
  const res = await http.get<T>('/robot/robot-version/list4Design', params)
  return res.data
}

/**
 * 恢复版本
 */
export function versionRecover(data) {
  return http.post('/robot/robot-version/recover-version', data)
}

/**
 * 启用版本
 */
export function versionEnable(data) {
  return http.post('/robot/robot-version/enable-version', data)
}

/**
 * 重命名
 */
export function rename(params) {
  return http.get('/robot/robot-design/rename', params)
}

/**
 * 重命名校验
 */
export function renameCheck(params) {
  return http.get('/robot/robot-design/design-name-dup', params)
}

/**
 * 创建副本
 */
export function createCopy(params) {
  return http.get('/robot/robot-design/copy-design-robot', params)
}

/**
 * 创建副本
 */
export async function getDefaultName() {
  const res = await http.post<string>('/robot/robot-design/create-name')
  return res.data
}

/**
 * 获取组件列表
 */
export async function getComponentList(data: {
  name: string
  dataSource: 'create' | 'market'
  pageNum?: number
  pageSize?: number
  sortType?: string
}) {
  const res = await http.post('/robot/component/page-list', data)
  return res.data
}

// 新建组件
export function createComponent(params: { componentName: string }) {
  return http.get('/robot/component/create', params, { toast: true })
}

/**
 * 新建组件-获取默认组件名称
 */
export async function getDefaultComponentName() {
  const res = await http.post<string>('/robot/component/create-name', null, { toast: false })
  return res.data
}

/**
 * 检查组件名称是否重复
 */
export async function checkComponentName(params: { name: string, componentId?: string }) {
  const res = await http.post<boolean>('/robot/component/check-name', params, { toast: false })
  return res.data
}

/**
 * 重命名组件
 */
export function renameComponent(params: { newName: string, componentId: string }) {
  return http.get('/robot/component/rename', params)
}

/**
 * 删除组件
 */
export async function deleteComponent(params: { componentId: string }) {
  const res = await http.get<boolean>('/robot/component/delete', params)
  return res.data
}

/**
 * 创建副本组件名称
 */
export async function createCopyComponentName(params: { componentId: string }) {
  const res = await http.get<string>('/robot/component/copy/create-name', params)
  return res.data
}

/**
 * 创建副本
 */
export async function createCopyComponent(params: { componentId: string, name: string }) {
  const res = await http.get<boolean>('/robot/component/copy', params)
  return res.data
}

/**
 * 获取组件详情
 */
export async function getComponentDetail(params: { componentId: string }) {
  const res = await http.get<RPA.ComponentDetail>('/robot/component/info', params)
  return res.data
}

/**
 * 获取组件下一个版本号
 */
export async function getComponentNextVersion(params: { componentId: string }) {
  const res = await http.get<number>('/robot/component-version/next-version', params)
  return res.data
}

/**
 * 组件发版
 */
export async function publishComponent<T>(params: T) {
  const res = await http.post<boolean>('/robot/component-version/create', params)
  return res.data
}
