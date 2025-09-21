import { message } from 'ant-design-vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import { group } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'
import { getSelected } from '@/views/Arrange/utils/contextMenu'

export function useToolsGroup() {
  const item: ArrangeTools = {
    key: 'group',
    title: 'group',
    name: '',
    fontSize: '',
    icon: 'tools-group',
    action: '',
    show: true,
    disable: () => isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: () => {
      const atomIds = useFlowStore().multiSelect ? useFlowStore().selectedAtomIds : getSelected()
      if (atomIds.length === 0) {
        message.warning(`请先选中一个节点再编组`)
        return
      }
      group(atomIds)
    },
  }
  return item
}
