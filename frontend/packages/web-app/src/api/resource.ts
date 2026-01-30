import type { FlowItem } from '@/views/Arrange/types/flow'

import type { RequestConfig } from './http'
import http from './http'
import { sseRequest } from './sse'
import { getBaseURL } from './http/env'

// 流程执行
export function flowRun(data) {
  return http.post('/api/project/flow/run', data)
}

export interface StartExecutorParams {
  project_id: string | number
  exec_position?: string
  process_id?: string | number
  jwt?: string
  debug?: string
  recording_config?: string
  hide_log_window?: boolean
  project_name?: string
  open_virtual_desk?: string
  line?: string | number
  end_line?: string | number
}
export async function startExecutor(data: StartExecutorParams) {
  const res = await http.post<{ addr: string }>('/scheduler/executor/run', data, { timeout: 0 })
  return res.data.addr
}

export function stopExecutor(data: { project_id: string | number }) {
  return http.post('/scheduler/executor/stop', data)
}

// 流程保存
export function flowSave(data: { robotId: string, processId: string, processJson: string }) {
  return http.post('/api/robot/process/save', data, { timeout: 10 * 1000 })
}

// 获取当前流程数据
export function getProcess(data: { robotId: string, processId: string }) {
  return http.post('/api/robot/process/process-json', data)
}

export async function getProcessAndCodeList(data: { robotId: string }): Promise<RPA.Flow.ProcessModule[]> {
  const res = await http.post<RPA.Flow.ProcessModule[]>('/api/robot/module/processModuleList', data)
  return res.data
}

/**
 * 获取 python 模块代码内容
 */
export async function getProcessPyCode(data: { robotId: string, mode?: string, moduleId: string }): Promise<string> {
  // mode 为空时，默认值为 EDIT_PAGE
  // EDIT_PAGE - 编辑页
  // PROJECT_LIST - 设计器列表页
  // EXECUTOR - 执行器应用列表页
  // CRONTAB - 触发器
  if (!data.mode) {
    data.mode = 'EDIT_PAGE'
  }

  const res = await http.post<{ moduleContent: string }>('/api/robot/module/open', data)
  return res.data.moduleContent
}

/**
 * 删除 python 模块代码内容
 */
export async function deleteProcessPyCode(moduleId: string) {
  const res = await http.get<boolean>('/api/robot/module/delete', { moduleId })
  return res.data
}

/**
 * 保存 python 模块代码内容
 */
export async function saveProcessPyCode(data: { robotId: string, moduleId: string, moduleContent: string }): Promise<boolean> {
  const res = await http.post<boolean>('/api/robot/module/save', data)
  return res.data
}

/**
 * 获取新增 Python 模块的名称
 */
export async function genProcessPyCodeName(params: { robotId: string }) {
  const res = await http.get<string>('/api/robot/module/newModuleName', params)
  return res.data
}

/**
 * 新增 Python 模块
 */
export async function addProcessPyCode(data: { robotId: string, moduleName: string }): Promise<string> {
  const res = await http.post<{ moduleId: string }>('/api/robot/module/create', data)
  return res.data.moduleId
}

/**
 * 复制 Python 模块
 */
export async function copyProcessPyCode(data: { robotId: string, moduleId: string }): Promise<unknown> {
  const res = await http.post<{ moduleId: string }>('/api/robot/process/copy', null, { params: { robotId: data.robotId, processId: data.moduleId, type: 'module' } })
  return res.data
}

/**
 * 重命名 Python 模块
 */
export async function renameProcessPyCode(data: { robotId: string, moduleId: string, moduleName: string }) {
  const res = await http.post('/api/robot/module/rename', data)
  return res.data
}

/**
 * 获取代码模块列表
 */
export async function getProcessPyCodeList(data: { robotId: string }) {
  const res = await http.post<{ moduleId: string, name: string }[]>('/api/robot/module/moduleList', data)
  return res.data
}

// 获取新增子流程的名称
export async function genProcessName(data: { robotId: string }) {
  const res = await http.post<string>('/api/robot/process/name', data)
  return res.data
}

// 新增子流程
export async function addProcess(data: { robotId: string, processName: string }): Promise<string> {
  const res = await http.post<{ processId: string }>('/api/robot/process/create', data)
  return res.data.processId
}

// 子流程重命名
export function renameProcess(data: { robotId: string, processId: string, processName: string }) {
  return http.post('/api/robot/process/rename', data)
}

// 删除子流程
export async function delProcess(data: FlowItem) {
  const res = await http.post<boolean>('/api/robot/process/delete', data)
  return res.data
}

// 复制子流程
export async function copyProcess(data: { robotId: string, processId: string }): Promise<unknown> {
  const res = await http.post<{ processId: string }>('/api/robot/process/copy', null, { params: { ...data, type: 'process' } })
  return res.data
}

type ElementType = 'common' | 'cv'
//  新建元素/图像分组
export function addElementGroup(params: { robotId: string, elementType?: ElementType, groupName: string }) {
  return http.post('/api/robot/group/create', null, { params })
}

//  重命名元素/图像分组
export function renameElementGroup(data: { robotId: string, groupId: string, elementType?: ElementType, groupName: string }) {
  return http.post('/api/robot/group/rename', data)
}

//  删除元素/图像分组
export function delElementGroup(params: { robotId: string, groupId: string }) {
  return http.post('/api/robot/group/delete', null, { params })
}

//  获取所有元素/图像
export function getElementsAll(params: { robotId: string, elementType?: ElementType }) {
  return http.post('/api/robot/element/all', null, { params })
}

// 查询元素/图像详细信息
export function getElementDetail(params: { robotId: string, elementId: string }) {
  return http.post('/api/robot/element/detail', null, { params })
}

// 保存元素信息----废弃
export function postSaveElement(data: any) {
  return http.post('/api/robot/element/save', data)
}

// 创建元素/图像信息
export function addElement(data: any) {
  return http.post<{ elementId: string, groupId: string }>('/api/robot/element/create', data)
}

// 更新元素/图像信息
export function updateElement(data: any) {
  return http.post('/api/robot/element/update', data)
}

// 移动元素/图像到分组
export function moveElement(params: { robotId: string, groupId: string, elementId: string }) {
  return http.post('/api/robot/element/move', null, { params })
}

// 删除元素/图像
export function postDeleteElement(params: { robotId: string, elementId: string }) {
  return http.post('/api/robot/element/delete', null, { params })
}

// 生成cv拾取图像名称
export function generateCvElementName(params: { robotId: string }) {
  return http.post('/api/robot/element/image/create-name', null, { params })
}

// 创建元素副本
export function createElementCopy(params: { robotId: string, elementId: string }) {
  return http.post('/api/robot/element/copy', null, { params })
}

// 新增全局变量
export function addGlobalVariable(data: RPA.GlobalVariable) {
  return http.post('/api/robot/global/create', data)
}

// 保存全局变量
export function saveGlobalVariable(data: RPA.GlobalVariable) {
  return http.post('/api/robot/global/save', data)
}

// 查询全局变量
export function getGlobalVariable(params: { robotId: string }) {
  return http.post<RPA.GlobalVariable[]>('/api/robot/global/all', null, { params })
}

// 查询全局变量名称列表
export function getGlobalVariableNameList(params: { robotId: string }) {
  return http.post('/api/robot/global/name-list', null, { params })
}

// 删除全局变量
export function deleteGlobalVariable(data: { robotId: string, globalId: string }) {
  return http.post('/api/robot/global/delete', data)
}

// 上传文件
export async function uploadFile(data: { file: File }, config: RequestConfig = {}) {
  const res = await http.postFormData<string>('/api/resource/file/upload', data, { timeout: 5000000, ...config })
  return res.data
}

// 发布上传视频文件
export async function uploadVideoFile(data: { file: File }, config: RequestConfig = {}) {
  const res = await http.postFormData<string>('/api/resource/file/upload-video', data, { timeout: 5000000, ...config })
  return res.data
}

// 查询依赖包版本号
export function packageVersion(params: { robotId: string, packageName: string }) {
  return http.post('/scheduler/package/version', {
    project_id: params.robotId,
    package: params.packageName,
  }, { timeout: 0 })
}

// 新增依赖包
export function addPyPackageApi(data: { robotId: string, packageName: string, packageVersion: string, mirror: string }) {
  return http.post('/api/robot/require/add', data)
}
// 删除依赖包
export function deletePyPackageApi(data: { robotId: string, idList: Array<string> }) {
  return http.post('/api/robot/require/delete', data)
}
// 更新依赖包
export function updatePyPackageApi(data: { robotId: string, packageName: string, packageVersion: string, mirror: string }) {
  return http.post('/api/robot/require/update', data)
}
// 获取依赖包列表
export function getPyPackageListApi(data: { robotId: string }) {
  return http.post('/api/robot/require/list', data)
}
/**
 * 读取文件，流式
 */
export function fileRead(data: { path: string }) {
  return http.postBlob('/scheduler/file/read', data, { toast: false, timeout: 5000000 })
}
/**
 * 写文件
 * @params { path: string, mode: 'w' | 'a', content: string } w 覆盖写 a 追加写
 */
export function fileWrite(data: { path: string, mode: string, content: string }) {
  return http.post('/scheduler/file/write', data, { timeout: 5000000 })
}
/**
 * 获取HTML格式的粘贴板内容
 * @params { is_html: boolean }
 */
export async function getHTMLClip(data: { is_html: boolean }) {
  const res = await http.post('/scheduler/clipboard', data)
  return res.data
}

/**
 * 获取数据表格内容
 * @param projectId
 */
export async function getDataTable(projectId: string) {
  const res = await http.post<RPA.IDataTableSheets>(
    '/scheduler/datatable/open',
    {
      project_id: projectId,
      filename: 'data_table', // 目前单个工程只会有一个数据表格文件，因此文件名先写死
    },
    { toast: false },
  )
  return res.data
}

/**
 * 更新数据表格单元格
 * @param projectId
 * @param data
 * @returns
 */
export async function updateDataTable(projectId: string, data: RPA.IUpdateDataTableCell[]) {
  const res = await http.post(
    '/scheduler/datatable/update-cells',
    {
      project_id: projectId,
      filename: 'data_table',
      updates: data,
    },
    { toast: false },
  )
  return res.data
}

/**
 * 关闭数据表格文件监听
 * @param projectId
 */
export async function closeDataTable(projectId: string) {
  const res = await http.post(
    '/scheduler/datatable/close',
    {
      project_id: projectId,
      filename: 'data_table',
    },
    { toast: false },
  )
  return res.data
}

/**
 * 删除数据表格
 * @param projectId
 * @returns
 */
export async function deleteDataTable(projectId: string) {
  const res = await http.post(
    '/scheduler/datatable/delete',
    {
      project_id: projectId,
      filename: 'data_table',
    },
    { toast: false },
  )
  return res.data
}

/**
 * 监听数据表格
 * @param projectId
 * @param callback
 * @returns
 */
export function startDataTableListener<T>(projectId: string, callback?: (data: { event: string, data: T }) => void) {
  return sseRequest.get(
    `${getBaseURL()}/scheduler/datatable/stream?project_id=${projectId}&filename=data_table`,
    (res) => {
      try {
        const dataJson: T = JSON.parse(res.data)
        callback?.({ event: res.event, data: dataJson })
      }
      catch (error) {
        console.error('解析 SSE 数据失败:', error, res.data)
      }
    },
  )
}
