/** @format */

interface DataType {
  produceType: string
  values: TableValueType[] | SimilarValueType[]
}

interface TableDataType extends DataType, ElementInfo {
  batchType?: 'normal' | 'head'
  produceType: 'table'
  xpath: string
  values: TableValueType[]
}

interface TableValueType {
  title: string
  value: string[]
  filterConfig: FilterConfig[]
  colFilterConfig: FilterConfig[]
  colDataProcessConfig: DataProcessConfig[]
}

interface FilterConfig {
  filterAssociation: string
  logical: string
  parameter: string
}

interface DataProcessConfig {
  processType: string
  isEnable: number
  parameters: Parameter[]
}

interface Parameter {
  [key: string]: any
}

interface SimilarDataType extends DataType {
  batchType?: 'normal' | 'head'
  produceType: 'similar'
  values: SimilarValueType[]
}

interface SimilarValueType extends ElementInfo {
  title: string
  filterConfig: FilterConfig[]
  colFilterConfig: FilterConfig[]
  colDataProcessConfig: DataProcessConfig[]
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

interface SimilarDataParams {
  key: string
  data: SimilarDataType
}

interface TableDataParams {
  key: string
  data: TableDataType
}

interface BatchElementParams extends ElementInfo {
  produceType: 'table' | 'similar'
  values?: SimilarValueType[]
  openSourcePage?: boolean
}

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
type BatchPickObject = TablePickObject | SimilarPickObject
