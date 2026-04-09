import { cloneDeep } from 'lodash-es'

import { ATOM_FORM_TYPE, OTHER_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import { generateName } from '@/views/Arrange/utils'
import { collectFlowVarNames } from '@/views/Arrange/canvasManager/adapters/VisualEditor/utils'

import { SMART_COMPONENT_KEY_PREFIX } from '../config/constants'
import type { SmartComp } from '../types'

const exceptionKeys = [
  '__skip_err__',
  '__retry_time__',
  '__retry_interval__',
]

export function isSmartComponentKey(key: string) {
  return key?.startsWith(SMART_COMPONENT_KEY_PREFIX)
}

export function getSmartComponentId(key: string) {
  return key?.split(`${SMART_COMPONENT_KEY_PREFIX}.`)?.[1] || ''
}

/**
 * 为表单项填充默认值
 */
function fillFormItemDefaults(items: RPA.AtomDisplayItem[], existingValues: any[] = []): RPA.AtomDisplayItem[] {
  return items.map((item) => {
    const { formType, key, default: defaultVal = '' } = item
    if (existingValues.length > 0) {
      const findItem = existingValues.find(v => v.key === key)
      if (findItem) {
        item.value = findItem.value
      }
      return item
    }
    const type = formType?.type || ''
    const typeArr = type.split('_')
    item.value = defaultVal
    if (typeArr.includes(ATOM_FORM_TYPE.INPUT) || type === ATOM_FORM_TYPE.PICK) {
      item.value = [{ type: OTHER_IN_TYPE, value: defaultVal }]
    }
    return item
  })
}

/**
 * 生成智能组件的输出表单
 * 如果 outputList 中的 key 在旧输出中存在则保留旧值，否则生成新的变量名
 */
function generateSmartCompOutItems(originArr: any[] = [], targetArr: any[] = [], excludeVariables: string[] = []) {
  const processStore = useProcessStore()
  const activeTab = processStore.canvasManager.activeTab
  const flowData = (activeTab as any)?.state?.data || []
  const allVariable = collectFlowVarNames(flowData)

  return originArr.map((item) => {
    if (targetArr.length > 0) {
      const findItem = targetArr.find(t => t.key === item.key)
      if (findItem) {
        item.value = findItem.value
        return item
      }
    }
    const obj = { type: VAR_IN_TYPE, value: '' }
    if (item.formType?.type === ATOM_FORM_TYPE.RESULT) {
      const regex = new RegExp(`^${item.key}_\\d+$`)
      const variables = allVariable.filter(v => regex.test(v) && !excludeVariables.includes(v))
      const newVarName = generateName(variables, item.key, '_')
      allVariable.push(newVarName)
      obj.value = newVarName
    }
    item.value = [obj]
    return item
  })
}

/**
 * 生成智能组件的高级参数表单
 */
function generateSmartCompAdvancedItems(initData: any, targetData: any[] = []) {
  const processStore = useProcessStore()
  const commonAdvanced = cloneDeep(processStore.commonAdvancedParameter).filter(item => !exceptionKeys.includes(item.key))
  return fillFormItemDefaults(commonAdvanced, targetData)
}

/**
 * 生成智能组件的异常处理表单
 */
function generateSmartCompExceptionItems(initData: any, targetData: any[] = []) {
  const processStore = useProcessStore()
  const exceptionArr = cloneDeep(processStore.commonAdvancedParameter).filter(item => exceptionKeys.includes(item.key))
  return fillFormItemDefaults(exceptionArr, targetData)
}

export function generateComponentForm(comp: SmartComp, oldOutputList?: any[]) {
  // 提取旧输出变量列表，用于排除当前组件的旧输出变量
  const excludeVariables: string[] = []
  // 构建旧输出项的映射，用于保留相同 key 的输出变量名
  const oldOutputMap = new Map<string, any>()

  if (oldOutputList) {
    oldOutputList.forEach((item) => {
      if (item.value && Array.isArray(item.value)) {
        item.value.forEach((v: any) => {
          if (v.type === VAR_IN_TYPE && v.value) {
            excludeVariables.push(v.value)
          }
        })
      }
      // 建立 key 到旧输出项的映射
      if (item.key) {
        oldOutputMap.set(item.key, item)
      }
    })
  }

  // 如果输出项的 key 匹配，保留原有的值；否则生成新的变量名
  const targetArr: any[] = []
  if (comp.outputList && oldOutputMap.size > 0) {
    comp.outputList.forEach((item) => {
      const oldItem = oldOutputMap.get(item.key)
      if (oldItem) {
        targetArr.push(oldItem)
      }
    })
  }

  return {
    ...comp,
    outputList: generateSmartCompOutItems(comp.outputList, targetArr, excludeVariables),
    advanced: generateSmartCompAdvancedItems(comp.outputList),
    exception: generateSmartCompExceptionItems(comp.outputList),
  }
}
