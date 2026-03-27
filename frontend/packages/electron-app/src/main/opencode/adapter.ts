import type { AssistantRecord, GroupRoomRecord } from '../../shared/assistants'
import type {
  OpencodeAssistantMessage,
  OpencodeMessageRecord,
  OpencodeSessionInfo,
  OpencodeTextPart,
  OpencodeToolPart,
} from '../../shared/sessions'

/**
 * These types mirror the AI Studio frontend's type definitions so we can keep
 * this adapter self-contained without importing from the web-app package.
 */
export type StudioSession = {
  id: string
  title: string
  time: string
  active?: boolean
}

export type StudioAssistant = {
  id: string
  name: string
  badge: string
  status: string
  sessions: StudioSession[]
  workspacePath?: string
  persona?: string
  capabilities?: string
  skills?: string[]
  groupParticipantAssistantIds?: string[]
  groupCollaborationMode?: 'auto' | 'pipeline' | 'race' | 'debate'
}

export type StudioAssistantGroup = {
  id: string
  title: string
  assistants: StudioAssistant[]
}

export type StudioMessage = {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  time?: string
  assistantName?: string
  order?: number
}

export type StudioToolCall = {
  name: string
  arg: string
  status: 'done' | 'running' | 'pending' | 'failed'
  detail?: string
  duration?: string
  result?: string
}

export type StudioChatCard =
  | {
      id: string
      type: 'text'
      content: string
      tone?: 'default' | 'subtle'
      assistantName?: string
      time?: string
      order?: number
    }
  | {
      id: string
      type: 'tool-call-list'
      title?: string
      summary?: string
      calls: StudioToolCall[]
      assistantName?: string
      time?: string
      order?: number
    }

export type StudioArtifact = {
  id: string
  name: string
  summary: string
  tag: string
  tagTone: 'primary' | 'success' | 'neutral'
}

export type StudioWorkspaceFile = {
  id: string
  name: string
  type: 'folder' | 'file'
  indent: number
}

export type StudioSessionDetail = {
  id: string
  mode?: 'regular' | 'group'
  headerTitle: string
  headerTag: string
  headerBadge: string
  assistantName: string
  messages: StudioMessage[]
  chatCards: StudioChatCard[]
  workspaceFiles: StudioWorkspaceFile[]
  artifacts: StudioArtifact[]
  workspacePath?: string
  inputPlaceholder?: string
}

export type AIStudioBootstrap = {
  assistantGroups: StudioAssistantGroup[]
  defaultSessionId: string
}

function formatRelativeTime(epochMs: number) {
  const diff = Date.now() - epochMs
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

function getAssistantBadge(assistant: AssistantRecord): string {
  if (assistant.avatar?.trim()) return assistant.avatar.trim().slice(0, 1)
  return assistant.name.trim().slice(0, 1).toUpperCase() || 'A'
}

function getGroupRoomBadge(room: GroupRoomRecord): string {
  return room.name.trim().slice(0, 1).toUpperCase() || '群'
}

/**
 * Convert opencode sessions + assistants/groupRooms to StudioAssistantGroup[].
 * This is what populates the AI Studio sidebar.
 */
export function toStudioAssistantGroups(
  assistants: AssistantRecord[],
  groupRooms: GroupRoomRecord[],
  sessionsByAssistantId: Map<string, OpencodeSessionInfo[]>,
  sessionsByGroupRoomId: Map<string, OpencodeSessionInfo[]>,
  unassignedSessions: OpencodeSessionInfo[],
): StudioAssistantGroup[] {
  const groups: StudioAssistantGroup[] = []

  const singleAssistants: StudioAssistant[] = assistants.map((assistant) => {
    const sessions = sessionsByAssistantId.get(assistant.id) ?? []
    return {
      id: assistant.id,
      name: assistant.name,
      badge: getAssistantBadge(assistant),
      status: '待命',
      workspacePath: undefined,
      persona: assistant.systemPrompt ?? undefined,
      capabilities: assistant.description ?? undefined,
      skills: assistant.skillIds.length ? [...assistant.skillIds] : undefined,
      sessions: sessions.map((s) => ({
        id: s.id,
        title: s.title || '未命名会话',
        time: formatRelativeTime(s.time.updated),
        active: false,
      })),
    }
  })

  if (singleAssistants.length > 0) {
    groups.push({
      id: 'single',
      title: '我的助手',
      assistants: singleAssistants,
    })
  }

  const collaborationAssistants: StudioAssistant[] = groupRooms.map((room) => {
    const sessions = sessionsByGroupRoomId.get(room.id) ?? []
    return {
      id: room.id,
      name: room.name,
      badge: getGroupRoomBadge(room),
      status: '群聊',
      persona: room.coordinatorPrompt ?? undefined,
      capabilities: room.description ?? undefined,
      groupParticipantAssistantIds: room.memberAssistantIds.length ? [...room.memberAssistantIds] : undefined,
      groupCollaborationMode: room.collaborationMode,
      sessions: sessions.map((s) => ({
        id: s.id,
        title: s.title || '未命名会话',
        time: formatRelativeTime(s.time.updated),
        active: false,
      })),
    }
  })

  if (collaborationAssistants.length > 0) {
    groups.push({
      id: 'collaboration',
      title: '协作群聊',
      assistants: collaborationAssistants,
    })
  }

  if (unassignedSessions.length > 0) {
    const defaultAssistant: StudioAssistant = {
      id: 'default',
      name: '通用对话',
      badge: 'AI',
      status: '待命',
      sessions: unassignedSessions.map((s) => ({
        id: s.id,
        title: s.title || '未命名会话',
        time: formatRelativeTime(s.time.updated),
        active: false,
      })),
    }
    groups.push({
      id: 'default',
      title: '会话',
      assistants: [defaultAssistant],
    })
  }

  return groups
}

/**
 * Build the default session ID from the most recently updated root session.
 */
export function resolveDefaultSessionId(sessions: OpencodeSessionInfo[]): string {
  const sorted = sessions
    .filter((s) => !s.parentID && !s.time.archived)
    .sort((a, b) => b.time.updated - a.time.updated)
  return sorted[0]?.id ?? ''
}

/**
 * Convert opencode messages into StudioSessionDetail for the AI Studio frontend.
 * Currently maps:
 *   - user messages → StudioMessage (role: user)
 *   - assistant text parts → StudioChatCard (type: text)
 *   - assistant tool parts → StudioChatCard (type: tool-call-list)
 */
export function toStudioSessionDetail(
  session: OpencodeSessionInfo,
  messageRecords: OpencodeMessageRecord[],
  assistantName: string = 'AI 助手',
  assistantBadge: string = 'AI',
): StudioSessionDetail {
  const messages: StudioMessage[] = []
  const chatCards: StudioChatCard[] = []
  let seq = 0

  const sorted = messageRecords
    .slice()
    .sort((a, b) => a.info.time.created - b.info.time.created)

  for (const record of sorted) {
    const { info, parts } = record

    if (info.role === 'user') {
      const textPart = parts.find((p): p is OpencodeTextPart => p.type === 'text')
      if (textPart?.text?.trim()) {
        messages.push({
          id: info.id,
          role: 'user',
          content: textPart.text,
          time: formatRelativeTime(info.time.created),
          order: seq++,
        })
      }
      continue
    }

    if (info.role === 'assistant') {
      const assistantMsg = info as OpencodeAssistantMessage
      const timeStr = formatRelativeTime(info.time.created)

      const toolParts = parts.filter((p): p is OpencodeToolPart => p.type === 'tool')
      const textParts = parts.filter((p): p is OpencodeTextPart => p.type === 'text' && !p.synthetic && !p.ignored)

      if (toolParts.length > 0) {
        const calls: StudioToolCall[] = toolParts.map((tp) => {
          const inputArg = tp.state.status !== 'pending'
            ? JSON.stringify(tp.state.input ?? {}, null, 2)
            : (tp.state as { raw: string }).raw ?? ''

          let toolStatus: StudioToolCall['status'] = 'pending'
          let result: string | undefined

          if (tp.state.status === 'completed') {
            toolStatus = 'done'
            result = tp.state.output
          }
          else if (tp.state.status === 'running') {
            toolStatus = 'running'
          }
          else if (tp.state.status === 'error') {
            toolStatus = 'failed'
            result = tp.state.error
          }

          const duration =
            tp.state.status === 'completed' || tp.state.status === 'error'
              ? `${((tp.state.time.end - tp.state.time.start) / 1000).toFixed(1)}s`
              : undefined

          return {
            name: tp.tool,
            arg: inputArg,
            status: toolStatus,
            result,
            duration,
          }
        })

        chatCards.push({
          id: `${assistantMsg.id}-tools`,
          type: 'tool-call-list',
          calls,
          assistantName,
          time: timeStr,
          order: seq++,
        })
      }

      const combinedText = textParts.map((p) => p.text).join('\n').trim()
      if (combinedText) {
        chatCards.push({
          id: assistantMsg.id,
          type: 'text',
          content: combinedText,
          assistantName,
          time: timeStr,
          order: seq++,
        })
      }
    }
  }

  return {
    id: session.id,
    mode: 'regular',
    headerTitle: session.title || '未命名会话',
    headerTag: '运行中',
    headerBadge: assistantBadge,
    assistantName,
    workspacePath: session.directory,
    inputPlaceholder: '向 AI 助手发送消息…',
    messages,
    chatCards,
    workspaceFiles: [],
    artifacts: [],
  }
}
