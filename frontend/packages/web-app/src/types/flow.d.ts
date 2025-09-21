declare namespace RPA {
  namespace Flow {
    type ProcessModuleType = 'process' | 'module'

    interface ProcessModule {
      resourceCategory: ProcessModuleType
      name: string
      resourceId: string
      isOpen?: boolean
      isSaveing?: boolean
      isMain?: boolean // 是否是主流程
      isLoading?: boolean // 是否正在加载
    }

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
  }

  // 配置参数
  interface ConfigParamData {
    id: string
    varDirection: 0 | 1 // 输入 / 输出
    varName: string // 参数名称
    varType: RPA.VariableType // 参数类型
    varValue: unknown // 参数默认值
    varDescribe: string // 参数描述
    robotId: string // 机器人id
    robotVersion?: number // 机器人版本
    processId: string // 流程id
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
