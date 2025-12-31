import { VAR_IN_TYPE } from '@/constants/atom'
import { generateAdvancedItems, generateExceptionItems, generateOutItems } from '@/views/Arrange/utils/generateData'

import { SMART_COMPONENT_KEY_PREFIX } from '../config/constants'
import type { SmartComp } from '../types'

export function isSmartComponentKey(key: string) {
  return key?.startsWith(SMART_COMPONENT_KEY_PREFIX)
}

export function getSmartComponentId(key: string) {
  return key?.split(`${SMART_COMPONENT_KEY_PREFIX}.`)?.[1] || ''
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
    outputList: generateOutItems(comp.outputList, targetArr, excludeVariables),
    advanced: generateAdvancedItems(comp.outputList),
    exception: generateExceptionItems(comp.outputList),
  }
}
