import type { WindowManager } from '@rpa/shared/platform'
import { noop } from 'lodash-es'

const { ipcRenderer } = window.electron

const loginWinState = {
  width: 1280,
  height: 750,
  maximized: false,
  center: true,
}

class ElectronWindowManager implements WindowManager {
  public platform = 'electron'
  public windows = new Map<string, any>()

  /**
   * 创建窗口
   */
  public async createWindow(options: any, closeCallback?: () => void): Promise<number | string> {
    const winId = await ipcRenderer.invoke('ipcCreateWindow', {
      ...options,
      title: options.title || options.label,
    })
    ipcRenderer.on('window-close', (_ev, id) => {
      id === winId && closeCallback?.()
    })
    return winId
  }

  /**
   *  窗口之间通信
   */
  async emitTo(message: {
    target: string // 目标窗口
    type: string // 消息类型
    data?: any // 消息内容
    from?: string // 发送方
  }): Promise<any> {
    return ipcRenderer.invoke('w2w', message)
  }

  /**
   * 显示窗口
   */
  async showWindow() {
    ipcRenderer.send('window-show')
  }

  /**
   * 隐藏窗口
   */
  async hideWindow() {
    ipcRenderer.send('window-hide')
  }

  /**
   * 最大化窗口，如果已经最大化，则还原
   */
  maximizeWindow(always: boolean = false): Promise<boolean> {
    return new Promise((resolve) => {
      ipcRenderer
        .invoke('window-is-maximized')
        .then((isMaximized: boolean) => {
          if (isMaximized && !always) {
            ipcRenderer.invoke('window-unmaximize').then(() => {
              this.centerWindow()
              resolve(false)
            })
          }
          else {
            ipcRenderer.invoke('window-maximize').then(() => {
              resolve(true)
            })
          }
        })
        .catch((err) => {
          console.error('Error checking window maximized state:', err)
          resolve(false)
        })
    })
  }

  /**
   * 最小化窗口
   */
  async minimizeWindow() {
    const res = await ipcRenderer.invoke('window-minimize')
    return res
  }

  /**
   * 还原窗口
   */
  async restoreWindow() {
    const res = await ipcRenderer.invoke('window-restore')
    return res
  }

  /**
   * 关闭窗口
   */
  closeWindow(label?: string | number) {
    ipcRenderer.send('window-close', { label }) // 发送关闭窗口的请求
  }

  /**
   * 设置窗口大小
   * @param width 默认屏幕宽度
   * @param height 默认为屏幕高度
   */
  setWindowSize: WindowManager['setWindowSize'] = async (params) => {
    const width = params?.width ?? screen.availWidth - 40
    const height = params?.height ?? screen.availHeight - 40

    ipcRenderer.send('window-set-size', width, height)
  }

  getScaleFactor() {
    return Promise.resolve(window.devicePixelRatio || 1)
  }

  scaleFactor() {
    return Promise.resolve(window.devicePixelRatio || 1)
  }

  async setWindowAlwaysOnTop(alwaysOnTop: boolean = true) {
    ipcRenderer.send('window-set-always-on-top', alwaysOnTop)
  }

  isMaximized(): Promise<boolean> {
    return new Promise((resolve) => {
      ipcRenderer
        .invoke('window-is-maximized')
        .then((isMaximized: boolean) => {
          resolve(isMaximized)
        })
        .catch((err) => {
          console.error('Error checking window maximized state:', err)
          resolve(false)
        })
    })
  }

  isMinimized(): Promise<boolean> {
    return new Promise((resolve) => {
      ipcRenderer
        .invoke('window-is-minimized')
        .then((isMinimized: boolean) => {
          resolve(isMinimized)
        })
        .catch((err) => {
          console.error('Error checking window minimized state:', err)
          resolve(false)
        })
    })
  }

  foucsWindow() {
    ipcRenderer
      .invoke('window-focus')
      .then((focused: boolean) => {
        if (!focused) {
          setTimeout(async () => {
            await ipcRenderer.invoke('window-focus')
          }, 300)
        }
      })
      .catch((err) => {
        console.error('Error focusing the window:', err)
      })
  }

  /**
   * 恢复到登录窗口大小
   */
  restoreLoginWindow() {
    ipcRenderer.send('window-set-size', loginWinState.width, loginWinState.height)
    this.centerWindow()
  }

  centerWindow() {
    ipcRenderer.send('window-center')
  }

  getScreenWorkArea() {
    return new Promise((resolve, reject) => {
      ipcRenderer
        .invoke('get-workarea')
        .then((workArea) => {
          resolve(workArea)
        })
        .catch((err) => {
          console.error('Error getting screen work area:', err)
          reject(err)
        })
    })
  }

  /**
   * set physical window position
   * @param x
   * @param y
   */
  async setWindowPosition(x: number = 0, y: number = 0) {
    const dpr = devicePixelRatio
    ipcRenderer.send('window-set-position', Math.floor(x / dpr), Math.floor(y / dpr))
  }

  /**
   * set logical window position
   * @param x
   * @param y
   */
  async setLogicalWindowPosition(x: number = 0, y: number = 0) {
    ipcRenderer.send('window-set-position', x, y)
  }

  showDecorations() {
    console.log('showDecorations')
    ipcRenderer.send('window-set-menubar', true)
  }

  hideDecorations() {
    // electron doesn't support hide close buttons
    ipcRenderer.send('window-set-menubar', false)
  }

  minLogWindow(bool: boolean) {
    const initialWidth = Math.floor(window.screen.availWidth)
    const initialHeight = Math.floor(window.screen.availHeight)
    if (bool) {
      this.setWindowSize({ width: 32, height: 128 })
      this.setLogicalWindowPosition(initialWidth - 32 - 2, initialHeight - 128 - 2)
    }
    else {
      this.setWindowSize({ width: 360, height: 128 })
      this.setLogicalWindowPosition(initialWidth - 360 - 2, initialHeight - 128 - 2)
    }
  }

  async onWindowResize(callback: () => void) {
    window.addEventListener('resize', callback)
    return noop
  }

  async onWindowClose(callback: () => void) {
    ipcRenderer.on('window-close-confirm', (_ev, _arg) => callback?.())
  }
}

export default ElectronWindowManager
