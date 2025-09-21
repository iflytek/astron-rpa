import { cloneDeep, unionWith } from 'lodash-es'

import type { VARIABLE_TYPE } from '@/constants/atom'
import { ATOM_FORM_TYPE, LIMIT_VARIABLE_SELECT, OTHER_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import { ProjectDocument } from '@/corobot'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { useVariableStore } from '@/stores/useVariableStore'
import { BASE_FORM } from '@/views/Arrange/config/atom'
import { Group, GroupEnd, LOOP_END_MAP } from '@/views/Arrange/config/atomKeyMap'
import { pickProcessAndModuleOptions } from '@/views/Arrange/utils'

import { generateName, genNonDuplicateID } from './index'

export const exceptionKeys = [
  '__skip_err__',
  '__retry_time__',
  '__retry_interval__',
]

let addNewAtomIdxArr = []

export function setAddAtomIdx(item: number | number[]) {
  addNewAtomIdxArr = Array.isArray(item) ? item : [item]
}

// 生成原子能力id
export function generateId(type) {
  let id = genNonDuplicateID()
  if (type === Group || type === GroupEnd)
    id = `group_${id}`
  return id
}

// 通过key循环获取对应原子能力
export async function loopAtomByKey(key: string) {
  const child = LOOP_END_MAP[key]
  if (child)
    await loopAtomByKey(child)
  if (!getAtomByKey(key)) {
    await useProjectDocStore().gainLastNodeAbility(key, true)
  }
}

// 生成组件节点
export async function createComponentAbility(key: string, version?: string | number) {
  if (!getAtomByKey(key, version)) {
    const node = await ProjectDocument.gainComponentAbility(key, version)
    return node
  }
}

// 通过key获取对应原子能力
export function getAtomByKey(key: string | number, version?: string | number) {
  let defaultVersion = version
  if (!version)
    defaultVersion = useProjectDocStore().noVersionMap()[key]

  const keys = `${key}***${defaultVersion}`
  return cloneDeep(useProjectDocStore().nodeAbility()[keys])
}

// 生成基础信息表单
export function generateBaseItems(initData, alias = '') {
  const baseItems = initData.baseForm || cloneDeep(BASE_FORM) || []
  return baseItems.map((i) => {
    const obj = {
      type: 'str',
      value: '',
    }
    if (i.key === 'baseName')
      obj.value = initData.title
    if (i.key === 'anotherName')
      obj.value = alias ?? initData.anotherName ?? initData.title

    i.value = [obj]

    if (initData.key === Group)
      i.title = '分组名称'
    return i
  })
}

// 获取流程中所有输出流变量
export function getFlowVariable() {
  let allFlowVariable = []
  const allNode = useFlowStore().simpleFlowUIData
  allNode.forEach((item) => {
    (item.outputList || []).forEach((i) => {
      allFlowVariable = allFlowVariable.concat((i.value as Array<any>).map(v => v.type === VAR_IN_TYPE ? v.value : null).filter(i => i))
    })
  })
  return allFlowVariable
}

// 获取所有全局变量
export function getAllGlobalVariable() {
  const variableStore = useVariableStore()
  const arr = variableStore.globalVariableList.map(i => i.varName)
  return arr
}

// 获取流程中所有输出流变量
export function generateVarName(typeVarName, allVariable) {
  // 查找出所有的typeVarName_1、typeVarName_2...的变量
  const regex = new RegExp(`${typeVarName}_` + `\\d`)
  const variables = allVariable.filter(i => regex.test(i))
  // 通过对比，生成新的后缀名称
  const newVarName = generateName(variables, typeVarName, '_')
  // 将新生成的变量添加到所有流变量，便于下一个输出表单后缀正确生成
  allVariable.push(newVarName)
  return newVarName
}

function generateFormItemDefaultVal(originArr: RPA.AtomDisplayItem[], targetArr: any[]) {
  return originArr.map((i) => {
    const { formType: { type }, key, types, default: defaultVal = '' } = i
    if (targetArr.length > 0) {
      const findItem = targetArr.find(item => item.key === key)
      if (findItem) {
        i.value = findItem.value
      }
      return i
    }
    const typeArr = type.split('_')
    i.value = defaultVal
    if (typeArr.includes(ATOM_FORM_TYPE.INPUT) || type === ATOM_FORM_TYPE.PICK) {
      // 只有input框类型的value才需要是数组
      const obj = {
        type: OTHER_IN_TYPE,
        value: defaultVal,
      }
      if (LIMIT_VARIABLE_SELECT.includes(types as VARIABLE_TYPE)) {
        useFlowStore().simpleFlowUIData.slice(0, addNewAtomIdxArr[0]).findLast((item) => {
          const findoutputListIdx = item?.outputList?.findIndex((v: RPA.AtomDisplayItem) => v.types === types)
          if (findoutputListIdx !== -1 && findoutputListIdx !== undefined) {
            obj.type = item.outputList[findoutputListIdx].value[0].type
            obj.value = item.outputList[findoutputListIdx].value[0].value
            return true
          }
          return false
        })
      }
      i.value = [obj]
    }
    return i
  })
}

// 生成输出信息表单
export function generateOutItems(originArr = [], targetArr: any[] = []) {
  const allFlowVariable = getFlowVariable()
  const allGlobalVariable = getAllGlobalVariable()
  const allVariable = allFlowVariable.concat(allGlobalVariable)
  const arr = originArr.map((i) => {
    if (targetArr.length > 0) {
      const findItem = targetArr.find(item => item.key === i.key)
      if (findItem) {
        i.value = findItem.value
      }
      return i
    }
    const obj = {
      type: VAR_IN_TYPE,
      value: '',
    }
    if (i.formType?.type === ATOM_FORM_TYPE.RESULT) {
      const newVarName = generateVarName(i.key, allVariable)
      obj.value = newVarName
    }
    i.value = [obj]
    return i
  })
  return arr
}

// 生成输入信息表单
export function generateInItems(initData, targetData: any[] = []) {
  return generateFormItemDefaultVal(initData.inputList?.filter(i => i.level !== 'advanced') || [], targetData)
}

// 生成高级信息表单
export function generateAdvancedItems(initData, targetData: any[] = []) {
  const processStore = useProcessStore()

  let advanceArr = []
  if (initData.advanced) {
    advanceArr = initData.advanced
  }
  else {
    const specialAdvanced = initData.inputList?.filter(i => i.level === 'advanced')
    // 高级参数公共配置
    let commonAdvanced = cloneDeep(processStore.commonAdvancedParameter).filter(item => !exceptionKeys.includes(item.key))

    // 没有输出信息的，高级参数中不要打印输出变量配置
    if (initData.outputList?.length === 0)
      commonAdvanced = commonAdvanced.filter(item => item.key !== '__res_print__')

    advanceArr = unionWith(specialAdvanced, commonAdvanced, (specialArr, commonArr) => {
      return specialArr.key === commonArr.key
    })
  }
  return generateFormItemDefaultVal(advanceArr, targetData)
}

// 生成异常信息表单
export function generateExceptionItems(initData, targetData: any[] = []) {
  const processStore = useProcessStore()
  const cloneConfig = cloneDeep(processStore.commonAdvancedParameter)
  const exceptionArr = initData.exception || cloneConfig.filter(item => exceptionKeys.includes(item.key)) || []
  return generateFormItemDefaultVal(exceptionArr, targetData)
}

export function generateGroupName() {
  const groups = useFlowStore().simpleFlowUIData.filter(val => val.key === Group)
  const groupNames = groups.map(i => i.alias)
  return generateName(groupNames, '编组', '-')
}

export function generateInputMap(key: string, specialRender = false) {
  const atom = getAtomByKey(key)
  if (!atom)
    return

  const nodeConfig = {
    ...atom,
    alias: key === Group ? generateGroupName() : atom.title,
    id: generateId(key),
    inputList: generateInItems(atom),
    outputList: generateOutItems(atom.outputList),
    advanced: generateAdvancedItems(atom),
    exception: generateExceptionItems(atom),
    disabled: false,
  }
  const configs = [nodeConfig]

  if (specialRender)
    return configs

  const nestedKey = LOOP_END_MAP[key]
  if (nestedKey) {
    const nodeArr = generateInputMap(nestedKey)
    nodeArr.forEach((node) => {
      useFlowStore().nodeContactMap[nodeConfig.id] = node.id
      if (node.key === GroupEnd) {
        node.alias = nodeConfig.alias
      }
      configs.push(node)
    })
  }

  return configs
}

export function generateFormMap(item) {
  const { alias, title, exception, inputList } = item
  if (inputList) {
    for (const item of inputList as RPA.AtomDisplayItem[]) {
      const options = pickProcessAndModuleOptions(item)
      if (options)
        item.options = options
    }
  }
  item.baseForm = generateBaseItems(item || { title }, alias)
  item.exception = generateExceptionItems({}, exception)
  return item
}
