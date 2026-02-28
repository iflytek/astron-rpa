import { message, Modal } from 'ant-design-vue'

import i18next from '@/plugins/i18next'

import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsClear() {
  const handleClear = () => {
    Modal.confirm({
      title: i18next.t('presentation'),
      zIndex: 100,
      content: i18next.t('confirmClearAll'),
      okText: i18next.t('confirm'),
      cancelText: i18next.t('cancel'),
      onOk: () => {
        useProjectDocStore().clear()
      },
      centered: true,
      keyboard: false,
    })
  }
  const item: ArrangeTools = {
    key: 'clear',
    title: 'clear',
    name: '',
    fontSize: '',
    icon: 'tools-clear',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => ['debug', 'run'].includes(status) || isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: handleClear,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning(i18next.t('runningOrDebuggingCannotClear'))
        return false
      }
      return true
    },
  }
  return item
}
