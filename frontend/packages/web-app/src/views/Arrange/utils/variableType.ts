// 所有变量类型，数据来源于接口返回
// eslint-disable-next-line import/no-mutable-exports
export let allVarType = {}
// 导出一个函数，用于设置变量类型
export function setVariableType(data = {}) {
  // 将传入的data参数赋值给allVarType变量，如果data参数为空，则赋值为空对象
  allVarType = data || {}
}
