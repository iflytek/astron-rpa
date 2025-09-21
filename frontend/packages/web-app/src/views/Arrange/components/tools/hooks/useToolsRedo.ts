import { message } from 'ant-design-vue'

import { REDO } from '@/constants/shortcuts'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsRedo() {
  const handleRedo = () => {
    useProjectDocStore().redo()
  }
  const item: ArrangeTools = {
    key: 'redo',
    title: 'redo',
    name: '',
    fontSize: '',
    icon: 'tools-recover',
    action: '',
    loading: false,
    show: true,
    hotkey: REDO,
    disable: ({ status, canRestore }) => ['debug', 'run'].includes(status) || !canRestore || isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: handleRedo,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('运行调试中或无操作记录, 不可进行重做操作')
        return false
      }
      return true
    },
  }
  return item
}
