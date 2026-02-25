import { useTranslation } from 'i18next-vue'

import { baseUrl } from '@/utils/env'

import { WINDOW_NAME } from '@/constants'
import { windowManager, type CreateWindowOptions } from '@/platform'

export function useSmartCompPickWindow(closeCallback?: () => void) {
  const { t } = useTranslation()

  // 智能组件拾取悬浮窗
  const openSmartCompPickMenuWindow = async () => {
    // 窗口不能置于后台，否则无法通过任务栏关闭所有窗口，导致应用无法关闭
    // windowManager.createWindow 设置的位置不准确，且创建窗口延迟较高，只能先创建窗口再通过 windowManager.setWindowPosition 调整窗口位置
    const options: CreateWindowOptions = {
      url: `${baseUrl}/smartcompickmenu.html`,
      title: t('smartComponentPick') || '智能组件拾取',
      label: WINDOW_NAME.SMART_COMP_PICK_MENU,
      alwaysOnTop: true,
      width: 160,
      height: 40,
      x: -999,
      y: -999,
      resizable: false,
      decorations: false,
      fileDropEnabled: false,
      maximizable: false,
      transparent: true,
      show: true,
      skipTaskbar: false,
    }

    await windowManager.createWindow(options, closeCallback)
  }

  const open = () => {
    openSmartCompPickMenuWindow()
  }

  return { open }
}
