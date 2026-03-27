import {
  IDLE_SESSION_STATUS,
  type DesktopRuntimeEvent,
  type DesktopSessionDetail,
  type DesktopSessionState,
  type DesktopSessionSummary,
  type OpencodeMessage,
  type OpencodeMessageRecord,
  type OpencodePart,
  type OpencodeSessionInfo,
  type OpencodeSessionStatus,
} from '../../shared/sessions'
import type { RuntimeApi } from '../opencode/api'

export type SessionStore = {
  listSessions: () => Promise<DesktopSessionSummary[]>
  getSession: (sessionID: string) => Promise<DesktopSessionDetail>
  loadSession: (sessionID?: string | null) => Promise<DesktopSessionState>
  getState: () => DesktopSessionState
  applyEvent: (event: DesktopRuntimeEvent) => void
}

export function createSessionStore(api: RuntimeApi): SessionStore {
  let state: DesktopSessionState = {
    summaries: [],
    activeSessionId: null,
    activeSession: null,
  }
  let loadRequestVersion = 0
  const dirtySessionIDs = new Set<string>()

  return {
    listSessions: async () => structuredClone(await fetchSummaries()),
    getSession: async (sessionID) => structuredClone(await fetchSessionDetail(sessionID)),
    loadSession: async (sessionID) => {
      const requestVersion = ++loadRequestVersion
      const summaries = await fetchSummaries()
      const preferredSessionId = sessionID ?? state.activeSessionId
      const nextSessionId =
        preferredSessionId && summaries.some((summary) => summary.id === preferredSessionId)
          ? preferredSessionId
          : summaries[0]?.id ?? null

      if (!nextSessionId) {
        const nextState = mergeLoadedState(state, { summaries, activeSessionId: null, activeSession: null })
        if (requestVersion === loadRequestVersion) {
          state = nextState
        }
        return structuredClone(requestVersion === loadRequestVersion ? nextState : state)
      }

      const shouldFetchDetail =
        sessionID !== undefined || state.activeSession?.session.id !== nextSessionId || dirtySessionIDs.has(nextSessionId)
      const activeSession = shouldFetchDetail ? await fetchSessionDetail(nextSessionId) : state.activeSession

      if (requestVersion !== loadRequestVersion) {
        return structuredClone(state)
      }

      dirtySessionIDs.delete(nextSessionId)
      state = mergeLoadedState(state, { summaries, activeSessionId: nextSessionId, activeSession })

      return structuredClone(state)
    },
    getState: () => structuredClone(state),
    applyEvent: (event) => {
      state = applyRuntimeEvent(state, event)
      if (event.type === 'session.compacted') {
        dirtySessionIDs.add(event.properties.sessionID)
        void refreshSessionDetail(event.properties.sessionID)
      }
    },
  }

  async function fetchSummaries() {
    const [sessions, statuses] = await Promise.all([api.listSessions(), safeGetStatuses(api)])
    return sessions
      .filter((session) => !session.parentID && !session.time.archived)
      .map((session) => toSummary(session, statuses[session.id]))
      .sort((left, right) => right.updatedAt - left.updatedAt)
  }

  async function fetchSessionDetail(sessionID: string): Promise<DesktopSessionDetail> {
    const [session, messages, statuses] = await Promise.all([
      api.getSession(sessionID),
      api.getSessionMessages(sessionID),
      safeGetStatuses(api),
    ])

    return {
      session,
      messages: sortMessageRecords(messages),
      status: statuses[sessionID] ?? IDLE_SESSION_STATUS,
    }
  }

  async function refreshSessionDetail(sessionID: string) {
    try {
      const detail = await fetchSessionDetail(sessionID)
      dirtySessionIDs.delete(sessionID)
      const nextSummary = toSummary(detail.session, detail.status)
      const summaries = mergeSummaries([nextSummary], state.summaries)

      if (state.activeSessionId === sessionID) {
        state = { ...state, summaries, activeSession: detail }
        return
      }

      state = { ...state, summaries }
    }
    catch {
      // keep the session marked dirty so the next explicit load rehydrates from the runtime.
    }
  }
}

function safeGetStatuses(api: Pick<RuntimeApi, 'getSessionStatuses'>) {
  return api.getSessionStatuses().catch((): Record<string, OpencodeSessionStatus> => ({}))
}

function toSummary(session: OpencodeSessionInfo, status?: OpencodeSessionStatus): DesktopSessionSummary {
  return {
    id: session.id,
    title: session.title,
    directory: session.directory,
    createdAt: session.time.created,
    updatedAt: session.time.updated,
    status: status ?? IDLE_SESSION_STATUS,
    summary: session.summary,
  }
}

function sortMessageRecords(messages: OpencodeMessageRecord[]) {
  return messages
    .slice()
    .sort((left, right) => left.info.time.created - right.info.time.created)
    .map((record) => ({ info: record.info, parts: record.parts.slice() }))
}

function applyRuntimeEvent(state: DesktopSessionState, event: DesktopRuntimeEvent): DesktopSessionState {
  switch (event.type) {
    case 'session.created':
    case 'session.updated':
      return applySessionUpsert(state, event.properties.info)
    case 'session.deleted':
      return applySessionDelete(state, event.properties.info.id)
    case 'session.status':
      return updateSessionStatus(state, event.properties.sessionID, event.properties.status)
    case 'session.idle':
      return updateSessionStatus(state, event.properties.sessionID, IDLE_SESSION_STATUS)
    case 'message.updated':
      return upsertMessage(state, event.properties.info)
    case 'message.removed':
      return removeMessage(state, event.properties.sessionID, event.properties.messageID)
    case 'message.part.updated':
      return upsertPart(state, event.properties.part)
    case 'message.part.delta':
      return appendPartDelta(state, event.properties)
    case 'message.part.removed':
      return removePart(state, event.properties)
    case 'session.compacted':
      return state
    default:
      return state
  }
}

function mergeLoadedState(current: DesktopSessionState, loaded: DesktopSessionState): DesktopSessionState {
  const summaries = mergeSummaries(loaded.summaries, current.summaries)

  if (!loaded.activeSessionId) {
    return { summaries, activeSessionId: null, activeSession: null }
  }

  return {
    summaries,
    activeSessionId: loaded.activeSessionId,
    activeSession: loaded.activeSession ?? null,
  }
}

function mergeSummaries(loaded: DesktopSessionSummary[], live: DesktopSessionSummary[]) {
  const merged = new Map<string, DesktopSessionSummary>(loaded.map((s) => [s.id, s]))

  for (const summary of live) {
    const existing = merged.get(summary.id)
    if (!existing) {
      merged.set(summary.id, summary)
      continue
    }

    merged.set(summary.id, summary.updatedAt >= existing.updatedAt ? summary : existing)
  }

  return [...merged.values()].sort((left, right) => right.updatedAt - left.updatedAt)
}

function applySessionUpsert(state: DesktopSessionState, session: OpencodeSessionInfo): DesktopSessionState {
  const summaries = state.summaries.slice()
  const summaryIndex = summaries.findIndex((item) => item.id === session.id)
  const includeInSummaries = !session.parentID && !session.time.archived

  if (includeInSummaries) {
    const nextSummary = toSummary(
      session,
      summaryIndex >= 0
        ? summaries[summaryIndex]?.status
        : state.activeSession?.session.id === session.id
          ? state.activeSession.status
          : undefined,
    )

    if (summaryIndex >= 0) {
      summaries[summaryIndex] = nextSummary
    }
    else {
      summaries.push(nextSummary)
    }
  }
  else if (summaryIndex >= 0) {
    summaries.splice(summaryIndex, 1)
  }

  summaries.sort((left, right) => right.updatedAt - left.updatedAt)

  const activeSession =
    state.activeSession?.session.id === session.id
      ? { ...state.activeSession, session }
      : state.activeSession

  const activeSessionId = state.activeSessionId === session.id && session.time.archived ? null : state.activeSessionId

  return { summaries, activeSessionId, activeSession: activeSessionId ? activeSession : null }
}

function applySessionDelete(state: DesktopSessionState, sessionID: string): DesktopSessionState {
  const summaries = state.summaries.filter((s) => s.id !== sessionID)
  const activeSessionId = state.activeSessionId === sessionID ? null : state.activeSessionId

  return { summaries, activeSessionId, activeSession: activeSessionId ? state.activeSession : null }
}

function updateSessionStatus(state: DesktopSessionState, sessionID: string, status: OpencodeSessionStatus): DesktopSessionState {
  return {
    summaries: state.summaries.map((s) => (s.id === sessionID ? { ...s, status } : s)),
    activeSessionId: state.activeSessionId,
    activeSession:
      state.activeSession?.session.id === sessionID
        ? { ...state.activeSession, status }
        : state.activeSession,
  }
}

function upsertMessage(state: DesktopSessionState, message: OpencodeMessage): DesktopSessionState {
  if (state.activeSession?.session.id !== message.sessionID) {
    return state
  }

  const messages = state.activeSession.messages.slice()
  const index = messages.findIndex((item) => item.info.id === message.id)
  const parts = index >= 0 ? messages[index]?.parts ?? [] : []
  const nextRecord: OpencodeMessageRecord = { info: message, parts: parts.slice() }

  if (index >= 0) {
    messages[index] = nextRecord
  }
  else {
    messages.push(nextRecord)
  }

  return {
    ...state,
    activeSession: { ...state.activeSession, messages: sortMessageRecords(messages) },
  }
}

function removeMessage(state: DesktopSessionState, sessionID: string, messageID: string): DesktopSessionState {
  if (state.activeSession?.session.id !== sessionID) {
    return state
  }

  return {
    ...state,
    activeSession: {
      ...state.activeSession,
      messages: state.activeSession.messages.filter((item) => item.info.id !== messageID),
    },
  }
}

function upsertPart(state: DesktopSessionState, part: OpencodePart): DesktopSessionState {
  if (state.activeSession?.session.id !== part.sessionID) {
    return state
  }

  return {
    ...state,
    activeSession: {
      ...state.activeSession,
      messages: state.activeSession.messages.map((record) => {
        if (record.info.id !== part.messageID) {
          return record
        }

        const parts = record.parts.slice()
        const index = parts.findIndex((item) => item.id === part.id)
        if (index >= 0) {
          parts[index] = part
        }
        else {
          parts.push(part)
        }

        return { ...record, parts }
      }),
    },
  }
}

function appendPartDelta(
  state: DesktopSessionState,
  payload: { sessionID: string; messageID: string; partID: string; field: string; delta: string },
): DesktopSessionState {
  if (state.activeSession?.session.id !== payload.sessionID) {
    return state
  }

  return {
    ...state,
    activeSession: {
      ...state.activeSession,
      messages: state.activeSession.messages.map((record) => {
        if (record.info.id !== payload.messageID) {
          return record
        }

        return {
          ...record,
          parts: record.parts.map((part) => {
            if (part.id !== payload.partID) {
              return part
            }

            const next = { ...part } as Record<string, unknown>
            const current = next[payload.field]
            if (typeof current === 'string') {
              next[payload.field] = current + payload.delta
            }
            else if (typeof current === 'undefined') {
              next[payload.field] = payload.delta
            }
            return next as OpencodePart
          }),
        }
      }),
    },
  }
}

function removePart(
  state: DesktopSessionState,
  payload: { sessionID: string; messageID: string; partID: string },
): DesktopSessionState {
  if (state.activeSession?.session.id !== payload.sessionID) {
    return state
  }

  return {
    ...state,
    activeSession: {
      ...state.activeSession,
      messages: state.activeSession.messages.map((record) => {
        if (record.info.id !== payload.messageID) {
          return record
        }

        return {
          ...record,
          parts: record.parts.filter((part) => part.id !== payload.partID),
        }
      }),
    },
  }
}
