import type { OpencodeMessageRecord, OpencodeSessionInfo, OpencodeSessionStatus } from '../../shared/sessions'
import { buildPromptRequestBody, type CreateSessionInput, type SendMessageInput } from '../../shared/runtime'
import type { SidecarManager } from './sidecar'

export type RuntimeApi = {
  listSessions: () => Promise<OpencodeSessionInfo[]>
  getSession: (sessionID: string) => Promise<OpencodeSessionInfo>
  getSessionMessages: (sessionID: string) => Promise<OpencodeMessageRecord[]>
  getSessionStatuses: () => Promise<Record<string, OpencodeSessionStatus>>
  createSession: (input: CreateSessionInput) => Promise<OpencodeSessionInfo>
  deleteSession: (sessionID: string) => Promise<void>
  sendMessage: (input: SendMessageInput) => Promise<void>
  openEventStream: (signal: AbortSignal) => Promise<Response>
}

export function createRuntimeApi(runtime: Pick<SidecarManager, 'getConnection'>): RuntimeApi {
  return {
    listSessions: () => requestJson<OpencodeSessionInfo[]>('/session?roots=true'),
    getSession: (sessionID) => requestJson<OpencodeSessionInfo>(`/session/${encodeURIComponent(sessionID)}`),
    getSessionMessages: (sessionID) =>
      requestJson<OpencodeMessageRecord[]>(`/session/${encodeURIComponent(sessionID)}/message`),
    getSessionStatuses: () => requestJson<Record<string, OpencodeSessionStatus>>('/session/status'),
    createSession: (input) =>
      requestJson<OpencodeSessionInfo>('/session', {
        method: 'POST',
        body: { ...(input.title?.trim() ? { title: input.title.trim() } : {}) },
      }),
    deleteSession: async (sessionID) => {
      await requestVoid(`/session/${encodeURIComponent(sessionID)}`, { method: 'DELETE' })
    },
    sendMessage: async (input) => {
      await requestVoid(`/session/${encodeURIComponent(input.sessionID)}/prompt_async`, {
        method: 'POST',
        body: buildPromptRequestBody(input),
      })
    },
    openEventStream: async (signal) => {
      const connection = await runtime.getConnection()
      const url = new URL('/event', connection.baseUrl)
      const response = await fetch(url, {
        headers: {
          ...connection.headers,
          accept: 'text/event-stream',
          cache: 'no-cache',
        },
        method: 'GET',
        signal,
      })

      if (!response.ok || !response.body) {
        throw new Error(`Bundled runtime event stream failed (${response.status} ${response.statusText})`)
      }

      return response
    },
  }

  async function requestJson<T>(pathname: string, init?: { method?: 'GET' | 'POST'; body?: unknown }) {
    const connection = await runtime.getConnection()
    const url = new URL(pathname, connection.baseUrl)
    const response = await fetch(url, {
      headers: {
        ...connection.headers,
        accept: 'application/json',
        ...(init?.body ? { 'content-type': 'application/json' } : {}),
      },
      method: init?.method ?? 'GET',
      body: init?.body ? JSON.stringify(init.body) : undefined,
    })

    if (!response.ok) {
      throw new Error(`Bundled runtime request failed for ${url.pathname} (${response.status} ${response.statusText})`)
    }

    return (await response.json()) as T
  }

  async function requestVoid(pathname: string, init: { method: 'POST' | 'DELETE'; body?: unknown }) {
    const connection = await runtime.getConnection()
    const url = new URL(pathname, connection.baseUrl)
    const response = await fetch(url, {
      headers: {
        ...connection.headers,
        accept: 'application/json',
        ...(init.body ? { 'content-type': 'application/json' } : {}),
      },
      method: init.method,
      body: init.body ? JSON.stringify(init.body) : undefined,
    })

    if (!response.ok) {
      throw new Error(`Bundled runtime request failed for ${url.pathname} (${response.status} ${response.statusText})`)
    }
  }
}
