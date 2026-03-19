<script setup lang="ts">
import {
  AppstoreOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  CodeOutlined,
  DatabaseOutlined,
  DownOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  HistoryOutlined,
  PlusOutlined,
  ScheduleOutlined,
  SendOutlined,
  SettingOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons-vue'
import { message as appMessage } from 'ant-design-vue'
import markdownit from 'markdown-it'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import { generateUUID } from '@/utils/common'

import { getConfiguredOpenClawToken, resolveOpenClawToken } from '@/api/openclaw-auth'
import { loadLocalFilePreview } from '@/api/local-file-preview'
import { openclawChatCompletions, openclawDeleteSession } from '@/api/openclaw'
import type { OpenClawToolEvent } from '@/api/openclaw'
import type { OpenClawManagerCurrentConfig } from '@/api/openclaw-manager'
import { getOpenClawManagerStatus } from '@/api/openclaw-manager'

import IMConnectPanel from './IMConnectPanel.vue'
import {
  buildRecentSessionList,
  resolveNextSessionIdAfterDelete,
} from './session-list'
import { resolveToolFileArtifact } from './tool-files'
import { resolveToolDisplay } from './tool-display'

type SidebarKey = 'chat' | 'history' | 'skills' | 'schedule'
type StarterFilter
  = | 'all'
    | 'workflow'
    | 'data'
    | 'integration'
    | 'daily'
    | 'monitoring'
type CardSection = 'skills' | 'schedule'

interface ChatAttachment {
  id: string
  dataUrl: string
  mimeType: string
  fileName: string
}

type ChatMessage
  = | {
    id: string
    role: 'user' | 'assistant'
    content: string
    createdAt: number
    attachments?: ChatAttachment[]
  }
  | {
    id: string
    role: 'tool'
    content: string
    createdAt: number
    toolCallId: string
    toolName: string
    toolStatus: 'running' | 'completed'
    toolArgs?: unknown
  }

interface ChatSession {
  id: string
  sessionKey: string
  title: string
  createdAt: number
  updatedAt: number
  messages: ChatMessage[]
  isDraft: boolean
  needsNewCommand: boolean
}

interface PersistedSessionState {
  version: 1
  currentSessionId?: string
  sessions: ChatSession[]
}

interface StarterCard {
  id: string
  title: string
  description: string
  prompt: string
  icon: any
  section: CardSection
  filter: Exclude<StarterFilter, 'all'>
}

const props = defineProps<{
  title?: string
  placeholder?: string
  openclawToken?: string
}>()

const STORAGE_KEY = 'astron.assistant.sessions.v1'
const MAX_STORED_SESSIONS = 24

const text = {
  title: 'Astron 助理',
  placeholder: '需要 Astron 帮你处理什么？按 Enter 发送，Shift + Enter 换行',
  heroLabel: 'AI 组件工作台',
  workspaceLabel: '已连接工作区',
  sending: 'Astron 正在处理中...',
  sendFailed: '发送失败',
  requestFailedPrefix: '（请求 OpenClaw 失败）',
  requestFailedSuffix:
    '。请确认 OpenClaw gateway 已在本机启动，并监听 19878 端口。',
  emptyResponse: '（OpenClaw 没有返回内容）',
  toolCompleted: 'Completed',
  toolRunning: 'Running...',
  connected: '已连接',
  notConnected: '未连接',
  modelUnconfigured: '点击配置模型',
  assistantSettings: '助手设置',
  assistantSettingsDesc: '模型、IM 和连接配置',
  quickContext: '上下文入口预留中',
  quickSkill: '已切换到技能推荐区',
  skillTitle: '推荐技能',
  scheduleTitle: '推荐计划',
  historyTitle: '历史会话',
  historyDesc: '继续之前的 OpenClaw 会话',
  historyEmpty: '还没有历史会话',
  historyEmptyDesc: '先从“新的任务”开始一次对话，这里会自动保留会话记录。',
  continueChat: '继续对话',
  messageCount: '条消息',
  heroChat: '告诉 Astron，你想自动化什么',
  heroSkills: '直接复用一套成熟的 AI 技能',
  heroSchedule: '把重复执行的任务交给计划调度',
  heroChatDesc: '支持流程设计、脚本生成、调度编排和本地 OpenClaw 协同分析。',
  heroSkillsDesc:
    '从常见自动化场景里挑一个起点，快速生成更贴近业务的任务描述。',
  heroScheduleDesc: '先定义执行目标，再补充时间、触发方式和通知动作。',
  allSkills: '全部技能',
  workflow: '流程设计',
  data: '数据处理',
  integration: '系统集成',
  allSchedules: '全部计划',
  daily: '日常执行',
  monitoring: '监控告警',
  newTask: '新的任务',
  newTaskDesc: '开始一轮新会话',
  skillCenter: '技能中心',
  skillCenterDesc: '挑选常见场景模板',
  scheduleTask: '定时任务',
  scheduleTaskDesc: '规划自动执行任务',
  userFallback: 'Astron 用户',
  workspaceFallback: '默认工作区',
  untitledSession: '未命名会话',
  sessionDraft: '新会话',
  sessionCreated: '新会话已创建',
  systemPrompt:
    '你是 Astron 助理，帮助用户使用 Astron RPA 设计器与执行器。回答请使用中文，并尽量给出可执行的步骤。',
} as const

const sidebarItems = [
  {
    key: 'chat' as const,
    title: text.newTask,
    description: text.newTaskDesc,
    icon: PlusOutlined,
  },
  {
    key: 'history' as const,
    title: text.historyTitle,
    description: text.historyDesc,
    icon: HistoryOutlined,
  },
  {
    key: 'skills' as const,
    title: text.skillCenter,
    description: text.skillCenterDesc,
    icon: AppstoreOutlined,
  },
  {
    key: 'schedule' as const,
    title: text.scheduleTask,
    description: text.scheduleTaskDesc,
    icon: ClockCircleOutlined,
  },
]

const starterCards: StarterCard[] = [
  {
    id: 'workflow-form',
    title: '表单流程搭建',
    description: '梳理从表格读取、网页录入到结果回写的完整步骤。',
    prompt:
      '帮我设计一个从 Excel 读取客户名单，进入网页录入并把结果回写到原表的 RPA 流程。',
    icon: CodeOutlined,
    section: 'skills',
    filter: 'workflow',
  },
  {
    id: 'data-clean',
    title: '数据清洗脚本',
    description: '生成适合本地运行的 Python 处理脚本。',
    prompt:
      '帮我生成一个 Python 脚本，清洗 Excel 中的手机号和邮箱字段，并输出一个新文件。',
    icon: DatabaseOutlined,
    section: 'skills',
    filter: 'data',
  },
  {
    id: 'system-integration',
    title: '接口联动方案',
    description: '串联数据库、Webhook、企业 IM 或内部系统接口。',
    prompt: '帮我规划一个调用企业微信机器人并回写结果到数据库的自动化方案。',
    icon: AppstoreOutlined,
    section: 'skills',
    filter: 'integration',
  },
  {
    id: 'document-summary',
    title: '文档整理助手',
    description: '批量读取文件并提取关键信息，形成可执行流程。',
    prompt:
      '帮我设计一个批量读取文件夹中的 PDF，提取关键信息后汇总到 Excel 的自动化任务。',
    icon: FileTextOutlined,
    section: 'skills',
    filter: 'workflow',
  },
  {
    id: 'daily-report',
    title: '日报自动汇总',
    description: '按固定时间汇总执行日志或关键指标并发送。',
    prompt:
      '帮我创建一个每天 9:00 执行的计划任务，汇总昨天的运行日志并发送邮件。',
    icon: ScheduleOutlined,
    section: 'schedule',
    filter: 'daily',
  },
  {
    id: 'folder-watch',
    title: '共享目录监听',
    description: '监控文件夹变化，发现新文件后自动触发处理。',
    prompt:
      '帮我创建一个监听共享文件夹新增 Excel 文件的计划任务，发现文件后自动处理并归档。',
    icon: FolderOpenOutlined,
    section: 'schedule',
    filter: 'monitoring',
  },
  {
    id: 'system-check',
    title: '巡检与告警',
    description: '周期性检查系统状态，并在异常时推送消息。',
    prompt:
      '帮我创建一个每 15 分钟巡检系统状态并在异常时通知钉钉机器人的任务。',
    icon: ThunderboltOutlined,
    section: 'schedule',
    filter: 'monitoring',
  },
  {
    id: 'weekly-sync',
    title: '周期同步任务',
    description: '按周或按天同步报表、主数据和附件。',
    prompt:
      '帮我创建一个每周一 8:30 自动同步 CRM 客户数据到本地表格的计划任务。',
    icon: ClockCircleOutlined,
    section: 'schedule',
    filter: 'daily',
  },
]

function getStorage() {
  try {
    return window.localStorage
  }
  catch {
    return null
  }
}

function createSessionTitle(content: string) {
  const normalized = content.replace(/\s+/g, ' ').trim()
  if (!normalized)
    return text.untitledSession
  return normalized.length > 24 ? `${normalized.slice(0, 24)}...` : normalized
}

function normalizeAttachments(
  attachments: unknown,
): ChatAttachment[] | undefined {
  if (!Array.isArray(attachments))
    return undefined

  const normalized = attachments.filter((attachment): attachment is ChatAttachment => {
    if (!attachment || typeof attachment !== 'object')
      return false
    const candidate = attachment as Record<string, unknown>
    return Boolean(
      typeof candidate.id === 'string'
      && typeof candidate.dataUrl === 'string'
      && typeof candidate.mimeType === 'string'
      && typeof candidate.fileName === 'string',
    )
  })

  return normalized.length > 0 ? normalized : undefined
}

function createDraftSession(): ChatSession {
  const now = Date.now()
  return {
    id: generateUUID(),
    sessionKey: generateUUID(),
    title: text.sessionDraft,
    createdAt: now,
    updatedAt: now,
    messages: [],
    isDraft: true,
    needsNewCommand: true,
  }
}

function normalizeSession(
  session: Partial<ChatSession> | null | undefined,
): ChatSession | null {
  if (!session?.id || !session.sessionKey)
    return null

  const messages = Array.isArray(session.messages)
    ? session.messages.filter((message): message is ChatMessage =>
        Boolean(
          message?.id && message?.role && typeof message.content === 'string',
        ),
      )
    : []

  const now = Date.now()
  return {
    id: session.id,
    sessionKey: session.sessionKey,
    title:
      typeof session.title === 'string' && session.title.trim()
        ? session.title
        : messages[0]?.role === 'user'
          ? createSessionTitle(messages[0].content)
          : text.untitledSession,
    createdAt: typeof session.createdAt === 'number' ? session.createdAt : now,
    updatedAt: typeof session.updatedAt === 'number' ? session.updatedAt : now,
    messages: messages.map((message) => {
      if (message.role === 'tool')
        return message

      return {
        ...message,
        attachments: normalizeAttachments((message as { attachments?: unknown }).attachments),
      }
    }),
    isDraft:
      typeof session.isDraft === 'boolean'
        ? session.isDraft
        : messages.length === 0,
    needsNewCommand:
      typeof session.needsNewCommand === 'boolean'
        ? session.needsNewCommand
        : messages.length === 0,
  }
}

function loadPersistedState() {
  const storage = getStorage()
  const raw = storage?.getItem(STORAGE_KEY)
  if (!raw) {
    return {
      sessions: [createDraftSession()],
      currentSessionId: undefined as string | undefined,
    }
  }

  try {
    const parsed = JSON.parse(raw) as PersistedSessionState
    const sessions = Array.isArray(parsed.sessions)
      ? parsed.sessions
          .map(normalizeSession)
          .filter((session): session is ChatSession => Boolean(session))
      : []

    if (!sessions.length) {
      return {
        sessions: [createDraftSession()],
        currentSessionId: undefined as string | undefined,
      }
    }

    const currentSessionId = sessions.some(
      session => session.id === parsed.currentSessionId,
    )
      ? parsed.currentSessionId
      : sessions[0].id

    return { sessions, currentSessionId }
  }
  catch {
    return {
      sessions: [createDraftSession()],
      currentSessionId: undefined as string | undefined,
    }
  }
}

function formatSessionTime(timestamp: number) {
  const date = new Date(timestamp)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }
  if (date.getFullYear() === now.getFullYear()) {
    return new Intl.DateTimeFormat('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  }).format(date)
}

function getSessionPreview(session: ChatSession) {
  const lastMessage = [...session.messages]
    .reverse()
    .find(message => message.role !== 'tool')
  if (!lastMessage)
    return text.historyDesc
  const textContent = lastMessage.content.replace(/\s+/g, ' ').trim()
  if (textContent)
    return textContent
  if (lastMessage.attachments?.length)
    return `${lastMessage.attachments.length} 张图片`
  return text.historyDesc
}

const initialState = loadPersistedState()
const openclawToken = ref<string | undefined>(
  getConfiguredOpenClawToken(props.openclawToken),
)
const sessions = ref<ChatSession[]>(initialState.sessions)
const currentSessionId = ref(
  initialState.currentSessionId || initialState.sessions[0]?.id || '',
)
const input = ref('')
const composerAttachments = ref<ChatAttachment[]>([])
const sending = ref(false)
const errorText = ref('')
const contextError = ref('')
const showSettings = ref(false)
const assistantConfig = ref<OpenClawManagerCurrentConfig | null>(null)
const scrollerRef = ref<HTMLElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const textareaKey = ref(0)
const activeSidebar = ref<SidebarKey>('chat')
const activeFilter = ref<StarterFilter>('all')
const deletingSessionId = ref('')
const previewArtifact = ref<ReturnType<typeof resolveToolFileArtifact> | null>(null)
const previewStatus = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const previewRenderedHtml = ref('')
const previewPdfUrl = ref('')
const previewError = ref('')
const md = markdownit({ breaks: true, linkify: true })

const currentSession = computed(
  () =>
    sessions.value.find(session => session.id === currentSessionId.value)
    || null,
)
const messages = computed(() => currentSession.value?.messages ?? [])
const canSend = computed(() =>
  !sending.value
  && (input.value.trim().length > 0 || composerAttachments.value.length > 0),
)
const hasConversation = computed(() => messages.value.length > 0)
const showHistoryPanel = computed(() => activeSidebar.value === 'history')
const showConversation = computed(
  () => !showHistoryPanel.value && hasConversation.value,
)
const userName = computed(() => import.meta.env.VITE_ASSISTANT_USER_NAME || text.userFallback)
const workspaceName = computed(
  () =>
    assistantConfig.value?.workspace
    || import.meta.env.VITE_ASSISTANT_WORKSPACE_NAME
    || text.workspaceFallback,
)
const userInitial = computed(() => userName.value.slice(0, 1).toUpperCase())
const currentModelLabel = computed(
  () => assistantConfig.value?.primary_model || text.modelUnconfigured,
)
const connectionStatusText = computed(() =>
  assistantConfig.value?.primary_model ? text.connected : text.notConnected,
)
const connectionStatusClass = computed(() =>
  assistantConfig.value?.primary_model ? 'text-[#0f9f6e]' : 'text-[#9a6b19]',
)
const heroTitle = computed(() =>
  activeSidebar.value === 'schedule'
    ? text.heroSchedule
    : activeSidebar.value === 'skills'
      ? text.heroSkills
      : text.heroChat,
)
const heroDescription = computed(() =>
  activeSidebar.value === 'schedule'
    ? text.heroScheduleDesc
    : activeSidebar.value === 'skills'
      ? text.heroSkillsDesc
      : text.heroChatDesc,
)
const starterTitle = computed(() =>
  activeSidebar.value === 'schedule' ? text.scheduleTitle : text.skillTitle,
)
const starterFilters = computed(() =>
  activeSidebar.value === 'schedule'
    ? [
        { key: 'all' as StarterFilter, label: text.allSchedules },
        { key: 'daily' as StarterFilter, label: text.daily },
        { key: 'monitoring' as StarterFilter, label: text.monitoring },
      ]
    : [
        { key: 'all' as StarterFilter, label: text.allSkills },
        { key: 'workflow' as StarterFilter, label: text.workflow },
        { key: 'data' as StarterFilter, label: text.data },
        { key: 'integration' as StarterFilter, label: text.integration },
      ],
)
const visibleStarterCards = computed(() => {
  const section: CardSection
    = activeSidebar.value === 'schedule' ? 'schedule' : 'skills'
  return starterCards.filter((card) => {
    if (card.section !== section)
      return false
    if (activeFilter.value === 'all')
      return true
    return card.filter === activeFilter.value
  })
})
const historySessions = computed(() => {
  return [...sessions.value]
    .filter(session => session.messages.length > 0)
    .sort((left, right) => right.updatedAt - left.updatedAt)
})
const recentSessions = computed(() =>
  buildRecentSessionList(historySessions.value, currentSessionId.value, 3),
)
const currentSessionTitle = computed(
  () => currentSession.value?.title || props.title || text.title,
)
const isNewTaskActive = computed(
  () => activeSidebar.value === 'chat' && !hasConversation.value,
)

function persistSessions() {
  const storage = getStorage()
  if (!storage)
    return

  const sorted = [...sessions.value].sort(
    (left, right) => right.updatedAt - left.updatedAt,
  )
  const keepIds = new Set<string>()
  for (const session of sorted) {
    if (session.messages.length > 0 || session.id === currentSessionId.value)
      keepIds.add(session.id)
    if (keepIds.size >= MAX_STORED_SESSIONS)
      break
  }

  const payload: PersistedSessionState = {
    version: 1,
    currentSessionId: currentSessionId.value,
    sessions: sessions.value.filter(session => keepIds.has(session.id)),
  }
  storage.setItem(STORAGE_KEY, JSON.stringify(payload))
}

function ensureCurrentSession() {
  if (currentSession.value)
    return currentSession.value

  const session = createDraftSession()
  sessions.value = [session, ...sessions.value]
  currentSessionId.value = session.id
  return session
}

function removeUnusedDraftSessions(exceptId?: string) {
  sessions.value = sessions.value.filter((session) => {
    if (session.messages.length > 0)
      return true
    if (session.id === exceptId)
      return true
    return false
  })
}

function activateSession(sessionId: string) {
  currentSessionId.value = sessionId
  activeSidebar.value = 'chat'
  errorText.value = ''
  composerAttachments.value = []
  previewArtifact.value = null
}

function createAndActivateDraftSession(notify = false) {
  removeUnusedDraftSessions()
  const session = createDraftSession()
  sessions.value = [session, ...sessions.value]
  currentSessionId.value = session.id
  input.value = ''
  composerAttachments.value = []
  errorText.value = ''
  activeSidebar.value = 'chat'
  activeFilter.value = 'all'
  previewArtifact.value = null
  textareaKey.value += 1
  if (notify)
    appMessage.info(text.sessionCreated)
  return session
}

function startNewTask() {
  createAndActivateDraftSession(true)
}

function markSessionUsed(session: ChatSession, content?: string) {
  session.updatedAt = Date.now()
  session.isDraft = false
  if (session.needsNewCommand && session.messages.length > 0)
    session.needsNewCommand = false
  if (
    content
    && (session.title === text.sessionDraft
      || session.title === text.untitledSession)
  ) {
    session.title = createSessionTitle(content)
  }
}

function appendMessageToSession(sessionId: string, message: ChatMessage) {
  const session = sessions.value.find(item => item.id === sessionId)
  if (!session)
    return

  session.messages.push(message)
  markSessionUsed(
    session,
    message.role === 'user' ? message.content : undefined,
  )
}

function upsertToolMessage(sessionId: string, event: OpenClawToolEvent) {
  const session = sessions.value.find(item => item.id === sessionId)
  if (!session)
    return

  const index = session.messages.findIndex(
    message =>
      message.role === 'tool' && message.toolCallId === event.toolCallId,
  )
  const previous = index >= 0 ? session.messages[index] : null
  const nextMessage: ChatMessage = {
    id: previous?.id || generateUUID(),
    role: 'tool',
    content:
      event.output ?? (previous?.role === 'tool' ? previous.content : ''),
    createdAt: previous?.role === 'tool' ? previous.createdAt : event.ts,
    toolCallId: event.toolCallId,
    toolName: event.name,
    toolStatus: event.phase === 'result' ? 'completed' : 'running',
    toolArgs:
      event.args ?? (previous?.role === 'tool' ? previous.toolArgs : undefined),
  }

  if (index >= 0)
    session.messages.splice(index, 1, nextMessage)
  else session.messages.push(nextMessage)

  session.updatedAt = Date.now()
}

function renderMarkdown(content: string) {
  return md.render(content || '')
}

function getToolSummary(message: Extract<ChatMessage, { role: 'tool' }>) {
  return resolveToolDisplay(message.toolName, message.toolArgs)
}

function getToolFileArtifact(message: Extract<ChatMessage, { role: 'tool' }>) {
  return resolveToolFileArtifact({
    toolName: message.toolName,
    args: message.toolArgs,
    output: message.content,
    createdAt: message.createdAt,
  })
}

function getAssistantFileArtifact(index: number) {
  const message = messages.value[index]
  if (!message || message.role !== 'assistant')
    return null

  for (let cursor = index - 1; cursor >= 0; cursor -= 1) {
    const candidate = messages.value[cursor]
    if (!candidate)
      continue
    if (candidate.role !== 'tool')
      break

    const artifact = getToolFileArtifact(candidate)
    if (artifact)
      return artifact
  }

  return null
}

function openArtifactPreview(artifact: ReturnType<typeof resolveToolFileArtifact>) {
  if (!artifact)
    return

  previewArtifact.value = artifact
}

function closeFilePreview() {
  previewArtifact.value = null
  previewStatus.value = 'idle'
  previewRenderedHtml.value = ''
  previewPdfUrl.value = ''
  previewError.value = ''
}

function openAttachmentPicker() {
  fileInputRef.value?.click()
}

function removeComposerAttachment(attachmentId: string) {
  composerAttachments.value = composerAttachments.value.filter(
    attachment => attachment.id !== attachmentId,
  )
}

async function readImageFile(file: File): Promise<ChatAttachment> {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.addEventListener('load', () => {
      resolve({
        id: generateUUID(),
        dataUrl: String(reader.result ?? ''),
        mimeType: file.type,
        fileName: file.name,
      })
    })
    reader.addEventListener('error', () => {
      reject(new Error(`Failed to read image: ${file.name}`))
    })
    reader.readAsDataURL(file)
  })
}

async function handleAttachmentSelection(event: Event) {
  const inputElement = event.target as HTMLInputElement
  const files = Array.from(inputElement.files ?? [])
  inputElement.value = ''

  if (!files.length)
    return

  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  if (!imageFiles.length) {
    appMessage.warning('目前只支持上传图片')
    return
  }

  const nextAttachments = await Promise.all(imageFiles.map(readImageFile))
  composerAttachments.value = [...composerAttachments.value, ...nextAttachments]
}

function dataUrlToBase64(dataUrl: string) {
  const match = /^data:([^;]+);base64,(.+)$/.exec(dataUrl)
  if (!match)
    return null
  return {
    mimeType: match[1],
    content: match[2],
  }
}

function scrollToBottom() {
  if (scrollerRef.value)
    scrollerRef.value.scrollTop = scrollerRef.value.scrollHeight
}

async function loadAssistantContext() {
  try {
    const status = await getOpenClawManagerStatus()
    assistantConfig.value = status.configured
    contextError.value = ''
  }
  catch (error: any) {
    assistantConfig.value = null
    contextError.value = error?.message || 'OpenClaw unavailable'
  }
}

async function ensureResolvedOpenClawToken() {
  if (!openclawToken.value)
    openclawToken.value = await resolveOpenClawToken(props.openclawToken)

  console.info('[OpenClaw][chat-panel]', 'resolved token before chat action', {
    hasToken: Boolean(openclawToken.value),
  })

  return openclawToken.value
}

async function resetSessionBeforeFirstMessage(
  session: ChatSession,
  token?: string,
) {
  if (!session.needsNewCommand)
    return

  await openclawChatCompletions({
    token,
    sessionKey: session.sessionKey,
    messages: [{ role: 'user', content: '/new' }],
  })
  session.needsNewCommand = false
  session.updatedAt = Date.now()
}

async function send() {
  const textToSend = input.value.trim()
  const attachmentsToSend = [...composerAttachments.value]
  if ((!textToSend && attachmentsToSend.length === 0) || sending.value)
    return

  const session = ensureCurrentSession()
  const sessionId = session.id

  errorText.value = ''
  sending.value = true
  input.value = ''
  composerAttachments.value = []
  textareaKey.value += 1
  activeSidebar.value = 'chat'

  try {
    const token = await ensureResolvedOpenClawToken()
    await resetSessionBeforeFirstMessage(session, token)

    appendMessageToSession(sessionId, {
      id: generateUUID(),
      role: 'user',
      content: textToSend,
      createdAt: Date.now(),
      attachments: attachmentsToSend.length > 0 ? attachmentsToSend : undefined,
    })

    const activeSession = sessions.value.find(item => item.id === sessionId)
    if (!activeSession)
      throw new Error('Chat session not found')

    const result = await openclawChatCompletions({
      token,
      sessionKey: activeSession.sessionKey,
      attachments: attachmentsToSend
        .map((attachment) => {
          const parsed = dataUrlToBase64(attachment.dataUrl)
          if (!parsed)
            return null
          return {
            type: 'image' as const,
            mimeType: parsed.mimeType,
            fileName: attachment.fileName,
            content: parsed.content,
          }
        })
        .filter((attachment): attachment is NonNullable<typeof attachment> => Boolean(attachment)),
      onToolEvent: event => upsertToolMessage(sessionId, event),
      messages: [
        { role: 'system', content: text.systemPrompt },
        ...activeSession.messages
          .filter(message => message.role !== 'tool')
          .map(message => ({ role: message.role, content: message.content })),
      ],
    })

    appendMessageToSession(sessionId, {
      id: generateUUID(),
      role: 'assistant',
      content: result.text || text.emptyResponse,
      createdAt: Date.now(),
    })
  }
  catch (error: any) {
    const reason = error?.message || text.sendFailed
    errorText.value = reason

    if (session.messages.length > 0) {
      appendMessageToSession(sessionId, {
        id: generateUUID(),
        role: 'assistant',
        content: `${text.requestFailedPrefix}${reason}${text.requestFailedSuffix}`,
        createdAt: Date.now(),
      })
    }
  }
  finally {
    sending.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void send()
  }
}

function handleSidebarClick(key: SidebarKey) {
  if (key === 'chat') {
    startNewTask()
    return
  }

  activeSidebar.value = key
  activeFilter.value = 'all'
  previewArtifact.value = null
}

function handleQuickAction(type: 'context' | 'skills') {
  if (type === 'context') {
    openAttachmentPicker()
    return
  }

  activeSidebar.value = 'skills'
  activeFilter.value = 'all'
  appMessage.info(text.quickSkill)
}

function applyStarterCard(card: StarterCard) {
  activeSidebar.value = 'chat'
  input.value = card.prompt
}

function isSidebarItemActive(key: SidebarKey) {
  if (key === 'chat')
    return isNewTaskActive.value
  return activeSidebar.value === key
}

function isSessionActive(sessionId: string) {
  return currentSessionId.value === sessionId
}

async function deleteSession(sessionId: string) {
  const session = sessions.value.find(item => item.id === sessionId)
  if (!session || deletingSessionId.value === sessionId)
    return

  if (sending.value && currentSessionId.value === sessionId) {
    appMessage.warning('当前会话正在处理中，暂时不能删除')
    return
  }

  deletingSessionId.value = sessionId
  errorText.value = ''

  try {
    const token = await ensureResolvedOpenClawToken()
    await openclawDeleteSession({
      sessionKey: session.sessionKey,
      token,
    })

    const nextSessionId = resolveNextSessionIdAfterDelete(
      historySessions.value,
      sessionId,
      currentSessionId.value,
    )

    sessions.value = sessions.value.filter(item => item.id !== sessionId)

    if (nextSessionId)
      currentSessionId.value = nextSessionId
    else createAndActivateDraftSession(false)

    appMessage.success('会话已删除')
  }
  catch (error: any) {
    const reason = error?.message || '删除会话失败'
    errorText.value = reason
    appMessage.error(reason)
  }
  finally {
    deletingSessionId.value = ''
  }
}

watch(
  messages,
  async () => {
    if (!showConversation.value)
      return

    await nextTick()
    scrollToBottom()
  },
  { deep: true },
)

watch(showSettings, (open) => {
  if (!open)
    void loadAssistantContext()
})

watch(previewArtifact, (artifact) => {
  previewStatus.value = 'idle'
  previewRenderedHtml.value = ''
  previewPdfUrl.value = ''
  previewError.value = ''

  if (!artifact)
    return

  previewStatus.value = 'loading'

  void loadLocalFilePreview(artifact)
    .then((result) => {
      if (
        previewArtifact.value?.path !== artifact.path
        || previewArtifact.value?.createdAt !== artifact.createdAt
      ) {
        return
      }

      if (result.kind === 'pdf') {
        previewPdfUrl.value = result.dataUrl || ''
      }
      else {
        previewRenderedHtml.value = renderMarkdown(result.textContent || '')
      }

      previewStatus.value = 'ready'
    })
    .catch((error) => {
      if (
        previewArtifact.value?.path !== artifact.path
        || previewArtifact.value?.createdAt !== artifact.createdAt
      ) {
        return
      }

      previewError.value = error instanceof Error ? error.message : '文件预览失败'
      previewStatus.value = 'error'
    })
})

watch(
  [sessions, currentSessionId],
  () => {
    persistSessions()
  },
  { deep: true },
)

onMounted(async () => {
  if (!openclawToken.value)
    openclawToken.value = await resolveOpenClawToken(props.openclawToken)

  if (!currentSession.value) {
    const session = createDraftSession()
    sessions.value = [session]
    currentSessionId.value = session.id
  }

  await loadAssistantContext()
})
</script>

<template>
  <section
    class="astron-assistant h-full min-h-0 w-full overflow-hidden rounded-[28px] border border-white/60 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.96),_rgba(243,246,255,0.98)_42%,_rgba(236,241,255,0.96))] shadow-[0_20px_60px_rgba(127,145,193,0.16)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[linear-gradient(180deg,_rgba(25,27,35,0.96),_rgba(17,19,27,0.98))]"
  >
    <IMConnectPanel v-model:open="showSettings" />
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      multiple
      class="hidden"
      @change="handleAttachmentSelection"
    >

    <div class="flex h-full min-h-0">
      <aside
        class="flex w-[268px] shrink-0 flex-col border-r border-[rgba(139,153,196,0.14)] bg-[rgba(245,247,255,0.82)] px-4 py-5 backdrop-blur-xl dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.03)]"
      >
        <div class="space-y-2">
          <button
            v-for="item in sidebarItems"
            :key="item.key"
            type="button"
            class="group flex w-full items-start gap-3 rounded-[20px] border px-4 py-4 text-left transition-all duration-200"
            :class="
              isSidebarItemActive(item.key)
                ? 'border-[#d7ddff] bg-white shadow-[0_16px_32px_rgba(112,126,171,0.12)] dark:border-[rgba(120,135,255,0.35)] dark:bg-[rgba(255,255,255,0.06)]'
                : 'border-transparent bg-transparent hover:border-[rgba(139,153,196,0.18)] hover:bg-white/70 dark:hover:border-[rgba(255,255,255,0.1)] dark:hover:bg-[rgba(255,255,255,0.04)]'
            "
            @click="handleSidebarClick(item.key)"
          >
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[16px]"
              :class="
                isSidebarItemActive(item.key)
                  ? 'bg-[linear-gradient(135deg,#5b70ff,#7a8cff)] text-white'
                  : 'bg-white text-[rgba(61,74,117,0.88)] shadow-[inset_0_0_0_1px_rgba(146,159,201,0.16)] dark:bg-[rgba(255,255,255,0.06)] dark:text-white'
              "
            >
              <component :is="item.icon" />
            </div>
            <div class="min-w-0 pt-1">
              <div
                class="text-[16px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]"
              >
                {{ item.title }}
              </div>
              <div
                class="mt-1 text-[12px] leading-[18px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.55)]"
              >
                {{ item.description }}
              </div>
            </div>
          </button>
        </div>

        <div
          class="mt-4 rounded-[24px] border border-white/70 bg-white/72 p-3 shadow-[0_12px_24px_rgba(128,144,190,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.03)]"
        >
          <div class="mb-2 flex items-center justify-between">
            <div
              class="text-[13px] font-semibold text-[rgba(30,39,67,0.88)] dark:text-[rgba(255,255,255,0.86)]"
            >
              最近会话
            </div>
            <button
              type="button"
              class="text-[12px] text-[rgba(91,112,255,0.88)]"
              @click="activeSidebar = 'history'"
            >
              查看全部
            </button>
          </div>
          <div v-if="recentSessions.length" class="space-y-2">
            <div
              v-for="session in recentSessions"
              :key="session.id"
              class="group relative"
            >
              <button
                type="button"
                class="w-full rounded-[18px] border px-3 py-3 pr-11 text-left transition"
                :class="
                  isSessionActive(session.id)
                    ? 'border-[#d7ddff] bg-white shadow-[0_12px_24px_rgba(112,126,171,0.12)] dark:border-[rgba(120,135,255,0.35)] dark:bg-[rgba(255,255,255,0.08)]'
                    : 'border-transparent bg-[rgba(244,247,255,0.9)] hover:border-[#d7ddff] hover:bg-white dark:bg-[rgba(255,255,255,0.04)]'
                "
                @click="activateSession(session.id)"
              >
                <div
                  class="truncate text-[13px] font-medium text-[rgba(30,39,67,0.92)] dark:text-[rgba(255,255,255,0.9)]"
                >
                  {{ session.title }}
                </div>
                <div
                  class="mt-1 line-clamp-2 text-[12px] leading-[18px] text-[rgba(71,83,120,0.6)] dark:text-[rgba(255,255,255,0.5)]"
                >
                  {{ getSessionPreview(session) }}
                </div>
              </button>
              <button
                type="button"
                :aria-label="'删除会话'"
                class="absolute top-3 right-3 flex h-7 w-7 items-center justify-center rounded-full border border-[rgba(139,153,196,0.18)] bg-white/96 text-[rgba(71,83,120,0.66)] opacity-0 transition group-hover:opacity-100 group-focus-within:opacity-100 dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(18,20,28,0.92)] dark:text-[rgba(255,255,255,0.62)]"
                :class="
                  deletingSessionId === session.id || (sending && currentSessionId === session.id)
                    ? 'pointer-events-none'
                    : 'hover:border-[rgba(255,92,92,0.24)] hover:text-[#d94841]'
                "
                :disabled="deletingSessionId === session.id || (sending && currentSessionId === session.id)"
                @click.stop="deleteSession(session.id)"
              >
                <DeleteOutlined />
              </button>
            </div>
          </div>
          <div
            v-else
            class="rounded-[18px] border border-dashed border-[rgba(147,159,198,0.28)] px-3 py-4 text-[12px] leading-[18px] text-[rgba(71,83,120,0.56)] dark:border-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.5)]"
          >
            {{ text.historyEmpty }}
          </div>
        </div>

        <div
          class="mt-auto rounded-[24px] border border-white/70 bg-white/88 p-4 shadow-[0_16px_30px_rgba(128,144,190,0.12)] backdrop-blur dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[linear-gradient(135deg,#6d7dff,#8ea4ff)] text-[18px] font-semibold text-white"
            >
              {{ userInitial }}
            </div>
            <div class="min-w-0 flex-1">
              <div
                class="truncate text-[16px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]"
              >
                {{ userName }}
              </div>
              <div
                class="truncate text-[12px] text-[rgba(71,83,120,0.6)] dark:text-[rgba(255,255,255,0.5)]"
              >
                {{ workspaceName }}
              </div>
            </div>
          </div>
          <button
            type="button"
            class="mt-4 flex w-full items-center justify-between rounded-[16px] border border-[rgba(125,141,188,0.16)] bg-[rgba(245,247,255,0.96)] px-4 py-3 text-left transition hover:border-[rgba(91,112,255,0.26)] hover:bg-white dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
            @click="showSettings = true"
          >
            <div class="min-w-0">
              <div
                class="text-[14px] font-medium text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.9)]"
              >
                {{ text.assistantSettings }}
              </div>
              <div
                class="mt-1 text-[12px] text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.5)]"
              >
                {{ text.assistantSettingsDesc }}
              </div>
            </div>
            <div
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-[rgba(68,83,128,0.88)] shadow-[inset_0_0_0_1px_rgba(146,159,201,0.18)] dark:bg-[rgba(255,255,255,0.06)] dark:text-white"
            >
              <SettingOutlined />
            </div>
          </button>
        </div>
      </aside>

      <div class="min-w-0 flex-1 p-4 pl-0">
        <div
          class="flex h-full min-h-0 flex-col gap-4 overflow-hidden rounded-[26px] bg-[linear-gradient(180deg,_rgba(255,255,255,0.94),_rgba(250,252,255,0.9))] px-6 py-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.6)] lg:flex-row dark:bg-[linear-gradient(180deg,_rgba(20,22,30,0.96),_rgba(18,20,28,0.98))]"
        >
          <div class="min-w-0 flex flex-1 flex-col overflow-hidden">
          <div
            v-if="showHistoryPanel"
            class="mx-auto flex h-full min-h-0 w-full max-w-[980px] flex-col overflow-hidden"
          >
            <div
              class="flex items-center justify-between gap-4 border-b border-[rgba(139,153,196,0.12)] pb-5 dark:border-[rgba(255,255,255,0.08)]"
            >
              <div>
                <div
                  class="text-[26px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]"
                >
                  {{ text.historyTitle }}
                </div>
                <div
                  class="mt-2 text-[14px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]"
                >
                  选择一个会话继续对话，OpenClaw 会沿用对应的 sessionKey。
                </div>
              </div>
              <button
                type="button"
                class="assistant-select-btn"
                @click="startNewTask"
              >
                <PlusOutlined />
                <span>{{ text.newTask }}</span>
              </button>
            </div>

            <div
              v-if="historySessions.length"
              class="mt-6 grid min-h-0 flex-1 gap-4 overflow-auto pr-1 md:grid-cols-2 xl:grid-cols-3"
            >
              <div
                v-for="session in historySessions"
                :key="session.id"
                class="group relative"
              >
                <button
                  type="button"
                  class="flex min-h-[208px] w-full flex-col rounded-[28px] border p-5 pr-14 text-left shadow-[0_18px_34px_rgba(138,150,185,0.1)] transition-all duration-200 hover:-translate-y-1 hover:border-[#d7ddff] hover:shadow-[0_24px_42px_rgba(117,132,180,0.16)]"
                  :class="
                    isSessionActive(session.id)
                      ? 'border-[#d7ddff] bg-white shadow-[0_24px_42px_rgba(117,132,180,0.16)] dark:border-[rgba(120,135,255,0.35)] dark:bg-[rgba(255,255,255,0.08)]'
                      : 'border-white/80 bg-white/88 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]'
                  "
                  @click="activateSession(session.id)"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <div
                        class="truncate text-[18px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]"
                      >
                        {{ session.title }}
                      </div>
                      <div
                        class="mt-2 text-[12px] text-[rgba(71,83,120,0.56)] dark:text-[rgba(255,255,255,0.48)]"
                      >
                        {{ formatSessionTime(session.updatedAt) }}
                      </div>
                    </div>
                    <div
                      class="rounded-full bg-[rgba(91,112,255,0.1)] px-3 py-1 text-[12px] font-medium text-[rgba(61,76,148,0.92)] dark:bg-[rgba(91,112,255,0.18)] dark:text-[rgba(255,255,255,0.86)]"
                    >
                      {{ session.messages.length }} {{ text.messageCount }}
                    </div>
                  </div>

                  <div
                    class="mt-5 flex-1 rounded-[20px] bg-[rgba(244,247,255,0.82)] px-4 py-4 text-[13px] leading-[22px] text-[rgba(71,83,120,0.66)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.55)]"
                  >
                    {{ getSessionPreview(session) }}
                  </div>

                  <div
                    class="mt-5 inline-flex items-center gap-2 text-[13px] font-medium text-[rgba(91,112,255,0.92)] dark:text-[rgba(143,157,255,0.92)]"
                  >
                    <HistoryOutlined />
                    <span>{{ text.continueChat }}</span>
                  </div>
                </button>
                <button
                  type="button"
                  :aria-label="'删除会话'"
                  class="absolute top-4 right-4 flex h-9 w-9 items-center justify-center rounded-full border border-[rgba(139,153,196,0.18)] bg-white/96 text-[rgba(71,83,120,0.66)] opacity-0 transition group-hover:opacity-100 group-focus-within:opacity-100 dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(18,20,28,0.92)] dark:text-[rgba(255,255,255,0.62)]"
                  :class="
                    deletingSessionId === session.id || (sending && currentSessionId === session.id)
                      ? 'pointer-events-none'
                      : 'hover:border-[rgba(255,92,92,0.24)] hover:text-[#d94841]'
                  "
                  :disabled="deletingSessionId === session.id || (sending && currentSessionId === session.id)"
                  @click.stop="deleteSession(session.id)"
                >
                  <DeleteOutlined />
                </button>
              </div>
            </div>

            <div v-else class="flex flex-1 items-center justify-center">
              <div class="max-w-[440px] text-center">
                <div
                  class="mx-auto flex h-20 w-20 items-center justify-center rounded-[28px] bg-[linear-gradient(135deg,#eef2ff,#f8fbff)] text-[30px] text-[rgba(61,76,148,0.92)] shadow-[0_18px_34px_rgba(138,150,185,0.08)] dark:bg-[rgba(91,112,255,0.14)] dark:text-white"
                >
                  <HistoryOutlined />
                </div>
                <div
                  class="mt-6 text-[24px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]"
                >
                  {{ text.historyEmpty }}
                </div>
                <div
                  class="mt-3 text-[14px] leading-[24px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]"
                >
                  {{ text.historyEmptyDesc }}
                </div>
              </div>
            </div>
          </div>

          <div
            v-else-if="showConversation"
            ref="scrollerRef"
            class="mx-auto flex-1 min-h-0 w-full max-w-[960px] overflow-auto pb-6"
          >
            <div class="space-y-4 px-1 pt-2">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <div
                    class="text-[20px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]"
                  >
                    {{ currentSessionTitle }}
                  </div>
                  <div
                    class="mt-1 text-[13px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]"
                  >
                    {{ text.workspaceLabel }}：{{ workspaceName }}
                  </div>
                </div>
                <button
                  type="button"
                  class="assistant-select-btn"
                  @click="showSettings = true"
                >
                  <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                </button>
              </div>
              <div
                v-if="contextError || errorText"
                class="rounded-[18px] border border-[#ffd6d1] bg-[#fff6f4] px-4 py-3 text-[13px] text-[#b44737] dark:border-[rgba(255,120,102,0.28)] dark:bg-[rgba(255,120,102,0.12)] dark:text-[#ffb2a5]"
              >
                {{ errorText || contextError }}
              </div>
              <div
                v-for="(message, index) in messages"
                :key="message.id"
                class="flex"
                :class="
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                "
              >
                <div
                  v-if="message.role !== 'tool'"
                  class="assistant-copyable max-w-[88%] rounded-[24px] px-5 py-4 text-[14px] leading-[24px] break-words shadow-[0_12px_26px_rgba(138,150,185,0.08)]"
                  :class="
                    message.role === 'user'
                      ? 'border border-[#d7ddff] bg-[linear-gradient(135deg,#f2f4ff,#edf3ff)] text-[rgba(30,39,67,0.95)] dark:border-[rgba(120,135,255,0.3)] dark:bg-[rgba(91,112,255,0.14)] dark:text-white'
                      : 'border border-white/70 bg-white text-[rgba(30,39,67,0.92)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.88)]'
                  "
                >
                  <div
                    v-if="message.attachments?.length"
                    class="mb-3 grid grid-cols-1 gap-3 sm:grid-cols-2"
                  >
                    <div
                      v-for="attachment in message.attachments"
                      :key="attachment.id"
                      class="overflow-hidden rounded-[18px] border border-white/50 bg-white/60 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
                    >
                      <img
                        :src="attachment.dataUrl"
                        :alt="attachment.fileName"
                        class="block h-auto max-h-[280px] w-full object-cover"
                      >
                    </div>
                  </div>
                  <div
                    class="assistant-markdown"
                    v-html="renderMarkdown(message.content)"
                  />
                  <button
                    v-if="message.role === 'assistant' && getAssistantFileArtifact(index)"
                    type="button"
                    class="assistant-file-card mt-4"
                    @click="openArtifactPreview(getAssistantFileArtifact(index))"
                  >
                    <div class="assistant-file-card__icon">
                      <FileTextOutlined />
                    </div>
                    <div class="min-w-0 flex-1 text-left">
                      <div class="truncate text-[15px] font-medium text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]">
                        {{ getAssistantFileArtifact(index)?.title }}
                      </div>
                      <div class="mt-1 truncate text-[12px] text-[rgba(71,83,120,0.56)] dark:text-[rgba(255,255,255,0.48)]">
                        创建时间：{{ formatSessionTime(getAssistantFileArtifact(index)!.createdAt) }}
                      </div>
                    </div>
                  </button>
                </div>
                <div
                  v-else
                  class="assistant-copyable w-full max-w-[90%] rounded-[22px] border border-[#ece7e3] bg-[#fbfaf8] px-5 py-4 shadow-[0_12px_26px_rgba(138,150,185,0.06)] dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(255,255,255,0.04)]"
                >
                  <details class="group">
                    <summary class="flex cursor-pointer list-none items-center justify-between gap-3">
                      <div class="min-w-0">
                        <div
                          class="text-[14px] font-medium text-[rgba(30,39,67,0.92)] dark:text-[rgba(255,255,255,0.88)]"
                        >
                          {{ getToolSummary(message).title }}
                        </div>
                        <div
                          v-if="getToolSummary(message).summary"
                          class="mt-1 truncate text-[12px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.48)]"
                        >
                          {{ getToolSummary(message).summary }}
                        </div>
                        <div
                          class="mt-1 text-[12px] text-[rgba(71,83,120,0.56)] dark:text-[rgba(255,255,255,0.45)]"
                        >
                          {{
                            message.toolStatus === "completed"
                              ? text.toolCompleted
                              : text.toolRunning
                          }}
                        </div>
                      </div>
                      <div class="flex items-center gap-3">
                        <div
                          class="h-2.5 w-2.5 rounded-full"
                          :class="
                            message.toolStatus === 'completed'
                              ? 'bg-[#52c41a]'
                              : 'bg-[#faad14]'
                          "
                        />
                        <span class="text-[12px] text-[rgba(71,83,120,0.56)] transition group-open:rotate-180 dark:text-[rgba(255,255,255,0.45)]">
                          <DownOutlined />
                        </span>
                      </div>
                    </summary>
                    <div class="mt-3 space-y-3">
                      <div
                        v-for="line in getToolSummary(message).detailLines"
                        :key="line"
                        class="rounded-[14px] bg-[#f4f1ed] px-4 py-3 text-[12px] leading-[20px] break-words text-[rgba(0,0,0,0.72)] dark:bg-[rgba(0,0,0,0.22)] dark:text-[rgba(255,255,255,0.78)]"
                      >
                        {{ line }}
                      </div>
                      <pre
                        v-if="message.content"
                        class="max-h-[220px] overflow-auto rounded-[16px] bg-[#f4f1ed] px-4 py-3 text-[12px] leading-[20px] whitespace-pre-wrap break-words text-[rgba(0,0,0,0.72)] dark:bg-[rgba(0,0,0,0.22)] dark:text-[rgba(255,255,255,0.78)]"
                      >{{ message.content }}</pre>
                      <div
                        v-else-if="message.toolStatus === 'completed'"
                        class="rounded-[14px] bg-[#f4f1ed] px-4 py-3 text-[12px] leading-[20px] text-[rgba(0,0,0,0.72)] dark:bg-[rgba(0,0,0,0.22)] dark:text-[rgba(255,255,255,0.78)]"
                      >
                        No output - tool completed successfully.
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="flex-1 min-h-0 overflow-auto">
            <div
              class="mx-auto flex w-full max-w-[980px] flex-col items-center px-4 pt-8 pb-4"
            >
              <div
                class="rounded-full border border-white/80 bg-white/80 px-4 py-2 text-[12px] font-medium tracking-[0.18em] text-[rgba(87,101,148,0.72)] uppercase shadow-[0_10px_18px_rgba(138,150,185,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.55)]"
              >
                {{ text.heroLabel }}
              </div>
              <div
                class="mt-6 flex flex-wrap items-center justify-center gap-5"
              >
                <div
                  class="flex h-[84px] w-[84px] items-center justify-center rounded-[28px] bg-[linear-gradient(135deg,#ff7e66,#ffb56b)] text-white shadow-[0_20px_30px_rgba(255,149,111,0.28)]"
                >
                  <ThunderboltOutlined class="text-[42px]" />
                </div>
                <div class="text-center sm:text-left">
                  <div
                    class="bg-[linear-gradient(120deg,#293a8a_0%,#5c72ff_42%,#d96ea0_100%)] bg-clip-text text-[52px] leading-none font-black tracking-[-0.06em] text-transparent sm:text-[72px]"
                  >
                    ASTRON
                  </div>
                  <div
                    class="mt-2 text-[15px] font-medium text-[rgba(71,83,120,0.68)] dark:text-[rgba(255,255,255,0.55)]"
                  >
                    {{ heroTitle }}
                  </div>
                </div>
              </div>
              <div
                class="mt-4 text-center text-[14px] leading-[24px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]"
              >
                {{ heroDescription }}
              </div>
              <div
                class="mt-4 inline-flex items-center gap-3 rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[13px] shadow-[0_10px_18px_rgba(138,150,185,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
              >
                <span
                  class="text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.48)]"
                >{{ text.workspaceLabel }}：</span>
                <span
                  class="font-medium text-[rgba(30,39,67,0.92)] dark:text-[rgba(255,255,255,0.9)]"
                >{{ workspaceName }}</span>
                <span
                  class="text-[12px] font-medium"
                  :class="connectionStatusClass"
                >{{ connectionStatusText }}</span>
              </div>
              <div
                v-if="contextError || errorText"
                class="mt-8 w-full max-w-[860px] rounded-[18px] border border-[#ffd6d1] bg-[#fff6f4] px-4 py-3 text-[13px] text-[#b44737] dark:border-[rgba(255,120,102,0.28)] dark:bg-[rgba(255,120,102,0.12)] dark:text-[#ffb2a5]"
              >
                {{ errorText || contextError }}
              </div>
              <div
                v-if="composerAttachments.length"
                class="mt-6 grid w-full max-w-[860px] grid-cols-2 gap-3 sm:grid-cols-3"
              >
                <div
                  v-for="attachment in composerAttachments"
                  :key="attachment.id"
                  class="relative overflow-hidden rounded-[22px] border border-white/80 bg-white/90 p-2 shadow-[0_12px_24px_rgba(138,150,185,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
                >
                  <img
                    :src="attachment.dataUrl"
                    :alt="attachment.fileName"
                    class="h-28 w-full rounded-[16px] object-cover"
                  >
                  <button
                    type="button"
                    class="absolute top-4 right-4 flex h-7 w-7 items-center justify-center rounded-full bg-[rgba(20,25,43,0.78)] text-[15px] text-white transition hover:bg-[rgba(20,25,43,0.92)]"
                    @click="removeComposerAttachment(attachment.id)"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div
                class="mt-8 w-full max-w-[860px] rounded-[28px] border border-white/80 bg-white/92 p-4 shadow-[0_20px_40px_rgba(138,150,185,0.12)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
              >
                <a-textarea
                  :key="textareaKey"
                  v-model:value="input"
                  :placeholder="props.placeholder || text.placeholder"
                  :auto-size="{ minRows: 3, maxRows: 6 }"
                  :disabled="sending"
                  class="assistant-textarea"
                  @keydown="handleKeydown"
                />
                <div
                  class="mt-4 flex flex-wrap items-center justify-between gap-3"
                >
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      class="assistant-round-btn"
                      @click="handleQuickAction('context')"
                    >
                      <PlusOutlined />
                    </button>
                    <button
                      type="button"
                      class="assistant-round-btn"
                      @click="handleQuickAction('skills')"
                    >
                      <ThunderboltOutlined />
                    </button>
                  </div>
                  <div class="flex items-center gap-3">
                    <button
                      type="button"
                      class="assistant-select-btn"
                      @click="showSettings = true"
                    >
                      <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                    </button>
                    <a-button
                      type="primary"
                      shape="circle"
                      :disabled="!canSend"
                      :loading="sending"
                      @click="send"
                    >
                      <template #icon>
                        <SendOutlined />
                      </template>
                    </a-button>
                  </div>
                </div>
              </div>
              <div class="mt-10 w-full max-w-[980px]">
                <div class="flex flex-wrap items-center gap-3">
                  <span
                    class="text-[16px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]"
                  >{{ starterTitle }}</span>
                  <button
                    v-for="filter in starterFilters"
                    :key="filter.key"
                    type="button"
                    class="rounded-full px-4 py-2 text-[13px] font-medium transition"
                    :class="
                      activeFilter === filter.key
                        ? 'bg-[linear-gradient(135deg,#eef2ff,#edf5ff)] text-[rgba(45,60,106,0.92)] shadow-[0_10px_20px_rgba(138,150,185,0.1)] dark:bg-[rgba(91,112,255,0.16)] dark:text-white'
                        : 'bg-transparent text-[rgba(71,83,120,0.62)] hover:bg-white/80 hover:text-[rgba(45,60,106,0.92)] dark:text-[rgba(255,255,255,0.5)] dark:hover:bg-[rgba(255,255,255,0.04)] dark:hover:text-white'
                    "
                    @click="activeFilter = filter.key"
                  >
                    {{ filter.label }}
                  </button>
                </div>
                <div class="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <button
                    v-for="card in visibleStarterCards"
                    :key="card.id"
                    type="button"
                    class="group rounded-[24px] border border-white/80 bg-white/88 p-5 text-left shadow-[0_18px_34px_rgba(138,150,185,0.1)] transition-all duration-200 hover:-translate-y-1 hover:border-[#d7ddff] hover:shadow-[0_24px_42px_rgba(117,132,180,0.16)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
                    @click="applyStarterCard(card)"
                  >
                    <div
                      class="flex h-12 w-12 items-center justify-center rounded-[16px] bg-[linear-gradient(135deg,#eef2ff,#fef0f3)] text-[rgba(62,76,120,0.9)] dark:bg-[rgba(91,112,255,0.14)] dark:text-white"
                    >
                      <component :is="card.icon" />
                    </div>
                    <div
                      class="mt-5 text-[18px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]"
                    >
                      {{ card.title }}
                    </div>
                    <div
                      class="mt-3 text-[13px] leading-[22px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]"
                    >
                      {{ card.description }}
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="showConversation"
            class="mx-auto mt-auto w-full max-w-[960px]"
          >
            <div
              class="rounded-[26px] border border-white/80 bg-white/92 p-4 shadow-[0_20px_40px_rgba(138,150,185,0.12)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
            >
              <div class="mb-3 flex items-center justify-between gap-3">
                <div
                  class="text-[13px] text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.48)]"
                >
                  {{
                    sending
                      ? text.sending
                      : `${text.workspaceLabel}：${workspaceName}`
                    }} 
                </div>
                <button
                  type="button"
                  class="assistant-select-btn"
                  @click="showSettings = true"
                >
                  <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                </button>
              </div>
              <div
                v-if="composerAttachments.length"
                class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4"
              >
                <div
                  v-for="attachment in composerAttachments"
                  :key="attachment.id"
                  class="relative overflow-hidden rounded-[20px] border border-white/80 bg-white/88 p-2 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
                >
                  <img
                    :src="attachment.dataUrl"
                    :alt="attachment.fileName"
                    class="h-24 w-full rounded-[14px] object-cover"
                  >
                  <button
                    type="button"
                    class="absolute top-3 right-3 flex h-7 w-7 items-center justify-center rounded-full bg-[rgba(20,25,43,0.78)] text-[15px] text-white transition hover:bg-[rgba(20,25,43,0.92)]"
                    @click="removeComposerAttachment(attachment.id)"
                  >
                    ×
                  </button>
                </div>
              </div>
              <a-textarea
                :key="textareaKey"
                v-model:value="input"
                :placeholder="props.placeholder || text.placeholder"
                :auto-size="{ minRows: 2, maxRows: 6 }"
                :disabled="sending"
                class="assistant-textarea"
                @keydown="handleKeydown"
              />
              <div class="mt-4 flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    class="assistant-round-btn"
                    @click="handleQuickAction('context')"
                  >
                    <PlusOutlined />
                  </button>
                  <button
                    type="button"
                    class="assistant-round-btn"
                    @click="handleQuickAction('skills')"
                  >
                    <ThunderboltOutlined />
                  </button>
                </div>
                <a-button
                  type="primary"
                  shape="circle"
                  :disabled="!canSend"
                  :loading="sending"
                  @click="send"
                >
                  <template #icon>
                    <SendOutlined />
                  </template>
                </a-button>
              </div>
            </div>
          </div>
          </div>
          <aside
            v-if="previewArtifact && showConversation"
            class="flex min-h-0 flex-col overflow-hidden rounded-[24px] border border-white/70 bg-[rgba(250,252,255,0.92)] shadow-[0_18px_40px_rgba(138,150,185,0.12)] lg:w-[380px] lg:shrink-0 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]"
          >
            <div class="flex items-center justify-between gap-3 border-b border-[rgba(139,153,196,0.12)] px-5 py-4 dark:border-[rgba(255,255,255,0.08)]">
              <div class="min-w-0">
                <div class="truncate text-[16px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]">
                  {{ previewArtifact.title }}
                </div>
                <div class="mt-1 truncate text-[12px] text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.48)]">
                  {{ previewArtifact.path }}
                </div>
              </div>
              <button
                type="button"
                class="flex h-9 w-9 items-center justify-center rounded-full bg-[rgba(240,244,255,0.92)] text-[18px] text-[rgba(55,69,110,0.82)] transition hover:bg-white dark:bg-[rgba(255,255,255,0.06)] dark:text-[rgba(255,255,255,0.82)]"
                @click="closeFilePreview"
              >
                ×
              </button>
            </div>
            <div class="border-b border-[rgba(139,153,196,0.12)] px-5 py-3 text-[12px] text-[rgba(71,83,120,0.58)] dark:border-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.48)]">
              创建时间：{{ formatSessionTime(previewArtifact.createdAt) }}
            </div>
            <div class="min-h-0 flex-1 overflow-auto px-5 py-5">
              <div
                v-if="previewStatus === 'loading'"
                class="flex h-full min-h-[240px] items-center justify-center rounded-[18px] border border-dashed border-[rgba(147,159,198,0.28)] text-[13px] text-[rgba(71,83,120,0.62)] dark:border-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.5)]"
              >
                正在加载预览...
              </div>
              <iframe
                v-else-if="previewStatus === 'ready' && previewPdfUrl"
                :src="previewPdfUrl"
                class="assistant-file-preview-frame"
                title="文件预览"
              />
              <div
                v-else-if="previewStatus === 'ready' && previewRenderedHtml"
                class="assistant-file-preview"
                v-html="previewRenderedHtml"
              />
              <div
                v-else-if="previewStatus === 'error'"
                class="rounded-[18px] border border-[#ffd6d1] bg-[#fff6f4] px-4 py-5 text-[13px] leading-[22px] text-[#b44737] dark:border-[rgba(255,120,102,0.28)] dark:bg-[rgba(255,120,102,0.12)] dark:text-[#ffb2a5]"
              >
                {{ previewError }}
              </div>
              <div
                v-else
                class="rounded-[18px] border border-dashed border-[rgba(147,159,198,0.28)] px-4 py-5 text-[13px] leading-[22px] text-[rgba(71,83,120,0.6)] dark:border-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.5)]"
              >
                当前只能预览工具调用里直接带回的文本内容，这个文件没有可用的内联内容。
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.assistant-round-btn {
  display: flex;
  height: 44px;
  width: 44px;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  border: 1px solid #e5eaf7;
  background: #f9fbff;
  color: rgba(65, 79, 123, 0.82);
  transition: all 0.2s ease;
}

.assistant-round-btn:hover {
  border-color: #cfd8f6;
  background: #fff;
}

.assistant-select-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 9999px;
  border: 1px solid #dfe5f6;
  background: #fafbff;
  padding: 8px 16px;
  font-size: 13px;
  color: rgba(50, 63, 103, 0.88);
  transition: all 0.2s ease;
}

.assistant-select-btn:hover {
  border-color: #cfd8f6;
  background: #fff;
}

.assistant-markdown {
  word-break: break-word;
}

.assistant-copyable,
.assistant-copyable * {
  user-select: text;
  -webkit-user-select: text;
}

.assistant-markdown :deep(p) {
  margin: 0 0 8px;
}

.assistant-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-markdown :deep(ul),
.assistant-markdown :deep(ol) {
  margin: 0 0 8px;
  padding-left: 20px;
}

.assistant-markdown :deep(li + li) {
  margin-top: 4px;
}

.assistant-markdown :deep(pre) {
  overflow: auto;
  margin: 8px 0;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f4f1ed;
  font-size: 12px;
  line-height: 18px;
}

.assistant-markdown :deep(code) {
  padding: 1px 4px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.06);
  font-size: 12px;
}

.assistant-markdown :deep(pre code) {
  padding: 0;
  background: transparent;
}

.assistant-markdown :deep(blockquote) {
  margin: 8px 0;
  padding-left: 12px;
  border-left: 3px solid #d8dbe8;
  color: rgba(0, 0, 0, 0.6);
}

.assistant-markdown :deep(a) {
  color: #1677ff;
  text-decoration: underline;
}

.assistant-markdown :deep(table) {
  width: 100%;
  margin: 8px 0;
  border-collapse: collapse;
  font-size: 12px;
}

.assistant-markdown :deep(th),
.assistant-markdown :deep(td) {
  padding: 6px 8px;
  border: 1px solid #e5e7ef;
  text-align: left;
}

.assistant-textarea :deep(textarea.ant-input) {
  border: none;
  box-shadow: none;
  padding: 0;
  font-size: 15px;
  line-height: 24px;
  background: transparent;
}

.assistant-textarea :deep(textarea.ant-input::placeholder) {
  color: rgba(71, 83, 120, 0.45);
}

.assistant-textarea :deep(.ant-input-textarea-show-count::after) {
  display: none;
}

.assistant-file-card {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 14px;
  border-radius: 18px;
  border: 1px solid #dde5f4;
  background: #fff;
  padding: 14px 16px;
  transition: all 0.2s ease;
}

.assistant-file-card:hover {
  border-color: #c6d3ef;
  background: #fbfcff;
  box-shadow: 0 10px 24px rgba(138, 150, 185, 0.08);
}

.assistant-file-card__icon {
  display: flex;
  height: 40px;
  width: 40px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: rgba(22, 119, 255, 0.08);
  color: #1677ff;
  font-size: 18px;
}

.assistant-file-preview {
  color: rgba(30, 39, 67, 0.9);
  word-break: break-word;
}

.assistant-file-preview-frame {
  height: 100%;
  min-height: 640px;
  width: 100%;
  border: none;
  border-radius: 18px;
  background: #fff;
}

.assistant-file-preview :deep(h1),
.assistant-file-preview :deep(h2),
.assistant-file-preview :deep(h3),
.assistant-file-preview :deep(h4) {
  margin: 0 0 16px;
  color: rgba(30, 39, 67, 0.96);
  line-height: 1.3;
}

.assistant-file-preview :deep(p) {
  margin: 0 0 12px;
  line-height: 1.8;
}

.assistant-file-preview :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-file-preview :deep(ul),
.assistant-file-preview :deep(ol) {
  margin: 0 0 12px;
  padding-left: 22px;
}

.assistant-file-preview :deep(li + li) {
  margin-top: 6px;
}

.assistant-file-preview :deep(pre) {
  overflow: auto;
  margin: 14px 0;
  padding: 14px 16px;
  border-radius: 16px;
  background: #f4f6fb;
  font-size: 12px;
  line-height: 20px;
}

.assistant-file-preview :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.06);
  font-size: 12px;
}

.assistant-file-preview :deep(pre code) {
  padding: 0;
  background: transparent;
}

.assistant-file-preview :deep(blockquote) {
  margin: 14px 0;
  padding-left: 12px;
  border-left: 3px solid #d7deef;
  color: rgba(71, 83, 120, 0.72);
}

.assistant-file-preview :deep(table) {
  width: 100%;
  margin: 14px 0;
  border-collapse: collapse;
}

.assistant-file-preview :deep(th),
.assistant-file-preview :deep(td) {
  padding: 8px 10px;
  border: 1px solid #e3e9f6;
  text-align: left;
}

.assistant-file-preview :deep(a) {
  color: #1677ff;
  text-decoration: underline;
}

.dark .assistant-round-btn {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
}

.dark .assistant-round-btn:hover {
  background: rgba(255, 255, 255, 0.06);
}

.dark .assistant-select-btn {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.88);
}

.dark .assistant-select-btn:hover {
  background: rgba(255, 255, 255, 0.06);
}

.dark .assistant-markdown :deep(pre) {
  background: rgba(0, 0, 0, 0.2);
}

.dark .assistant-markdown :deep(code) {
  background: rgba(255, 255, 255, 0.08);
}

.dark .assistant-markdown :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.62);
}

.dark .assistant-markdown :deep(th),
.dark .assistant-markdown :deep(td) {
  border-color: rgba(255, 255, 255, 0.12);
}

.dark .assistant-file-card {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
}

.dark .assistant-file-card:hover {
  background: rgba(255, 255, 255, 0.06);
  box-shadow: none;
}

.dark .assistant-file-card__icon {
  background: rgba(22, 119, 255, 0.16);
}

.dark .assistant-file-preview {
  color: rgba(255, 255, 255, 0.84);
}

.dark .assistant-file-preview-frame {
  background: rgba(255, 255, 255, 0.04);
}

.dark .assistant-file-preview :deep(h1),
.dark .assistant-file-preview :deep(h2),
.dark .assistant-file-preview :deep(h3),
.dark .assistant-file-preview :deep(h4) {
  color: rgba(255, 255, 255, 0.92);
}

.dark .assistant-file-preview :deep(pre) {
  background: rgba(0, 0, 0, 0.22);
}

.dark .assistant-file-preview :deep(code) {
  background: rgba(255, 255, 255, 0.08);
}

.dark .assistant-file-preview :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.58);
}

.dark .assistant-file-preview :deep(th),
.dark .assistant-file-preview :deep(td) {
  border-color: rgba(255, 255, 255, 0.12);
}

.dark .assistant-textarea :deep(textarea.ant-input::placeholder) {
  color: rgba(255, 255, 255, 0.36);
}
</style>
