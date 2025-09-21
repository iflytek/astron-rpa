import { message } from 'ant-design-vue'
import { onBeforeUnmount, onMounted } from 'vue'

import BUS from '@/utils/eventBus'

import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import { useRecordWindow } from '@/views/Arrange/hook/useRecordWindow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'
import { addRecordAtomData } from '@/views/Arrange/utils/record'

export function useToolsRecorder() {
  const { open } = useRecordWindow()
  const processStore = useProcessStore()

  onMounted(() => {
    BUS.$off('record-save')
    BUS.$on('record-save', addRecordAtomData)
  })

  onBeforeUnmount(() => {
    BUS.$off('record-save')
  })

  const item: ArrangeTools = {
    key: 'intelligentRecording',
    title: 'smartRecording',
    name: 'smartRecording',
    fontSize: '',
    icon: 'tools-record',
    action: 'design_recorder',
    loading: false,
    show: true,
    disable: ({ status }) => {
      return isPyModel(processStore.activeProcess?.resourceCategory) || ['debug', 'run'].includes(status)
    },
    clickFn: open,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('正在运行/调试, 请先停止')
        return false
      }
      return true
    },
  }

  return item
}
