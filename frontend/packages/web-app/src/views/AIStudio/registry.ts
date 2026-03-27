export type AIStudioSkillRegistryGroup = {
  id: string
  label: string
  skills: {
    id: string
    label: string
    description: string
  }[]
}

export type AIStudioWorkspaceSuggestion = {
  id: string
  label: string
  hint: string
}

export const aiStudioSkillRegistry: AIStudioSkillRegistryGroup[] = [
  {
    id: 'office',
    label: '办公协作',
    skills: [
      { id: '文件读写', label: '文件读写', description: '读取、整理和写入本地工作文件。' },
      { id: '邮件发送', label: '邮件发送', description: '生成并发送邮件或通知草稿。' },
      { id: '日历日程', label: '日历日程', description: '安排会议、同步提醒和例行计划。' },
      { id: '审批流', label: '审批流', description: '发起审批、汇总结果并回填状态。' },
    ],
  },
  {
    id: 'data',
    label: '分析与检索',
    skills: [
      { id: '数据库查询', label: '数据库查询', description: '执行数据库查询并整理结果。' },
      { id: 'SQL 分析', label: 'SQL 分析', description: '分析查询链路和性能瓶颈。' },
      { id: '图表生成', label: '图表生成', description: '生成图表、表格和结构化摘要。' },
      { id: '知识库检索', label: '知识库检索', description: '检索内部知识库、FAQ 和规程。' },
      { id: '知识图谱', label: '知识图谱', description: '关联多源知识节点与上下文。' },
    ],
  },
  {
    id: 'delivery',
    label: '执行与集成',
    skills: [
      { id: 'API 调用', label: 'API 调用', description: '连接外部服务、系统接口和业务能力。' },
      { id: '浏览器自动化', label: '浏览器自动化', description: '执行网页巡检、录入和抓取。' },
      { id: '网页抓取', label: '网页抓取', description: '抓取公开网页内容并提取结构化信息。' },
      { id: 'RPA 执行', label: 'RPA 执行', description: '触发星辰RPA 流程、任务和执行器动作。' },
      { id: '代码执行', label: '代码执行', description: '执行脚本、补丁和工程分析任务。' },
    ],
  },
  {
    id: 'document',
    label: '文档与识别',
    skills: [
      { id: 'PDF 解析', label: 'PDF 解析', description: '解析合同、报告与扫描件内容。' },
      { id: 'OCR 识别', label: 'OCR 识别', description: '识别截图、票据和图片文本。' },
      { id: '表格处理', label: '表格处理', description: '批量处理 Excel、CSV 和对账表。' },
    ],
  },
]

export const aiStudioWorkspaceSuggestions: AIStudioWorkspaceSuggestion[] = [
  { id: 'documents', label: '~/Documents', hint: '通用工作区' },
  { id: 'ai-studio', label: '~/Projects/astron-rpa/ai-studio', hint: 'AI 工作室前端联调目录' },
  { id: 'design-sync', label: '~/Projects/design-sync', hint: '设计还原与截图对比目录' },
  { id: 'finance', label: '~/Projects/finance-workbench', hint: '财务与报表自动化目录' },
]
