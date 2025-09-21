import { message } from 'ant-design-vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import { ungroup } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'
import { getSelected } from '@/views/Arrange/utils/contextMenu'
import { findPairId } from '@/views/Arrange/utils/flowUtils'

function recursiveUnGroup(groupIds: string[]) {
  const nodeMap = useFlowStore().nodeContactMap
  const groupStartId = groupIds[0]
  const groupEndId = findPairId(nodeMap, groupStartId)
  ungroup([groupStartId, groupEndId])
  const remainGroupIds = groupIds.filter(id => ![groupStartId, groupEndId].includes(id))
  if (remainGroupIds.length > 0) {
    recursiveUnGroup(remainGroupIds)
  }
}

export function useToolsUnGroup() {
  const item: ArrangeTools = {
    key: 'ungroup',
    title: 'releaseGrouping',
    name: '',
    fontSize: '',
    icon: 'tools-un-group',
    action: '',
    show: true,
    disable: () => isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: () => {
      const atomIds = useFlowStore().multiSelect ? useFlowStore().selectedAtomIds : getSelected()
      const groupIds = atomIds.filter((i: any) => i.startsWith('group'))
      if (groupIds.length === 0) {
        return message.warning('请先选择一个分组，再释放分组')
      }
      recursiveUnGroup(groupIds)
    },
  }
  return item
}
