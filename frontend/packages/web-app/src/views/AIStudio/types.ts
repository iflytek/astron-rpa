export interface StudioSession {
  id: string
  title: string
  time: string
  active?: boolean
}

export type StudioSessionStatus = 'idle' | 'running' | 'waiting-confirm' | 'completed' | 'failed'
export type StudioRunStatus = 'queued' | 'running' | 'waiting-input' | 'waiting-approval' | 'completed' | 'failed' | 'cancelled'
export type StudioRunSyncMode = 'poll' | 'sse'

export type StudioRunEventType =
  | 'run.created'
  | 'run.updated'
  | 'message.delta'
  | 'message.completed'
  | 'card.created'
  | 'card.updated'
  | 'card.removed'
  | 'artifact.updated'
  | 'workspace.updated'
  | 'todo.updated'
  | 'permission.required'
  | 'permission.resolved'
  | 'error'

export interface StudioAssistant {
  id: string
  name: string
  badge: string
  status: string
  tag?: string
  workspacePath?: string
  persona?: string
  capabilities?: string
  skills?: string[]
  groupParticipantAssistantIds?: string[]
  groupCollaborationMode?: StudioCollaborationMode
  sessions: StudioSession[]
}

export interface StudioAssistantGroup {
  id: string
  title: string
  assistants: StudioAssistant[]
}

export interface StudioOption {
  id: string
  title: string
  description: string
}

export interface StudioMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  time?: string
  assistantName?: string
  order?: number
  originRole?: 'coordinator' | 'participant' | 'system'
  participantAssistantId?: string
  taskId?: string
}

export type StudioToolStatus = 'done' | 'running' | 'pending' | 'failed'

export interface StudioToolCall {
  name: string
  arg: string
  status: StudioToolStatus
  detail?: string
  duration?: string
  result?: string
  steps?: string[]
}

export interface StudioChoiceOption {
  id: string
  label: string
  description: string
}

export interface StudioParamField {
  id: string
  label: string
  required?: boolean
  type: 'date' | 'choice'
  value?: string
  choices?: { id: string, label: string }[]
}

export interface StudioChartSeriesRow {
  label: string
  value: number
  over?: boolean
}

export interface StudioAction {
  id: string
  label: string
  tone?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'soft'
}

export interface StudioLabeledValue {
  label: string
  value: string
}

export type StudioKnowledgeSourceType = 'file' | 'connector' | 'web' | 'workspace'
export type StudioKnowledgeSourceStatus = 'connected' | 'indexed' | 'retrieved' | 'needs-auth' | 'blocked'

export interface StudioKnowledgeSource {
  id: string
  label: string
  type: StudioKnowledgeSourceType
  status: StudioKnowledgeSourceStatus
  detail?: string
}

export interface StudioPlanStep {
  id: string
  title: string
  description?: string
  status: StudioToolStatus
}

export interface StudioCitationEntry {
  id: string
  title: string
  excerpt: string
  source: string
  meta?: string
}

export type StudioWorkItemStatus = 'todo' | 'in-progress' | 'done' | 'blocked'

export interface StudioWorkItem {
  id: string
  title: string
  owner?: string
  due?: string
  detail?: string
  status: StudioWorkItemStatus
}

export interface StudioLegendItem {
  label: string
  color: string
}

export interface StudioSummaryItem {
  label: string
  value: string
  tone?: 'default' | 'danger' | 'success'
}

export interface StudioTableRow {
  id: string
  cells: string[]
  tone?: 'default' | 'danger' | 'success'
}

export interface StudioArtifactPreviewPayload {
  kind: 'chart' | 'code' | 'summary' | 'table'
  fileName: string
  status: string
  title: string
  description?: string
  tag?: string
  language?: string
  code?: string
  chartRows?: StudioChartRow[]
  legend?: StudioLegendItem[]
  items?: StudioSummaryItem[]
  columns?: string[]
  rows?: StudioTableRow[]
}

export interface StudioSessionRun {
  id: string
  status: StudioSessionStatus
  label: string
  summary?: string
  phase?: StudioRunStatus
  syncMode?: StudioRunSyncMode
  startedAt?: string
  updatedAt?: string
  modelId?: string
  opencodeSessionId?: string
}

export interface StudioPermissionOption {
  id: string
  label: string
  tone?: 'primary' | 'secondary' | 'ghost' | 'danger'
}

export interface StudioPermissionRequest {
  id: string
  title: string
  description: string
  scope?: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
  options: StudioPermissionOption[]
}

export interface StudioRunEvent<TPayload = Record<string, unknown>> {
  id: string
  sessionId: string
  runId: string
  type: StudioRunEventType
  createdAt: string
  messageId?: string
  cardId?: string
  artifactId?: string
  payload: TPayload
}

interface StudioChatCardBase {
  id: string
  assistantId?: string
  assistantName?: string
  assistantBadge?: string
  time?: string
  order?: number
}

export type StudioChatCard =
  | (StudioChatCardBase & {
    type: 'thinking'
    title: string
    description: string
  })
  | (StudioChatCardBase & {
    type: 'context-scope'
    title: string
    description?: string
    fields: StudioLabeledValue[]
    tags?: string[]
  })
  | (StudioChatCardBase & {
    type: 'knowledge-sources'
    title: string
    description?: string
    sources: StudioKnowledgeSource[]
  })
  | (StudioChatCardBase & {
    type: 'plan'
    title: string
    description?: string
    steps: StudioPlanStep[]
  })
  | (StudioChatCardBase & {
    type: 'tool-call-list'
    title?: string
    summary?: string
    calls: StudioToolCall[]
  })
  | (StudioChatCardBase & {
    type: 'choice-form'
    title: string
    description?: string
    confirmLabel: string
    options: StudioChoiceOption[]
  })
  | (StudioChatCardBase & {
    type: 'prompt-suggestions'
    title: string
    description?: string
    suggestions: StudioOption[]
  })
  | (StudioChatCardBase & {
    type: 'param-form'
    title: string
    description?: string
    confirmLabel: string
    fields: StudioParamField[]
  })
  | (StudioChatCardBase & {
    type: 'citation-list'
    title: string
    description?: string
    citations: StudioCitationEntry[]
  })
  | (StudioChatCardBase & {
    type: 'text'
    content: string
    tone?: 'default' | 'subtle'
  })
  | (StudioChatCardBase & {
    type: 'draft-review'
    title: string
    description?: string
    draftKind: 'email' | 'document' | 'reply'
    subject?: string
    recipients?: string[]
    sections: StudioLabeledValue[]
    actions: StudioAction[]
  })
  | (StudioChatCardBase & {
    type: 'code'
    fileName: string
    language?: string
    tag?: string
    code: string
  })
  | (StudioChatCardBase & {
    type: 'artifact-preview'
    preview?: StudioArtifactPreviewPayload
    fileName?: string
    tag?: string
    previewTitle?: string
    chartRows?: StudioChartSeriesRow[]
    legend?: StudioLegendItem[]
  })
  | (StudioChatCardBase & {
    type: 'work-item-list'
    title: string
    description?: string
    items: StudioWorkItem[]
  })
  | (StudioChatCardBase & {
    type: 'meeting-recap'
    title: string
    description?: string
    participants?: string[]
    decisions: string[]
    openQuestions?: string[]
    actionItems?: StudioWorkItem[]
  })
  | (StudioChatCardBase & {
    type: 'schedule'
    title: string
    description?: string
    scheduleLabel: string
    nextRun: string
    deliveryChannel?: string
    statusTag: string
    actions: StudioAction[]
  })
  | (StudioChatCardBase & {
    type: 'connect-auth'
    title: string
    description: string
    provider: string
    statusTag: string
    scopes: string[]
    actions: StudioAction[]
  })
  | (StudioChatCardBase & {
    type: 'error-boundary'
    title: string
    description: string
    severity: 'warning' | 'critical'
    blockedBy?: string
    suggestions: string[]
    actions?: StudioAction[]
  })
  | (StudioChatCardBase & {
    type: 'approval'
    title: string
    description: string
    levelTag: string
    actions: Array<StudioAction | string>
  })

export interface StudioWorkspaceFile {
  id: string
  name: string
  type: 'folder' | 'file'
  indent: number
  expanded?: boolean
  highlighted?: boolean
  color?: string
  status?: string
}

export interface StudioArtifact {
  id: string
  name: string
  summary: string
  tag: string
  tagTone: 'primary' | 'success' | 'neutral'
  preview?: StudioArtifactPreviewPayload
}

export interface StudioChartRow {
  label: string
  value: number
  over?: boolean
}

export type StudioWorkspacePreview = StudioArtifactPreviewPayload

export type StudioCollaborationMode = 'auto' | 'pipeline' | 'race' | 'debate'
export type StudioCollaborationState =
  | 'intake'
  | 'clarifying'
  | 'planning'
  | 'executing'
  | 'converging'
  | 'confirming'
  | 'completed'
  | 'blocked'

export interface StudioSessionDetail {
  id: string
  mode?: 'regular' | 'group'
  status?: StudioSessionStatus
  headerTitle: string
  headerTag: string
  headerBadge: string
  assistantName: string
  run?: StudioSessionRun
  participantAssistantIds?: string[]
  coordinatorAssistantId?: string
  coordinatorPersonaPreset?: 'general' | 'pace' | 'risk' | 'outcome'
  collaborationMode?: StudioCollaborationMode
  collaborationState?: StudioCollaborationState
  clarificationOwner?: 'coordinator'
  collaborationSummary?: {
    activeTasks: number
    completedTasks: number
    blockedTasks: number
  }
  promptTitle?: string
  promptDescription?: string
  options?: StudioOption[]
  confirmLabel?: string
  attachments?: string[]
  inputPlaceholder?: string
  workspacePath?: string
  chartTitle?: string
  chartRows?: StudioChartRow[]
  workspacePreview?: StudioWorkspacePreview
  selectedArtifactId?: string
  pendingPermissions?: StudioPermissionRequest[]
  messages: StudioMessage[]
  chatCards?: StudioChatCard[]
  workspaceFiles: StudioWorkspaceFile[]
  artifacts: StudioArtifact[]
}
