import { message } from 'ant-design-vue'

import { NEXT_DEBUG } from '@/constants/shortcuts'
import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsDebugNextStep() {
  const debugNextStep = () => {
    useRunningStore().nextStepDebug()
  }
  const item: ArrangeTools = {
    key: 'debugNextStep',
    title: 'debuggingNext',
    name: 'debuggingNext',
    fontSize: '',
    icon: 'tools-debug-next-step',
    action: '',
    loading: false,
    hotkey: NEXT_DEBUG,
    show: ({ status }) => ['debug'].includes(status),
    disable: ({ status, isBreak }) => ['free', 'run'].includes(status) || !isBreak,
    clickFn: debugNextStep,
    validateFn: ({ disable, show }) => {
      if (!show) {
        message.warning('请先开启调试模式, 再进行调试操作')
        return false
      }
      if (disable) {
        message.warning('正在运行调试, 请稍后')
        return false
      }

      return true
    },
  }
  return item
}
