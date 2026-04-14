import { useProcessStore } from '@/stores/useProcessStore'
import type { VisualEditor } from '@/views/Arrange/canvasManager'

export function changeDebugging(id?: string, processId?: string) {
  const processStore = useProcessStore()
  const tabs = processStore.canvasManager.processList as VisualEditor[]

  tabs.forEach((tab) => {
    let changed = false

    tab.state.data?.forEach((item) => {
      const shouldDebugging = !!id && (!processId || tab.id === processId) && item.id === id
      if (!!item.debugging === shouldDebugging) {
        return
      }

      const node = tab.astParser.getNode(item.id)
      if (!node) {
        return
      }

      if (shouldDebugging) {
        node.raw.debugging = true
      }
      else {
        delete node.raw.debugging
      }
      changed = true
    })

    if (changed) {
      tab.updateData()
    }
  })
}
