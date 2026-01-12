/// <reference types="@rpa/shared/platform" />

export interface IConfig {
  remote_addr: string
  skip_engine_start: boolean
}

export interface W2WType {
  from: string // 来源窗口
  target: string // 目标窗口
  type: string // 类型
  data?: any // 数据
}

export interface WindowOptions {
  width?: number
  height?: number
  url: string
  name?: string
  title?: 'SubWindow'
  position?: 'center' | 'left_top' | 'right_top' | 'left_bottom' | 'right_bottom' | 'top_center'
  top?: boolean
  resizable?: boolean
  label?: string
  alwaysOnTop?: boolean
  decorations?: boolean
  fileDropEnabled?: boolean
  maximizable?: boolean
  transparent?: boolean
  visible?: boolean
  skipTaskbar?: boolean
  x?: number
  y?: number
}

export interface DialogObj {
  title: string
  multiple?: boolean
  directory?: boolean
  properties?: string[]
  filters?: any[]
  defaultPath?: string
}

export interface AxiosResponse {
  code: string | number
  message: string
  data: any
}

declare global {
  interface Window {
    electron: {
      ipcRenderer: {
        invoke: (channel: string, ...args: any[]) => Promise<any>
        send: (channel: string, ...args: any[]) => void
        sendTo: (webContentsId: number, channel: string, ...args: any[]) => void
        on: (channel: string, listener: (...args: any[]) => void) => void
        off: (channel: string, listener: (...args: any[]) => void) => void
      }
      globalShortcut: {
        register: (shortcut: string, callback: () => void) => Promise<boolean>
        unregister: (shortcut: string) => Promise<boolean>
        unregisterAll: () => Promise<boolean>
      }
      clipboard: {
        readText: () => Promise<string>
        writeText: (text: string) => Promise<boolean>
      }
    }
    api: unknown
  }
}

export interface ElectronPreloadApi {}
