import { includes } from 'lodash-es'

import { useProcessStore } from '@/stores/useProcessStore'

/**
 * select 类型的表单项定义在 options 字段，但是存在 options 的动态的情况，需要根据表单项的 formType 和 params 来确定 options 的值
 * 目前存在动态的表单项有：
 * 1. 子流程
 * 2. 子模块
 * @param item 
 */
export const useProcessSelectOptions = (item: RPA.AtomDisplayItem) => {
  const { canvasManager } = useProcessStore()
  const formTypeParams = item?.formType?.params?.filters

  if (includes(formTypeParams, 'Process')) { // 判断是否是选择子流程
    // 挑选出所有的流程
    const flowList = canvasManager.tabs.map(item => item.state).filter(item => item.resourceCategory === 'process')
    // 过滤掉自己和主流程
    const filterFlow = flowList.filter(item => item.resourceId !== canvasManager.activeTabId && !item.isMain)
    // 把流程节点转换为表单选项
    return filterFlow.map(item => ({
      label: item.name,
      value: item.resourceId,
    }))
  }

  if (includes(formTypeParams, 'PyModule')) { // 判断是否是选择py模块
    // 挑选出所有 py 模块
    const pyModuleList = canvasManager.tabs.map(item => item.state).filter(item => item.resourceCategory === 'module')
    return pyModuleList.map(item => ({
      label: item.name,
      value: item.resourceId,
    }))
  }

  return item?.options
}
