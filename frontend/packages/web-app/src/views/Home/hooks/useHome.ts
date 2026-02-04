import BUS from '@/utils/eventBus'

import { useFileLogModal } from '@/hooks/useFileLog'

import { useBrowerPlugin } from '@/components/SettingCenterModal/components/pluginInstall/hooks/useBrowerPlugin'

export function useHome() {
  const { openFileLogModal } = useFileLogModal()
  const { pluginUpdateModal } = useBrowerPlugin()
  pluginUpdateModal()
  BUS.$off('open-log-modal')
  BUS.$on('open-log-modal', openFileLogModal)
}
