/// <reference types="@rpa/types/global" />

export interface DialogObj {
  title: string
  multiple?: boolean
  directory?: boolean
  properties?: string[]
  filters?: any[]
  defaultPath?: string
}

export interface UpdateManifest {
  version: string
  date: string
  body: string
}

export interface UpdateInfo {
  shouldUpdate: boolean
  manifest?: UpdateManifest | null
}
