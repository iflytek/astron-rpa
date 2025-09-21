import type { VNode } from 'vue'

// 列表资源类型
export interface resourceListType {
  key: string
  value: string
}

export interface ElementsPure {
  name: string
  key?: string
}

export interface ElementsT extends ElementsPure {
  type: string
  robotId: string
  groupName: string
  element: ElementsType
}

export interface ElementsType extends ElementsPure {
  id?: string // 创建时没有id
  name: string
  imageId?: string
  parentImageId?: string // 图片id
  icon?: string
  elementData?: string
  groupName?: string // 所属组名
  groupId?: string // 所属组id
  imageUrl?: string
  parentImageUrl?: string // 图片地址
  elements?: ElementsType[]
  commonSubType?: string
}

export interface ElementsTree extends ElementsPure {
  name: string
  id: string
  elements: ElementsType[]
  groupName?: string
  icon?: string
  key?: string
}

// 自定义编辑数据类型
export interface CustomValueType {
  name: string
  value: string
}
// 可视化编辑数据属性类型
export interface DirectoryAttrItem {
  name: string
  value: string
  type: number
  checked: boolean
}
// 可视化编辑数据类型
export interface DirectoryItem {
  tag_name?: string // uia 是tag_name
  tag: string
  checked: boolean
  value: string
  attrs?: DirectoryAttrItem[]
  name?: string
  disable_keys?: string[]
}

export interface VarDataType {
  type: string
  value: string
}
export interface EleVariableType {
  rpa: 'special'
  value: VarDataType[]
}

export interface WebElementType {
  xpath: string
  cssSelector: string
  pathDirs?: Array<DirectoryItem>
  parentClass: string
  domain: string
  url: string
  shadowRoot: boolean
  tabTitle?: string
  tabUrl?: string
  favIconUrl?: string
  isFrame?: boolean
  checkType?: string
  frameId?: number
  iframeXpath?: string
  iframeCssSelector?: string
  tag?: string
  text?: string
}

export interface PickElementType {
  app: string
  path: DirectoryItem[] | WebElementType
  type: ElementType
  version?: string
  img?: {
    self: string
    parent: string
  }
  picker_type?: PickerType
  relative_path?: DirectoryItem[] // uia 的相似元素存在
  similar_count?: number // 相似元素个数
}

export interface PickParams {
  pick_sign: 'START' | 'VALIDATE' | 'RECORD'
  pick_type?: string
  record_action?: RecordAction
  data: string
  ext_data?: any
}

/**
 * 录制动作
 * RECORD_LISTENING: 开启录制监听
 * RECORD_START: 录制开始
 * RECORD_PAUSE: 录制暂停
 * RECORD_END：录制结束
 * RECORD_AUTOMIC_HOVER_START: 前端窗口hover住告知后端关闭拾取
 * RECORD_AUTOMIC_END: 选择原子能力结束 - 前端发送信号，后端告知前端拾取信息
 * RECORD_AUTOMIC_HOVER_END：鼠标悬停两秒元素 - 前端告知后端hover结束开启拾取
 */
export type RecordAction = 'RECORD_LISTENING' | 'RECORD_START' | 'RECORD_PAUSE' | 'RECORD_AUTOMIC_HOVER_START' | 'RECORD_AUTOMIC_END' | 'RECORD_AUTOMIC_HOVER_END' | 'RECORD_END'

export type PickStepType = 'new' | 'repick' | 'similar' | 'anchor'

export interface PickUseItemType {
  processId: string
  processName: string
  open?: boolean
  atoms?: Array<any>
}

type ElementType = 'uia' | 'web' | 'cv' | 'jab' | 'sap'
type PickerType = 'ELEMENT' | 'WINDOW' | 'POINT' | 'SIMILAR' | 'OTHERS'

export interface ElementData {
  version: string
  type: ElementType
  app: string
  path: any // uia 和 web 具体实现，cv 为空
  img: {
    self: string // 图片ID
    parent: string // 图片ID
  }
  pos?: Record<string, number | string> // 位置
  sr?: Record<string, number> // 分辨率
  picker_type: PickerType
}

export interface Element {
  id?: string
  name: string
  version?: string // elementData 协议版本
  type?: ElementType
  app?: string // 所属应用名称，当type为CV时，该字段无效。
  imageUrl?: string // 当前元素的图像
  parentImageUrl?: string // 父元素的图像，用于定位。当type为CV时，该字段为锚点。
  elementData?: string // 原始的元素数据，ElementData 的 JSON 字符串
  imageId?: string
  parentImageId?: string
}

export interface ElementGroup {
  id: string
  name: string
  elements: Element[]
}

export type ElementActionType = 'edit' | 'searchUse' | 'move' | 'delete' | 'copy' | 'repick' | 'copy-references' | 'quoted'

export type GroupContextMenuType = 'add' | 'rename' | 'delete' | 'elementPick'

export interface MenuItem {
  key: string
  label: string
  icon?: VNode
  type?: T
  menus?: Array<MenuItem>
  children?: Array<MenuItem>
}
