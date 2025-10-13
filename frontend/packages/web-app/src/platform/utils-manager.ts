import type { UtilsManager } from '@rpa/shared/platform'

const Utils: UtilsManager = {
  getAppVersion: () => Promise.resolve('0.0.0'),
  getAppPath: () => Promise.resolve('/unknown'),
  getUserPath: () => Promise.resolve('/unknown'),
  getBuildInfo: () => Promise.resolve('browser'),
  getSystemEnv: () => Promise.resolve('browser'),
  getAppEnv: () => 'browser',
  isBrowser: true,
  openInBrowser: (url: string) => {
    window.open(url, '_blank')
  },
  listenEvent: (_eventName: string, _callback: (data: any) => void) => {
    console.warn('listenEvent is not supported in browser environment')
  },
  invoke: (_channel: string, _args: any[]) => {
    return Promise.reject(new Error('invoke is not supported in browser environment'))
  },
  readFile: (_fileName: string) => {
    return Promise.reject(new Error('readFile is not supported in browser environment'))
  },
  playVideo: (videoPath: string) => {
    window.open(videoPath, '_blank')
  },
  pathJoin: (dirArr: Array<string>) => {
    return Promise.resolve(dirArr.join('/').replace(/\/+/g, '/'))
  },
  shellopen: (path: string) => {
    window.open(path, '_blank')
    return Promise.resolve()
  },
  openPlugins: () => {
    return Promise.reject(new Error('openPlugins is not supported in browser environment'))
  },
  showDialog: (_dialogProps: any) => {
    return Promise.reject(new Error('showDialog is not supported in browser environment'))
  },
  getPluginPath: (_filePath: string) => {
    return Promise.reject(new Error('getPluginPath is not supported in browser environment'))
  },
  getPluginList: () => {
    return Promise.reject(new Error('getPluginList is not supported in browser environment'))
  },
}

export default Utils
