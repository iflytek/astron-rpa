import path from 'node:path'

import { app, shell } from 'electron'

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

export async function openPath(targetPath: string): Promise<void> {
  // 使用 Electron 内置的 shell.openPath，它通过原生系统 API 打开文件/文件夹，
  // 不经过任何 shell 解析，因此路径中的 shell 元字符（如 "; "）不会被当作命令执行。
  // 之前基于 child_process.exec 拼接 shell 命令的实现存在命令注入风险。
  const path = require('node:path')
  const resolvedPath = path.resolve(targetPath)
  const errorMessage = await shell.openPath(resolvedPath)
  if (errorMessage) {
    throw new Error(errorMessage)
  }
}
