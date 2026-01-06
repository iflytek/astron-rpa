import { NiceModal } from '@rpa/components'

import { useRunlogStore } from '@/stores/useRunlogStore'
import { LogModal } from '@/views/Home/components/modals'

export function useFileLogModal() {
  function openFileLogModal(path: string, dataTablePath?: string) {
    NiceModal.show(LogModal, {
      logPath: path,
      dataTablePath,
      onClearLogs: () => useRunlogStore().clearLogs(),
    })
  }

  return { openFileLogModal }
}
