import { message } from 'ant-design-vue'

import i18next from '@/plugins/i18next'

import { useRouteBack } from '@/hooks/useCommonRoute'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsBack() {
  const processStore = useProcessStore()

  const backToMain = async () => {
    try {
      await processStore.saveProject()
      await message.success(i18next.t('common.saveSuccess'), 0.5)
      useRouteBack()
      useFlowStore().toggleMultiSelect(false)
      useProjectDocStore().clearAllData()
      useRunlogStore().clearLogs()
    }
    catch (error) {
      console.log(error)
      message.error(i18next.t('common.saveFailedRetry'))
    }
  }

  const item: ArrangeTools = {
    key: 'back',
    title: 'goBack',
    name: '',
    fontSize: '24',
    icon: 'chevron-left',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => processStore.operationDisabled || ['debug', 'run'].includes(status),
    clickFn: backToMain,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning(i18next.t('arrange.stopRunningOrDebugFirst'))
      }

      return !disable
    },
  }

  return item
}
