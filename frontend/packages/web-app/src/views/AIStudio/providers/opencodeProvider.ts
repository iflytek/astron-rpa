import type {
  AIStudioBootstrap,
  AIStudioCardActionPayload,
  AIStudioChoiceSubmissionPayload,
  AIStudioCreateSessionPayload,
  AIStudioParamSubmissionPayload,
  AIStudioProvider,
  AIStudioRenameSessionPayload,
  AIStudioSendMessagePayload,
  AIStudioSessionMutationResult,
} from '../contracts'
import type { StudioMessageAttachment } from '../types'

export type OpencodeDesktopApi = {
  getBootstrap: () => Promise<AIStudioBootstrap>
  getSession: (sessionId: string) => Promise<unknown>
  createSession: (payload: { title?: string | null; assistantId?: string | null; groupRoomId?: string | null; workspacePath?: string | null }) => Promise<{ id: string }>
  renameSession: (payload: { sessionId: string; title?: string | null }) => Promise<{ success: boolean }>
  deleteSession: (sessionId: string) => Promise<{ success: boolean }>
  sendMessage: (payload: {
    sessionID: string
    text: string
    attachments?: Array<{
      id: string
      name: string
      mime: string
      url: string
    }>
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

function toDesktopAttachment(attachment: StudioMessageAttachment) {
  return {
    id: attachment.id,
    name: attachment.name,
    mime: attachment.mime,
    url: attachment.url,
  }
}

function sameAttachmentList(
  left: StudioMessageAttachment[] | undefined,
  right: StudioMessageAttachment[] | undefined,
) {
  const leftItems = left || []
  const rightItems = right || []
  if (leftItems.length !== rightItems.length)
    return false
  return leftItems.every((item, index) => {
    const candidate = rightItems[index]
    return candidate
      && candidate.name === item.name
      && candidate.mime === item.mime
      && candidate.url === item.url
  })
}

function unsupportedRuntimeMutation(name: string): never {
  throw new Error(`AI Studio runtime does not support ${name} yet`)
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
      attachments: payload.attachments?.map(toDesktopAttachment),
    })
    const session = await fetchSessionDetail(payload.sessionId)
    // Opencode processes messages asynchronously; the user message may not yet
    // be persisted when we fetch right after sendMessage. Add it optimistically
    // so it is immediately visible in the UI.
    const latestUserMessage = [...session.messages].reverse().find(message => message.role === 'user')
    const alreadyPresent = !!latestUserMessage
      && latestUserMessage.content === payload.content
      && sameAttachmentList(latestUserMessage.attachments, payload.attachments)
    if (!alreadyPresent) {
      session.messages = [
        ...session.messages,
        {
          id: `user-optimistic-${Date.now()}`,
          role: 'user',
          content: payload.content,
          attachments: payload.attachments ? [...payload.attachments] : undefined,
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
      workspacePath: payload.workspacePath ?? null,
    })
    const session = await fetchSessionDetail(created.id)
    return { session }
  },

  renameSession: async (payload: AIStudioRenameSessionPayload): Promise<AIStudioSessionMutationResult> => {
    const api = getOpencodeDesktopApi()
    await api.renameSession({
      sessionId: payload.sessionId,
      title: payload.title ?? null,
    })
    const session = await fetchSessionDetail(payload.sessionId)
    return { session }
  },

  submitChoiceForm: async (_payload: AIStudioChoiceSubmissionPayload): Promise<AIStudioSessionMutationResult> => {
    return unsupportedRuntimeMutation('choice-form submission')
  },

  submitParamForm: async (_payload: AIStudioParamSubmissionPayload): Promise<AIStudioSessionMutationResult> => {
    return unsupportedRuntimeMutation('param-form submission')
  },

  submitCardAction: async (_payload: AIStudioCardActionPayload): Promise<AIStudioSessionMutationResult> => {
    return unsupportedRuntimeMutation('card action')
  },
}
