export type AIStudioWorkspaceSuggestion = {
  id: string
  label: string
  hint: string
}

export const aiStudioWorkspaceSuggestions: AIStudioWorkspaceSuggestion[] = [
  { id: 'documents', label: '~/Documents', hint: '通用工作区' },
  { id: 'ai-studio', label: '~/Projects/astron-rpa/ai-studio', hint: 'AI 工作室前端联调目录' },
  { id: 'design-sync', label: '~/Projects/design-sync', hint: '设计还原与截图对比目录' },
  { id: 'finance', label: '~/Projects/finance-workbench', hint: '财务与报表自动化目录' },
]
