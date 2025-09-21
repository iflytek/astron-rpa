import { useTranslation } from 'i18next-vue'

import { baseUrl } from '@/utils/env'

import { WINDOW_NAME } from '@/constants'
import { windowManager } from '@/platform'

export function useRecordWindow() {
  const { t } = useTranslation()

  // 智能录制窗口
  const openRecordWindow = async () => {
    const options = {
      url: `${baseUrl}/record.html`,
      title: t('smartRecording'),
      label: WINDOW_NAME.RECORD,
      alwaysOnTop: false,
      position: 'right_center', // 自定义参数
      offset: 40,
      width: 392,
      height: 572,
      resizable: false,
      decorations: false,
      fileDropEnabled: false,
      maximizable: false,
      transparent: true,
    }

    await windowManager.createWindow(options, () => {
      windowManager.showWindow()
    })

    windowManager.hideWindow()
  }

  const openRecordMenuWindow = async () => {
    const options = {
      url: `${baseUrl}/recordmenu.html`,
      title: t('smartRecording'),
      label: WINDOW_NAME.RECORD_MENU,
      alwaysOnTop: true,
      position: 'center',
      width: 20,
      height: 20,
      resizable: false,
      decorations: false,
      fileDropEnabled: false,
      maximizable: false,
      transparent: true,
      visible: false,
      skipTaskbar: true,
    }

    await windowManager.createWindow(options)
  }

  const open = () => {
    openRecordWindow()
    openRecordMenuWindow()
  }

  return { open }
}
