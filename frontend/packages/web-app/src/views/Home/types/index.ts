import type { Fun } from '@/types/common'

// 表格数据属性
export interface Resource {
  createTime?: string
  creator?: string
  dataPath?: string
  groupIds?: null | string
  marketName?: string
  menuRight?: { downloadLocal: boolean, edit: boolean }
  mode?: string
  resourceId?: string
  resourceName?: string
  resourceType?: string
  terminalType?: string
  updateTime?: string
}

// 函数资源类型
export interface ResourceFn {
  [id: string]: Fun
}

// 表格操作栏基本类型
export interface TableBaseAction {
  key: string
  text: string
  icon?: string
  clickFn?: (...args: any[]) => void
  disableFn?: (...args: any[]) => void
  disableTip?: string
  action?: string
}

export interface TableOrdinaryAction extends TableBaseAction {
  // icon: VNode | string
  icon: any
}

export interface TableMoreAction extends TableBaseAction {
  parentKey?: string
  hideKey?: string | string[]
  icon?: any
}

export interface resOption {
  code: string
  msg: string | null
  data: any
}

export interface TaskFormState {
  taskId: string
  name: string
  description: string
  executeSequence: string[]
  exceptionHandleWay: string
  taskType?: string
  startAt: string
  endAt: string
  timeTask: {
    runMode: string
    cycleFrequency: string
    cycleNum: number
    cycleUnit: string
    scheduleType: string
    scheduleRule: {
      second: number
      minute: number
      hour: number
      date: number
      month: number
      year: number
      dayOfWeek: number
    }
    cronExpression: string
  }
  taskEnabled: boolean
}

export interface robotItem {
  robotId: string
  robotName: string
  updateTime: string
  version: string | number
  appId?: string
  sourceName?: string
  editEnable?: number
  publishStatus?: string
}
