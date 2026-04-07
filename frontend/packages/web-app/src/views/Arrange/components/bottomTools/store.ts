import { createInjectionState, reactiveComputed } from '@vueuse/core'
import { computed, ref, shallowRef } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

import { useCVManager } from './components/CvManager/useCVManager.ts'
import { useElementManager } from './components/ElementManager/useElementManager.ts'
import { useLog } from './components/Log/useLog.ts'
import { useProvideConfigParameter } from './components/ConfigParameter/useConfigParameter.ts'
import { useDebugLog } from './components/DebugLog/useDebugLog.ts'
import { useSubProcessUse } from './components/SubProcessSearch/useSubProcessUse'

import type { TabConfig } from './types'

const [useProvideToolsStore, useToolsStore] = createInjectionState(() => {
  // 创建并提供 configParameter 实例
  const { configParamsTabConfig } = useProvideConfigParameter()
  const logConfig = useLog()
  const elementManagerConfig = useElementManager()
  const cvManagerConfig = useCVManager()
  const subProcessUseConfig = useSubProcessUse()
  const debugLogConfig = useDebugLog()

  // watch(() => useRunningStore().running, (val) => {
  //   if (['run', 'debug'].includes(val)) {
  //     expand(false)
  //   }
  //   if (val === 'run') {
  //     activeKey.value = 'logs'
  //   }
  //   if (val === 'debug') {
  //     tabs.value = [...tabs.value, useDebugLog()]
  //     activeKey.value = 'debugLog'
  //   }
  //   else {
  //     tabs.value = tabs.value.filter(tab => tab.key !== 'debugLog')
  //     activeKey.value = tabs.value[0].key
  //   }
  // })
  
  // watch(() => processStore.searchSubProcessId, (val) => {
  //   if (val) {
  //     tabs.value = [useSubProcessUse()]
  //     activeKey.value = tabs.value[0].key
  //     expand(false)
  //   }
  //   else {
  //     tabs.value = initTabs
  //     activeKey.value = tabs.value[0].key
  //     expand(true)
  //   }
  // })

  const tabs = computed<TabConfig[]>(() => {
    return [logConfig, elementManagerConfig, cvManagerConfig, configParamsTabConfig]
  })

  const activeKey = ref(tabs.value[0].key)
  const collapsed = ref(false) // 展开折叠
  const searchText = ref('') // 搜索文本
  const moduleType = ref('default') // 展示模块类型 moduleType: 'default' | 'unuse'-未使用 | 'quoted'-被引用
  const refresh = ref(true) // 刷新
  const unUseNum = ref(0) // 未使用元素数量

  const activeTab = computed<TabConfig>(() => tabs.value.find(tab => tab.key === activeKey.value))

  return { collapsed, searchText, moduleType, refresh, unUseNum, activeTab, activeKey, tabs }
})

export { useProvideToolsStore, useToolsStore }
