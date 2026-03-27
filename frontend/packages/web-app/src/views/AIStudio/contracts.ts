import type {
  StudioAssistantGroup,
  StudioRunEvent,
  StudioRunSyncMode,
  StudioSessionDetail,
  StudioSessionRun,
} from './types'

export const DEFAULT_AI_STUDIO_SESSION_ID = 'finance-q3'

export interface AIStudioBootstrap {
  assistantGroups: StudioAssistantGroup[]
  defaultSessionId: string
}

export interface AIStudioSendMessagePayload {
  sessionId: string
  content: string
  attachments?: string[]
  mentions?: string[]
  skills?: string[]
}

export interface AIStudioCreateSessionPayload {
  assistantId: string
  title: string
  seedPrompt?: string
  workspacePath?: string
  participantAssistantIds?: string[]
  agentId?: string
}

export interface AIStudioChoiceSubmissionPayload {
  sessionId: string
  cardId: string
  optionId: string
}

export interface AIStudioParamSubmissionPayload {
  sessionId: string
  cardId: string
  values: Record<string, string>
}

export interface AIStudioCardActionPayload {
  sessionId: string
  cardId: string
  actionId: string
}

export interface AIStudioRunQueryPayload {
  sessionId: string
  runId: string
}

export interface AIStudioRunEventQueryPayload extends AIStudioRunQueryPayload {
  cursor?: string
  limit?: number
}

export interface AIStudioPermissionResolutionPayload extends AIStudioRunQueryPayload {
  permissionId: string
  decision: 'allow-once' | 'allow-always' | 'reject'
  note?: string
}

export interface AIStudioSessionMutationResult {
  session: StudioSessionDetail
}

export interface AIStudioRunResult {
  run: StudioSessionRun
}

export interface AIStudioRunEventBatch {
  run: StudioSessionRun
  events: StudioRunEvent[]
  nextCursor?: string
  syncMode?: StudioRunSyncMode
}

export interface AIStudioProvider {
  getBootstrap: () => Promise<AIStudioBootstrap>
  getSessionDetail: (sessionId: string) => Promise<StudioSessionDetail>
  sendMessage: (payload: AIStudioSendMessagePayload) => Promise<AIStudioSessionMutationResult>
  submitChoiceForm: (payload: AIStudioChoiceSubmissionPayload) => Promise<AIStudioSessionMutationResult>
  submitParamForm: (payload: AIStudioParamSubmissionPayload) => Promise<AIStudioSessionMutationResult>
  submitCardAction: (payload: AIStudioCardActionPayload) => Promise<AIStudioSessionMutationResult>
  createSession?: (payload: AIStudioCreateSessionPayload) => Promise<AIStudioSessionMutationResult>
  getRun?: (payload: AIStudioRunQueryPayload) => Promise<AIStudioRunResult>
  listRunEvents?: (payload: AIStudioRunEventQueryPayload) => Promise<AIStudioRunEventBatch>
  resolvePermissionRequest?: (payload: AIStudioPermissionResolutionPayload) => Promise<AIStudioSessionMutationResult>
}
