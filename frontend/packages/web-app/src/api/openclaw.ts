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

type OpenClawDeviceIdentity = {
  version: 1
  deviceId: string
  publicKey: string
  privateKey: string
  createdAtMs: number
}

type OpenClawStoredDeviceToken = {
  token: string
  scopes: string[]
  updatedAtMs: number
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

type ElectronOpenClawBridge = {
  getToken?: () => Promise<string | undefined>
  getDeviceIdentity?: () => Promise<{ deviceId: string, publicKey: string } | undefined>
  signDevicePayload?: (payload: string) => Promise<string | undefined>
  getDeviceToken?: (role?: string) => Promise<{ token: string, scopes?: string[] } | undefined>
  storeDeviceToken?: (params: { role?: string, token: string, scopes?: string[] }) => Promise<boolean>
  approveDeviceRequest?: (requestId: string) => Promise<boolean>
  chatCompletions?: (params: { messages: OpenClawChatMessage[] }) => Promise<OpenClawChatResult>
}

const OPENCLAW_CLIENT_ID = 'openclaw-control-ui'
const OPENCLAW_CLIENT_MODE = 'webchat'
const OPENCLAW_SCOPES = ['operator.read', 'operator.write'] as const
const OPENCLAW_CAPS = ['tool-events'] as const
const OPENCLAW_CONNECT_TIMEOUT_MS = 5000
const OPENCLAW_DEVICE_IDENTITY_KEY = 'astron.openclaw.deviceIdentity.v1'
const OPENCLAW_DEVICE_TOKEN_KEY = 'astron.openclaw.deviceToken.v1'

function getElectronOpenClawBridge(): ElectronOpenClawBridge | undefined {
  return (window as any)?.electron?.openclaw
}

function wsUrlForOpenClawProxy(): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/openclaw`
}

function toBase64Url(bytes: Uint8Array): string {
  let binary = ''
  for (const byte of bytes)
    binary += String.fromCharCode(byte)

  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '')
}

function fromBase64Url(input: string): Uint8Array {
  const normalized = input
    .replace(/-/g, '+')
    .replace(/_/g, '/')
    .padEnd(Math.ceil(input.length / 4) * 4, '=')
  const binary = atob(normalized)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i += 1)
    bytes[i] = binary.charCodeAt(i)
  return bytes
}

function getOpenClawStorage(): Storage | null {
  try {
    return window.localStorage
  }
  catch {
    return null
  }
}

function normalizeDeviceMetadata(value: string | undefined): string {
  return value?.trim().toLowerCase() ?? ''
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer
}

async function sha256Hex(input: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', toArrayBuffer(input))
  return [...new Uint8Array(digest)]
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('')
}

async function loadOrCreateDeviceIdentity(): Promise<OpenClawDeviceIdentity> {
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.getDeviceIdentity) {
    const identity = await electronBridge.getDeviceIdentity()
    if (identity?.deviceId && identity?.publicKey) {
      return {
        version: 1,
        deviceId: identity.deviceId,
        publicKey: identity.publicKey,
        privateKey: '',
        createdAtMs: Date.now(),
      }
    }
  }

  const storage = getOpenClawStorage()
  const raw = storage?.getItem(OPENCLAW_DEVICE_IDENTITY_KEY)

  if (raw) {
    try {
      const parsed = JSON.parse(raw) as OpenClawDeviceIdentity
      if (parsed?.version === 1 && parsed.deviceId && parsed.publicKey && parsed.privateKey)
        return parsed
    }
    catch {
      // fall through to regenerate identity
    }
  }

  const keyPair = await crypto.subtle.generateKey(
    { name: 'Ed25519' },
    true,
    ['sign', 'verify'],
  )

  const publicKeyRaw = new Uint8Array(await crypto.subtle.exportKey('raw', keyPair.publicKey))
  const privateKeyPkcs8 = new Uint8Array(await crypto.subtle.exportKey('pkcs8', keyPair.privateKey))
  const identity: OpenClawDeviceIdentity = {
    version: 1,
    deviceId: await sha256Hex(publicKeyRaw),
    publicKey: toBase64Url(publicKeyRaw),
    privateKey: toBase64Url(privateKeyPkcs8),
    createdAtMs: Date.now(),
  }

  storage?.setItem(OPENCLAW_DEVICE_IDENTITY_KEY, JSON.stringify(identity))
  return identity
}

async function signDevicePayload(identity: OpenClawDeviceIdentity, payload: string): Promise<string> {
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.signDevicePayload) {
    const signature = await electronBridge.signDevicePayload(payload)
    if (!signature)
      throw new Error('Failed to sign OpenClaw device payload')
    return signature
  }

  const privateKey = await crypto.subtle.importKey(
    'pkcs8',
    toArrayBuffer(fromBase64Url(identity.privateKey)),
    { name: 'Ed25519' },
    false,
    ['sign'],
  )
  const signature = await crypto.subtle.sign(
    { name: 'Ed25519' },
    privateKey,
    toArrayBuffer(new TextEncoder().encode(payload)),
  )
  return toBase64Url(new Uint8Array(signature))
}

function buildDeviceAuthPayload(params: {
  deviceId: string
  clientId: string
  clientMode: string
  role: string
  scopes: readonly string[]
  signedAtMs: number
  token?: string
  nonce: string
  platform: string
  deviceFamily?: string
}): string {
  return [
    'v3',
    params.deviceId,
    params.clientId,
    params.clientMode,
    params.role,
    params.scopes.join(','),
    String(params.signedAtMs),
    params.token ?? '',
    params.nonce,
    normalizeDeviceMetadata(params.platform),
    normalizeDeviceMetadata(params.deviceFamily),
  ].join('|')
}

function loadStoredDeviceToken(deviceId: string, role: string): OpenClawStoredDeviceToken | null {
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.getDeviceToken) {
    // Electron path uses the official OpenClaw device-auth store in main process.
    return null
  }

  const storage = getOpenClawStorage()
  const raw = storage?.getItem(OPENCLAW_DEVICE_TOKEN_KEY)
  if (!raw)
    return null

  try {
    const parsed = JSON.parse(raw) as Record<string, Record<string, OpenClawStoredDeviceToken>>
    const token = parsed?.[deviceId]?.[role]
    if (token?.token)
      return token
  }
  catch {
    // ignore invalid storage
  }

  return null
}

async function getStoredDeviceToken(deviceId: string, role: string): Promise<OpenClawStoredDeviceToken | null> {
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.getDeviceToken) {
    const token = await electronBridge.getDeviceToken(role)
    if (token?.token) {
      return {
        token: token.token,
        scopes: Array.isArray(token.scopes) ? token.scopes : [],
        updatedAtMs: Date.now(),
      }
    }
    return null
  }

  return loadStoredDeviceToken(deviceId, role)
}

async function storeDeviceToken(deviceId: string, role: string, token: string, scopes: string[] | undefined) {
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.storeDeviceToken) {
    await electronBridge.storeDeviceToken({ role, token, scopes })
    return
  }

  const storage = getOpenClawStorage()
  if (!storage || !token)
    return

  let nextStore: Record<string, Record<string, OpenClawStoredDeviceToken>> = {}
  const raw = storage.getItem(OPENCLAW_DEVICE_TOKEN_KEY)

  if (raw) {
    try {
      nextStore = JSON.parse(raw) as Record<string, Record<string, OpenClawStoredDeviceToken>>
    }
    catch {
      nextStore = {}
    }
  }

  nextStore[deviceId] ??= {}
  nextStore[deviceId][role] = {
    token,
    scopes: Array.isArray(scopes) ? scopes : [],
    updatedAtMs: Date.now(),
  }
  storage.setItem(OPENCLAW_DEVICE_TOKEN_KEY, JSON.stringify(nextStore))
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
  return await openclawChatViaWsInternal(params, false)
}

async function openclawChatViaWsInternal(params: {
  text: string
  token?: string
  sessionKey?: string
  onToolEvent?: (event: OpenClawToolEvent) => void
}, pairingRetried: boolean): Promise<OpenClawChatResult> {
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

  const role = 'operator'
  const identity = await loadOrCreateDeviceIdentity()
  const storedDeviceToken = (await getStoredDeviceToken(identity.deviceId, role))?.token
  const connectId = crypto?.randomUUID?.() ?? String(Date.now())

  const connectReady = new Promise<void>((resolve, reject) => {
    let settled = false
    const timeout = window.setTimeout(() => {
      cleanup()
      reject(new Error('openclaw gateway connect challenge timeout'))
    }, OPENCLAW_CONNECT_TIMEOUT_MS)

    const cleanup = () => {
      if (settled)
        return
      settled = true
      window.clearTimeout(timeout)
      ws.removeEventListener('message', onMessage)
      ws.removeEventListener('close', onClose)
    }

    const onClose = () => {
      cleanup()
      reject(new Error('openclaw gateway connection closed'))
    }

    const onMessage = async (ev: MessageEvent) => {
      let frame: WsFrame | null = null

      try {
        frame = JSON.parse(String(ev.data ?? '')) as WsFrame
      }
      catch {
        return
      }

      if (frame.type === 'event' && frame.event === 'connect.challenge') {
        const nonce = typeof frame.payload?.nonce === 'string' ? frame.payload.nonce.trim() : ''
        if (!nonce) {
          cleanup()
          reject(new Error('openclaw gateway connect challenge missing nonce'))
          return
        }

        const signedAtMs = Date.now()
        const signatureToken = params.token || storedDeviceToken || undefined
        const payload = buildDeviceAuthPayload({
          deviceId: identity.deviceId,
          clientId: OPENCLAW_CLIENT_ID,
          clientMode: OPENCLAW_CLIENT_MODE,
          role,
          scopes: OPENCLAW_SCOPES,
          signedAtMs,
          token: signatureToken,
          nonce,
          platform: 'web',
          deviceFamily: 'browser',
        })
        const signature = await signDevicePayload(identity, payload)

        ws.send(JSON.stringify({
          type: 'req',
          id: connectId,
          method: 'connect',
          params: {
            minProtocol: 3,
            maxProtocol: 3,
            client: {
              id: OPENCLAW_CLIENT_ID,
              displayName: 'Astron RPA',
              version: 'web-app',
              platform: 'web',
              deviceFamily: 'browser',
              mode: OPENCLAW_CLIENT_MODE,
            },
            role,
            scopes: OPENCLAW_SCOPES,
            caps: OPENCLAW_CAPS,
            auth: params.token || storedDeviceToken
              ? {
                  token: params.token,
                  deviceToken: storedDeviceToken,
                }
              : undefined,
            device: {
              id: identity.deviceId,
              publicKey: identity.publicKey,
              signature,
              signedAt: signedAtMs,
              nonce,
            },
          },
        } satisfies WsReqFrame))
        return
      }

      if (frame.type === 'res' && frame.id === connectId) {
        cleanup()
        if (!frame.ok) {
          const requestId = typeof frame?.error?.details?.requestId === 'string' ? frame.error.details.requestId : ''
          const detailCode = typeof frame?.error?.details?.code === 'string' ? frame.error.details.code : ''
          const electronBridge = getElectronOpenClawBridge()

          if (!pairingRetried && detailCode === 'PAIRING_REQUIRED' && requestId && electronBridge?.approveDeviceRequest) {
            try {
              const approved = await electronBridge.approveDeviceRequest(requestId)
              if (approved) {
                try {
                  ws.close()
                }
                catch {
                  // ignore close errors
                }
                resolve()
                return
              }
            }
            catch {
              // fall through to normal error
            }
          }

          reject(new Error(frame?.error?.message || 'openclaw request failed'))
          return
        }

        const auth = frame.payload?.auth
        if (typeof auth?.deviceToken === 'string' && auth.deviceToken) {
          await storeDeviceToken(
            identity.deviceId,
            typeof auth.role === 'string' && auth.role ? auth.role : role,
            auth.deviceToken,
            Array.isArray(auth.scopes) ? auth.scopes : undefined,
          )
        }
        resolve()
      }
    }

    ws.addEventListener('message', onMessage)
    ws.addEventListener('close', onClose, { once: true })
  })

  await connectReady

  if (!pairingRetried) {
    const electronBridge = getElectronOpenClawBridge()
    if (electronBridge?.approveDeviceRequest) {
      const latestToken = await getStoredDeviceToken(identity.deviceId, role)
      if (!latestToken && identity.privateKey === '') {
        return await openclawChatViaWsInternal(params, true)
      }
    }
  }

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
  const electronBridge = getElectronOpenClawBridge()
  if (electronBridge?.chatCompletions) {
    const result = await electronBridge.chatCompletions({
      messages: params.messages,
    })
    for (const event of result.toolEvents)
      params.onToolEvent?.(event)
    return result
  }

  const lastUser = [...params.messages].reverse().find(m => m.role === 'user')?.content ?? ''
  return await openclawChatViaWs({
    text: lastUser,
    token: params.token,
    onToolEvent: params.onToolEvent,
  })
}
