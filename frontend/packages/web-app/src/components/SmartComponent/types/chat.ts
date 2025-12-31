export type SmartType = 'web_auto' | 'data_process'

export type SceneCode = `smart_${SmartType | 'optimize_input'}`

export type Role = 'user' | 'assistant'

export type MessageStatus = 'generating' | 'completed' | 'failed'

export interface MessageOutput {
  text: string
  smartCode?: string
  status?: MessageStatus // 消息状态
  version?: number // 组件版本
  error?: string
  tip?: string
  duration?: number // 组件生成耗时（秒）
  packages?: string[] // 依赖包列表
}

export interface Message {
  role: Role
  content: MessageInput | MessageOutput
}

export interface MessageInput {
  sceneCode?: SceneCode
  user: string

  needFix?: boolean
  fixInfo?: {
    consoleLog: string
    traceback: string
  }
  currentCode?: string

  elements?: any[]
  chatHistory?: Message[]
}
