// 变量类型当前放在 atom-meta.json 里
export type VariableType = RPA.VariableType

export type ArgumentValueType = 'other' | 'python' | 'var' // atom-meta 里会有 str，但已经弃用。需要确认前端有没有用到。
export interface ArgumentValue {
  type: string
  value: string
  data?: string // 元素信息
  varId?: string
  varName?: string
  varValue?: any
}

export interface NodeArgument {
  key: string
  show?: boolean
  value: string | number | boolean | ArgumentValue[]
}

export interface ProcessNode extends Record<string, any> {
  key: string // 原子能力的key
  version: string // 指向引用原子能力的版本
  id: string // 节点唯一ID。但似乎不是必须的？
  inputList: NodeArgument[] // 默认值可不填充，下同
  advanced: NodeArgument[]
  exception: NodeArgument[]
  outputList: NodeArgument[]
  alias: string // 别名
  disabled?: boolean // 是否禁用
  breakpoint?: boolean // 是否断点
  // collapsed: boolean
}

/**
 * 流程参数，影刀使用了，我们暂时没用到
 */
export interface ProcessVariable {
  id: string
  name: string
  type: VariableType
  value: string
  desc: string
  direction: 'input' | 'output'
}

export interface Process {
  id: string
  name: string
  nodes: ProcessNode[]
  // variables: ProcessVariable[] // 暂时不启用
}

export interface GlobalVariable {
  id: string
  name: string
  type: VariableType
  value: string
  desc: string
}

/**
 * 环境变量，用于本地存储密码等信息，服务端不保存 value
 */
export interface EnvVariable {
  id: string
  name: string
  type: VariableType
  value: null | string
  desc: string
}

export interface PythonPackage {
  name: string
  version: string
  mirror: string
}

export type ElementType = 'uia' | 'web' | 'cv' | 'jab'
export type PickerType = 'ELEMENT' | 'WINDOW' | 'POINT' | 'SIMILAR' | 'OTHERS'

export interface ElementData {
  version: string
  type: ElementType
  app: string
  path: any // uia 和 web 具体实现，cv 为空
  img: {
    self: string // 图片ID
    parent: string // 图片ID
  }
  pos?: Record<string, number> // 位置
  sr?: Record<string, number> // 分辨率
  picker_type: PickerType
}

export interface Element {
  id: string
  name: string
  version: string // elementData 协议版本
  type: ElementType
  app: string // 所属应用名称，当type为CV时，该字段无效。
  imageUrl: string // 当前元素的图像
  parentImageUrl: string // 父元素的图像，用于定位。当type为CV时，该字段为锚点。

  elementData: string // 原始的元素数据，ElementData 的 JSON 字符串
}

export interface ElementGroup {
  id: string
  name: string
  elements: Element[]
}

export interface Robot {
  id: string
  name: string

  processes: RPA.Flow.ProcessModule[]
  packages: PythonPackage[]

  global: GlobalVariable[]
  env: EnvVariable[]

  elements: ElementGroup[]
  images: ElementGroup[]
}
