import type { AppEnv, UtilsManager as UtilsManagerType } from '@rpa/shared/platform'
import { dialog } from '@tauri-apps/api'
import { getTauriVersion, getVersion } from '@tauri-apps/api/app'
import { listen } from '@tauri-apps/api/event'
import { BaseDirectory, readBinaryFile } from '@tauri-apps/api/fs'
import { arch, platform, version } from '@tauri-apps/api/os'
import { appDataDir, join, resourceDir } from '@tauri-apps/api/path'
import { open } from '@tauri-apps/api/shell'
import { invoke } from '@tauri-apps/api/tauri'

import type { DialogObj } from '../types'

import ClipboardManager from './clipboardManager'

function getAppEnv(): AppEnv {
  return 'tauri'
}

function openInBrowser(url: string, browser?: string) {
  browser ? open(url, 'google chrome') : open(url)
}

function listenEvent(eventName: string, callback: (data: any) => void) {
  listen(eventName, (event) => {
    callback(event.payload)
  })
}

async function getAppVersion() {
  const version = await getVersion()
  return version
}

async function getAppPath() {
  const path = await resourceDir()
  if (path.startsWith('\\\\?\\')) {
    return path.slice(4)
  }
  return path
}

async function getUserPath() {
  const path = await appDataDir()
  return path
}

async function getBuildInfo() {
  const v = await getTauriVersion()
  const buildInfo = `Build by Tauri ${v}`
  return buildInfo
}

async function getSystemEnv() {
  const platformInfo = await platform()
  const archInfo = await arch()
  const versionInfo = await version()
  const sysInfo = `${versionInfo} ${platformInfo} ${archInfo} `
  return sysInfo
}

async function _invoke(channel: string, ...args: any[]): Promise<any> {
  const res = await invoke(channel, ...args)
  return res
}

async function readFile(fileName: string) {
  const contents = readBinaryFile(fileName, { dir: BaseDirectory.Home })
  return contents
}

function playVideo(videoPath: string) {
  open(videoPath)
}

async function pathJoin(dirArr: Array<string>) {
  const path = await join(...dirArr)
  return path
}

function shellopen(path: string) {
  return new Promise<void>((resolve, reject) => {
    const fullPath = path.replace(/\\/g, '/')
    console.log('fullPath: ', fullPath)
    ClipboardManager.writeClipboardText(fullPath)
    open(fullPath).then(resolve).catch(reject)
  })
}

async function openPlugins() {
  const appPath = await getAppPath()
  let userDataPath = await getUserPath()
  if (!userDataPath.endsWith('/')) {
    userDataPath += '/'
  }
  if (appPath.startsWith('C:') || appPath.startsWith('c:') || appPath.startsWith('/')) {
    shellopen(`${userDataPath}python_core/Lib/site-packages/rpa_browser_plugin/plugins`)
  }
  else {
    shellopen(`${appPath}data/python_core/Lib/site-packages/rpa_browser_plugin/plugins`)
  }
}

const showDialog: UtilsManagerType['showDialog'] = (dialogProps) => {
  const { file_type, filters: dialogFilters, multiple, defaultPath = '' } = dialogProps
  let isDirectory = false // 默认打开文件
  let isMultiple = false // 默认单选
  const dialogObj: DialogObj = { title: '选择文件目录', defaultPath }
  if (file_type === 'folder')
    isDirectory = true // 如果是文件夹，则打开文件夹
  if (file_type === 'files')
    isMultiple = true
  if (file_type === 'file')
    isMultiple = multiple
  if (dialogFilters && dialogFilters.length > 0) {
    const filtersType = dialogFilters.map((item: string) => item.replace('.', ''))
    dialogObj.filters = [{ name: '', extensions: filtersType }]
  }
  return new Promise((resolve) => {
    dialogObj.directory = isDirectory
    dialogObj.multiple = isMultiple
    dialog.open(dialogObj).then((result) => {
      if (result) {
        resolve(result)
      }
    })
  })
}

const getPluginPath: UtilsManagerType['getPluginPath'] = async (_filePath) => {
  console.log('getPluginPath')
  return ""
}

const getPluginList: UtilsManagerType['getPluginList'] = async () => {
  console.log('getPluginList')
  return []
}

const UtilsManager: UtilsManagerType = {
  getAppEnv,
  isBrowser: false,
  openInBrowser,
  listenEvent,
  getAppVersion,
  getAppPath,
  getUserPath,
  getBuildInfo,
  getSystemEnv,
  invoke: _invoke,
  readFile,
  playVideo,
  pathJoin,
  shellopen,
  openPlugins,
  showDialog,
  getPluginPath,
  getPluginList,
}

export default UtilsManager
