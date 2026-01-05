import path from 'node:path'

import { app } from 'electron'

export const resourcePath = path.join(app.getAppPath(), 'resources')
export const userDataPath = app.getPath('userData')
export const appPath = app.getAppPath()
export const appDataPath = app.getPath('appData')
export const notFoundPath = path.join(resourcePath, '404.html')
export const appWorkPath = path.join(appDataPath, 'iflyrpa')
export const pythonCore = path.join(appWorkPath, 'python_core')
export const pythonBase = path.join(appWorkPath, 'python_base')
export const pythonExe = path.join(pythonCore, 'python.exe')
export const confPath = path.join(resourcePath, 'conf.json')
export const d7zrPath = path.join(resourcePath, '7zr.exe')

export function openPath(targetPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const { exec } = require('node:child_process')
    const path = require('node:path')

    // 要打开的文件或文件夹路径
    targetPath = path.resolve(targetPath)

    // 根据操作系统选择命令
    const openCommand = process.platform === 'win32' ? `start "" "${targetPath}"` : `xdg-open "${targetPath}"`

    exec(openCommand, (error) => {
      if (error) {
        reject(error)
      }
      resolve()
    })
  })
}
