/**
 * 全局数据更新导致的流程，配置更新
 * 全局变量， 元素等
 */
import { useFlowStore } from '@/stores/useFlowStore'
import { getProjectAllFlow } from '@/views/Arrange/utils/flowUtils'

export function useGlobalDataUpdate() {
  /**
   * 元素重命名
   * @param element 元素
   */
  const elementRenameAndUpdateFlow = (element) => {
    console.log('elementRenameAndUpdateFlow: ', element)
    // console.log('element: ', element)
    const { allFlowList } = getProjectAllFlow()
    const worker = new Worker(new URL('@/worker/index.ts', import.meta.url))
    worker.postMessage({
      key: 'flowDataElementUpdate',
      params: {
        element: {
          elementId: element.elementId,
          name: element.name,
        },
        currentFlowData: JSON.stringify(allFlowList),
        type: 'rename',
      },
    })
    worker.onmessage = (e) => {
      const { key, params } = e.data
      if (key === 'flowDataElementUpdate') {
        useFlowStore().updataOriginFlowData(params)
        worker.terminate()
      }
    }
  }
  /**
   * 删除元素
   * @param element 元素
   */
  const elementDeleteAndUpdateFlow = (element) => {
    console.log('elementDeleteAndUpdateFlow: ')
    const { allFlowList } = getProjectAllFlow()
    const worker = new Worker(new URL('@/worker/index.ts', import.meta.url))
    worker.postMessage({
      key: 'flowDataElementUpdate',
      params: {
        element: {
          elementIds: element.elementIds,
        },
        currentFlowData: JSON.stringify(allFlowList),
        type: 'delete',
      },
    })
    worker.onmessage = (e) => {
      const { key, params } = e.data
      if (key === 'flowDataElementUpdate') {
        useFlowStore().updataOriginFlowData(params)
        worker.terminate()
      }
    }
  }

  /**
   * 本流程使用的所有元素
   */
  const elementUsedInFlow = () => {
    return new Promise((resolve, reject) => {
      try {
        const worker = new Worker(new URL('@/worker/index.ts', import.meta.url))
        worker.postMessage({
          key: 'elementUsedInFlow',
          params: {
            currentFlowData: useFlowStore().simpleFlowUIData,
          },
        })
        worker.onmessage = (e) => {
          const { key, params } = e.data
          if (key === 'elementUsedInFlow') {
            const { usedElementsIds } = params
            resolve(usedElementsIds)
          }
        }
      }
      catch (error) {
        reject(error)
      }
    })
  }

  return {
    elementRenameAndUpdateFlow,
    elementDeleteAndUpdateFlow,
    elementUsedInFlow,
  }
}
