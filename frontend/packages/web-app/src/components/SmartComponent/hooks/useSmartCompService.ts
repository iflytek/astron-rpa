import { useRoute } from 'vue-router'

import { saveSmartComp } from '@/api/component'
import { useProcessStore } from '@/stores/useProcessStore'

import { SMART_COMPONENT_KEY_PREFIX } from '../config/constants'
import type { SmartComp, SmartType } from '../types'
import { getSmartComponentId } from '../utils'

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

    // TODO merge: adapt to canvasManager (need flowStore.simpleFlowUIData and addAtomData)
    // 如果组件不存在于流程中，添加到流程
    // const hasExist = flowStore.simpleFlowUIData.find(item => item.key === smartComp.key)
    // if (!hasExist) {
    //   await addAtomData(key, route.query.newIndex ? Number(route.query.newIndex) : undefined)
    // }
    // else {
    //   updateDocAndFlowNode(smartComp)
    // }

    return updatedComp
  }

  // TODO merge: adapt to canvasManager (need flowStore.simpleFlowUIData and updataOriginFlowData)
  function updateDocAndFlowNode(smartComp: SmartComp) {
    // TODO: adapt to canvasManager
    // const index = flowStore.simpleFlowUIData.findIndex(item => item.key === smartComp.key)
    // const flowNode = flowStore.simpleFlowUIData[index]
    // ...
  }

  return {
    saveSmartCompWithVersionList,
  }
}
