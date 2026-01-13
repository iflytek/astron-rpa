import type { AppEnv, UtilsManager as UtilsManagerType } from '@rpa/shared/platform'

import type { DialogObj } from '../types'

import ClipboardManager from './clipboardManager'

const { ipcRenderer } = window.electron

function getAppEnv(): AppEnv {
  return 'electron'
}

function openInBrowser(url: string) {
  ipcRenderer.send('open-in-browser', url)
}

function listenEvent(eventName: string, callback: (data: any) => void) {
  ipcRenderer.on(eventName, (_event, data) => callback(data))
}

function getFromElectronInfo<T>(key: string, defaultValue: T): Promise<T> {
  return new Promise((resolve) => {
    const electronInfo = localStorage.getItem('electron');
    if (electronInfo) {
      try {
        const info = JSON.parse(electronInfo);
        resolve(info[key] ?? defaultValue);
      } catch (e) {
        console.error('Failed to parse electron info from localStorage', e);
        resolve(defaultValue);
      }
    } else {
      resolve(defaultValue);
    }
  });
}

function getAppVersion() {
  return getFromElectronInfo<string>('appVersion', 'latest')
}

function getAppPath() {
  return getFromElectronInfo<string>('appPath', '')
}

function getUserPath() {
  return getFromElectronInfo<string>('userDataPath', '')
}

function getResourcePath() {
  return getFromElectronInfo<string>('resourcePath', '')
}

async function getBuildInfo() {
  const electronVersion = await getFromElectronInfo<string>('electronVersion', '')
  return `Build by Electron ${electronVersion}`
}

function getSystemEnv() {
  return new Promise<string>((resolve) => {
    const electronInfo = localStorage.getItem('electron')
    if (electronInfo) {
      const { arch, platform, release } = JSON.parse(electronInfo)
      const sysInfo = `${release} ${platform} ${arch} `
      resolve(sysInfo)
    }
    else {
      resolve('')
    }
  })
}

function invoke(channel: string, ...args: any[]): Promise<any> {
  return new Promise<any>((resolve, reject) => {
    ipcRenderer.invoke(channel, ...args).then((res) => {
      resolve(res)
    }).catch(err => reject(err))
  })
}

const readFile: UtilsManagerType['readFile'] = (fileName, dir) => {
  return ipcRenderer.invoke('read-file', `${dir}/${fileName}`)
}

const saveFile: UtilsManagerType['saveFile'] = (fileName, buffer) => {
  return ipcRenderer.invoke('save-file', fileName, buffer)
}

function playVideo(videoPath: string) {
  ipcRenderer.invoke('open-path', videoPath).then((res) => {
    if (res) {
      console.log('Video played successfully')
    }
    else {
      console.error('Failed to play video')
    }
  })
}

function pathJoin(dirArr: Array<string>) {
  return new Promise((resolve) => {
    ipcRenderer.invoke('path-join', ...dirArr).then((path) => {
      resolve(path)
    })
  })
}

function shellopen(path: string) {
  return new Promise<void>((resolve, reject) => {
    const fullPath = path.replace(/\\/g, '/')
    console.log('fullPath: ', fullPath)
    ClipboardManager.writeClipboardText(fullPath)
    ipcRenderer
      .invoke('open-path', fullPath)
      .then((res) => {
        if (res) {
          console.log('Shell opened successfully')
          resolve()
        }
        else {
          console.error('Failed to open shell')
          reject(new Error('Failed to open shell'))
        }
      })
      .catch((err) => {
        console.error('Error opening shell:', err)
        reject(err)
      })
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
    const fileArr: any[] = []
    const directoryRes = isDirectory ? 'openDirectory' : 'openFile'
    fileArr.push(directoryRes)
    if (isMultiple)
      fileArr.push('multiSelections')
    dialogObj.properties = fileArr
    ipcRenderer.invoke('open-dialog', dialogObj).then((res) => {
      if (res) {
        resolve(res)
      }
      else {
        resolve(null)
      }
    })
  })
}

const getPluginPath: UtilsManagerType['getPluginPath'] = async (_filePath) => {
  console.log('getPluginPath')
  return ''
}

const getPluginList: UtilsManagerType['getPluginList'] = async () => {
  console.log('getPluginList')
  return []
}

const UtilsManager: UtilsManagerType = {
  getAppEnv,
  getAppPath,
  getAppVersion,
  getBuildInfo,
  getSystemEnv,
  getUserPath,
  listenEvent,
  readFile,
  saveFile,
  invoke,
  openInBrowser,
  openPlugins,
  pathJoin,
  playVideo,
  shellopen,
  showDialog,
  getPluginPath,
  getPluginList,
  getResourcePath,
}

export default UtilsManager
