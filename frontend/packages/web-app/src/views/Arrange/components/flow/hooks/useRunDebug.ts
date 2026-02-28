import { message } from 'ant-design-vue'
import { nextTick, watch } from 'vue'

import i18next from '@/plugins/i18next'

import $loading from '@/utils/globalLoading'

import { useFlowStore } from '@/stores/useFlowStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { atomScrollIntoView } from '@/views/Arrange/utils'

export function useRunDebug() {
  const runningStore = useRunningStore()
  // 每次debugData变化，自动滚动到当前debug的节点
  watch(() => runningStore?.breakpointAtom?.id, () => {
    const debugAtom = runningStore?.breakpointAtom
    if (debugAtom) {
      useFlowStore().setActiveAtom(useFlowStore().simpleFlowUIData.find(item => item.id === debugAtom.id))
      nextTick(() => atomScrollIntoView(debugAtom.id))
    }
  })

  // 监听运行调试状态，
  watch(() => runningStore?.status, () => {
    switch (runningStore?.status) {
      case 'starting':
        $loading.open({ msg: i18next.t('arrange.startingExecution') })
        break
      case 'startSuccess':
        $loading.close()
        message.success(i18next.t('arrange.executionStartSuccess'))
        break
      case 'startFailed':
        $loading.close()
        message.error(i18next.t('arrange.executionStartFailedRetry'))
        break
      case 'runSuccess':
        message.success(i18next.t('arrange.executionFinished'))
        break
      case 'runFailed':
        message.error(i18next.t('arrange.executionFailedRetry'))
        break
      case 'stopping':
        break
      case 'stopSuccess':
        message.success(i18next.t('arrange.executionStopped'))
        break
      case 'stopFailed':
        break
      default:
        break
    }
  })
}
