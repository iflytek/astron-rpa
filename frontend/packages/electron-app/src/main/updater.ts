import { autoUpdater } from "electron-updater"
import { app } from 'electron'
import type { UpdateInfo } from '@rpa/shared/platform'

import logger from "./log"
import { version } from "os"

autoUpdater.logger = logger
autoUpdater.forceDevUpdateConfig = true
// 退出后自动安装
autoUpdater.autoInstallOnAppQuit = true

// const server = 'https://your-deployment-url.com'
// const url = `${server}/update/${process.platform}/${app.getVersion()}`
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
autoUpdater.on("download-progress", (info) => {
  logger.info(`Download speed: ${info.bytesPerSecond}`);
  logger.info(`Downloaded ${info.percent}%`);
  logger.info(`Transferred ${info.transferred}/${info.total}`);
});

// 监听'update-downloaded'事件，新版本下载完成时触发
autoUpdater.on("update-downloaded", (event) => {
})

//检测更新
export const checkForUpdates = async (): Promise<UpdateInfo> => {
  const result = await autoUpdater.checkForUpdates();

  const shouldUpdate = result?.isUpdateAvailable || false

  let manifest: UpdateInfo['manifest'] = null
  if (result?.updateInfo) {
    manifest = {
      version: result.updateInfo.version,
      date: result.updateInfo.releaseDate,
      body: result.updateInfo.releaseNotes?.toString() ?? '',
    }
  }

  return { shouldUpdate, manifest }
}

// 退出并安装更新
export const quitAndInstallUpdates = () => {
  autoUpdater.quitAndInstall()
}
