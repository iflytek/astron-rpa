import { NiceModal } from '@rpa/components'

import { useRunlogStore } from '@/stores/useRunlogStore'
import { LogModal } from '@/views/Home/components/modals'

export function useFileLogModal() {
  function openFileLogModal(path: string) {
    NiceModal.show(LogModal, {
      logPath: path,
      onClearLogs: () => {
        useRunlogStore().clearLogs()
      },
    })
  }

  return { openFileLogModal }
}
