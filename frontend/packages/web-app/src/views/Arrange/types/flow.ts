export interface ContextmenuInfo {
  visible: boolean
  $event?: MouseEvent
  atom?: any
}
export interface FlowItem {
  processId: string
  processName: string
  isOpen?: boolean
  isMain?: boolean
  robotId: string
}

export interface FlowHistoryAtomItem {
  atoms?: Array<any>
  isGroup?: boolean
  preId?: string | number
  oldPreId?: string | number
  moveToChildren?: boolean
  oldPreIdMapMoveToChildren?: any
  updateData?: any
  oldAttrMap?: any
  newAttrMap?: any
}

export interface FlowHistoryItem {
  processId: string
  isHistory?: boolean
  type: string
  detail: {
    data: FlowHistoryAtomItem[]
    deleteChildren?: boolean
  }
}

export interface FlowAllProcessHistory {
  [processId: string]: {
    historyList: FlowHistoryItem[]
    tempList: FlowHistoryItem[]
  }
}

export interface VarTreeItem {
  title: string
  key: string
  id?: string
  definition?: string
  template?: string
  children?: VarTreeItem[]
}
