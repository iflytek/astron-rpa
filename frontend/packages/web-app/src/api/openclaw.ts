export type OpenClawChatMessage = {
  role: 'system' | 'developer' | 'user' | 'assistant' | 'tool'
  content: string
}

export type OpenClawToolEvent = {
  toolCallId: string
  runId?: string
  name: string
  phase: 'start' | 'update' | 'result'
  args?: unknown
  output?: string
  ts: number
}

export type OpenClawChatResult = {
  text: string
  toolEvents: OpenClawToolEvent[]
}

type WsReqFrame = {
  type: 'req'
  id: string
  method: string
  params?: any
}

type WsResFrame = {
  type: 'res'
  id: string
  ok: boolean
  payload?: any
  error?: { code?: string, message?: string, details?: any }
}

type WsEventFrame = {
  type: 'event'
  event: string
  payload?: any
  seq?: number
  stateVersion?: any
  stream?: string
  runId?: string
  sessionKey?: string
  ts?: number
  data?: Record<string, any>
}

type WsFrame = WsReqFrame | WsResFrame | WsEventFrame

type StreamEvent = {
  stream?: string
  runId?: string
  sessionKey?: string
  ts?: number
  data?: Record<string, any>
}

type MessageContentBlock = {
  type?: string
  text?: string
  content?: string
  name?: string
  arguments?: unknown
  args?: unknown
}

function wsUrlForOpenClawProxy(): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/openclaw`
}

function stringifyToolOutput(value: unknown): string | undefined {
  if (typeof value === 'string')
    return value.trim() || undefined
  if (value == null)
    return undefined

  if (typeof value === 'number' || typeof value === 'boolean')
    return String(value)

  if (typeof value === 'object') {
    const record = value as Record<string, unknown>

    if (typeof record.text === 'string' && record.text.trim())
      return record.text.trim()

    if (Array.isArray(record.content)) {
      const text = record.content
        .map((item) => {
          if (!item || typeof item !== 'object')
            return null
          const entry = item as Record<string, unknown>
          if (entry.type === 'text' && typeof entry.text === 'string')
            return entry.text
          return null
        })
        .filter((item): item is string => Boolean(item?.trim()))
        .join('\n')
        .trim()

      if (text)
        return text
    }
  }

  try {
    return JSON.stringify(value, null, 2)
  }
  catch {
    return String(value)
  }
}

function normalizeToolStream(frame: WsEventFrame): StreamEvent | null {
  if (typeof frame.stream === 'string') {
    return {
      stream: frame.stream,
      runId: frame.runId,
      sessionKey: frame.sessionKey,
      ts: frame.ts,
      data: frame.data,
    }
  }

  if (frame.event === 'agent' && frame.payload && typeof frame.payload === 'object') {
    const payload = frame.payload as StreamEvent
    if (typeof payload.stream === 'string') {
      return {
        stream: payload.stream,
        runId: payload.runId,
        sessionKey: payload.sessionKey,
        ts: payload.ts,
        data: payload.data,
      }
    }
  }

  return null
}

function extractTextFromMessage(message: any): string {
  if (!message || typeof message !== 'object')
    return ''

  if (typeof message.text === 'string' && message.text.trim())
    return message.text.trim()

  const content = Array.isArray(message.content) ? message.content as MessageContentBlock[] : []
  return content
    .map((item) => {
      if (!item || typeof item !== 'object')
        return null
      if (item.type === 'text' && typeof item.text === 'string')
        return item.text
      return null
    })
    .filter((item): item is string => Boolean(item?.trim()))
    .join('\n')
    .trim()
}

function extractToolEventsFromMessage(message: any, fallbackTs: number): OpenClawToolEvent[] {
  if (!message || typeof message !== 'object' || !Array.isArray(message.content))
    return []

  const timestamp = typeof message.timestamp === 'number' ? message.timestamp : fallbackTs
  const runId = typeof message.runId === 'string' ? message.runId : undefined
  const messageToolCallId = typeof message.toolCallId === 'string' ? message.toolCallId : ''
  const blocks = message.content as MessageContentBlock[]

  const callEvents = blocks
    .map((item, index) => {
      const type = typeof item?.type === 'string' ? item.type.toLowerCase() : ''
      const isToolCall = ['toolcall', 'tool_call', 'tooluse', 'tool_use'].includes(type)
        || (typeof item?.name === 'string' && item?.arguments != null)

      if (!isToolCall)
        return null

      return {
        toolCallId: messageToolCallId || `${runId ?? 'tool'}:call:${index}`,
        runId,
        name: typeof item.name === 'string' ? item.name : 'tool',
        phase: 'start' as const,
        args: item.arguments ?? item.args,
        ts: timestamp,
      }
    })
    .filter(Boolean) as OpenClawToolEvent[]

  const resultEvents = blocks
    .map((item, index) => {
      const type = typeof item?.type === 'string' ? item.type.toLowerCase() : ''
      if (type !== 'toolresult' && type !== 'tool_result')
        return null

      const matchingCall = callEvents.find(call => call.name === item.name)
      return {
        toolCallId: matchingCall?.toolCallId || messageToolCallId || `${runId ?? 'tool'}:result:${index}`,
        runId,
        name: typeof item.name === 'string' ? item.name : matchingCall?.name ?? 'tool',
        phase: 'result' as const,
        output: typeof item.text === 'string'
          ? item.text
          : typeof item.content === 'string'
            ? item.content
            : undefined,
        ts: timestamp,
      }
    })
    .filter(Boolean) as OpenClawToolEvent[]

  return [...callEvents, ...resultEvents]
}

async function openclawChatViaWs(params: {
  text: string
  token?: string
  sessionKey?: string
  onToolEvent?: (event: OpenClawToolEvent) => void
}): Promise<OpenClawChatResult> {
  const ws = new WebSocket(wsUrlForOpenClawProxy())

  const awaitOpen = new Promise<void>((resolve, reject) => {
    ws.addEventListener('open', () => resolve(), { once: true })
    ws.addEventListener('error', () => reject(new Error('Unable to connect to openclaw gateway.')), { once: true })
  })

  const waitForRes = (id: string) => {
    return new Promise<WsResFrame>((resolve, reject) => {
      const onMessage = (ev: MessageEvent) => {
        try {
          const frame = JSON.parse(String(ev.data ?? '')) as WsFrame
          if (frame?.type === 'res' && frame.id === id) {
            ws.removeEventListener('message', onMessage)
            if (frame.ok)
              resolve(frame)
            else
              reject(new Error(frame?.error?.message || 'openclaw request failed'))
          }
        }
        catch {
          // ignore non-json frames
        }
      }

      ws.addEventListener('message', onMessage)

      const onClose = () => {
        ws.removeEventListener('message', onMessage)
        reject(new Error('openclaw gateway connection closed'))
      }

      ws.addEventListener('close', onClose, { once: true })
    })
  }

  await awaitOpen

  const connectId = crypto?.randomUUID?.() ?? String(Date.now())
  ws.send(JSON.stringify({
    type: 'req',
    id: connectId,
    method: 'connect',
    params: {
      minProtocol: 3,
      maxProtocol: 3,
      client: {
        id: 'webchat-ui',
        displayName: 'Astron RPA',
        version: 'web-app',
        platform: 'web',
        mode: 'ui',
      },
      role: 'operator',
      scopes: ['operator.read', 'operator.write'],
      caps: ['tool-events'],
      auth: params.token ? { token: params.token } : undefined,
      userAgent: navigator.userAgent,
      locale: navigator.language,
    },
  } satisfies WsReqFrame))

  await waitForRes(connectId)

  const sendId = crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`
  let latestText = ''
  const toolEvents: OpenClawToolEvent[] = []
  const seenToolEventKeys = new Set<string>()

  const pushToolEvent = (event: OpenClawToolEvent) => {
    const key = [
      event.toolCallId,
      event.phase,
      event.name,
      stringifyToolOutput(event.args) ?? '',
      event.output ?? '',
      String(event.ts),
    ].join('::')

    if (seenToolEventKeys.has(key))
      return

    seenToolEventKeys.add(key)
    toolEvents.push(event)
    params.onToolEvent?.(event)
  }

  const finalResult = new Promise<OpenClawChatResult>((resolve, reject) => {
    const onMessage = (ev: MessageEvent) => {
      let frame: WsFrame | null = null

      try {
        frame = JSON.parse(String(ev.data ?? '')) as WsFrame
      }
      catch {
        return
      }

      if (frame.type === 'event') {
        const streamEvent = normalizeToolStream(frame)
        if (streamEvent?.stream === 'tool') {
          const data = streamEvent.data ?? {}
          const toolCallId = typeof data.toolCallId === 'string' ? data.toolCallId : ''
          const phase = typeof data.phase === 'string' ? data.phase : ''

          if (toolCallId && (phase === 'start' || phase === 'update' || phase === 'result')) {
            pushToolEvent({
              toolCallId,
              runId: typeof streamEvent.runId === 'string' ? streamEvent.runId : undefined,
              name: typeof data.name === 'string' ? data.name : 'tool',
              phase,
              args: phase === 'start' ? data.args : undefined,
              output: phase === 'update'
                ? stringifyToolOutput(data.partialResult)
                : phase === 'result'
                  ? stringifyToolOutput(data.result)
                  : undefined,
              ts: typeof streamEvent.ts === 'number' ? streamEvent.ts : Date.now(),
            })
          }

          return
        }

        if (frame.event === 'chat') {
          const state = frame.payload?.state
          const message = frame.payload?.message
          const text = extractTextFromMessage(message)

          if (text)
            latestText = text

          if (state === 'final') {
            for (const event of extractToolEventsFromMessage(message, Date.now()))
              pushToolEvent(event)

            cleanup()
            resolve({
              text: latestText || '(openclaw returned no content)',
              toolEvents,
            })
            return
          }

          if (state === 'error') {
            cleanup()
            reject(new Error(frame.payload?.errorMessage || 'openclaw execution failed'))
          }
        }
      }

      if (frame.type === 'res' && frame.id === sendId && frame.ok === false) {
        cleanup()
        reject(new Error(frame?.error?.message || 'openclaw chat.send failed'))
      }
    }

    const onClose = () => {
      cleanup()
      reject(new Error('openclaw gateway connection closed'))
    }

    const cleanup = () => {
      ws.removeEventListener('message', onMessage)
      ws.removeEventListener('close', onClose)

      try {
        ws.close()
      }
      catch {
        // ignore close errors
      }
    }

    ws.addEventListener('message', onMessage)
    ws.addEventListener('close', onClose)
  })

  ws.send(JSON.stringify({
    type: 'req',
    id: sendId,
    method: 'chat.send',
    params: {
      sessionKey: params.sessionKey ?? 'main',
      message: params.text,
      deliver: false,
      idempotencyKey: sendId,
    },
  } satisfies WsReqFrame))

  return await finalResult
}

export async function openclawChatCompletions(params: {
  messages: OpenClawChatMessage[]
  model?: string
  token?: string
  onToolEvent?: (event: OpenClawToolEvent) => void
}): Promise<OpenClawChatResult> {
  const lastUser = [...params.messages].reverse().find(m => m.role === 'user')?.content ?? ''
  return await openclawChatViaWs({
    text: lastUser,
    token: params.token,
    onToolEvent: params.onToolEvent,
  })
}
