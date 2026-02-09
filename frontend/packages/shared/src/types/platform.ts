import type { IPluginConfig } from './plugin'

export interface IAppConfig {
  remote_addr: string
  skip_engine_start?: boolean
  app_auth_type: 'uap' | 'casdoor'
  app_edition: 'saas' | 'enterprise'
}

// 窗口管理相关类型
export interface WindowManager {
  platform: string
  windows: Map<string, any>
  getScaleFactor: () => Promise<number>
  createWindow: (options?: CreateWindowOptions, closeCallback?: () => void) => Promise<any>
  scaleFactor: () => Promise<number>
  showWindow: (label?: string | number) => Promise<void>
  hideWindow: () => Promise<void>
  closeWindow: (label?: string | number) => void
  maximizeWindow: (always?: boolean) => Promise<boolean>
  minimizeWindow: () => void
  restoreWindow: () => void
  setWindowSize: (params?: { width?: number, height?: number }) => Promise<void>
  setWindowAlwaysOnTop: (alwaysOnTop?: boolean) => Promise<void>
  centerWindow: (options?: any) => void
  isMaximized: () => Promise<boolean>
  isMinimized: () => Promise<boolean>
  showDecorations: () => void
  hideDecorations: () => void
  foucsWindow: () => void
  restoreLoginWindow: () => void
  getScreenWorkArea: () => any
  setWindowPosition: (x?: number, y?: number) => Promise<void>
  minLogWindow: (bool: boolean) => void
  onWindowResize: (callback: () => void) => Promise<() => void>
  onWindowClose: (callback: () => void) => void
  emitTo: (msg: WindowMessage) => Promise<any>
}

export type WindowPosition = 'left_top' | 'right_top' | 'left_bottom' | 'right_bottom' | 'top_center' | 'center' | 'right_center'

// 窗口创建选项
export interface CreateWindowOptions {
  url: string
  position?: WindowPosition
  offset?: number
  x?: number
  y?: number
  width?: number
  height?: number
  minWidth?: number
  minHeight?: number
  maxWidth?: number
  maxHeight?: number
  resizable?: boolean
  title?: string
  label?: string
  fullscreen?: boolean
  focus?: boolean
  transparent?: boolean
  maximized?: boolean
  show?: boolean
  decorations?: boolean
  alwaysOnTop?: boolean
  contentProtected?: boolean
  skipTaskbar?: boolean
  fileDropEnabled?: boolean
  hiddenTitle?: boolean
  acceptFirstMouse?: boolean
  tabbingIdentifier?: string
  userAgent?: string
  maximizable?: boolean
  minimizable?: boolean
  closable?: boolean
}

// 窗口消息类型
export interface WindowMessage {
  from?: string // window label
  target: string // window label
  type: string // message type
  data?: any // message data
}

// 剪贴板管理器
export interface ClipboardManager {
  writeClipboardText: (text: string) => Promise<void>
  readClipboardText: () => Promise<string>
}

// 应用环境类型
export type AppEnv = 'tauri' | 'electron' | 'browser'

// 工具管理器
export interface UtilsManager {
  getAppEnv: () => AppEnv
  isBrowser?: boolean
  openInBrowser: (url: string, browser?: string) => void
  listenEvent: (eventName: string, callback: (data: any) => void) => void
  getAppVersion: () => Promise<string>
  getAppPath: () => Promise<string>
  getAppConfig: () => Promise<IAppConfig>
  getUserPath: () => Promise<string>
  getBuildInfo: () => Promise<string>
  getSystemEnv: () => Promise<string>
  getResourcePath: () => Promise<string>
  invoke: (channel: string, ...args: any[]) => Promise<any>
  readFile: (filePath: string, encoding?: string) => Promise<string | Uint8Array | ArrayBuffer>
  saveFile: (fileName: string, buffer: ArrayBuffer | string) => Promise<boolean>
  playVideo: (videoPath: string) => void
  pathJoin: (dirArr: Array<string>) => Promise<any>
  shellopen: (path: string) => Promise<void>
  openPlugins: () => Promise<void>
  showDialog: (dialogProps: any) => Promise<any>
  getPluginList: () => Promise<IPluginConfig[]>
}

// 快捷键管理器
export interface ShortCutManager {
  register: (shortKey: string, handler: any) => void
  unregister: (shortKey: string) => void
  unregisterAll: () => void
  regeisterToolbar: () => void
  regeisterFlow: () => void
}

// 更新清单
export interface UpdateManifest {
  version: string
  date: string
  body: string
}

// 更新信息
export interface UpdateInfo {
  couldUpdate: boolean
  downloaded?: boolean
  manifest?: UpdateManifest | null
}

// 更新管理器
export interface UpdaterManager {
  checkUpdate: () => Promise<UpdateInfo>
  quitAndInstall: () => void
}
