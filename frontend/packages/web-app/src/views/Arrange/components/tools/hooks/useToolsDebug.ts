import { message } from 'ant-design-vue'

import { DEBUG } from '@/constants/shortcuts'
import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsDebug() {
  const processStore = useProcessStore()

  const handleDebugBreakpoint = async () => {
    await processStore.saveProject()
    useRunningStore().startDebug(processStore.project.id, processStore.activeProcessId)
  }

  const item: ArrangeTools = {
    key: 'debug',
    title: 'debug',
    name: 'debug',
    fontSize: '',
    icon: 'tools-debug',
    action: '',
    loading: false,
    hotkey: DEBUG,
    show: ({ status }) => ['free'].includes(status),
    disable: ({ status }) => {
      const isPy = isPyModel(processStore.activeProcess?.resourceCategory)

      return isPy || processStore.operationDisabled || ['debug', 'run'].includes(status)
    },
    clickFn: handleDebugBreakpoint,
    validateFn: ({ disable, show }) => {
      const disabled = disable || !show

      if (disabled) {
        message.warning('当前正在运行/调试, 请勿重复操作')
      }

      return !disabled
    },
  }
  return item
}
