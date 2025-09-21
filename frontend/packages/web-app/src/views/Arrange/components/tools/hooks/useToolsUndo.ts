import { message } from 'ant-design-vue'

import { UNDO } from '@/constants/shortcuts'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsUndo() {
  const handleUndo = () => {
    useProjectDocStore().undo()
  }
  const item: ArrangeTools = {
    key: 'undo',
    title: 'undo',
    name: '',
    fontSize: '',
    icon: 'tools-undo',
    action: '',
    loading: false,
    show: true,
    disable: ({ status, canUndo }) => ['debug', 'run'].includes(status) || !canUndo || isPyModel(useProcessStore().activeProcess?.resourceCategory),
    hotkey: UNDO,
    clickFn: handleUndo,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('运行调试中或无操作记录, 不可进行撤销操作')
        return false
      }
      return true
    },
  }
  return item
}
