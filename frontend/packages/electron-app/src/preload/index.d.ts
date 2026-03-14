import type { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI & {
      openclaw?: {
        getToken: () => Promise<string | undefined>
        chatCompletions: (params: { messages: Array<{ role: 'system' | 'developer' | 'user' | 'assistant' | 'tool', content: string }> }) => Promise<{ text: string, toolEvents: Array<{ toolCallId: string, runId?: string, name: string, phase: 'start' | 'update' | 'result', args?: unknown, output?: string, ts: number }> }>
      }
    }
    api: unknown
  }
}
