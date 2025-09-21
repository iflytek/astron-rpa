export interface FlowVariable {
  id: string
  types: string
  value: Array<RPA.AtomFormItemResult>
  dialogResult?: string
}

export interface GlobalVariable {
  globalId: string
  projectId: string
  varName: string
  varType: string
  varDescribe: string
}

export interface VariableFunction {
  funcDesc: string
  key: string
  resDesc: string
  resType: string
  useSrc: string
}
