import type { Component } from 'vue'

export interface TabConfig {
  text: string
  key: string
  icon: string
  component: Component
  rightExtra?: Component
  hideCollapsed?: boolean
}
