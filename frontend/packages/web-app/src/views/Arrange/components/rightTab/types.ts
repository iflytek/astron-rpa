import { Ref } from "vue"

export type Position = 'top' | 'left' | 'right' | 'bottom'

export interface Tab {
  name: string
  value: PropertyKey
  show?: boolean
  size?: string | number
}

export interface TabsContext {
  activeTab: Ref<Tab['value']>
  position: Ref<Position>
  registerTab: (tab: Tab) => void
  updateTab: (key: PropertyKey, tab: Partial<Tab>) => void
}
