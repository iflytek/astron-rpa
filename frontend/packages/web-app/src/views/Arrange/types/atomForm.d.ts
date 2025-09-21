export interface AtomDisplayBaseConfig {
  name?: object
  key: string
  formItems: RPA.AtomDisplayItem[]
  id?: string
  atomKey?: string
  value?: RPA.AtomFormItemResult[]
}

export interface AtomDisplayConfig {
  baseParam: AtomDisplayBaseConfig[]
  advancedParam: AtomDisplayBaseConfig[]
  exceptParam: AtomDisplayBaseConfig[]
}

export interface AtomTabs {
  key: string
  name: string
  params: AtomDisplayBaseConfig[]
}

export type VariableTypes = 'globalVariables' | 'processVariables' | 'configParameters' | ''
