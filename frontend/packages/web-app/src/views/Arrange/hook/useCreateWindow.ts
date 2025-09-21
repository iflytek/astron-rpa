import { baseUrl } from '@/utils/env'

import { WINDOW_NAME } from '@/constants'
import { windowManager } from '@/platform'
import { usePickStore } from '@/stores/usePickStore'
import { useProcessStore } from '@/stores/useProcessStore'

/**
 * 应用内打开窗口
 */
export function useCreateWindow() {
  const pickStore = usePickStore()
  const processStore = useProcessStore()

  // 数据抓取窗口
  const openDataPickWindow = async (customOptions?: { id: string, noEmit: boolean }) => {
    // 只允许一个数据抓取窗口
    if (pickStore.isDataPicking)
      return

    const robotId = processStore.project.id
    const { id, noEmit } = customOptions || {}
    let url = `${baseUrl}/batch.html?robotId=${robotId}`
    if (id) {
      url = `${url}&elementId=${id}&isEdit=true`
    }
    if (noEmit) {
      url = `${url}&noEmit=true`
    }

    const options = {
      url,
      title: '数据抓取',
      label: WINDOW_NAME.BATCH,
      alwaysOnTop: false,
      position: 'right_top', // 自定义参数
      width: 580,
      height: 480,
      resizable: false,
      decorations: false,
      fileDropEnabled: false,
      maximizable: false,
      transparent: true,
    }
    await windowManager.createWindow(options, () => {
      pickStore.setDataPicking(false)
      windowManager.showWindow()
    })

    pickStore.setDataPicking(true)

    windowManager.hideWindow()
  }

  return { openDataPickWindow }
}
