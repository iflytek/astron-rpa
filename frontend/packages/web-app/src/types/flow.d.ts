declare namespace RPA {
  namespace Flow {
    interface Process {
      id: string
      name: string
      description: string
      code: string
      version: number
      robotId: string
      createTime: string
      updateTime: string
    }

    interface Code {
      id: string
      name: string
      description: string
    }

    type ArgumentValueType = 'other' | 'python' | 'var'

    interface FlowItemValue extends Record<string, any> {
      key: string // 原子能力的key
      version: string // 指向引用原子能力的版本
      id: string // 节点唯一ID。但似乎不是必须的？
      inputList: RPA.AtomDisplayItem[] // 默认值可不填充，下同
      advanced: RPA.AtomDisplayItem[]
      exception: RPA.AtomDisplayItem[]
      outputList: RPA.AtomDisplayItem[]
      alias: string // 别名
      disabled?: boolean // 是否禁用
      breakpoint?: boolean // 是否断点
      // collapsed: boolean
    }
  }

  // 配置参数
  interface ConfigParamData {
    id: string
    varDirection: 0 | 1 // 输入 / 输出
    varName: string // 参数名称
    varType: RPA.VariableType // 参数类型
    varValue: unknown // 参数默认值
    varDescribe: string // 参数描述
    robotId: string // 应用id
    robotVersion?: number // 应用版本
    processId?: string // 流程id
    moduleId?: string // 模块id
  }

  // 组件属性
  interface ComponentAttrData extends ConfigParamData {
    varFormType: {
      type: string
      value: any[]
    }
  }

  // 创建配置参数
  type CreateConfigParamData = Omit<ConfigParamData, 'id'>

  // 创建组件属性
  type CreateComponentAttrData = Omit<ComponentAttrData, 'id'>

  // 全局变量
  interface GlobalVariable {
    varName: string
    varType: string
    varValue: string
    varDescribe: string
    globalId?: string
    robotId?: string
    projectId?: string
  }

  type RunMode = 'PROJECT_LIST' | 'EXECUTOR' | 'CRONTAB' | 'EDIT_PAGE'
}
