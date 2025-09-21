// packages/web-app/src/types/normalTable.d.ts

// 定义表单组件类型
export type FormComponentType
  = | 'input'
    | 'select'
    | 'datePicker'
    | 'rangePicker'
    | 'cascader'
    | 'treeSelect'
    | 'checkbox'
    | 'radio'
    | 'switch'
    | 'back'
    | 'filter'

// 定义按钮类型
export type ButtonType = 'default' | 'primary' | 'dashed' | 'link' | 'text'

// 定义表格尺寸
export type TableSize = 'small' | 'middle' | 'large'

// 定义分页尺寸
export type PaginationSize = 'small' | 'default'

// 表单配置项接口
export interface FormItemConfig {
  componentType: FormComponentType
  bind: string
  label?: string
  placeholder?: string
  prefix?: any
  suffix?: any
  options?: Array<{
    label: string
    value: any
    disabled?: boolean
  }>
  span?: number
  hidden?: boolean
  disabled?: boolean
  required?: boolean
  rules?: any[]
  defaultValue?: any
  isTrim?: boolean
  [key: string]: any
}

// 按钮配置项接口
export interface ButtonItemConfig {
  label: string
  action?: string
  clickFn?: (...args: any[]) => void
  type?: ButtonType
  hidden?: boolean
  disabled?: boolean
  danger?: boolean
  btnType?: 'button' | 'dropdown'
  options?: Array<{
    key: string
    label: string
    clickFn?: (...args: any[]) => void
  }>
  [key: string]: any
}

// 表格列配置接口
export interface TableColumnConfig {
  title: string
  dataIndex: string
  key: string
  width?: number | string
  ellipsis?: boolean
  sorter?: boolean | ((a: any, b: any) => number)
  customRender?: (params: { record: any, text: any, index: number }) => any
  [key: string]: any
}

// 表格属性配置接口
export interface TablePropsConfig {
  columns: TableColumnConfig[]
  rowKey?: string
  size?: TableSize
  customRow?: (record: any) => any
  [key: string]: any
}

// 分页参数配置接口
export interface PageParamsConfig {
  pageNoName?: string
  pageSizeName?: string
}

// 排序参数配置接口
export interface OrderParamsConfig {
  orderName?: string
  orderStatus?: string
}

// 分页配置接口
export interface PageConfig {
  total?: number
  current?: number
  pageSize?: number
  pageSizeOptions?: string[]
  size?: PaginationSize
  showSizeChanger?: boolean
  showQuickJumper?: boolean
  [key: string]: any
}

// 数据获取函数类型
export type GetDataFunction = (params: Record<string, any>) => Promise<{
  records: any[]
  total: number
  [key: string]: any
}>

// 主要的 tableOption 接口
export interface TableOption {
  // 基础配置
  refresh?: boolean
  immediate?: boolean
  page?: boolean
  size?: TableSize
  emptyText?: string

  // 数据相关
  getData: GetDataFunction
  params?: Record<string, any>

  // 表单配置
  formList?: FormItemConfig[]
  formListAlign?: 'left' | 'right'

  // 按钮配置
  buttonList?: ButtonItemConfig[]
  buttonListAlign?: 'left' | 'right'

  // 表格配置
  tableProps: TablePropsConfig
  tableCellHeight?: number

  // 分页配置
  pageParams?: PageParamsConfig
  pageConfig?: PageConfig

  // 排序配置
  orderParams?: OrderParamsConfig

  [key: string]: any
}
