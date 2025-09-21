export interface EditorSettings {
  strictMode?: boolean
  configOverrides?: { [name: string]: boolean }
  locale?: string
  projectId: string
}

export interface EditorState {
  code: string
  settings: EditorSettings
}
