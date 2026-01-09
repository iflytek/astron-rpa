import { autoUpdater, type UpdateInfo as ElectronUpdateInfo } from "electron-updater"
import { to } from 'await-to-js'
// import { app } from 'electron'
import type { UpdateInfo, UpdateManifest } from '@rpa/shared/platform'
import { withTimeout } from '@rpa/shared'

import logger from "./log"
// import { version } from "os"
import { mainToRender } from './event'

autoUpdater.logger = logger
// autoUpdater.forceDevUpdateConfig = true
// 退出后不自动安装
autoUpdater.autoInstallOnAppQuit = false

// const server = 'https://your-deployment-url.com'
// const url = `${server}/update/${process.platform}/${app.getVersion()}\xxxx.exe
const url = 'http://localhost:9000'
autoUpdater.setFeedURL(url)

//监听'error'事件
// autoUpdater.on("error", (err) => {
//   logger.error("出错:", err);
// });

//监听'update-available'事件，发现有新版本时触发
// autoUpdater.on("update-available", () => {
//   logger.info("found new version");
// });

//默认会自动下载新版本，如果不想自动下载，设置autoUpdater.autoDownload = false
// 监听'download-progress'事件，下载进度更新时触发
// autoUpdater.on("download-progress", (info) => {
//   logger.info(`Download speed: ${info.bytesPerSecond}`);
//   logger.info(`Downloaded ${info.percent}%`);
//   logger.info(`Transferred ${info.transferred}/${info.total}`);
// });

const convertUpdateInfo = (info: ElectronUpdateInfo): UpdateManifest => ({
  version: info.version,
  date: info.releaseDate,
  body: info.releaseNotes?.toString() ?? '',
})

// 监听'update-downloaded'事件，新版本下载完成时触发
autoUpdater.on("update-downloaded", (event) => {
  const manifest = convertUpdateInfo(event)
  mainToRender('update-downloaded', JSON.stringify(manifest))
})

//检测更新
export const checkForUpdates = async (): Promise<UpdateInfo> => {
  const [error, result] = await to(autoUpdater.checkForUpdates());
  if (error) {
    return { couldUpdate: false }
  }

  let couldUpdate = result?.isUpdateAvailable ?? false
  let downloaded = false
  const manifest: UpdateManifest | null = result?.updateInfo ? convertUpdateInfo(result.updateInfo) : null

  if (couldUpdate && result?.downloadPromise) {
    // 有新版时，检测安装包是否已经下载，只有安装包全部下载完，可重启安装时，才返回有新版本
    // 由于 autoUpdater 没有 api 直接检测安装包是否已下载完，曲线救国，用 downloadPromise 来判断
    // 如果在 500ms 内，downloadPromise 没有 resolve，说明安装包还没有下载完
    try {
      await withTimeout(result?.downloadPromise, 500)
      downloaded = true
    } catch {
      downloaded = false
    }
  }

  return { couldUpdate, downloaded, manifest }
}

// 退出并安装更新
export const quitAndInstallUpdates = () => {
  autoUpdater.quitAndInstall()
}
