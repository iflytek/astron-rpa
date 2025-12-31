import type { Message, SmartType } from './chat'

export interface SmartComp extends Omit<RPA.Atom, 'version'> {
  key: string
  version?: number
  smartType: SmartType
  smartCode: string
  createTime?: number // 组件生成时间（时间戳，毫秒）
  detail: {
    packages: string[]
    elements: string[]
    chatHistory: Message[]
  }
}
