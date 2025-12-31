import { inject, provide, ref } from 'vue'

import { useRunlogStore } from '@/stores/useRunlogStore'

import type { Message, SmartComp, SmartType } from '../types'

import { useSmartCompService } from '.'

// 创建智能组件上下文
export function useSmartCompContext() {
  const { saveSmartCompWithVersionList } = useSmartCompService()
  const editingSmartComp = ref<SmartComp>()
  const smartType = ref<SmartType>()
  const versionList = ref<SmartComp[]>([])
  // 当前版本索引，-1 表示没有版本
  const currentVersionIndex = ref<number>(-1)

  function setEditingSmartComp(comp?: SmartComp) {
    editingSmartComp.value = comp

    if (comp?.version && versionList.value.length > 0) {
      const index = versionList.value.findIndex(v => v.version === comp.version)

      if (index >= 0) {
        currentVersionIndex.value = index
        versionList.value[index] = editingSmartComp.value
      }
    }
    else if (!comp) {
      currentVersionIndex.value = -1
    }

    console.log('editingSmartComp', editingSmartComp.value, 'currentVersionIndex', currentVersionIndex.value)
  }

  function initVersionList(versionListData: SmartComp[], targetVersion?: number) {
    versionList.value = versionListData
    if (versionListData.length > 0) {
      const targetVer = targetVersion || Math.max(...versionListData.map(v => v.version || 0))
      switchToVersion(targetVer)
    }
    else {
      currentVersionIndex.value = -1
      editingSmartComp.value = undefined
    }
  }

  function updateEditingCompFromVersion(version: number) {
    const index = versionList.value.findIndex(v => v.version === version)
    if (index >= 0) {
      setEditingSmartComp(versionList.value[index])
    }
  }

  function getNextVersionNumber(): number {
    // 版本从1开始
    if (versionList.value.length === 0) {
      return 1
    }
    const maxVersion = Math.max(...versionList.value.map(v => v.version || 0))
    return maxVersion + 1
  }

  function addNewVersion(newVersion: SmartComp) {
    versionList.value.push(newVersion)
    setEditingSmartComp(newVersion)
    useRunlogStore().clearLogs()
  }

  function updateCurrentVersionChatHistory(chatHistory: Message[]) {
    setEditingSmartComp({
      ...editingSmartComp.value,
      detail: {
        ...editingSmartComp.value.detail,
        chatHistory,
      },
    })
  }

  function switchToVersion(version: number) {
    updateEditingCompFromVersion(version)
  }

  async function saveSmartComp() {
    if (!editingSmartComp.value)
      return
    const updatedComp = await saveSmartCompWithVersionList(
      editingSmartComp.value,
      smartType.value,
      versionList.value,
    )
    setEditingSmartComp(updatedComp)
  }

  return {
    editingSmartComp,
    smartType,
    versionList,
    currentVersionIndex,
    setEditingSmartComp,
    initVersionList,
    getNextVersionNumber,
    addNewVersion,
    updateCurrentVersionChatHistory,
    switchToVersion,
    saveSmartComp,
  }
}

export type SmartCompContext = ReturnType<typeof useSmartCompContext>

export function provideSmartCompContext(context: SmartCompContext) {
  provide('smartComp', context)
}

// 智能组件注入
export function useSmartComp() {
  const context = inject<SmartCompContext>('smartComp')
  if (!context) {
    throw new Error('useSmartComp must be used within SmartComponent Index component')
  }
  return context
}
