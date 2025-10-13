import type { CreateWindowOptions, WindowManager } from '@rpa/shared/platform'
import { appWindow, getCurrent, LogicalPosition, LogicalSize, PhysicalPosition, PhysicalSize, primaryMonitor, WebviewWindow } from '@tauri-apps/api/window'

const loginWinState = {
  width: 1200,
  height: 718,
  maximized: false,
  center: true,
}

const windowScreen = {
  width: screen.availWidth * devicePixelRatio,
  height: screen.availHeight * devicePixelRatio,
}

const windowSize = new PhysicalSize(windowScreen.width, windowScreen.height)

/**
 * 创建一个TauriWindowManager实例
 */
class TauriWindowManager implements WindowManager {
  public platform = 'tauri'
  public windows: Map<string, WebviewWindow> = new Map()

  constructor() {
    const win = getCurrent()
    win.onResized(async () => {
      await win.setAlwaysOnTop(false)
      await win.setResizable(true)
    })
  }

  getWindow() {
    return getCurrent()
  }

  async getScaleFactor(): Promise<number> {
    const win = getCurrent()
    const scale = await win.scaleFactor()
    return devicePixelRatio / scale
  }

  /**
   * 创建一个新窗口
   */
  async createWindow(_options?: CreateWindowOptions, closeCallback?: () => void): Promise<any> {
    const win = getCurrent()
    const primary = await primaryMonitor()
    const currentScale = await win.scaleFactor()
    const { label, position, offset = 0, ...options } = _options as any
    const scale = primary?.scaleFactor || currentScale
    const screenWidth = windowSize.toLogical(scale).width
    const screenHeight = windowSize.toLogical(scale).height
    const screenScale = await this.getScaleFactor()

    // tauri 的width， height重新计算
    options.width = options.width * screenScale
    options.height = options.height * screenScale

    switch (position) {
      case 'center':
        options.x = screenWidth / 2 - options.width / 2
        options.y = screenHeight / 2 - options.height / 2
        break
      case 'top':
        options.x = screenWidth / 2 - options.width / 2
        options.y = 2
        break
      case 'left_top':
        options.x = 2
        options.y = 2
        break
      case 'left_bottom':
        options.x = 2
        options.y = screenHeight - options.height - 2
        break
      case 'right_top':
        options.x = screenWidth - options.width - 2
        options.y = 2
        break
      case 'right_bottom':
        options.x = screenWidth - options.width - 2
        options.y = screenHeight - options.height - 2
        break
      case 'right_center':
        options.x = screenWidth - options.width - offset
        options.y = screenHeight / 2 - options.height / 2
        break
      default:
        break
    }

    // await invoke('create_window', { options: { label, ...options } })
    const webview = new WebviewWindow(label, options)
    webview.onCloseRequested(() => closeCallback?.())
    return label
  }

  async scaleFactor(): Promise<number> {
    const win = getCurrent()
    return await win.scaleFactor()
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
    const targrt = WebviewWindow.getByLabel(message.target)
    if (targrt) {
      targrt.emit('w2w', message)
    }
  }

  /**
   * 显示当前窗口
   */
  async showWindow(label?: string | number) {
    const win = label ? WebviewWindow.getByLabel(label.toString()) : getCurrent()
    await win?.show()
  }

  /**
   * 隐藏当前窗口
   */
  async hideWindow() {
    const win = getCurrent()
    await win.hide()
  }

  /**
   * 最大化窗口，如果窗口已经是最大化状态，则恢复窗口
   */
  async maximizeWindow(always: boolean = false) {
    const win = getCurrent()
    if (always) {
      await win.maximize()
    }
    else {
      await win.toggleMaximize()
    }
    await win.setFocus()
    const isFocused = await win.isFocused()
    if (!isFocused) {
      await this.foucsWindow()
    }
    return await win.isMaximized()
  }

  /**
   * 最小化窗口
   */
  async minimizeWindow() {
    const win = getCurrent()
    await win.minimize()
  }

  /**
   * 恢复窗口（如果窗口被最大化）
   */
  async restoreWindow() {
    const win = getCurrent()
    const ismax = await win.isMaximized()
    const ismin = await win.isMinimized()
    if (ismax) {
      await win.unmaximize()
    }
    if (ismin) {
      await win.unminimize()
    }
    await win.setFocus()
    const isFocused = await win.isFocused()
    if (!isFocused) {
      await this.foucsWindow()
    }
  }

  /**
   * 关闭指定窗口（如果未指定，则关闭当前窗口）
   */
  async closeWindow(label?: string | number) {
    let win: WebviewWindow | null = null
    if (label) {
      win = WebviewWindow.getByLabel(label.toString())
      if (win) {
        await win.close()
      }
      else {
        console.warn(`No window found with label: ${label}`)
      }
    }
    else {
      win = getCurrent()
      await win.close()
    }
  }

  /**
   * 设置窗口大小
   */
  async setWindowSize(params?: { width?: number, height?: number }) {
    const win = getCurrent()
    if (win) {
      await win.setResizable(true)
      const scale = await win.scaleFactor()
      const newWidth = params?.width ?? windowSize.toLogical(scale).width - 40
      const newHeight = params?.height ?? windowSize.toLogical(scale).height - 40
      await win.setSize(new LogicalSize(newWidth, newHeight))
      await win.setResizable(false)
    }
  }

  async isMaximized() {
    const win = getCurrent()
    return await win.isMaximized()
  }

  async isMinimized() {
    const win = getCurrent()
    return await win.isMinimized()
  }

  async foucsWindow() {
    const win = getCurrent()

    await win.setFocus()
    await win.setAlwaysOnTop(true)
    const isFocused = await win.isFocused()
    setTimeout(async () => {
      if (!isFocused) {
        await win.setFocus()
        await win.setAlwaysOnTop(true)
        setTimeout(() => {
          win.setAlwaysOnTop(false)
        }, 300)
      }
      await win.setAlwaysOnTop(false)
    }, 300)
  }

  /**
   * 恢复到登录窗口大小
   */
  async restoreLoginWindow() {
    const win = getCurrent()
    await win.unmaximize()
    await win.setResizable(true)
    await win.setSize(new LogicalSize(loginWinState.width, loginWinState.height))
    await win.center()
    await win.setResizable(false)
  }

  async centerWindow() {
    const win = getCurrent()
    await win.center()
  }

  async getScreenWorkArea() {
    const win = getCurrent()
    const scale = await win.scaleFactor()
    return windowSize.toLogical(scale)
  }

  async setWindowPosition(x: number = 0, y: number = 0) {
    const win = getCurrent()
    await win.setResizable(true)
    await win.setPosition(new PhysicalPosition(x, y))
    await win.setResizable(false)
  }

  async setWindowAlwaysOnTop(alwaysOnTop: boolean = true) {
    const win = getCurrent()
    await win.setAlwaysOnTop(alwaysOnTop)
  }

  async showDecorations() {
    await appWindow.setDecorations(true)
    await appWindow.setTitle('登录晓悟RPA')
  }

  async hideDecorations() {
    await appWindow.setDecorations(false)
    await appWindow.setTitle('晓悟RPA')
  }

  /**
   * 日志窗口 变形
   * 宽度为 屏幕宽度的0.2 * scale 并且在360-450 之间
   * 高度为 屏幕高度的0.13 * scale 并且在120-150 之间
   * @param bool
   */
  async minLogWindow(bool: boolean) {
    const win = getCurrent()
    const scale = await win.scaleFactor()
    const screenWidth = windowSize.toLogical(scale).width
    const screenHeight = windowSize.toLogical(scale).height
    const logwinWidth = 0.2 * windowScreen.width * scale
    const logwinHeight = 0.13 * windowScreen.height * scale
    const winPhySize = new PhysicalSize(logwinWidth, logwinHeight)
    const originWidth = winPhySize.toLogical(scale).width
    const originHeight = winPhySize.toLogical(scale).height
    const minWidth = 0.1 * originWidth
    const minHeight = originHeight
    if (bool) {
      await this.setWindowSize({ width: minWidth, height: minHeight })
      await win.setPosition(new LogicalPosition(screenWidth - minWidth - 2, screenHeight - minHeight - 2))
    }
    else {
      await win.setPosition(new LogicalPosition(screenWidth - originWidth - 2, screenHeight - originHeight - 2))
      await this.setWindowSize({ width: originWidth, height: originHeight })
    }
  }

  async onWindowResize(callback: () => void) {
    const win = getCurrent()
    return await win.onResized(() => callback())
  }

  async onWindowClose(callback: () => void) {
    const win = getCurrent()
    await win.onCloseRequested(async (ev) => {
      ev.preventDefault()
      await this.maximizeWindow(true)
      callback()
    })
  }
}

export default TauriWindowManager
