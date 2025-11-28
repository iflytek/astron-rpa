import type { Component, Ref } from 'vue'

export interface TabContentProps {
  height: number
}

export interface TabConfig {
  text: string | Ref<string>
  key: string
  icon: string
  component: Component<TabContentProps>
  rightExtra?: Component
  hideCollapsed?: boolean
}
