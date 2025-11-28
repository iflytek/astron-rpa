declare namespace RPA {
  interface AnyObj {
    [key: string]: any
  }

  interface AtomTreeNode {
    uniqueId?: string
    key: string
    title: string
    icon?: string
    parentKey?: string
    likeId?: string
    iconColor?: string
    atomics?: RPA.AtomTreeNode[]
  }

  interface AtomFormItemType {
    type: string
    params?: {
      values?: string[]
      use?: string
      file_type?: string
      filters?: string[]
      [key: string]: any
    }
  }

  interface AtomFormItemResult {
    type: string
    rId?: string
    value: any
    data?: any
    varId?: string
    varName?: string
    varValue?: any
  }

  interface SharedVariableValueT {
    value: string
    data: number | string
  }

  interface AtomFormItemConditional {
    expression: string
    key: string
  }

  interface AtomFormBaseForm extends AnyObj {
    formType?: AtomFormItemType
    title?: string
    subTitle?: string
    key: string
    sourceValue: string
    value: string | boolean | number | Array<AtomFormItemResult>
    noInput?: boolean // 禁止编辑
  }

  interface AtomDisplayItem extends AtomFormBaseForm {
    rowIdx?: number
    required?: boolean
    types?: string
    default?: string | boolean | number
    show?: boolean
    dynamics?: AtomFormItemConditional[]
    options?: { label: string; value: string }[]
    errors?: string[] // 校验错误信息
    level?: 'advanced' // level = advanced 表示高级参数
    linkageValue?: {
      originKey: string
      updateKeyArr: number[]
    }
  }

  /**
   * 原子能力
   */
  interface Atom {
    id: string
    key: string
    icon?: string
    title?: string
    level?: number
    version: string
    alias: string
    showInput?: boolean
    debugging?: boolean
    disabled?: boolean
    nodeError?: string[]
    isHide?: boolean
    isOpen?: boolean
    advanced: AtomDisplayItem[]
    exception: AtomDisplayItem[]
    inputList: AtomDisplayItem[]
    outputList: AtomDisplayItem[]
    [key: string]: any
  }

  type VariableType
    = | 'Any'
      | 'Float'
      | 'Int'
      | 'Bool'
      | 'Str'
      | 'List'
      | 'Dict'
      | 'PATH'
      | 'Date'
      | 'URL'
      | 'Pick'
      | 'WebPick'
      | 'WinPick'
      | 'Browser'
      | 'DocxObj'
      | 'ExcelObj'
      | 'Password'

  interface VariableValueType {
    /**
     * 全局变量的使用场景，global 表示全局变量，main 表示主流程的配置参数，'' 表示流程变量，可以有多个场景，用逗号分隔
     */
    channel: string
    template: string
    desc: string
    funcList: VariableFunction[]
    key: string
    src: string
    version: string
  }

  interface AtomMetaData {
    atomicTree: AtomTreeNode[]
    atomicTreeExtend: AtomTreeNode[]
    commonAdvancedParameter: AtomFormBaseForm[]
    types: Record<string, VariableValueType>
  }

  interface SharedVariableType {
    label: string
    value: number | string
    subVarList: any[]
  }

  interface SharedFileType {
    fileId: string
    fileName: string
    tags: any[]
  }
}
