/** @format */
import type { WebElementType } from './resource.d'

export interface BatchDataTableMenu {
  key: string
  label: string
  active?: boolean
  showType?: 'similar' | 'table'
  children?: BatchDataTableSubMenu[]
}
export interface BatchDataTableSubMenu {
  key: string
  label: string
  checkable?: boolean
  checked?: boolean
  modal?: boolean
  showEdit?: boolean
}

export interface BatchElementDataInfo {
  app: string
  type: string
  version: string
  path: any
  picker_type?: string
}
export interface ElementInfo {
  elementData: string
  id: string
  name: string
}

// 抓取元素信息
interface PathInfo extends WebElementType {
  produceType: 'similar' | 'table'
}
// 表格元素信息
interface TableElementInfo extends PathInfo {
  produceType: 'table'
  values: TableValuesType[]
}
// 相似元素信息
interface SimilarElementsInfo extends WebElementType {
  produceType: 'similar'
  values: SimilarElementInfo[]
}

interface TableValuesType {
  title: string
  filterConfig?: FilterConfig[] // 筛选条件
  colFilterConfig?: FilterConfig[] // 列过滤条件
  colDataProcessConfig?: DataProcessConfig[] // 列数据处理条件
  value: string[] // 列的数据
}

interface SimilarElementInfo extends WebElementType {
  value: ValueType[]
  title: string
  filterConfig?: FilterConfig[] // 筛选条件
  colFilterConfig?: FilterConfig[] // 列过滤条件
  colDataProcessConfig?: DataProcessConfig[] // 列数据处理条件
}

enum ProcessType {
  Replace = 'Replace',
  ExtractNum = 'ExtractNum',
  Trim = 'Trim',
  Prefix = 'Prefix',
  Suffix = 'Suffix',
  FormatTime = 'FormatTime',
  Regular = 'Regular',
}

// 列元素信息
interface TableColumnElementInfo extends SimilarElementsInfo {}

interface TableData2Type {
  tableColumnData: TableColumnElementInfo
  tableData: TableElementInfo
  isTable: true
}

export interface FilterConfig {
  logical: string
  parameter: string
}

export interface DataProcessConfig {
  processType: ProcessType // 处理类型
  isEnable: 0 | 1 // 是否启用, 0:不启用, 1:启用
  parameters: Parameter[] // 处理条件
}

interface Parameter { // 字符串替换的处理条件
  [key: string]: any
}

interface ValueType {
  attrs: Attrs
  text: string
}
interface Attrs {
  src: string
  href: string
  text: string
}

export interface ColumnInfo {
  title: string
  field: string
  dataIndex: string
  [key: string]: any
}
