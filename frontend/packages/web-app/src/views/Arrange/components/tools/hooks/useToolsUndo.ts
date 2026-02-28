import { message } from 'ant-design-vue'

import i18next from '@/plugins/i18next'

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
        message.warning(i18next.t('arrange.undoUnavailable'))
        return false
      }
      return true
    },
  }
  return item
}
