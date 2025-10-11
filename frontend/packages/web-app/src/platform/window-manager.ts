import type { WindowManager } from '@rpa/shared/platform'
import { noop } from 'lodash-es'

import type { WINDOW_NAME } from '@/constants'

export type UnlistenFn = () => void

class BrowserWindowManager implements WindowManager {
  public windows = new Map<string, any>()
  public platform: string

  constructor() {
    this.windows = new Map()
  }

  getScaleFactor(): Promise<number> {
    return Promise.resolve(1)
  }

  createWindow(_options?: any, closeCallback?: () => void): Promise<any> {
    return new Promise((resolve) => {
      resolve(1)
    }).catch(() => {
      closeCallback && closeCallback()
    })
  }

  scaleFactor(): Promise<number> {
    return new Promise((resolve) => {
      resolve(1)
    })
  }

  showWindow(): Promise<void> {
    return Promise.resolve()
  }

  hideWindow(): Promise<void> {
    return Promise.resolve()
  }

  closeWindow() {}

  maximizeWindow(_always?: boolean): Promise<boolean> {
    return Promise.resolve(false)
  }

  minimizeWindow() {}

  restoreWindow() {}

  setWindowSize(_params?: {
    width?: number
    height?: number
    windowName?: string
  }): Promise<void> {
    return Promise.resolve()
  }

  setWindowAlwaysOnTop(_alwaysOnTop?: boolean): Promise<void> {
    return Promise.resolve()
  }

  centerWindow(_options?: any) {}

  isMaximized(): Promise<boolean> {
    return Promise.resolve(false)
  }

  isMinimized(): Promise<boolean> {
    return Promise.resolve(false)
  }

  showDecorations() {}

  hideDecorations() {}

  foucsWindow() {}

  restoreLoginWindow() {}

  getScreenWorkArea(): any {}

  setWindowPosition(_x?: number, _y?: number): Promise<void> {
    return Promise.resolve()
  }

  minLogWindow(_bool: boolean) {}

  async onWindowResize(_callback: () => void): Promise<UnlistenFn> {
    return noop
  }

  onWindowClose(_callback: () => void) {}

  emitTo(_msg: {
    from?: WINDOW_NAME
    target: WINDOW_NAME
    type: string
    data?: any
  }): Promise<any> {
    return new Promise((resolve) => {
      resolve(true)
    })
  }
}

export default BrowserWindowManager
