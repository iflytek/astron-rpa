/** @format */

interface DataType {
  produceType: string // 抓取类型
  values: TableValueType[] | SimilarValueType[] // 数据
}

interface TableDataType extends DataType, ElementInfo {
  batchType?: 'normal' | 'head'
  produceType: 'table'
  xpath: string
  values: TableValueType[]
}

interface TableValueType {
  title: string // 单元格名称
  value: string[] // 单元格数据
  filterConfig: FilterConfig[] // 筛选条件
  colFilterConfig: FilterConfig[] // 列筛选条件
  colDataProcessConfig: DataProcessConfig[] // 列数据处理条件
}

export interface FilterConfig {
  filterAssociation: string // "and" / "or"
  logical: string
  parameter: string
}

export interface DataProcessConfig {
  processType: string // 处理类型
  isEnable: number // 是否启用
  parameters: Parameter[] // 处理条件
}

interface Parameter {
  // 字符串替换的处理条件
  [key: string]: any
}

export interface SimilarDataType extends DataType {
  batchType?: 'normal' | 'head'
  produceType: 'similar'
  values: SimilarValueType[]
}

interface SimilarValueType extends ElementInfo {
  title: string
  filterConfig: FilterConfig[] // 筛选条件
  colFilterConfig: FilterConfig[] // 列筛选条件
  colDataProcessConfig: DataProcessConfig[] // 列数据处理条件
  xpath: string
  value: ValueValue[]
}
interface ValueValue {
  attrs: Attrs
  text: string
}
interface Attrs {
  src: string
  href: string
  text: string
}

export interface SimilarDataParams {
  key: string
  data: SimilarDataType
}

export interface TableDataParams {
  key: string
  data: TableDataType
}

export interface BatchElementParams extends ElementInfo {
  produceType: 'table' | 'similar'
  values?: SimilarValueType[]
  openSourcePage?: boolean // 是否打开源页面
}

// 表格抓取对象
interface TablePickObject extends DataType, ElementInfo {
  isTable: boolean
  produceType: 'table'
  values: TableValueType[]
}

interface SimilarPickObject extends DataType, ElementInfo {
  isTable: boolean
  produceType: 'similar'
  values: SimilarValueType[]
}
//  抓取对象数据类型
type BatchPickObject = TablePickObject | SimilarPickObject
