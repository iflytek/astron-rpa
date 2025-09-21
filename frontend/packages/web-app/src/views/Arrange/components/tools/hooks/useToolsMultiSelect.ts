import { useFlowStore } from '@/stores/useFlowStore'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsMultiSelect() {
  const item: ArrangeTools = {
    key: 'multiSelect',
    title: () => useFlowStore().multiSelect ? 'deselect' : 'multiSelect',
    name: '',
    fontSize: '',
    icon: 'tools-multi-select',
    action: '',
    noParams: true,
    show: true,
    disable: () => isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: () => {
      useFlowStore().toggleMultiSelect() // 开启多选功能
    },
  }
  return item
}
