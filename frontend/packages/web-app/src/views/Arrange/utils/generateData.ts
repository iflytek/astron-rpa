import { useVariableStore } from '@/stores/useVariableStore'

import { generateName } from './index'

// 获取所有全局变量
export function getAllGlobalVariable() {
  const variableStore = useVariableStore()
  const arr = variableStore.globalVariableList.map(i => i.varName)
  return arr
}

// 获取流程中所有输出流变量
export function generateVarName(typeVarName, allVariable, excludeVariables: string[] = []) {
  // 查找出所有的typeVarName_1、typeVarName_2...的变量，但排除指定的变量
  const regex = new RegExp(`${typeVarName}_` + `\\d`)
  const variables = allVariable.filter(i => regex.test(i) && !excludeVariables.includes(i))
  // 通过对比，生成新的后缀名称
  const newVarName = generateName(variables, typeVarName, '_')
  // 将新生成的变量添加到所有流变量，便于下一个输出表单后缀正确生成
  allVariable.push(newVarName)
  return newVarName
}
