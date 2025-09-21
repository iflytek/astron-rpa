import { message } from 'ant-design-vue'

import { CONTINUE_DEBUG } from '@/constants/shortcuts'
import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsDebugContinue() {
  const debugNextBreakpoint = () => {
    useRunningStore().continueDebug()
  }

  const item: ArrangeTools = {
    key: 'debugContinue',
    title: 'debuggingContinues',
    name: 'debuggingContinues',
    fontSize: '',
    icon: 'tools-debug-continue',
    action: '',
    loading: false,
    hotkey: CONTINUE_DEBUG,
    show: ({ status }) => ['debug'].includes(status),
    disable: ({ status, isBreak }) => ['free', 'run'].includes(status) || !isBreak,
    clickFn: debugNextBreakpoint,
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
