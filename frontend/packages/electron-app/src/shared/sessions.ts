export type OpencodeFileDiff = {
  file: string
  before: string
  after: string
  additions: number
  deletions: number
  status?: "added" | "deleted" | "modified"
}

export type OpencodeSessionStatus =
  | { type: "idle" }
  | { type: "retry"; attempt: number; message: string; next: number }
  | { type: "busy" }

export type OpencodeSessionInfo = {
  id: string
  slug: string
  projectID: string
  workspaceID?: string
  directory: string
  parentID?: string
  summary?: {
    additions: number
    deletions: number
    files: number
    diffs?: OpencodeFileDiff[]
  }
  share?: { url: string }
  title: string
  version: string
  time: {
    created: number
    updated: number
    compacting?: number
    archived?: number
  }
}

export type OpencodeUserMessage = {
  id: string
  sessionID: string
  role: "user"
  time: { created: number }
  summary?: { title?: string; body?: string; diffs: OpencodeFileDiff[] }
  agent: string
  model: { providerID: string; modelID: string }
  system?: string
  variant?: string
}

export type OpencodeAssistantMessage = {
  id: string
  sessionID: string
  role: "assistant"
  time: { created: number; completed?: number }
  error?: { name: string; data?: { message?: string; [key: string]: unknown } }
  parentID: string
  modelID: string
  providerID: string
  mode: string
  agent: string
  path: { cwd: string; root: string }
  summary?: boolean
  cost: number
  finish?: string
  variant?: string
}

export type OpencodeMessage = OpencodeUserMessage | OpencodeAssistantMessage

export type OpencodeTextPart = {
  id: string
  sessionID: string
  messageID: string
  type: "text"
  text: string
  synthetic?: boolean
  ignored?: boolean
  time?: { start: number; end?: number }
  metadata?: Record<string, unknown>
}

export type OpencodeFilePart = {
  id: string
  sessionID: string
  messageID: string
  type: "file"
  mime: string
  filename?: string
  url: string
}

export type OpencodeToolPart = {
  id: string
  sessionID: string
  messageID: string
  type: "tool"
  callID: string
  tool: string
  state:
    | { status: "pending"; input: Record<string, unknown>; raw: string }
    | { status: "running"; input: Record<string, unknown>; title?: string; metadata?: Record<string, unknown>; time: { start: number } }
    | { status: "completed"; input: Record<string, unknown>; output: string; title: string; metadata: Record<string, unknown>; time: { start: number; end: number; compacted?: number }; attachments?: OpencodeFilePart[] }
    | { status: "error"; input: Record<string, unknown>; error: string; metadata?: Record<string, unknown>; time: { start: number; end: number } }
  metadata?: Record<string, unknown>
}

export type OpencodePatchPart = {
  id: string
  sessionID: string
  messageID: string
  type: "patch"
  hash: string
  files: string[]
}

export type OpencodeReasoningPart = {
  id: string
  sessionID: string
  messageID: string
  type: "reasoning"
  text: string
}

export type OpencodeSubtaskPart = {
  id: string
  sessionID: string
  messageID: string
  type: "subtask"
  prompt: string
  description: string
  agent: string
}

export type OpencodeStepStartPart = {
  id: string
  sessionID: string
  messageID: string
  type: "step-start"
  snapshot?: string
}

export type OpencodeStepFinishPart = {
  id: string
  sessionID: string
  messageID: string
  type: "step-finish"
  reason: string
  snapshot?: string
}

export type OpencodeSnapshotPart = {
  id: string
  sessionID: string
  messageID: string
  type: "snapshot"
  snapshot: string
}

export type OpencodeAgentPart = {
  id: string
  sessionID: string
  messageID: string
  type: "agent"
  name: string
}

export type OpencodeRetryPart = {
  id: string
  sessionID: string
  messageID: string
  type: "retry"
  attempt: number
  error: { name: string; data?: { message?: string; [key: string]: unknown } }
  time: { created: number }
}

export type OpencodeCompactionPart = {
  id: string
  sessionID: string
  messageID: string
  type: "compaction"
  auto: boolean
  overflow?: boolean
}

export type OpencodePart =
  | OpencodeTextPart
  | OpencodeFilePart
  | OpencodeToolPart
  | OpencodePatchPart
  | OpencodeReasoningPart
  | OpencodeSubtaskPart
  | OpencodeStepStartPart
  | OpencodeStepFinishPart
  | OpencodeSnapshotPart
  | OpencodeAgentPart
  | OpencodeRetryPart
  | OpencodeCompactionPart

export type OpencodeMessageRecord = {
  info: OpencodeMessage
  parts: OpencodePart[]
}

export type DesktopSessionSummary = {
  id: string
  title: string
  directory: string
  createdAt: number
  updatedAt: number
  status: OpencodeSessionStatus
  summary?: OpencodeSessionInfo["summary"]
}

export type DesktopSessionDetail = {
  session: OpencodeSessionInfo
  messages: OpencodeMessageRecord[]
  status: OpencodeSessionStatus
}

export type DesktopSessionState = {
  summaries: DesktopSessionSummary[]
  activeSessionId: string | null
  activeSession: DesktopSessionDetail | null
}

export type DesktopRuntimeEvent =
  | { type: "server.connected" | "server.heartbeat"; properties: Record<string, unknown> }
  | { type: "runtime.restarted"; properties: { reason: string } }
  | { type: "session.created" | "session.updated" | "session.deleted"; properties: { info: OpencodeSessionInfo } }
  | { type: "session.status"; properties: { sessionID: string; status: OpencodeSessionStatus } }
  | { type: "session.idle"; properties: { sessionID: string } }
  | { type: "message.updated"; properties: { info: OpencodeMessage } }
  | { type: "message.removed"; properties: { sessionID: string; messageID: string } }
  | { type: "message.part.updated"; properties: { part: OpencodePart } }
  | { type: "message.part.delta"; properties: { sessionID: string; messageID: string; partID: string; field: string; delta: string } }
  | { type: "message.part.removed"; properties: { sessionID: string; messageID: string; partID: string } }
  | { type: "session.compacted"; properties: { sessionID: string } }

export const IDLE_SESSION_STATUS: OpencodeSessionStatus = { type: "idle" }
