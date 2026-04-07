import { useRoute } from 'vue-router'

import { saveSmartComp } from '@/api/component'
import { useProcessStore } from '@/stores/useProcessStore'
import type { VisualEditor } from '@/views/Arrange/canvasManager/adapters'

import { SMART_COMPONENT_KEY_PREFIX } from '../config/constants'
import type { SmartComp, SmartType } from '../types'
import { getSmartComponentId } from '../utils'

/**
 * 获取当前活动 tab 的流程数据（VisualEditor 的 state.data）
 */
function getActiveFlowData(processStore: ReturnType<typeof useProcessStore>): RPA.Atom[] {
  const activeTab = processStore.canvasManager.activeTab as VisualEditor | null
  return activeTab?.state?.data || []
}

// 业务逻辑服务
export function useSmartCompService() {
  const processStore = useProcessStore()
  const route = useRoute()

  async function saveSmartCompWithVersionList(
    smartComp: SmartComp,
    smartType: SmartType | undefined,
    versionList: SmartComp[],
  ) {
    if (!smartComp) {
      throw new Error('smartComp is required')
    }

    const smartId = getSmartComponentId(smartComp.key)
    const isNewComponent = !smartId

    // 保存到服务器
    const savedSmartId = await saveSmartComp({
      robotId: processStore.project.id,
      robotVersion: processStore.project.version,
      smartId,
      smartType,
      detail: {
        versionList,
      },
    })

    const key = `${SMART_COMPONENT_KEY_PREFIX}.${savedSmartId}`
    const updatedComp = smartComp
    updatedComp.key = key

    // 更新 versionList 中所有版本的 key
    if (versionList.length > 0) {
      versionList.forEach((version) => {
        version.key = key
      })
    }

    // 如果是新组件，需要再次保存以更新 versionList 中的 key
    if (isNewComponent) {
      await saveSmartComp({
        robotId: processStore.project.id,
        robotVersion: processStore.project.version,
        smartId: savedSmartId,
        smartType,
        detail: {
          versionList,
        },
      })
    }

    // 如果组件不存在于流程中，添加到流程
    const flowData = getActiveFlowData(processStore)
    const hasExist = flowData.find(item => item.key === smartComp.key)
    if (!hasExist) {
      const activeTab = processStore.canvasManager.activeTab as VisualEditor | null
      if (activeTab?.add) {
        const newIndex = route.query.newIndex ? Number(route.query.newIndex) : undefined
        await activeTab.add(key, newIndex)
      }
    }
    else {
      updateFlowNode(smartComp)
    }

    return updatedComp
  }

  /**
   * 更新流程中已有的智能组件节点数据
   */
  function updateFlowNode(smartComp: SmartComp) {
    const flowData = getActiveFlowData(processStore)
    const activeTab = processStore.canvasManager.activeTab as VisualEditor | null
    if (!activeTab) return

    const flowNode = flowData.find(item => item.key === smartComp.key)
    if (!flowNode) return

    const node = activeTab.astParser.getNode(flowNode.id)
    if (!node) return

    const oldItem = { ...node.raw }
    const newItem = {
      ...node.raw,
      alias: smartComp.alias || smartComp.title,
      inputList: smartComp.inputList || [],
      outputList: smartComp.outputList || [],
      advanced: smartComp.advanced || [],
      exception: smartComp.exception || [],
    }

    activeTab.undoManager.update({
      type: 'update',
      items: [{ id: flowNode.id, oldItem, newItem }],
    })
  }

  return {
    saveSmartCompWithVersionList,
  }
}
