/// <reference types="@rpa/shared/platform" />

import type { IpcRendererEvent } from 'electron'

export type IpcRendererListener = (event: IpcRendererEvent, ...args: any[]) => void

export interface W2WType {
  from: string // 来源窗口
  target: string // 目标窗口
  type: string // 类型
  data?: any // 数据
}

export interface DialogObj {
  title: string
  multiple?: boolean
  directory?: boolean
  properties?: string[]
  filters?: any[]
  defaultPath?: string
}

export interface AxiosResponse<T = any> {
  code: string | number
  message: string
  data: T
}

export interface IpcRenderer {
  on(channel: string, listener: IpcRendererListener): () => void
  send(channel: string, ...args: any[]): void
  invoke(channel: string, ...args: any[]): Promise<any>
  off(channel: string, listener: IpcRendererListener): void
}

declare global {
  interface Window {
    electron: {
      ipcRenderer: IpcRenderer
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
  }
}
