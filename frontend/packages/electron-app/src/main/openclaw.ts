import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { homedir } from 'node:os'
import { createHash, createPrivateKey, createPublicKey, generateKeyPairSync, sign } from 'node:crypto'
import { execFile, execFileSync } from 'node:child_process'
import { pathToFileURL } from 'node:url'
import { promisify } from 'node:util'
import logger from './log'

export interface OpenClawConfig {
  gateway?: {
    port?: number
    auth?: {
      mode?: string
      token?: string
    }
  }
}

interface OpenClawDeviceIdentity {
  version: 1
  deviceId: string
  publicKeyPem: string
  privateKeyPem: string
  createdAtMs: number
}

interface OpenClawDeviceAuthStore {
  version: 1
  deviceId: string
  tokens?: Record<string, {
    token: string
    role: string
    scopes: string[]
    updatedAtMs: number
  }>
}

export interface OpenClawChatMessage {
  role: 'system' | 'developer' | 'user' | 'assistant' | 'tool'
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

interface OpenClawGatewayClient {
  start: () => void
  stop: () => void
  request: (method: string, params?: unknown, opts?: { expectFinal?: boolean }) => Promise<any>
}

interface OpenClawGatewayClientCtor {
  new (opts: Record<string, unknown>): OpenClawGatewayClient
}

const execFileAsync = promisify(execFile)
let cachedOpenClawCommand: string | null = null
let cachedGatewayClientCtor: Promise<OpenClawGatewayClientCtor> | null = null

function resolveOpenClawDir() {
  return join(homedir(), '.openclaw')
}

function resolveOpenClawCommand() {
  if (cachedOpenClawCommand)
    return cachedOpenClawCommand

  const candidates = [
    join(dirname(process.execPath), 'openclaw.cmd'),
    join(dirname(process.execPath), 'openclaw'),
    'C:\\nvm4w\\nodejs\\openclaw.cmd',
    'C:\\nvm4w\\nodejs\\openclaw',
  ]

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      cachedOpenClawCommand = candidate
      return candidate
    }
  }

  try {
    const resolved = execFileSync('where', ['openclaw'], {
      stdio: 'pipe',
      encoding: 'utf-8',
    })
      .split(/\r?\n/)
      .map(line => line.trim())
      .find(Boolean)

    if (resolved) {
      cachedOpenClawCommand = resolved
      return resolved
    }
  }
  catch {
    // ignore lookup failures and surface a clearer error below
  }

  throw new Error('OpenClaw CLI executable not found')
}

function resolveIdentityPath() {
  return join(resolveOpenClawDir(), 'identity', 'astron-rpa-device.json')
}

function resolveDeviceAuthPath() {
  return join(resolveOpenClawDir(), 'identity', 'astron-rpa-device-auth.json')
}

function base64UrlEncode(buffer: Buffer) {
  return buffer.toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '')
}

function publicKeyRawBase64UrlFromPem(publicKeyPem: string) {
  const publicKey = createPublicKey(publicKeyPem)
  const raw = publicKey.export({ format: 'der', type: 'spki' }) as Buffer
  return base64UrlEncode(raw.subarray(-32))
}

function fingerprintPublicKey(publicKeyPem: string) {
  const publicKey = createPublicKey(publicKeyPem)
  const raw = publicKey.export({ format: 'der', type: 'spki' }) as Buffer
  return createHash('sha256').update(raw.subarray(-32)).digest('hex')
}

function readJsonFile<T>(filePath: string): T | null {
  try {
    const content = readFileSync(filePath, 'utf-8')
    return JSON.parse(content) as T
  }
  catch {
    return null
  }
}

function writeJsonFile(filePath: string, data: unknown) {
  mkdirSync(dirname(filePath), { recursive: true })
  writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, { encoding: 'utf-8', mode: 0o600 })
}

/**
 * 读取 OpenClaw 配置文件
 * 默认路径: ~/.openclaw/openclaw.json
 */
export function readOpenClawConfig(): OpenClawConfig | null {
  try {
    const configPath = join(resolveOpenClawDir(), 'openclaw.json')
    const content = readFileSync(configPath, 'utf-8')
    const config = JSON.parse(content) as OpenClawConfig
    logger.info('OpenClaw config loaded successfully')
    return config
  } catch (error: any) {
    logger.warn(`Failed to read OpenClaw config: ${error?.message || 'unknown error'}`)
    return null
  }
}

/**
 * 从配置中提取 gateway token
 */
export function getOpenClawToken(): string | undefined {
  const config = readOpenClawConfig()
  return config?.gateway?.auth?.token
}

export function loadOrCreateOpenClawDeviceIdentity() {
  const identityPath = resolveIdentityPath()
  const existing = readJsonFile<OpenClawDeviceIdentity>(identityPath)

  if (existing?.version === 1 && existing.deviceId && existing.publicKeyPem && existing.privateKeyPem) {
    return {
      deviceId: existing.deviceId,
      publicKey: publicKeyRawBase64UrlFromPem(existing.publicKeyPem),
    }
  }

  const keyPair = generateKeyPairSync('ed25519')
  const publicKeyPem = keyPair.publicKey.export({ type: 'spki', format: 'pem' }).toString()
  const privateKeyPem = keyPair.privateKey.export({ type: 'pkcs8', format: 'pem' }).toString()
  const deviceId = fingerprintPublicKey(publicKeyPem)
  const created: OpenClawDeviceIdentity = {
    version: 1,
    deviceId,
    publicKeyPem,
    privateKeyPem,
    createdAtMs: Date.now(),
  }
  writeJsonFile(identityPath, created)

  return {
    deviceId,
    publicKey: publicKeyRawBase64UrlFromPem(publicKeyPem),
  }
}

export function signOpenClawDevicePayload(payload: string) {
  const identity = readJsonFile<OpenClawDeviceIdentity>(resolveIdentityPath())
  if (!identity?.privateKeyPem)
    throw new Error('OpenClaw device identity not found')

  const privateKey = createPrivateKey(identity.privateKeyPem)
  return base64UrlEncode(sign(null, Buffer.from(payload, 'utf-8'), privateKey))
}

export function getOpenClawDeviceToken(role = 'operator') {
  const store = readJsonFile<OpenClawDeviceAuthStore>(resolveDeviceAuthPath())
  const token = store?.tokens?.[role]
  if (!token?.token)
    return undefined

  return {
    token: token.token,
    scopes: token.scopes,
  }
}

export function storeOpenClawDeviceToken(params: { role?: string, token: string, scopes?: string[] }) {
  const role = params.role || 'operator'
  const identity = readJsonFile<OpenClawDeviceIdentity>(resolveIdentityPath())
  if (!identity?.deviceId)
    throw new Error('OpenClaw device identity not found')

  const store = readJsonFile<OpenClawDeviceAuthStore>(resolveDeviceAuthPath()) ?? {
    version: 1 as const,
    deviceId: identity.deviceId,
    tokens: {},
  }

  store.deviceId = identity.deviceId
  store.tokens ??= {}
  store.tokens[role] = {
    token: params.token,
    role,
    scopes: params.scopes ?? [],
    updatedAtMs: Date.now(),
  }
  writeJsonFile(resolveDeviceAuthPath(), store)
}

export function approveOpenClawDeviceRequest(requestId: string) {
  const gatewayToken = getOpenClawToken()
  if (!gatewayToken)
    throw new Error('OpenClaw gateway token not found')

  execFileSync(resolveOpenClawCommand(), ['devices', 'approve', requestId, '--json', '--token', gatewayToken], {
    stdio: 'pipe',
    encoding: 'utf-8',
  })
  return true
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
  }

  try {
    return JSON.stringify(value, null, 2)
  }
  catch {
    return String(value)
  }
}

function extractTextFromMessage(message: any): string {
  if (!message || typeof message !== 'object')
    return ''

  if (typeof message.text === 'string' && message.text.trim())
    return message.text.trim()

  const content = Array.isArray(message.content) ? message.content : []
  return content
    .map((item: any) => {
      if (!item || typeof item !== 'object')
        return null
      if (item.type === 'text' && typeof item.text === 'string')
        return item.text
      return null
    })
    .filter((item: string | null): item is string => Boolean(item?.trim()))
    .join('\n')
    .trim()
}

function extractToolEventsFromChatPayload(payload: any): OpenClawToolEvent[] {
  if (!payload || typeof payload !== 'object')
    return []

  const stream = payload.stream
  const data = payload.data
  if (stream !== 'tool' || !data || typeof data !== 'object')
    return []

  const phase = typeof data.phase === 'string' ? data.phase : ''
  if (phase !== 'start' && phase !== 'update' && phase !== 'result')
    return []

  const toolCallId = typeof data.toolCallId === 'string' ? data.toolCallId : ''
  if (!toolCallId)
    return []

  return [{
    toolCallId,
    runId: typeof payload.runId === 'string' ? payload.runId : undefined,
    name: typeof data.name === 'string' ? data.name : 'tool',
    phase,
    args: phase === 'start' ? data.args : undefined,
    output: phase === 'update'
      ? stringifyToolOutput(data.partialResult)
      : phase === 'result'
        ? stringifyToolOutput(data.result)
        : undefined,
    ts: typeof payload.ts === 'number' ? payload.ts : Date.now(),
  }]
}

function resolveOpenClawPackageDir() {
  const candidates: string[] = []

  const commandPathCandidates = [
    join(dirname(process.execPath), 'openclaw.cmd'),
    join(dirname(process.execPath), 'openclaw'),
    'C:\\nvm4w\\nodejs\\openclaw.cmd',
    'C:\\nvm4w\\nodejs\\openclaw',
  ]

  for (const commandPath of commandPathCandidates) {
    if (existsSync(commandPath))
      candidates.push(join(dirname(commandPath), 'node_modules', 'openclaw'))
  }

  try {
    const resolved = execFileSync('where', ['openclaw'], {
      stdio: 'pipe',
      encoding: 'utf-8',
    })
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)

    for (const commandPath of resolved)
      candidates.push(join(dirname(commandPath), 'node_modules', 'openclaw'))
  }
  catch {
    // ignore path lookup failures
  }

  candidates.push(join(dirname(process.execPath), 'node_modules', 'openclaw'))

  for (const candidate of candidates) {
    if (existsSync(join(candidate, 'package.json')))
      return candidate
  }

  throw new Error('OpenClaw package directory not found')
}

async function loadOpenClawGatewayClientCtor(): Promise<OpenClawGatewayClientCtor> {
  if (cachedGatewayClientCtor)
    return await cachedGatewayClientCtor

  cachedGatewayClientCtor = (async () => {
  const packageDir = resolveOpenClawPackageDir()
  const distDir = join(packageDir, 'dist')
  const chunk = readdirSync(distDir).find(name => /^auth-profiles-.*\.js$/i.test(name))
  if (!chunk)
    throw new Error('OpenClaw gateway runtime chunk not found')

  const mod = await import(pathToFileURL(join(distDir, chunk)).href) as Record<string, unknown>
  const GatewayClient = mod.bc

  if (typeof GatewayClient !== 'function')
    throw new Error('OpenClaw GatewayClient export unavailable')

  return GatewayClient as OpenClawGatewayClientCtor
  })()

  try {
    return await cachedGatewayClientCtor
  }
  catch (error) {
    cachedGatewayClientCtor = null
    throw error
  }
}

async function runOpenClawAgentFallback(text: string): Promise<OpenClawChatResult> {
  const { stdout } = await execFileAsync(resolveOpenClawCommand(), ['agent', '--agent', 'main', '--message', text, '--json'], {
    encoding: 'utf-8',
    timeout: 120000,
    windowsHide: true,
  })
  const parsed = JSON.parse(stdout) as { payloads?: Array<{ text?: string }> }
  const answer = parsed.payloads?.find(item => typeof item?.text === 'string' && item.text.trim())?.text?.trim()

  return {
    text: answer || '(openclaw returned no content)',
    toolEvents: [],
  }
}

export async function openclawChatCompletion(params: {
  messages: OpenClawChatMessage[]
}): Promise<OpenClawChatResult> {
  const text = [...params.messages].reverse().find(message => message.role === 'user')?.content?.trim() || ''
  if (!text)
    throw new Error('OpenClaw message is empty')

  const gatewayToken = getOpenClawToken()
  if (!gatewayToken)
    return await runOpenClawAgentFallback(text)

  try {
    const GatewayClient = await loadOpenClawGatewayClientCtor()
    return await new Promise<OpenClawChatResult>((resolve, reject) => {
      const seenToolEventKeys = new Set<string>()
      const toolEvents: OpenClawToolEvent[] = []
      const runId = `astron-${Date.now()}`
      let latestText = ''
      let settled = false
      let requestStarted = false

      const settle = (error?: Error, result?: OpenClawChatResult) => {
        if (settled)
          return
        settled = true
        try {
          client.stop()
        }
        catch {
          // ignore stop failures
        }
        if (error)
          reject(error)
        else if (result)
          resolve(result)
      }

      const pushToolEvents = (events: OpenClawToolEvent[]) => {
        for (const event of events) {
          const key = [
            event.toolCallId,
            event.phase,
            event.name,
            stringifyToolOutput(event.args) ?? '',
            event.output ?? '',
            String(event.ts),
          ].join('::')

          if (seenToolEventKeys.has(key))
            continue

          seenToolEventKeys.add(key)
          toolEvents.push(event)
        }
      }

      const timer = setTimeout(() => {
        settle(new Error('openclaw request timeout'))
      }, 120000)

      const client = new GatewayClient({
        token: gatewayToken,
        clientName: 'gateway-client',
        clientDisplayName: 'Astron RPA',
        mode: 'backend',
        platform: process.platform,
        deviceFamily: 'desktop',
        role: 'operator',
        scopes: ['operator.read', 'operator.write'],
        caps: ['tool-events'],
        onHelloOk: async () => {
          if (requestStarted)
            return
          requestStarted = true
          try {
            await client.request('chat.send', {
              sessionKey: 'main',
              message: text,
              deliver: false,
              idempotencyKey: runId,
            })
          }
          catch (error: any) {
            clearTimeout(timer)
            settle(error instanceof Error ? error : new Error(String(error)))
          }
        },
        onEvent: (evt: any) => {
          if (evt?.event !== 'chat' && evt?.event !== 'agent')
            return

          const payload = evt?.payload
          if (!payload || payload.runId !== runId)
            return

          if (evt.event === 'agent') {
            pushToolEvents(extractToolEventsFromChatPayload(payload))
            return
          }

          const nextText = extractTextFromMessage(payload.message)
          if (nextText)
            latestText = nextText

          if (payload.state === 'error') {
            clearTimeout(timer)
            settle(new Error(payload.errorMessage || 'openclaw execution failed'))
            return
          }

          if (payload.state === 'final') {
            clearTimeout(timer)
            settle(undefined, {
              text: latestText || '(openclaw returned no content)',
              toolEvents,
            })
          }
        },
        onConnectError: (error: Error) => {
          clearTimeout(timer)
          settle(error)
        },
        onClose: (_code: number, reason: string) => {
          clearTimeout(timer)
          settle(new Error(reason ? `openclaw gateway closed: ${reason}` : 'openclaw gateway connection closed'))
        },
      })

      client.start()
    })
  }
  catch (error) {
    logger.warn(`OpenClaw backend bridge failed, falling back to CLI agent: ${String(error)}`)
    return await runOpenClawAgentFallback(text)
  }
}
