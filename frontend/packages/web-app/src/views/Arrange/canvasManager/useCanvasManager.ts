import { ref, computed, Ref, shallowRef, triggerRef } from 'vue'
import { isFunction } from 'lodash-es'

import { getProcessAndCodeList } from '@/api/resource'
import { PROCESS_OPEN_KEYS } from '@/constants'
import { LRUCache } from '@/utils/lruCache'

import { newTabInstance, createTabInstance, genName } from './adapters'

export const useCanvasManagerStore = (project: Ref<{ id: string }>) => {
  const openProcessLRUCache = new LRUCache<string[]>(PROCESS_OPEN_KEYS, 10, [])

  /** 所有 tab 列表 */
  const processList = shallowRef<RPA.Process.TabInstance[]>([])
  /** 当前打开的 tab 列表 */
  const tabs = shallowRef<RPA.Process.TabInstance[]>([])
  /** 当前激活的 tab ID */
  const activeTabId = ref<string | null>(null)

  /** 当前激活的 tab */
  const activeTab = computed(() => {
    if (!activeTabId.value) return null
    return tabs.value.find(tab => tab.id === activeTabId.value) || null
  })

  /** Tab 数量 */
  const tabCount = computed(() => tabs.value.length)

  /** 是否有未保存的 tab */
  const hasDirtyTabs = computed(() => processList.value.some(tab => tab.state.isDirty))

  const init = async (projectId: string) => {
    // 从缓存中获取打开的流程
    const openProcessKeys = openProcessLRUCache.get(projectId) ?? []
    const list = await getProcessAndCodeList({ robotId: projectId })

    processList.value = list
      .map(it => ({ ...it, isMain: it.name === '主流程' }))
      .sort((a, b) => (b.isMain ? 1 : 0) - (a.isMain ? 1 : 0)) // 根据 isMain 进行排序
      .map(it => newTabInstance(projectId, it))

    tabs.value = processList.value.filter(it => it.state.isMain || openProcessKeys.includes(it.id))

    const initActiveId = tabs.value[0]?.id;
    initActiveId && activateTab(initActiveId)
  }

  /** 保存已打开的 tabs 到本地缓存中 */
  function saveOpenTabsToCache() {
    openProcessLRUCache.set(project.value.id, tabs.value.map(it => it.id))
  }

  async function genTabName(type: RPA.Process.ProcessModuleType) {
    return await genName(project.value.id, type)
  }

  /**
   * 创建 tab
   * @param type 
   * @param name 
   */
  async function createTab(type: RPA.Process.ProcessModuleType, name: string) {
    const newTabId = await createTabInstance(project.value.id, type, name)
    const processModule: RPA.Process.ProcessModule = {
      resourceCategory: type,
      name,
      resourceId: newTabId,
    }
    const processInstance = newTabInstance(project.value.id, processModule)
    processList.value.push(processInstance)
    return addTab(processInstance)
  }

  /**
   * 添加 tab
   */
  async function addTab(tabInstance: RPA.Process.TabInstance): Promise<RPA.Process.TabInstance> {
    // 检查是否已存在相同的 tab
    const existingTab = tabs.value.find(tab => tab.id === tabInstance.id)

    if (!existingTab) {
      tabs.value = [...tabs.value, tabInstance]
    }
    
    await activateTab(tabInstance.id)

    saveOpenTabsToCache()

    return tabInstance
  }

  /**
   * 关闭 tab
   */
  async function closeTab(tabId: string) {
    const index = tabs.value.findIndex(tab => tab.id === tabId)
    if (index < 0) return false

    const tab = tabs.value[index]
    
    // 调用关闭前钩子
    if (tab.onBeforeClose) {
      const canClose = await tab.onBeforeClose()
      if (canClose === false) {
        return false
      }
    }
    
    // 调用关闭钩子
    if (tab.onClose) {
      await tab.onClose()
    }

    tabs.value = tabs.value.filter(it => it.id !== tabId)
    
    // 如果关闭的是当前激活的 tab，激活其他 tab
    if (activeTabId.value === tabId) {
      if (tabs.value.length > 0) {
        // 优先激活相邻的 tab
        const newIndex = Math.min(index, tabs.value.length - 1)
        await activateTab(tabs.value[newIndex].id)
      } else {
        activeTabId.value = null
      }
    }
    
    saveOpenTabsToCache()

    return true
  }

  /**
   * 关闭所有 tab
   */
  async function closeAllTabs() {
    const tabIds = [...tabs.value.map(tab => tab.id)]
    
    for (const tabId of tabIds) {
      await closeTab(tabId)
    }

    saveOpenTabsToCache()

    return true
  }

  /**
   * 激活 tab
   */
  async function activateTab(tabId: string) {
    const tab = processList.value.find(t => t.id === tabId)
    if (!tab) return false

    if (tabId === activeTabId.value) return true

    // 失活当前 tab
    if (activeTab.value && activeTab.value.id !== tabId) {
      if (activeTab.value.onDeactivate) {
        await activeTab.value.onDeactivate()
      }
    }

    // 激活新 tab
    activeTabId.value = tabId
    tab.updateState({ shouldRender: true })

    if (!tabs.value.includes(tab)) {
      tabs.value = [...tabs.value, tab]
      saveOpenTabsToCache()
    }

    if (tab.onActivate) {
      await tab.onActivate()
    }

    return true
  }

  /**
   * 更新 tab
   */
  function updateTab(tabId: string, updates: Partial<RPA.Process.ProcessModule>) {
    const tab = getTab(tabId)

    if (!tab) return false

    tab.updateState(updates)
    triggerRef(tabs)
  }

  /**
   * 重命名 tab
   * @param tabId 
   * @param name 新名称
   */
  function renameTab(tabId: string, name: string) {
    const tab = getTab(tabId)
    if (!tab) return false

    return tab.rename(name)
  }

  /**
   * 获取 tab
   */
  function getTab<T>(tabId: string): RPA.Process.TabInstance<T> | undefined {
    return tabs.value.find(t => t.id === tabId)
  }

  /**
   * 获取操作状态（如果不传 tabId 则获取当前激活的 tab 的状态）
   */
  function getActionState(actionKey: string, tabId?: string): RPA.Process.TabActionState {
    const targetTabId = tabId ?? activeTabId.value
    if (!targetTabId) {
      return { visible: false, disabled: true }
    }

    const tab = getTab(targetTabId)
    if (!tab) {
      return { visible: false, disabled: true }
    }

    // 优先使用 tab 实例的方法
    if (tab.getActionState) {
      return tab.getActionState(actionKey)
    }

    // 默认状态
    return { visible: true, disabled: false }
  }

  async function saveTab(tabId?: string) {
    const targetTab = tabId ? getTab(tabId) : activeTab.value
    if (!targetTab) return false

    if (targetTab.save && isFunction(targetTab.save)) {
      updateTab(targetTab.id, { isSaveing: true })
      await targetTab.save()
      updateTab(targetTab.id, { isDirty: false, isSaveing: false, isSaved: true })
      return true
    }

    return false
  }

  /**
   * 重置状态
   */
  function reset() {
    tabs.value = []
    activeTabId.value = null
  }

  return {
    // State
    tabs,
    processList,
    activeTabId,
    activeTab,
    tabCount,
    hasDirtyTabs,

    // Actions
    init,
    saveTab,
    addTab,
    createTab,
    genTabName,
    closeTab,
    closeAllTabs,
    activateTab,
    updateTab,
    renameTab,
    getTab,
    getActionState,
    reset,
  }
}
