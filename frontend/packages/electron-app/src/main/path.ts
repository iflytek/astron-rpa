import path from 'node:path'

import { app } from 'electron'

export const appPath = app.getAppPath()
export const userDataPath = app.getPath('userData')
export const appDataPath = app.getPath('appData')

// 打包后，资源文件存储在 appPath 下的 resources 目录，否则存储在根目录下的 resources 目录
export const resourcePath = app.isPackaged ? path.join(appPath, '../') : path.join(appPath, '../../../resources')
// 打包后，数据存储在 userDataPath ，否则存储在 appPath 下的 data 目录
export const appWorkPath = app.isPackaged ? userDataPath : path.join(appPath, 'data')
export const pythonCore = path.join(appWorkPath, 'python_core')
export const pythonExe = path.join(pythonCore, 'python.exe')
export const confPath = path.join(resourcePath, 'conf.yaml')
export const d7zrPath = path.join(resourcePath, '7zr.exe')
// 插件目录
export const extensionPath = [
  path.join(appPath, 'extensions'), // 系统插件目录
  path.join(appWorkPath, 'extensions'), // 用户插件目录
]
export const extensionHost = 'extensions'
export const extensionBaseUrl =  `rpa://${extensionHost}/`

export const rendererPath = path.join(__dirname, '../renderer')
export const windowBaseUrl  = app.isPackaged ? 'rpa://localhost/' : 'http://localhost:1420/'

export function openPath(targetPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const { exec } = require('node:child_process')
    const path = require('node:path')

    // 要打开的文件或文件夹路径
    targetPath = path.resolve(targetPath)

    // 根据操作系统选择命令
    const openCommand = process.platform === 'win32' ? `start "" "${targetPath}"` : `xdg-open "${targetPath}"`

    exec(openCommand, (error) => {
      error ? reject(error) : resolve()
    })
  })
}
