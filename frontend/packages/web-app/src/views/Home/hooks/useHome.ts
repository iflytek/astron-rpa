import { useFileLogModal } from '@/hooks/useFileLog'
import BUS from '@/utils/eventBus'

export function useHome() {
  const { openFileLogModal } = useFileLogModal()
  BUS.$off('open-log-modal')
  BUS.$on('open-log-modal', openFileLogModal)
}
