import type { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: unknown
    opencodeApi: {
      getRuntimeStatus: () => Promise<unknown>
      awaitInitialization: () => Promise<unknown>
      getBootstrap: () => Promise<{ assistantGroups: unknown[]; defaultSessionId: string }>
      getSession: (sessionId: string) => Promise<unknown>
      createSession: (payload: { title?: string | null; assistantId?: string | null; groupRoomId?: string | null }) => Promise<unknown>
      deleteSession: (sessionId: string) => Promise<{ success: boolean }>
      sendMessage: (payload: { sessionID: string; text: string; model?: string | null; providerId?: string | null }) => Promise<{ success: boolean }>
      getSettings: () => Promise<unknown>
      saveProvider: (input: unknown) => Promise<unknown>
      saveDefaultModel: (input: unknown) => Promise<unknown>
      listAssistants: () => Promise<unknown[]>
      saveAssistant: (input: unknown) => Promise<unknown>
      deleteAssistant: (id: string) => Promise<unknown>
      listGroupRooms: () => Promise<unknown[]>
      saveGroupRoom: (input: unknown) => Promise<unknown>
      deleteGroupRoom: (id: string) => Promise<unknown>
      listSkills: () => Promise<unknown>
      onRuntimeEvent: (listener: (event: unknown) => void) => () => void
    }
  }
}
