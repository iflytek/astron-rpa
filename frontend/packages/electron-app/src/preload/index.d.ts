import type { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI & {
      openclaw?: {
        getToken: () => Promise<string | undefined>
        getDeviceIdentity: () => Promise<{ deviceId: string, publicKey: string } | undefined>
        signDevicePayload: (payload: string) => Promise<string | undefined>
        getDeviceToken: (role?: string) => Promise<{ token: string, scopes?: string[] } | undefined>
        storeDeviceToken: (params: { role?: string, token: string, scopes?: string[] }) => Promise<boolean>
        approveDeviceRequest: (requestId: string) => Promise<boolean>
        chatCompletions: (params: {
          messages: Array<{ role: 'system' | 'developer' | 'user' | 'assistant' | 'tool', content: string }>
          sessionKey?: string
          attachments?: Array<{ type: 'image', mimeType: string, fileName?: string, content: string }>
          allowCliFallback?: boolean
        }) => Promise<{ text: string, toolEvents: Array<{ toolCallId: string, runId?: string, name: string, phase: 'start' | 'update' | 'result', args?: unknown, output?: string, ts: number }> }>
        readLocalFile: (params: { path: string, mode: 'text' | 'data-url' }) => Promise<{ textContent?: string, dataUrl?: string, mimeType?: string, base64?: string } | undefined>
      }
    }
    api: unknown
  }
}
