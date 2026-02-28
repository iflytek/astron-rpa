import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'

import i18next from '@/plugins/i18next'

import { SAVE } from '@/constants/shortcuts'
import { useProcessStore } from '@/stores/useProcessStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsSave() {
  const processStore = useProcessStore()

  const save = throttle(async () => {
    try {
      await processStore.saveProject()
      message.success(i18next.t('common.saveSuccess'))
    }
    catch {
      message.error(i18next.t('common.saveFailed'))
    }
  }, 1500, { leading: true, trailing: false })

  const item: ArrangeTools = {
    key: 'save',
    title: 'save',
    name: 'save',
    fontSize: '',
    icon: 'tools-save',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => processStore.operationDisabled || ['debug', 'run'].includes(status),
    hotkey: SAVE,
    clickFn: save,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning(i18next.t('arrange.cannotSaveWhileRunningOrDebug'))
      }

      return !disable
    },
  }

  return item
}
