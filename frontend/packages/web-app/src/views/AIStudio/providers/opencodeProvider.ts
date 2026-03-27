import type {
  AIStudioBootstrap,
  AIStudioCardActionPayload,
  AIStudioChoiceSubmissionPayload,
  AIStudioCreateSessionPayload,
  AIStudioParamSubmissionPayload,
  AIStudioProvider,
  AIStudioSendMessagePayload,
  AIStudioSessionMutationResult,
} from '../contracts'
import { mockAIStudioProvider } from './mockProvider'

export type OpencodeDesktopApi = {
  getBootstrap: () => Promise<AIStudioBootstrap>
  getSession: (sessionId: string) => Promise<unknown>
  createSession: (payload: { title?: string | null; assistantId?: string | null; groupRoomId?: string | null }) => Promise<{ id: string }>
  deleteSession: (sessionId: string) => Promise<{ success: boolean }>
  sendMessage: (payload: {
    sessionID: string
    text: string
    model?: string | null
    providerId?: string | null
  }) => Promise<{ success: boolean }>
  listAssistants: () => Promise<unknown[]>
  saveAssistant: (input: unknown) => Promise<unknown>
  deleteAssistant: (id: string) => Promise<unknown>
  listGroupRooms: () => Promise<unknown[]>
  saveGroupRoom: (input: unknown) => Promise<unknown>
  deleteGroupRoom: (id: string) => Promise<unknown>
  onRuntimeEvent: (listener: (event: unknown) => void) => () => void
}

function isElectron() {
  return typeof window !== 'undefined' && 'opencodeApi' in window
}

export function getOpencodeDesktopApi(): OpencodeDesktopApi {
  if (!isElectron()) {
    throw new Error('opencodeApi is not available outside Electron context')
  }
  return window.opencodeApi as OpencodeDesktopApi
}

async function fetchSessionDetail(sessionId: string): Promise<import('../types').StudioSessionDetail> {
  const api = getOpencodeDesktopApi()
  const result = await api.getSession(sessionId)
  return result as import('../types').StudioSessionDetail
}

export const opencodeAIStudioProvider: AIStudioProvider = {
  getBootstrap: async (): Promise<AIStudioBootstrap> => {
    const api = getOpencodeDesktopApi()
    const result = await api.getBootstrap()
    return result as AIStudioBootstrap
  },

  getSessionDetail: async (sessionId: string) => {
    return fetchSessionDetail(sessionId)
  },

  sendMessage: async (payload: AIStudioSendMessagePayload): Promise<AIStudioSessionMutationResult> => {
    const api = getOpencodeDesktopApi()
    await api.sendMessage({
      sessionID: payload.sessionId,
      text: payload.content,
    })
    const session = await fetchSessionDetail(payload.sessionId)
    // Opencode processes messages asynchronously; the user message may not yet
    // be persisted when we fetch right after sendMessage. Add it optimistically
    // so it is immediately visible in the UI.
    const alreadyPresent = session.messages.some(
      m => m.role === 'user' && m.content === payload.content,
    )
    if (!alreadyPresent) {
      session.messages = [
        ...session.messages,
        {
          id: `user-optimistic-${Date.now()}`,
          role: 'user',
          content: payload.content,
          time: '刚刚',
        },
      ]
    }
    return { session }
  },

  createSession: async (payload: AIStudioCreateSessionPayload): Promise<AIStudioSessionMutationResult> => {
    const api = getOpencodeDesktopApi()
    const created = await api.createSession({
      title: payload.title ?? null,
      assistantId: payload.assistantId ?? null,
      groupRoomId: payload.agentId ?? null,
    })
    const session = await fetchSessionDetail(created.id)
    return { session }
  },

  submitChoiceForm: async (payload: AIStudioChoiceSubmissionPayload): Promise<AIStudioSessionMutationResult> => {
    return mockAIStudioProvider.submitChoiceForm(payload)
  },

  submitParamForm: async (payload: AIStudioParamSubmissionPayload): Promise<AIStudioSessionMutationResult> => {
    return mockAIStudioProvider.submitParamForm(payload)
  },

  submitCardAction: async (payload: AIStudioCardActionPayload): Promise<AIStudioSessionMutationResult> => {
    return mockAIStudioProvider.submitCardAction(payload)
  },
}
