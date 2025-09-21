import type { AnyObj } from '@/types/common'

export interface FormItemConfig {
  id: string
  dialogFormType: string
  dialogFormName: string
  configKeys: Array<string>
  label?: any
  placeholder?: any
  defaultValue?: any
  bind?: any
  required?: any
  fontFamily?: any
  fontSize?: any
  fontStyle?: any
  textContent?: any
  [key: string]: any
}

export interface DialogFormItem {
  dialogFormType: string
  label?: string
  bind?: string
  placeholder?: string
  defaultValue?: string | Array<string>
  options?: Array<{
    label: string
    value: string
  }>
  [key: string]: any
}

export interface DialogOption {
  mode: string
  title: string
  buttonType: string // confirm_cancel, confirm, yes_no_cancel, yes_no
  itemList: Array<DialogFormItem>
  formModel?: AnyObj
  table_required?: boolean // 后端需要
}
