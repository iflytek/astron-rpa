import type { UpdateInfo, UpdaterManager as UpdaterManagerType } from '@rpa/shared/platform'

import { promiseTimeout } from '../utils/promiseTimeout'

export async function checkUpdate(): Promise<UpdateInfo> {
  const defaultResult: UpdateInfo = { shouldUpdate: false, manifest: null }

  try {
    const updater = await import('@tauri-apps/api/updater')
    return await promiseTimeout(updater.checkUpdate(), 2000, { default: defaultResult })
  }
  catch (error) {
    console.error(error)
  }

  return defaultResult
}

export async function installUpdate(progressCallback: (percent: number) => void) {
  const [updater, event, process] = await Promise.all([import('@tauri-apps/api/updater'), import('@tauri-apps/api/event'), import('@tauri-apps/api/process')])

  const unDownloadProgressListener = await event.listen<{ chunkLength: number, contentLength: number }>(event.TauriEvent.DOWNLOAD_PROGRESS, (ev) => {
    const progress = ev.payload
    const downloadedBytes = progress.chunkLength // 当前下载的字节数
    const totalBytes = progress.contentLength // 总字节数
    const percent = ((downloadedBytes / totalBytes) * 100).toFixed(2)
    progressCallback(Number(percent))
  })

  const unUpdaterListener = await updater.onUpdaterEvent(({ status }) => {
    if (status === 'DONE') {
      progressCallback(100)
      unDownloadProgressListener()
      unUpdaterListener()
    }
  })

  // 安装依赖，在 windows 上会自动重启
  await updater.installUpdate()
  // 在 macOS 和 Linux 上需要手动重启
  await process.relaunch()
}

const UpdaterManager: UpdaterManagerType = {
  checkUpdate,
  installUpdate,
}

export default UpdaterManager
