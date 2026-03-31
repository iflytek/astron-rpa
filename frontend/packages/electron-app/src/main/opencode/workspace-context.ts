import type {
  AssistantRecord,
  AssistantSessionRecord,
  GroupRoomRecord,
  GroupRoomSessionRecord,
} from '../../shared/assistants'

export type SessionMessageContext = {
  agent?: string | null
  system?: string | null
}

export type SessionWorkspaceContext = {
  workspacePath?: string | null
}

export function buildAssistantDirectAgentName(assistantId: string) {
  return `assistant-direct-${assistantId}`
}

export function buildAssistantWorkerAgentName(assistantId: string) {
  return `assistant-worker-${assistantId}`
}

export function buildRoomCoordinatorAgentName(roomId: string) {
  return `room-coordinator-${roomId}`
}

export function buildAssistantWorkspacePrompt(assistant: Pick<AssistantRecord, 'name' | 'workspacePath'>) {
  return buildWorkspaceInstructions({
    workspacePath: assistant.workspacePath,
    ownerName: assistant.name,
    kind: 'assistant',
  })
}

export function buildGroupWorkspacePrompt(room: Pick<GroupRoomRecord, 'name' | 'workspacePath'>) {
  return buildWorkspaceInstructions({
    workspacePath: room.workspacePath,
    ownerName: room.name,
    kind: 'group',
  })
}

export function appendPromptSection(basePrompt: string | null | undefined, section: string | null) {
  const normalizedBase = typeof basePrompt === 'string' && basePrompt.trim() ? basePrompt.trim() : ''
  const normalizedSection = typeof section === 'string' && section.trim() ? section.trim() : ''

  if (!normalizedBase) {
    return normalizedSection || undefined
  }

  if (!normalizedSection) {
    return normalizedBase
  }

  return `${normalizedBase}\n\n${normalizedSection}`
}

export function resolveSessionMessageContext(
  sessionID: string,
  assistants: AssistantRecord[],
  groupRooms: GroupRoomRecord[],
  assistantSessions: AssistantSessionRecord[],
  groupRoomSessions: GroupRoomSessionRecord[],
): SessionMessageContext {
  const groupSession = groupRoomSessions.find((session) => session.runtimeSessionId === sessionID)
  if (groupSession) {
    const room = groupRooms.find((item) => item.id === groupSession.groupRoomId)
    if (room) {
      return {
        agent: buildRoomCoordinatorAgentName(room.id),
        system: buildGroupWorkspacePrompt(room) ?? null,
      }
    }
  }

  const assistantSession = assistantSessions.find((session) => session.runtimeSessionId === sessionID)
  if (assistantSession) {
    const assistant = assistants.find((item) => item.id === assistantSession.assistantId)
    if (assistant) {
      return {
        agent: buildAssistantDirectAgentName(assistant.id),
        system: buildAssistantWorkspacePrompt(assistant) ?? null,
      }
    }
  }

  return {}
}

export function resolveSessionWorkspaceContext(
  sessionID: string,
  assistants: AssistantRecord[],
  groupRooms: GroupRoomRecord[],
  assistantSessions: AssistantSessionRecord[],
  groupRoomSessions: GroupRoomSessionRecord[],
): SessionWorkspaceContext {
  const groupSession = groupRoomSessions.find((session) => session.runtimeSessionId === sessionID)
  if (groupSession) {
    const room = groupRooms.find((item) => item.id === groupSession.groupRoomId)
    return { workspacePath: room?.workspacePath ?? null }
  }

  const assistantSession = assistantSessions.find((session) => session.runtimeSessionId === sessionID)
  if (assistantSession) {
    const assistant = assistants.find((item) => item.id === assistantSession.assistantId)
    return { workspacePath: assistant?.workspacePath ?? null }
  }

  return {}
}

function buildWorkspaceInstructions(input: {
  workspacePath?: string
  ownerName: string
  kind: 'assistant' | 'group'
}) {
  const workspacePath = typeof input.workspacePath === 'string' && input.workspacePath.trim()
    ? input.workspacePath.trim()
    : null

  if (!workspacePath) {
    return null
  }

  const lines = [
    `Workspace root: ${workspacePath}`,
    'This is a soft application-level workspace constraint, not an enforced runtime cwd.',
  ]

  if (input.kind === 'group') {
    lines.push(`Use this workspace root for shared room artifacts and coordination outputs for ${input.ownerName}.`)
  }
  else {
    lines.push(`Treat this workspace as the primary working area for ${input.ownerName}.`)
  }

  lines.push('Prefer reading, writing, and creating files only under this workspace root.')
  lines.push('When you reference files or run tools, use explicit absolute paths under this workspace root whenever possible.')
  lines.push('If the user asks to work outside this workspace, explicitly acknowledge that you are leaving the assigned workspace before proceeding.')

  return lines.join('\n')
}
