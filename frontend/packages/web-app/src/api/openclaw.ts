import { getDirectOpenClawGatewayWsUrl, getOpenClawProxyWsUrl } from './runtime'
import { extractTextFromOpenClawMessage } from './openclaw-message'

export interface OpenClawChatMessage {
  role: 'system' | 'developer' | 'user' | 'assistant' | 'tool'
  content: string
}

export interface OpenClawChatAttachment {
  type: 'image'
  mimeType: string
  fileName?: string
  content: string
}

export interface OpenClawToolEvent {
  toolCallId: string
  runId?: string
  name: string
  phase: 'start' | 'update' | 'result'
  args?: unknown
  output?: string
  ts: number
}

export interface OpenClawChatResult {
  text: string
  toolEvents: OpenClawToolEvent[]
}

export interface OpenClawDeleteSessionResult {
  ok: boolean
  key?: string
  deleted?: boolean
  archived?: unknown[]
}

export interface OpenClawGatewayConnection {
  ws: WebSocket
  request<T = unknown>(method: string, params?: unknown, timeoutMs?: number): Promise<T>
  close(): void
}

interface OpenClawDeviceIdentity {
  version: 1
  deviceId: string
  publicKey: string
  privateKey: string
  createdAtMs: number
}

interface OpenClawStoredDeviceToken {
  token: string
  scopes: string[]
  updatedAtMs: number
}

interface WsReqFrame {
  type: 'req'
  id: string
  method: string
  params?: any
}

interface WsResFrame {
  type: 'res'
  id: string
  ok: boolean
  payload?: any
  error?: { code?: string, message?: string, details?: any }
}

interface WsEventFrame {
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

interface StreamEvent {
  stream?: string
  runId?: string
  sessionKey?: string
  ts?: number
  data?: Record<string, any>
}

interface MessageContentBlock {
  type?: string
  text?: string
  content?: string
  name?: string
  arguments?: unknown
  args?: unknown
}

interface ElectronOpenClawBridge {
  getToken?: () => Promise<string | undefined>
  readLocalFile?: (params: {
    path: string
    mode: 'text' | 'data-url'
  }) => Promise<{
    textContent?: string
    dataUrl?: string
    mimeType?: string
    base64?: string
  } | undefined>
  getDeviceIdentity?: () => Promise<
    { deviceId: string, publicKey: string } | undefined
  >
  signDevicePayload?: (payload: string) => Promise<string | undefined>
  getDeviceToken?: (
    role?: string,
  ) => Promise<{ token: string, scopes?: string[] } | undefined>
  storeDeviceToken?: (params: {
    role?: string
    token: string
    scopes?: string[]
  }) => Promise<boolean>
  approveDeviceRequest?: (requestId: string) => Promise<boolean>
  chatCompletions?: (params: {
    messages: OpenClawChatMessage[]
    sessionKey?: string
    attachments?: OpenClawChatAttachment[]
    allowCliFallback?: boolean
  }) => Promise<OpenClawChatResult>
}

const OPENCLAW_CLIENT_ID = 'openclaw-control-ui'
const OPENCLAW_CLIENT_MODE = 'webchat'
// Match the official OpenClaw control UI scope set so control actions like
// `sessions.delete` can be authorized through the same gateway connection.
const OPENCLAW_SCOPES = [
  'operator.admin',
  'operator.approvals',
  'operator.pairing',
] as const
const OPENCLAW_CAPS = ['tool-events'] as const
const OPENCLAW_CONNECT_TIMEOUT_MS = 5000
const OPENCLAW_REQUEST_TIMEOUT_MS = 5000
const OPENCLAW_DEVICE_IDENTITY_KEY = 'astron.openclaw.deviceIdentity.v1'
const OPENCLAW_DEVICE_TOKEN_KEY = 'astron.openclaw.deviceToken.v1'

function logOpenClawTransport(
  message: string,
  extra?: Record<string, unknown>,
) {
  if (extra)
    console.info('[OpenClaw][transport]', message, extra)
  else console.info('[OpenClaw][transport]', message)
}

function getElectronOpenClawBridge(): ElectronOpenClawBridge | undefined {
  return (window as any)?.electron?.openclaw
}

function shouldUseElectronChatBridge() {
  if ((window as any)?.electron)
    return false

  return true
}

function closeOpenClawSocket(ws: WebSocket) {
  try {
    ws.close()
  }
  catch {
    // ignore close errors
  }
}

function wsUrlForOpenClawProxy(): string {
  return getOpenClawProxyWsUrl()
}

function getDefaultChatWsUrls(): string[] {
  const directUrl = getDirectOpenClawGatewayWsUrl()
  const proxyUrl = getOpenClawProxyWsUrl()

  if ((window as any)?.electron)
    return [directUrl, proxyUrl]

  if (window.location.protocol === 'rpa:' || window.location.protocol === 'file:')
    return [directUrl, proxyUrl]

  return [proxyUrl, directUrl]
}

function toBase64Url(bytes: Uint8Array): string {
  let binary = ''
  for (const byte of bytes) binary += String.fromCharCode(byte)

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
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i)
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
  return bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  ) as ArrayBuffer
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
      if (
        parsed?.version === 1
        && parsed.deviceId
        && parsed.publicKey
        && parsed.privateKey
      ) {
        return parsed
      }
    }
    catch {
      // fall through to regenerate identity
    }
  }

  const keyPair = await crypto.subtle.generateKey({ name: 'Ed25519' }, true, [
    'sign',
    'verify',
  ])

  const publicKeyRaw = new Uint8Array(
    await crypto.subtle.exportKey('raw', keyPair.publicKey),
  )
  const privateKeyPkcs8 = new Uint8Array(
    await crypto.subtle.exportKey('pkcs8', keyPair.privateKey),
  )
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

async function signDevicePayload(
  identity: OpenClawDeviceIdentity,
  payload: string,
): Promise<string> {
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

function loadStoredDeviceToken(
  deviceId: string,
  role: string,
): OpenClawStoredDeviceToken | null {
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
    const parsed = JSON.parse(raw) as Record<
      string,
      Record<string, OpenClawStoredDeviceToken>
    >
    const token = parsed?.[deviceId]?.[role]
    if (token?.token)
      return token
  }
  catch {
    // ignore invalid storage
  }

  return null
}

async function getStoredDeviceToken(
  deviceId: string,
  role: string,
): Promise<OpenClawStoredDeviceToken | null> {
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

async function storeDeviceToken(
  deviceId: string,
  role: string,
  token: string,
  scopes: string[] | undefined,
) {
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
      nextStore = JSON.parse(raw) as Record<
        string,
        Record<string, OpenClawStoredDeviceToken>
      >
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

  if (
    frame.event === 'agent'
    && frame.payload
    && typeof frame.payload === 'object'
  ) {
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
  return extractTextFromOpenClawMessage(message)
}

function extractToolEventsFromMessage(
  message: any,
  fallbackTs: number,
): OpenClawToolEvent[] {
  if (
    !message
    || typeof message !== 'object'
    || !Array.isArray(message.content)
  ) {
    return []
  }

  const timestamp
    = typeof message.timestamp === 'number' ? message.timestamp : fallbackTs
  const runId = typeof message.runId === 'string' ? message.runId : undefined
  const messageToolCallId
    = typeof message.toolCallId === 'string' ? message.toolCallId : ''
  const blocks = message.content as MessageContentBlock[]

  const callEvents = blocks
    .map((item, index) => {
      const type
        = typeof item?.type === 'string' ? item.type.toLowerCase() : ''
      const isToolCall
        = ['toolcall', 'tool_call', 'tooluse', 'tool_use'].includes(type)
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
      const type
        = typeof item?.type === 'string' ? item.type.toLowerCase() : ''
      if (type !== 'toolresult' && type !== 'tool_result')
        return null

      const matchingCall = callEvents.find(call => call.name === item.name)
      return {
        toolCallId:
          matchingCall?.toolCallId
          || messageToolCallId
          || `${runId ?? 'tool'}:result:${index}`,
        runId,
        name:
          typeof item.name === 'string'
            ? item.name
            : (matchingCall?.name ?? 'tool'),
        phase: 'result' as const,
        output:
          typeof item.text === 'string'
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

function summarizeOpenClawMessage(message: any) {
  if (!message || typeof message !== 'object') {
    return {
      kind: typeof message,
      text: '',
      textLength: 0,
      contentType: typeof message?.content,
      contentBlockTypes: [] as string[],
    }
  }

  const extractedText = extractTextFromMessage(message)
  const content = message.content
  return {
    role: typeof message.role === 'string' ? message.role : undefined,
    text: extractedText,
    textLength: extractedText.length,
    hasTextField:
      typeof message.text === 'string' && message.text.trim().length > 0,
    contentType: Array.isArray(content) ? 'array' : typeof content,
    contentBlockTypes: Array.isArray(content)
      ? content
          .map((item) =>
            item && typeof item === 'object' && typeof item.type === 'string'
              ? item.type
              : typeof item,
          )
          .slice(0, 12)
      : [],
  }
}

async function loadLatestAssistantTextFromHistory(
  connection: OpenClawGatewayConnection,
  sessionKey: string,
): Promise<string> {
  const payload = await connection.request<{ messages?: unknown[] }>(
    'chat.history',
    {
      sessionKey,
      limit: 50,
    },
  )

  const messages = Array.isArray(payload?.messages) ? payload.messages : []
  const latestAssistantMessage = [...messages]
    .reverse()
    .find((message) => {
      if (!message || typeof message !== 'object')
        return false
      return typeof (message as Record<string, unknown>).role === 'string'
        && (message as Record<string, unknown>).role === 'assistant'
    })

  const text = extractTextFromMessage(latestAssistantMessage)
  logOpenClawTransport('chat.history fallback resolved', {
    sessionKey,
    messageCount: messages.length,
    textLength: text.length,
    summary: summarizeOpenClawMessage(latestAssistantMessage),
  })
  return text
}

function createOpenClawGatewayRequest(ws: WebSocket) {
  return async function request<T = unknown>(
    method: string,
    params?: unknown,
    timeoutMs: number = OPENCLAW_REQUEST_TIMEOUT_MS,
  ): Promise<T> {
    const requestId = crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`

    return await new Promise<T>((resolve, reject) => {
      const timeout = window.setTimeout(() => {
        cleanup()
        closeOpenClawSocket(ws)
        reject(new Error(`openclaw ${method} request timed out`))
      }, timeoutMs)

      const cleanup = () => {
        window.clearTimeout(timeout)
        ws.removeEventListener('message', onMessage)
        ws.removeEventListener('close', onClose)
      }

      const onClose = () => {
        cleanup()
        reject(new Error('openclaw gateway connection closed'))
      }

      const onMessage = (ev: MessageEvent) => {
        let frame: WsFrame | null = null

        try {
          frame = JSON.parse(String(ev.data ?? '')) as WsFrame
        }
        catch {
          return
        }

        if (frame.type !== 'res' || frame.id !== requestId)
          return

        cleanup()
        if (!frame.ok) {
          reject(new Error(frame?.error?.message || `openclaw ${method} failed`))
          return
        }

        resolve(frame.payload as T)
      }

      ws.addEventListener('message', onMessage)
      ws.addEventListener('close', onClose)
      ws.send(
        JSON.stringify({
          type: 'req',
          id: requestId,
          method,
          params,
        } satisfies WsReqFrame),
      )
    })
  }
}

export async function connectOpenClawGateway(params?: {
  token?: string
  wsUrl?: string
  connectTimeoutMs?: number
}): Promise<OpenClawGatewayConnection> {
  return await connectOpenClawGatewayInternal(params, false)
}

async function connectOpenClawGatewayInternal(
  params: {
    token?: string
    wsUrl?: string
    connectTimeoutMs?: number
  } | undefined,
  pairingRetried: boolean,
): Promise<OpenClawGatewayConnection> {
  const ws = new WebSocket(params?.wsUrl || wsUrlForOpenClawProxy())
  const connectTimeoutMs = params?.connectTimeoutMs ?? OPENCLAW_CONNECT_TIMEOUT_MS
  let sawChallenge = false
  let sentConnect = false

  const awaitOpen = new Promise<void>((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      ws.removeEventListener('open', onOpen)
      ws.removeEventListener('error', onError)
      reject(new Error('Unable to connect to openclaw gateway.'))
    }, connectTimeoutMs)

    const onOpen = () => {
      window.clearTimeout(timeout)
      ws.removeEventListener('error', onError)
      logOpenClawTransport('gateway websocket opened', {
        wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
      })
      resolve()
    }

    const onError = () => {
      window.clearTimeout(timeout)
      ws.removeEventListener('open', onOpen)
      reject(new Error('Unable to connect to openclaw gateway.'))
    }

    ws.addEventListener('open', onOpen, { once: true })
    ws.addEventListener('error', onError, { once: true })
  })

  await awaitOpen

  const role = 'operator'
  const connectId = crypto?.randomUUID?.() ?? String(Date.now())
  let identity: OpenClawDeviceIdentity | null = null

  const connectReady = new Promise<void>((resolve, reject) => {
    let settled = false
    const timeout = window.setTimeout(() => {
      cleanup()
      logOpenClawTransport('gateway connect stage timed out', {
        wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
        sawChallenge,
        sentConnect,
      })
      reject(new Error('openclaw gateway connect challenge timeout'))
    }, connectTimeoutMs)

    const cleanup = () => {
      if (settled)
        return
      settled = true
      window.clearTimeout(timeout)
      ws.removeEventListener('message', onMessage)
      ws.removeEventListener('close', onClose)
    }

    const onClose = () => {
      logOpenClawTransport('gateway websocket closed during connect stage', {
        wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
        sawChallenge,
        sentConnect,
      })
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
        sawChallenge = true
        const nonce
          = typeof frame.payload?.nonce === 'string'
            ? frame.payload.nonce.trim()
            : ''
        logOpenClawTransport('gateway connect challenge received', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          hasNonce: Boolean(nonce),
        })
        if (!nonce) {
          cleanup()
          reject(new Error('openclaw gateway connect challenge missing nonce'))
          return
        }

        logOpenClawTransport('gateway loading device identity', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
        })
        identity = await loadOrCreateDeviceIdentity()
        logOpenClawTransport('gateway device identity ready', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          deviceId: identity.deviceId,
          hasBridgeKey: identity.privateKey === '',
        })
        const latestStoredDeviceToken = (
          await getStoredDeviceToken(identity.deviceId, role)
        )?.token
        logOpenClawTransport('gateway device token resolved', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          hasGatewayToken: Boolean(params?.token),
          hasStoredDeviceToken: Boolean(latestStoredDeviceToken),
        })

        const signedAtMs = Date.now()
        const signatureToken = params?.token || latestStoredDeviceToken || undefined
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
        logOpenClawTransport('gateway signing device payload', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          payloadLength: payload.length,
        })
        const signature = await signDevicePayload(identity, payload)
        logOpenClawTransport('gateway device payload signed', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          signatureLength: signature.length,
        })

        ws.send(
          JSON.stringify({
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
              auth:
                params?.token || latestStoredDeviceToken
                  ? {
                      token: params?.token,
                      deviceToken: latestStoredDeviceToken,
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
          } satisfies WsReqFrame),
        )
        sentConnect = true
        logOpenClawTransport('gateway connect request sent', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          hasGatewayToken: Boolean(params?.token),
          hasStoredDeviceToken: Boolean(latestStoredDeviceToken),
        })
        return
      }

      if (frame.type === 'res' && frame.id === connectId) {
        logOpenClawTransport('gateway connect response received', {
          wsUrl: params?.wsUrl || wsUrlForOpenClawProxy(),
          ok: frame.ok,
          error: frame.ok ? undefined : frame?.error?.message,
          errorCode: frame.ok ? undefined : frame?.error?.code,
          detailCode:
            frame.ok ? undefined : frame?.error?.details?.code,
        })
        cleanup()
        if (!frame.ok) {
          const requestId
            = typeof frame?.error?.details?.requestId === 'string'
              ? frame.error.details.requestId
              : ''
          const detailCode
            = typeof frame?.error?.details?.code === 'string'
              ? frame.error.details.code
              : ''
          const electronBridge = getElectronOpenClawBridge()

          if (
            !pairingRetried
            && detailCode === 'PAIRING_REQUIRED'
            && requestId
            && electronBridge?.approveDeviceRequest
          ) {
            try {
              const approved = await electronBridge.approveDeviceRequest(requestId)
              if (approved) {
                closeOpenClawSocket(ws)
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

  if (!pairingRetried && identity) {
    const electronBridge = getElectronOpenClawBridge()
    if (electronBridge?.approveDeviceRequest) {
      const latestToken = await getStoredDeviceToken(identity.deviceId, role)
      if (!latestToken && identity.privateKey === '')
        return await connectOpenClawGatewayInternal(params, true)
    }
  }

  return {
    ws,
    request: createOpenClawGatewayRequest(ws),
    close: () => closeOpenClawSocket(ws),
  }
}

async function openclawChatViaWs(params: {
  text: string
  token?: string
  sessionKey?: string
  wsUrl?: string
  attachments?: OpenClawChatAttachment[]
  onToolEvent?: (event: OpenClawToolEvent) => void
}): Promise<OpenClawChatResult> {
  const candidateUrls = params.wsUrl
    ? [params.wsUrl]
    : getDefaultChatWsUrls()
  let lastError: unknown

  for (const wsUrl of candidateUrls) {
    try {
      logOpenClawTransport('chat websocket attempt started', {
        wsUrl,
        sessionKey: params.sessionKey ?? 'main',
      })
      return await openclawChatViaWsInternal({
        ...params,
        wsUrl,
      })
    }
    catch (error) {
      lastError = error
      logOpenClawTransport('chat websocket attempt failed', {
        wsUrl,
        sessionKey: params.sessionKey ?? 'main',
        error: error instanceof Error ? error.message : String(error),
      })
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error('Unable to connect to openclaw gateway.')
}

async function openclawChatViaWsInternal(
  params: {
    text: string
    token?: string
    sessionKey?: string
    wsUrl?: string
    attachments?: OpenClawChatAttachment[]
    onToolEvent?: (event: OpenClawToolEvent) => void
  },
): Promise<OpenClawChatResult> {
  const connection = await connectOpenClawGateway({
    token: params.token,
    wsUrl: params.wsUrl,
  })
  const { ws } = connection

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
    const onMessage = async (ev: MessageEvent) => {
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
          const toolCallId
            = typeof data.toolCallId === 'string' ? data.toolCallId : ''
          const phase = typeof data.phase === 'string' ? data.phase : ''

          if (
            toolCallId
            && (phase === 'start' || phase === 'update' || phase === 'result')
          ) {
            pushToolEvent({
              toolCallId,
              runId:
                typeof streamEvent.runId === 'string'
                  ? streamEvent.runId
                  : undefined,
              name: typeof data.name === 'string' ? data.name : 'tool',
              phase,
              args: phase === 'start' ? data.args : undefined,
              output:
                phase === 'update'
                  ? stringifyToolOutput(data.partialResult)
                  : phase === 'result'
                    ? stringifyToolOutput(data.result)
                    : undefined,
              ts:
                typeof streamEvent.ts === 'number'
                  ? streamEvent.ts
                  : Date.now(),
            })
          }

          return
        }

        if (frame.event === 'chat') {
          const state = frame.payload?.state
          const message = frame.payload?.message
          const text = extractTextFromMessage(message)

          logOpenClawTransport('chat event received', {
            state,
            runId:
              typeof frame.payload?.runId === 'string'
                ? frame.payload.runId
                : undefined,
            summary: summarizeOpenClawMessage(message),
          })

          if (text)
            latestText = text

          if (state === 'final') {
            for (const event of extractToolEventsFromMessage(
              message,
              Date.now(),
            ))
              pushToolEvent(event)

            if (!latestText) {
              logOpenClawTransport('chat final resolved without extracted text', {
                state,
                latestText,
                payloadKeys:
                  frame.payload && typeof frame.payload === 'object'
                    ? Object.keys(frame.payload)
                    : [],
                messageSummary: summarizeOpenClawMessage(message),
                rawMessage: message,
              })

              try {
                latestText = await loadLatestAssistantTextFromHistory(
                  connection,
                  params.sessionKey ?? 'main',
                )
              }
              catch (historyError) {
                logOpenClawTransport('chat.history fallback failed', {
                  sessionKey: params.sessionKey ?? 'main',
                  error:
                    historyError instanceof Error
                      ? historyError.message
                      : String(historyError),
                })
              }
            }

            cleanup()
            resolve({
              text: latestText || '(openclaw returned no content)',
              toolEvents,
            })
            return
          }

          if (state === 'error') {
            cleanup()
            reject(
              new Error(
                frame.payload?.errorMessage || 'openclaw execution failed',
              ),
            )
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
      connection.close()
    }

    ws.addEventListener('message', onMessage)
    ws.addEventListener('close', onClose)
  })

  ws.send(
    JSON.stringify({
      type: 'req',
      id: sendId,
      method: 'chat.send',
      params: {
        sessionKey: params.sessionKey ?? 'main',
        message: params.text,
        deliver: false,
        idempotencyKey: sendId,
        attachments: params.attachments,
      },
    } satisfies WsReqFrame),
  )

  logOpenClawTransport('chat.send dispatched', {
    sessionKey: params.sessionKey ?? 'main',
    hasToken: Boolean(params.token),
    textLength: params.text.trim().length,
  })

  return await finalResult
}

export async function openclawDeleteSession(params: {
  sessionKey: string
  token?: string
  wsUrl?: string
}): Promise<OpenClawDeleteSessionResult> {
  const connection = await connectOpenClawGateway({
    token: params.token,
    wsUrl: params.wsUrl,
  })

  try {
    return await connection.request<OpenClawDeleteSessionResult>(
      'sessions.delete',
      {
        key: params.sessionKey,
      },
    )
  }
  finally {
    connection.close()
  }
}

export async function openclawChatCompletions(params: {
  messages: OpenClawChatMessage[]
  model?: string
  token?: string
  sessionKey?: string
  attachments?: OpenClawChatAttachment[]
  onToolEvent?: (event: OpenClawToolEvent) => void
}): Promise<OpenClawChatResult> {
  const requestId = crypto?.randomUUID?.() ?? `openclaw-${Date.now()}`
  const startedAt = Date.now()
  const electronBridge = getElectronOpenClawBridge()
  const lastUser
    = [...params.messages].reverse().find(m => m.role === 'user')?.content
      ?? ''

  if (
    shouldUseElectronChatBridge()
    && electronBridge?.chatCompletions
    && !params.attachments?.length
  ) {
    logOpenClawTransport('chat request started via electron bridge', {
      requestId,
      transport: 'electron-ipc',
    })

    try {
      const result = await electronBridge.chatCompletions({
        messages: params.messages,
        sessionKey: params.sessionKey,
        attachments: params.attachments,
        allowCliFallback: false,
      })
      logOpenClawTransport('chat request completed via electron bridge', {
        requestId,
        transport: 'electron-ipc',
        durationMs: Date.now() - startedAt,
        toolEventCount: result.toolEvents.length,
      })
      for (const event of result.toolEvents) params.onToolEvent?.(event)
      return result
    }
    catch (error) {
      logOpenClawTransport('chat request failed via electron bridge', {
        requestId,
        transport: 'electron-ipc',
        durationMs: Date.now() - startedAt,
        error: error instanceof Error ? error.message : String(error),
      })
      logOpenClawTransport('falling back to websocket after electron bridge failure', {
        requestId,
        transport: 'websocket',
      })
    }
  }

  logOpenClawTransport('chat request started via websocket', {
    requestId,
    transport: 'websocket',
  })

  try {
    const result = await openclawChatViaWs({
      text: lastUser,
      token: params.token,
      sessionKey: params.sessionKey,
      attachments: params.attachments,
      onToolEvent: params.onToolEvent,
    })
    logOpenClawTransport('chat request completed via websocket', {
      requestId,
      transport: 'websocket',
      durationMs: Date.now() - startedAt,
      toolEventCount: result.toolEvents.length,
    })
    return result
  }
  catch (error) {
    logOpenClawTransport('chat request failed via websocket', {
      requestId,
      transport: 'websocket',
      durationMs: Date.now() - startedAt,
      error: error instanceof Error ? error.message : String(error),
    })
    throw error
  }
}
