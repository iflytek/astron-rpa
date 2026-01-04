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
  saveFile: async (fileName: string, buffer: ArrayBuffer) => {
    const link = document.createElement('a')

    let blob: Blob
    if (typeof buffer === 'string') {
      blob = new Blob([buffer], { type: 'text/csv;charset=utf-8;' })
    }
    else {
      blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8',
      })
    }

    const url = URL.createObjectURL(blob)
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.addEventListener('click', () => {
      link.remove()
      setTimeout(() => {
        URL.revokeObjectURL(url)
      }, 200)
    })

    link.click()
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
