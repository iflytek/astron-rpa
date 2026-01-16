import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'

import { RUN } from '@/constants/shortcuts'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsRun() {
  const processStore = useProcessStore()

  const handleConfirmRun = throttle(async () => {
    await processStore.saveProject()
    useRunningStore().startRun(processStore.project.id, processStore.activeProcessId)
  }, 1500, { leading: true, trailing: false })

  const item: ArrangeTools = {
    key: 'run',
    title: 'run',
    name: 'run',
    fontSize: '',
    icon: 'tools-run',
    action: '',
    loading: false,
    hotkey: RUN,
    show: ({ status }) => ['free'].includes(status),
    disable: ({ status }) => {
      const isPy = isPyModel(processStore.activeProcess?.resourceCategory)

      return isPy || processStore.operationDisabled || ['debug', 'run'].includes(status)
    },
    clickFn: handleConfirmRun,
    validateFn: ({ disable, show }) => {
      if (disable || !show) {
        message.warning('当前正在运行/调试, 请勿重复操作')
      }

      return !disable
    },
  }

  return item
}
