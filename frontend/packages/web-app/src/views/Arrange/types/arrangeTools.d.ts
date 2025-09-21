import type { Component } from 'vue'

import type { Fun } from '@/types/common'

export interface ArrangeTools {
  key: string
  title: string | Fun
  name: string
  fontSize: string
  class?: string
  clickFn: Fun
  icon: string
  color?: string
  action: string
  loading?: boolean
  show?: boolean | Fun
  disable?: boolean | Fun
  hotkey?: string
  validateFn?: Fun
  noParams?: boolean
  component?: Component
}

export interface NodeFieldsType {
  key: string
  name: string
  checked: string
}

export interface AttrFieldsType {
  key: string
  name: string
  type: string
  value: string
  checked: string
}
