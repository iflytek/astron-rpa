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

interface OpenClawGatewayClient {
  start: () => void
  stop: () => void
  request: (method: string, params?: unknown, opts?: { expectFinal?: boolean }) => Promise<any>
}

interface OpenClawGatewayClientCtor {
  new (opts: Record<string, unknown>): OpenClawGatewayClient
}

const execFileAsync = promisify(execFile)
let cachedOpenClawCommand: { command: string, argsPrefix: string[] } | null = null
let cachedGatewayClientCtor: Promise<OpenClawGatewayClientCtor> | null = null

function resolveOpenClawDir() {
  return join(homedir(), '.openclaw')
}

function resolveAstronOpenClawStateDir() {
  if (process.platform === 'win32')
    return join(process.env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local'), 'astronverse-openclaw', '.openclaw-state')

  return join(homedir(), '.openclaw-state')
}

function resolveManagedOpenClawPackageRoot() {
  if (process.platform === 'win32')
    return join(process.env.APPDATA || join(homedir(), 'AppData', 'Roaming'), 'astron-rpa', 'python_core', 'Lib', 'site-packages', 'astronverse', 'openclaw')

  return join(homedir(), '.astron-rpa', 'python_core', 'Lib', 'site-packages', 'astronverse', 'openclaw')
}

function resolveManagedOpenClawSourceDir() {
  return join(resolveManagedOpenClawPackageRoot(), 'openclaw-src')
}

function resolveManagedNodeBinary() {
  const packageRoot = resolveManagedOpenClawPackageRoot()
  const nodeCandidates = [
    join(packageRoot, 'binary', 'node', 'node.exe'),
    join(packageRoot, 'binary', 'node', 'node'),
  ]

  for (const candidate of nodeCandidates) {
    if (existsSync(candidate))
      return candidate
  }

  throw new Error(`Managed OpenClaw node executable not found under: ${packageRoot}`)
}

function buildManagedOpenClawEnv() {
  const stateDir = resolveAstronOpenClawStateDir()
  return {
    ...process.env,
    OPENCLAW_HOME: stateDir,
    OPENCLAW_STATE_DIR: stateDir,
    OPENCLAW_CONFIG_PATH: join(stateDir, 'openclaw.json'),
  }
}

function applyManagedOpenClawProcessEnv() {
  const managedEnv = buildManagedOpenClawEnv()
  process.env.OPENCLAW_HOME = managedEnv.OPENCLAW_HOME
  process.env.OPENCLAW_STATE_DIR = managedEnv.OPENCLAW_STATE_DIR
  process.env.OPENCLAW_CONFIG_PATH = managedEnv.OPENCLAW_CONFIG_PATH
}

function createOpenClawFallbackSessionId() {
  return `astron-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function resolveOpenClawCommand() {
  if (cachedOpenClawCommand)
    return cachedOpenClawCommand

  const sourceDir = resolveManagedOpenClawSourceDir()
  const cliCandidates = [
    join(sourceDir, 'node_modules', '.bin', 'openclaw.cmd'),
    join(sourceDir, 'node_modules', '.bin', 'openclaw'),
  ]

  for (const candidate of cliCandidates) {
    if (existsSync(candidate)) {
      cachedOpenClawCommand = { command: candidate, argsPrefix: [] }
      return cachedOpenClawCommand
    }
  }

  const packageRoot = resolveManagedOpenClawPackageRoot()
  const nodeCandidates = [
    join(packageRoot, 'binary', 'node', 'node.exe'),
    join(packageRoot, 'binary', 'node', 'node'),
  ]
  const localEntry = join(sourceDir, 'node_modules', 'openclaw', 'openclaw.mjs')

  for (const nodeCandidate of nodeCandidates) {
    if (existsSync(nodeCandidate) && existsSync(localEntry)) {
      cachedOpenClawCommand = { command: nodeCandidate, argsPrefix: [localEntry] }
      return cachedOpenClawCommand
    }
  }

  throw new Error(`Managed OpenClaw CLI executable not found under: ${sourceDir}`)
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
 * 读取 Astron 托管的 OpenClaw 配置文件
 * Windows 默认路径: %LOCALAPPDATA%/astronverse-openclaw/.openclaw-state/openclaw.json
 */
export function readOpenClawConfig(): OpenClawConfig | null {
  try {
    const configPath = join(resolveAstronOpenClawStateDir(), 'openclaw.json')
    logger.info(`Reading OpenClaw config from: ${configPath}`)
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

  const resolved = resolveOpenClawCommand()
  execFileSync(resolved.command, [...resolved.argsPrefix, 'devices', 'approve', requestId, '--json', '--token', gatewayToken], {
    stdio: 'pipe',
    encoding: 'utf-8',
    env: buildManagedOpenClawEnv(),
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

function extractTextFromAgentCliResult(result: any): string {
  if (!result || typeof result !== 'object')
    return ''

  const payloadGroups = [
    Array.isArray(result.payloads) ? result.payloads : [],
    Array.isArray(result.result?.payloads) ? result.result.payloads : [],
  ]

  for (const payloads of payloadGroups) {
    const answer = payloads.find((item: any) => typeof item?.text === 'string' && item.text.trim())?.text?.trim()
    if (answer)
      return answer
  }

  return extractTextFromMessage(result.message ?? result.result?.message)
}

function extractToolEventsFromMessage(message: any, fallbackTs: number): OpenClawToolEvent[] {
  if (!message || typeof message !== 'object' || !Array.isArray(message.content))
    return []

  const timestamp = typeof message.timestamp === 'number' ? message.timestamp : fallbackTs
  const runId = typeof message.runId === 'string' ? message.runId : undefined
  const messageToolCallId = typeof message.toolCallId === 'string' ? message.toolCallId : ''
  const blocks = message.content as any[]

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

function summarizeToolEvents(events: OpenClawToolEvent[]) {
  return events.map(event => ({
    toolCallId: event.toolCallId,
    runId: event.runId,
    name: event.name,
    phase: event.phase,
    hasArgs: event.args != null,
    outputLength: typeof event.output === 'string' ? event.output.length : 0,
    ts: event.ts,
  }))
}

function summarizeMessageContent(message: any) {
  if (!message || typeof message !== 'object') {
    return {
      role: undefined,
      contentType: typeof message?.content,
      contentBlockTypes: [],
      textLength: 0,
    }
  }

  const content = Array.isArray(message.content) ? message.content : []
  const text = extractTextFromMessage(message)

  return {
    role: typeof message.role === 'string' ? message.role : undefined,
    contentType: Array.isArray(message.content) ? 'array' : typeof message.content,
    contentBlockTypes: content.map((item: any) => {
      if (!item || typeof item !== 'object')
        return typeof item
      return typeof item.type === 'string' ? item.type : 'object'
    }),
    textLength: text.length,
    toolCallId:
      typeof message.toolCallId === 'string' ? message.toolCallId : undefined,
    runId: typeof message.runId === 'string' ? message.runId : undefined,
  }
}

function resolveOpenClawPackageDir() {
  const candidate = join(resolveManagedOpenClawSourceDir(), 'node_modules', 'openclaw')
  if (existsSync(join(candidate, 'package.json')))
    return candidate

  throw new Error(`Managed OpenClaw package directory not found under: ${candidate}`)
}

async function loadOpenClawGatewayClientCtor(): Promise<OpenClawGatewayClientCtor> {
  if (cachedGatewayClientCtor)
    return await cachedGatewayClientCtor

  cachedGatewayClientCtor = (async () => {
    applyManagedOpenClawProcessEnv()
    const packageDir = resolveOpenClawPackageDir()
    const distDir = join(packageDir, 'dist')
    const chunk = readdirSync(distDir).find(name => /^auth-profiles-.*\.js$/i.test(name))
    if (!chunk)
      throw new Error('OpenClaw gateway runtime chunk not found')

    const mod = await import(pathToFileURL(join(distDir, chunk)).href) as Record<string, unknown>
    const candidates = Object.values(mod).filter(
      value => typeof value === 'function',
    ) as Function[]
    const GatewayClient = (
      mod.GatewayClient
      ?? candidates.find(value => value.name === 'GatewayClient')
    )

    if (typeof GatewayClient !== 'function')
      throw new Error('OpenClaw GatewayClient export unavailable')

    logger.info(`Resolved OpenClaw GatewayClient from chunk: ${chunk}`)
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

function buildManagedGatewayBridgeScript() {
  return String.raw`
import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const RESULT_PREFIX = '__OPENCLAW_RESULT__';

function stringifyToolOutput(value) {
  if (typeof value === 'string')
    return value.trim() || undefined;
  if (value == null)
    return undefined;
  if (typeof value === 'number' || typeof value === 'boolean')
    return String(value);
  if (typeof value === 'object') {
    if (typeof value.text === 'string' && value.text.trim())
      return value.text.trim();
    if (Array.isArray(value.content)) {
      const text = value.content
        .map((item) => {
          if (!item || typeof item !== 'object')
            return null;
          if (item.type === 'text' && typeof item.text === 'string')
            return item.text;
          return null;
        })
        .filter((item) => Boolean(item && item.trim()))
        .join('\n')
        .trim();
      if (text)
        return text;
    }
  }
  try {
    return JSON.stringify(value, null, 2);
  }
  catch {
    return String(value);
  }
}

function extractTextFromMessage(message) {
  if (!message || typeof message !== 'object')
    return '';

  if (typeof message.text === 'string' && message.text.trim())
    return message.text.trim();

  const content = Array.isArray(message.content) ? message.content : [];
  return content
    .map((item) => {
      if (!item || typeof item !== 'object')
        return null;
      if (item.type === 'text' && typeof item.text === 'string')
        return item.text;
      return null;
    })
    .filter((item) => Boolean(item && item.trim()))
    .join('\n')
    .trim();
}

function extractToolEventsFromMessage(message, fallbackTs) {
  if (!message || typeof message !== 'object' || !Array.isArray(message.content))
    return [];

  const timestamp = typeof message.timestamp === 'number' ? message.timestamp : fallbackTs;
  const runId = typeof message.runId === 'string' ? message.runId : undefined;
  const messageToolCallId = typeof message.toolCallId === 'string' ? message.toolCallId : '';
  const blocks = message.content;

  const callEvents = blocks
    .map((item, index) => {
      const type = typeof item?.type === 'string' ? item.type.toLowerCase() : '';
      const isToolCall = ['toolcall', 'tool_call', 'tooluse', 'tool_use'].includes(type)
        || (typeof item?.name === 'string' && item?.arguments != null);

      if (!isToolCall)
        return null;

      return {
        toolCallId: messageToolCallId || (runId || 'tool') + ':call:' + index,
        runId,
        name: typeof item.name === 'string' ? item.name : 'tool',
        phase: 'start',
        args: item.arguments ?? item.args,
        ts: timestamp,
      };
    })
    .filter(Boolean);

  const resultEvents = blocks
    .map((item, index) => {
      const type = typeof item?.type === 'string' ? item.type.toLowerCase() : '';
      if (type !== 'toolresult' && type !== 'tool_result')
        return null;

      const matchingCall = callEvents.find(call => call.name === item.name);
      return {
        toolCallId: matchingCall?.toolCallId || messageToolCallId || (runId || 'tool') + ':result:' + index,
        runId,
        name: typeof item.name === 'string' ? item.name : (matchingCall?.name ?? 'tool'),
        phase: 'result',
        output: typeof item.text === 'string'
          ? item.text
          : typeof item.content === 'string'
            ? item.content
            : undefined,
        ts: timestamp,
      };
    })
    .filter(Boolean);

  return [...callEvents, ...resultEvents];
}

function extractToolEventsFromChatPayload(payload) {
  if (!payload || typeof payload !== 'object')
    return [];

  const stream = payload.stream;
  const data = payload.data;
  if (stream !== 'tool' || !data || typeof data !== 'object')
    return [];

  const phase = typeof data.phase === 'string' ? data.phase : '';
  if (phase !== 'start' && phase !== 'update' && phase !== 'result')
    return [];

  const toolCallId = typeof data.toolCallId === 'string' ? data.toolCallId : '';
  if (!toolCallId)
    return [];

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
  }];
}

const payload = JSON.parse(process.argv[1] || '{}');
const packageDir = process.env.OPENCLAW_PACKAGE_DIR;
const distDir = join(packageDir, 'dist');
const chunk = readdirSync(distDir).find(name => /^auth-profiles-.*\.js$/i.test(name));
if (!chunk)
  throw new Error('OpenClaw gateway runtime chunk not found');

const mod = await import(pathToFileURL(join(distDir, chunk)).href);
const candidates = Object.values(mod).filter(value => typeof value === 'function');
const GatewayClient = mod.GatewayClient ?? candidates.find(value => value.name === 'GatewayClient');
if (typeof GatewayClient !== 'function')
  throw new Error('OpenClaw GatewayClient export unavailable');

const seenToolEventKeys = new Set();
const toolEvents = [];
let latestText = '';
let settled = false;
let requestStarted = false;
const runId = 'astron-' + Date.now();

await new Promise((resolve, reject) => {
  const settle = (error, result) => {
    if (settled)
      return;
    settled = true;
    try {
      client.stop();
    }
    catch {}
    if (error) {
      reject(error);
      return;
    }
    process.stdout.write(RESULT_PREFIX + JSON.stringify(result) + '\n');
    resolve();
  };

  const pushToolEvents = (events) => {
    for (const event of events) {
      const key = [
        event.toolCallId,
        event.phase,
        event.name,
        stringifyToolOutput(event.args) ?? '',
        event.output ?? '',
        String(event.ts),
      ].join('::');
      if (seenToolEventKeys.has(key))
        continue;
      seenToolEventKeys.add(key);
      toolEvents.push(event);
    }
  };

  const timer = setTimeout(() => {
    settle(new Error('openclaw request timeout'));
  }, 120000);

  const client = new GatewayClient({
    token: payload.token,
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
        return;
      requestStarted = true;
      try {
        await client.request('chat.send', {
          sessionKey: payload.sessionKey || 'main',
          message: payload.text,
          deliver: false,
          idempotencyKey: runId,
          attachments: Array.isArray(payload.attachments) ? payload.attachments : undefined,
        });
      }
      catch (error) {
        clearTimeout(timer);
        settle(error instanceof Error ? error : new Error(String(error)));
      }
    },
    onEvent: (evt) => {
      if (evt?.event !== 'chat' && evt?.event !== 'agent')
        return;

      const eventPayload = evt?.payload;
      if (!eventPayload || eventPayload.runId !== runId)
        return;

      if (evt.event === 'agent') {
        pushToolEvents(extractToolEventsFromChatPayload(eventPayload));
        return;
      }

      const nextText = extractTextFromMessage(eventPayload.message);
      if (nextText)
        latestText = nextText;

      if (eventPayload.state === 'error') {
        clearTimeout(timer);
        settle(new Error(eventPayload.errorMessage || 'openclaw execution failed'));
        return;
      }

      if (eventPayload.state === 'final') {
        pushToolEvents(extractToolEventsFromMessage(eventPayload.message, Date.now()));
        clearTimeout(timer);
        settle(undefined, {
          text: latestText || '(openclaw returned no content)',
          toolEvents,
        });
      }
    },
    onConnectError: (error) => {
      clearTimeout(timer);
      settle(error);
    },
    onClose: (_code, reason) => {
      clearTimeout(timer);
      settle(new Error(reason ? 'openclaw gateway closed: ' + reason : 'openclaw gateway connection closed'));
    },
  });

  client.start();
});
`
}

async function runOpenClawGatewayBridge(params: {
  token: string
  text: string
  sessionKey?: string
  attachments?: OpenClawChatAttachment[]
}): Promise<OpenClawChatResult> {
  const nodeBinary = resolveManagedNodeBinary()
  const packageDir = resolveOpenClawPackageDir()
  const script = buildManagedGatewayBridgeScript()
  const payload = JSON.stringify({
    token: params.token,
    text: params.text,
    sessionKey: params.sessionKey,
    attachments: params.attachments,
  })

  logger.info(`OpenClaw managed bridge start: sessionKey=${params.sessionKey || 'main'}, attachments=${params.attachments?.length || 0}`)

  const { stdout, stderr } = await execFileAsync(
    nodeBinary,
    ['--input-type=module', '-e', script, payload],
    {
      encoding: 'utf-8',
      timeout: 120000,
      windowsHide: true,
      env: {
        ...buildManagedOpenClawEnv(),
        OPENCLAW_PACKAGE_DIR: packageDir,
      },
      maxBuffer: 1024 * 1024 * 8,
    },
  )

  if (stderr?.trim())
    logger.warn(`OpenClaw managed bridge stderr: ${stderr.trim()}`)

  const resultLine = stdout
    .split(/\r?\n/)
    .reverse()
    .find(line => line.startsWith('__OPENCLAW_RESULT__'))

  if (!resultLine)
    throw new Error(`OpenClaw managed bridge returned no result. stdout=${stdout.trim()}`)

  const result = JSON.parse(
    resultLine.slice('__OPENCLAW_RESULT__'.length),
  ) as OpenClawChatResult

  logger.info(
    `OpenClaw managed bridge success: sessionKey=${params.sessionKey || 'main'}, textLength=${result.text.length}, toolEventCount=${result.toolEvents.length}`,
  )
  if (result.toolEvents.length > 0)
    logger.info(`OpenClaw managed bridge tool events: ${JSON.stringify(summarizeToolEvents(result.toolEvents))}`)

  return result
}

async function runOpenClawAgentFallback(text: string): Promise<OpenClawChatResult> {
  const sessionId = createOpenClawFallbackSessionId()
  const resolved = resolveOpenClawCommand()
  logger.warn(`OpenClaw CLI fallback start: sessionId=${sessionId}, textLength=${text.length}`)
  const { stdout } = await execFileAsync(resolved.command, [...resolved.argsPrefix, 'agent', '--agent', 'main', '--session-id', sessionId, '--message', text, '--json'], {
    encoding: 'utf-8',
    timeout: 120000,
    windowsHide: true,
    env: buildManagedOpenClawEnv(),
  })
  const parsed = JSON.parse(stdout) as Record<string, unknown>
  const answer = extractTextFromAgentCliResult(parsed)
  logger.warn(`OpenClaw CLI fallback completed: sessionId=${sessionId}, textLength=${answer.length}, toolEventCount=0`)

  return {
    text: answer || '(openclaw returned no content)',
    toolEvents: [],
  }
}

export async function openclawChatCompletion(params: {
  messages: OpenClawChatMessage[]
  sessionKey?: string
  attachments?: OpenClawChatAttachment[]
  allowCliFallback?: boolean
}): Promise<OpenClawChatResult> {
  const text = [...params.messages].reverse().find(message => message.role === 'user')?.content?.trim() || ''
  if (!text)
    throw new Error('OpenClaw message is empty')

  const gatewayToken = getOpenClawToken()
  logger.info(
    `OpenClaw chat start: sessionKey=${params.sessionKey || 'main'}, messageCount=${params.messages.length}, textLength=${text.length}, attachments=${params.attachments?.length || 0}, hasGatewayToken=${Boolean(gatewayToken)}, allowCliFallback=${params.allowCliFallback !== false}`,
  )
  if (!gatewayToken)
    return await runOpenClawAgentFallback(text)

  try {
    const managedBridgeResult = await runOpenClawGatewayBridge({
      token: gatewayToken,
      text,
      sessionKey: params.sessionKey,
      attachments: params.attachments,
    })
    return managedBridgeResult
  }
  catch (error) {
    logger.warn(`OpenClaw managed bridge failed, trying in-process bridge: ${error instanceof Error ? error.stack || error.message : String(error)}`)
  }

  try {
    const GatewayClient = await loadOpenClawGatewayClientCtor()
    logger.info(`OpenClaw GatewayClient ready for sessionKey=${params.sessionKey || 'main'}`)
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
        if (error) {
          logger.warn(`OpenClaw chat settle with error: sessionKey=${params.sessionKey || 'main'}, runId=${runId}, message=${error.message}`)
        }
        else if (result) {
          logger.info(
            `OpenClaw chat settle success: sessionKey=${params.sessionKey || 'main'}, runId=${runId}, textLength=${result.text.length}, toolEventCount=${result.toolEvents.length}`,
          )
          if (result.toolEvents.length > 0)
            logger.info(`OpenClaw tool events: ${JSON.stringify(summarizeToolEvents(result.toolEvents))}`)
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

        if (events.length > 0) {
          logger.info(
            `OpenClaw tool events captured: sessionKey=${params.sessionKey || 'main'}, runId=${runId}, captured=${events.length}, total=${toolEvents.length}, events=${JSON.stringify(summarizeToolEvents(events))}`,
          )
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
            logger.info(
              `OpenClaw chat.send dispatch: sessionKey=${params.sessionKey || 'main'}, runId=${runId}, attachments=${params.attachments?.length || 0}`,
            )
            await client.request('chat.send', {
              sessionKey: params.sessionKey || 'main',
              message: text,
              deliver: false,
              idempotencyKey: runId,
              attachments: params.attachments,
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

          logger.info(
            `OpenClaw gateway event: sessionKey=${params.sessionKey || 'main'}, runId=${runId}, event=${evt.event}, state=${typeof payload.state === 'string' ? payload.state : ''}, stream=${typeof payload.stream === 'string' ? payload.stream : ''}, message=${JSON.stringify(summarizeMessageContent(payload.message))}`,
          )

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
            pushToolEvents(extractToolEventsFromMessage(payload.message, Date.now()))
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
    if (params.allowCliFallback === false)
      throw error instanceof Error ? error : new Error(String(error))

    logger.warn(`OpenClaw backend bridge failed, falling back to CLI agent: ${error instanceof Error ? error.stack || error.message : String(error)}`)
    return await runOpenClawAgentFallback(text)
  }
}
