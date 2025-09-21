/**
 * 处理 table 形式的数据
 * 数据抓取的元素， table 为 单一元素， 相似元素为 多个元素
 * 对于单一元素， 只需要调用一次获取元素及数据， 对于多个元素， 需要循环调用获取元素及数据
 */

import type { SimilarDataType, TableDataType } from '../types/data_grab'

class DataTable {
  public data: TableDataType | SimilarDataType
  private produceType: 'table' | 'similar'
  constructor(params, values, produceType: 'table' | 'similar') {
    // 初始化
    this.produceType = produceType
    if (produceType === 'table') {
      this.data = {
        ...params,
        produceType,
        values,
      }
    }
    if (produceType === 'similar') {
      const vals = {
        ...params,
        value: values,
      }
      this.data = {
        produceType,
        values: [vals],
      }
    }
  }

  public getTable() {
    return this.data
  }

  public isSimilarDataType() {
    return this.produceType === 'similar'
  }
}

export default DataTable
