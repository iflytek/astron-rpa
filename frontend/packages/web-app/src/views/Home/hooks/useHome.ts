import { NiceModal } from '@rpa/components'
import { onUnmounted } from 'vue'

import BUS from '@/utils/eventBus'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { LogModal } from '@/views/Home/components/modals'

export function useHome() {
  function openFileLogModal(path: string, dataTablePath?: string) {
    NiceModal.show(LogModal, {
      logPath: path,
      dataTablePath,
      onClearLogs: () => useRunlogStore().clearLogs(),
    })
  }

  BUS.$on('open-log-modal', openFileLogModal)

  onUnmounted(() => {
    BUS.$off('open-log-modal', openFileLogModal)
  })
}
