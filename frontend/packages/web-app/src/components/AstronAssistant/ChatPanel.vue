<script setup lang="ts">
import {
  AppstoreOutlined,
  ClockCircleOutlined,
  CodeOutlined,
  DatabaseOutlined,
  DownOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
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

import type { OpenClawToolEvent } from '@/api/openclaw'
import { openclawChatCompletions } from '@/api/openclaw'
import type { OpenClawManagerCurrentConfig } from '@/api/openclaw-manager'
import { getOpenClawManagerStatus } from '@/api/openclaw-manager'
import { useUserStore } from '@/stores/useUserStore'

import IMConnectPanel from './IMConnectPanel.vue'

type SidebarKey = 'chat' | 'skills' | 'schedule'
type StarterFilter = 'all' | 'workflow' | 'data' | 'integration' | 'daily' | 'monitoring'
type CardSection = Exclude<SidebarKey, 'chat'>

type ChatMessage
  = | { id: string, role: 'user' | 'assistant', content: string, createdAt: number }
    | {
      id: string
      role: 'tool'
      content: string
      createdAt: number
      toolCallId: string
      toolName: string
      toolStatus: 'running' | 'completed'
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

const text = {
  title: 'Astron 助理',
  placeholder: '需要 Astron 帮你处理什么？按 Enter 发送，Shift + Enter 换行',
  heroLabel: 'AI 组件工作台',
  workspaceLabel: '已连接工作区',
  sending: 'Astron 正在处理中…',
  send: '发送',
  sendFailed: '发送失败',
  requestFailedPrefix: '（请求 OpenClaw 失败）',
  requestFailedSuffix: '。请确认 OpenClaw gateway 已在本机启动，并监听 19878 端口。',
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
  heroChat: '告诉 Astron，你想自动化什么',
  heroSkills: '直接复用一套成熟的 AI 技能',
  heroSchedule: '把重复执行的任务交给计划调度',
  heroChatDesc: '支持流程设计、脚本生成、调度编排和本地 OpenClaw 协同分析。',
  heroSkillsDesc: '从常见自动化场景里挑一个起点，快速生成更贴近业务的任务描述。',
  heroScheduleDesc: '先定义执行目标，再补充时间、触发方式和通知动作。',
  allSkills: '全部技能',
  workflow: '流程设计',
  data: '数据处理',
  integration: '系统集成',
  allSchedules: '全部计划',
  daily: '日常执行',
  monitoring: '监控告警',
  newTask: '新的任务',
  newTaskDesc: '开始一轮新对话',
  skillCenter: '技能中心',
  skillCenterDesc: '挑选常见场景模板',
  scheduleTask: '定时任务',
  scheduleTaskDesc: '规划自动执行任务',
  userFallback: 'Astron 用户',
  workspaceFallback: '默认工作区',
  systemPrompt: '你是 Astron 助理，帮助用户使用 Astron RPA 设计器与执行器。回答请使用中文，并尽量给出可执行的步骤。',
} as const

const sidebarItems = [
  { key: 'chat' as SidebarKey, title: text.newTask, description: text.newTaskDesc, icon: PlusOutlined },
  { key: 'skills' as SidebarKey, title: text.skillCenter, description: text.skillCenterDesc, icon: AppstoreOutlined },
  { key: 'schedule' as SidebarKey, title: text.scheduleTask, description: text.scheduleTaskDesc, icon: ClockCircleOutlined },
]

const starterCards: StarterCard[] = [
  { id: 'workflow-form', title: '表单流程搭建', description: '梳理从表格读取、网页录入到结果回写的完整步骤。', prompt: '帮我设计一个从 Excel 读取客户名单，进入网页录入并把结果回写到原表的 RPA 流程。', icon: CodeOutlined, section: 'skills', filter: 'workflow' },
  { id: 'data-clean', title: '数据清洗脚本', description: '生成适合本地运行的 Python 处理脚本。', prompt: '帮我生成一个 Python 脚本，清洗 Excel 中的手机号和邮箱字段，并输出一个新文件。', icon: DatabaseOutlined, section: 'skills', filter: 'data' },
  { id: 'system-integration', title: '接口联动方案', description: '串联数据库、Webhook、企业 IM 或内部系统接口。', prompt: '帮我规划一个调用企业微信机器人并回写结果到数据库的自动化方案。', icon: AppstoreOutlined, section: 'skills', filter: 'integration' },
  { id: 'document-summary', title: '文档整理助手', description: '批量读取文件并提取关键字段，形成可执行流程。', prompt: '帮我设计一个批量读取文件夹中的 PDF，提取关键字段后汇总到 Excel 的自动化任务。', icon: FileTextOutlined, section: 'skills', filter: 'workflow' },
  { id: 'daily-report', title: '日报自动汇总', description: '按固定时间汇总执行日志或关键指标并发送。', prompt: '帮我创建一个每天 9:00 执行的计划任务，汇总昨天的运行日志并发送邮件。', icon: ScheduleOutlined, section: 'schedule', filter: 'daily' },
  { id: 'folder-watch', title: '共享目录监听', description: '监控文件夹变化，发现新文件后自动触发处理。', prompt: '帮我创建一个监控共享文件夹新 Excel 文件的计划任务，发现文件后自动处理并归档。', icon: FolderOpenOutlined, section: 'schedule', filter: 'monitoring' },
  { id: 'system-check', title: '巡检与告警', description: '周期性检查系统状态，并在异常时推送消息。', prompt: '帮我创建一个每 15 分钟巡检系统状态并在异常时通知钉钉机器人的任务。', icon: ThunderboltOutlined, section: 'schedule', filter: 'monitoring' },
  { id: 'weekly-sync', title: '周期同步任务', description: '按周或按天同步报表、主数据和附件。', prompt: '帮我创建一个每周一 8:30 自动同步 CRM 客户数据到本地表格的计划任务。', icon: ClockCircleOutlined, section: 'schedule', filter: 'daily' },
]

const userStore = useUserStore()
const openclawToken = ref<string | undefined>(props.openclawToken || import.meta.env.VITE_OPENCLAW_TOKEN)
const electronBridge = (window as any).electron
const messages = ref<ChatMessage[]>([])
const input = ref('')
const sending = ref(false)
const errorText = ref('')
const contextError = ref('')
const showSettings = ref(false)
const assistantConfig = ref<OpenClawManagerCurrentConfig | null>(null)
const scrollerRef = ref<HTMLElement | null>(null)
const textareaKey = ref(0)
const activeSidebar = ref<SidebarKey>('chat')
const activeFilter = ref<StarterFilter>('all')
const md = markdownit({ breaks: true, linkify: true })

const canSend = computed(() => !sending.value && input.value.trim().length > 0)
const hasConversation = computed(() => messages.value.length > 0)
const userName = computed(() => userStore.currentUserInfo?.name || userStore.currentUserInfo?.loginName || text.userFallback)
const workspaceName = computed(() => userStore.currentTenant?.name || assistantConfig.value?.workspace || text.workspaceFallback)
const userInitial = computed(() => userName.value.slice(0, 1).toUpperCase())
const currentModelLabel = computed(() => assistantConfig.value?.primary_model || text.modelUnconfigured)
const connectionStatusText = computed(() => assistantConfig.value?.primary_model ? text.connected : text.notConnected)
const connectionStatusClass = computed(() => assistantConfig.value?.primary_model ? 'text-[#0f9f6e]' : 'text-[#9a6b19]')
const heroTitle = computed(() => activeSidebar.value === 'schedule' ? text.heroSchedule : activeSidebar.value === 'skills' ? text.heroSkills : text.heroChat)
const heroDescription = computed(() => activeSidebar.value === 'schedule' ? text.heroScheduleDesc : activeSidebar.value === 'skills' ? text.heroSkillsDesc : text.heroChatDesc)
const starterTitle = computed(() => activeSidebar.value === 'schedule' ? text.scheduleTitle : text.skillTitle)
const starterFilters = computed(() => activeSidebar.value === 'schedule'
  ? [{ key: 'all' as StarterFilter, label: text.allSchedules }, { key: 'daily' as StarterFilter, label: text.daily }, { key: 'monitoring' as StarterFilter, label: text.monitoring }]
  : [{ key: 'all' as StarterFilter, label: text.allSkills }, { key: 'workflow' as StarterFilter, label: text.workflow }, { key: 'data' as StarterFilter, label: text.data }, { key: 'integration' as StarterFilter, label: text.integration }])
const visibleStarterCards = computed(() => {
  const section = activeSidebar.value === 'schedule' ? 'schedule' : 'skills'
  return starterCards.filter((card) => {
    if (card.section !== section)
      return false
    if (activeFilter.value === 'all')
      return true
    return card.filter === activeFilter.value
  })
})

function renderMarkdown(content: string) {
  return md.render(content || '')
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

watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

watch(showSettings, (open) => {
  if (!open)
    void loadAssistantContext()
})

function upsertToolMessage(event: OpenClawToolEvent) {
  const index = messages.value.findIndex(message => message.role === 'tool' && message.toolCallId === event.toolCallId)
  const nextContent = event.output ?? (index >= 0 && messages.value[index].role === 'tool' ? messages.value[index].content : '')
  const nextMessage: ChatMessage = {
    id: index >= 0 ? messages.value[index].id : generateUUID(),
    role: 'tool',
    content: nextContent,
    createdAt: index >= 0 ? messages.value[index].createdAt : event.ts,
    toolCallId: event.toolCallId,
    toolName: event.name,
    toolStatus: event.phase === 'result' ? 'completed' : 'running',
  }
  if (index >= 0)
    messages.value.splice(index, 1, nextMessage)
  else
    messages.value.push(nextMessage)
}

async function send() {
  const textToSend = input.value.trim()
  if (!textToSend || sending.value)
    return

  errorText.value = ''
  sending.value = true
  input.value = ''
  textareaKey.value += 1
  activeSidebar.value = 'chat'
  messages.value.push({ id: generateUUID(), role: 'user', content: textToSend, createdAt: Date.now() })

  try {
    const result = await openclawChatCompletions({
      token: openclawToken.value,
      onToolEvent: upsertToolMessage,
      messages: [
        { role: 'system', content: text.systemPrompt },
        ...messages.value.filter(message => message.role !== 'tool').map(message => ({ role: message.role, content: message.content })),
      ],
    })
    messages.value.push({ id: generateUUID(), role: 'assistant', content: result.text || text.emptyResponse, createdAt: Date.now() })
  }
  catch (error: any) {
    const reason = error?.message || text.sendFailed
    errorText.value = reason
    messages.value.push({ id: generateUUID(), role: 'assistant', content: `${text.requestFailedPrefix}${reason}${text.requestFailedSuffix}`, createdAt: Date.now() })
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

function startNewTask() {
  messages.value = []
  input.value = ''
  errorText.value = ''
  activeSidebar.value = 'chat'
  activeFilter.value = 'all'
  textareaKey.value += 1
}

function handleSidebarClick(key: SidebarKey) {
  if (key === 'chat') {
    startNewTask()
    return
  }
  activeSidebar.value = key
  activeFilter.value = 'all'
}

function handleQuickAction(type: 'context' | 'skills') {
  if (type === 'context') {
    appMessage.info(text.quickContext)
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

onMounted(async () => {
  if (!openclawToken.value && electronBridge?.openclaw?.getToken) {
    try {
      const token = await electronBridge.openclaw.getToken()
      if (token)
        openclawToken.value = token
    }
    catch (error) {
      console.warn('Failed to load OpenClaw token from Electron:', error)
    }
  }
  await loadAssistantContext()
})
</script>

<template>
  <section class="astron-assistant h-full min-h-0 w-full overflow-hidden rounded-[28px] border border-white/60 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.96),_rgba(243,246,255,0.98)_42%,_rgba(236,241,255,0.96))] shadow-[0_20px_60px_rgba(127,145,193,0.16)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[linear-gradient(180deg,_rgba(25,27,35,0.96),_rgba(17,19,27,0.98))]">
    <IMConnectPanel v-model:open="showSettings" />

    <div class="flex h-full min-h-0">
      <aside class="flex w-[268px] shrink-0 flex-col border-r border-[rgba(139,153,196,0.14)] bg-[rgba(245,247,255,0.82)] px-4 py-5 backdrop-blur-xl dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.03)]">
        <div class="space-y-2">
          <button v-for="item in sidebarItems" :key="item.key" type="button" class="group flex w-full items-start gap-3 rounded-[20px] border px-4 py-4 text-left transition-all duration-200" :class="activeSidebar === item.key ? 'border-[#d7ddff] bg-white shadow-[0_16px_32px_rgba(112,126,171,0.12)] dark:border-[rgba(120,135,255,0.35)] dark:bg-[rgba(255,255,255,0.06)]' : 'border-transparent bg-transparent hover:border-[rgba(139,153,196,0.18)] hover:bg-white/70 dark:hover:border-[rgba(255,255,255,0.1)] dark:hover:bg-[rgba(255,255,255,0.04)]'" @click="handleSidebarClick(item.key)">
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-[16px]" :class="activeSidebar === item.key ? 'bg-[linear-gradient(135deg,#5b70ff,#7a8cff)] text-white' : 'bg-white text-[rgba(61,74,117,0.88)] shadow-[inset_0_0_0_1px_rgba(146,159,201,0.16)] dark:bg-[rgba(255,255,255,0.06)] dark:text-white'">
              <component :is="item.icon" />
            </div>
            <div class="min-w-0 pt-1">
              <div class="text-[16px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]">
                {{ item.title }}
              </div>
              <div class="mt-1 text-[12px] leading-[18px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.55)]">
                {{ item.description }}
              </div>
            </div>
          </button>
        </div>

        <div class="mt-auto rounded-[24px] border border-white/70 bg-white/88 p-4 shadow-[0_16px_30px_rgba(128,144,190,0.12)] backdrop-blur dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[linear-gradient(135deg,#6d7dff,#8ea4ff)] text-[18px] font-semibold text-white">
              {{ userInitial }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-[16px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]">
                {{ userName }}
              </div>
              <div class="truncate text-[12px] text-[rgba(71,83,120,0.6)] dark:text-[rgba(255,255,255,0.5)]">
                {{ workspaceName }}
              </div>
            </div>
          </div>
          <button type="button" class="mt-4 flex w-full items-center justify-between rounded-[16px] border border-[rgba(125,141,188,0.16)] bg-[rgba(245,247,255,0.96)] px-4 py-3 text-left transition hover:border-[rgba(91,112,255,0.26)] hover:bg-white dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]" @click="showSettings = true">
            <div class="min-w-0">
              <div class="text-[14px] font-medium text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.9)]">
                {{ text.assistantSettings }}
              </div>
              <div class="mt-1 text-[12px] text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.5)]">
                {{ text.assistantSettingsDesc }}
              </div>
            </div>
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-[rgba(68,83,128,0.88)] shadow-[inset_0_0_0_1px_rgba(146,159,201,0.18)] dark:bg-[rgba(255,255,255,0.06)] dark:text-white">
              <SettingOutlined />
            </div>
          </button>
        </div>
      </aside>

      <div class="min-w-0 flex-1 p-4 pl-0">
        <div class="flex h-full min-h-0 flex-col overflow-hidden rounded-[26px] bg-[linear-gradient(180deg,_rgba(255,255,255,0.94),_rgba(250,252,255,0.9))] px-6 py-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.6)] dark:bg-[linear-gradient(180deg,_rgba(20,22,30,0.96),_rgba(18,20,28,0.98))]">
          <div v-if="hasConversation" ref="scrollerRef" class="mx-auto flex-1 min-h-0 w-full max-w-[960px] overflow-auto pb-6">
            <div class="space-y-4 px-1 pt-2">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <div class="text-[20px] font-semibold text-[rgba(30,39,67,0.96)] dark:text-[rgba(255,255,255,0.92)]">
                    {{ props.title || text.title }}
                  </div>
                  <div class="mt-1 text-[13px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]">
                    {{ text.workspaceLabel }}：{{ workspaceName }}
                  </div>
                </div>
                <button type="button" class="assistant-select-btn" @click="showSettings = true">
                  <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                </button>
              </div>
              <div v-if="contextError || errorText" class="rounded-[18px] border border-[#ffd6d1] bg-[#fff6f4] px-4 py-3 text-[13px] text-[#b44737] dark:border-[rgba(255,120,102,0.28)] dark:bg-[rgba(255,120,102,0.12)] dark:text-[#ffb2a5]">
                {{ errorText || contextError }}
              </div>
              <div v-for="message in messages" :key="message.id" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
                <div v-if="message.role !== 'tool'" class="max-w-[88%] rounded-[24px] px-5 py-4 text-[14px] leading-[24px] break-words shadow-[0_12px_26px_rgba(138,150,185,0.08)]" :class="message.role === 'user' ? 'border border-[#d7ddff] bg-[linear-gradient(135deg,#f2f4ff,#edf3ff)] text-[rgba(30,39,67,0.95)] dark:border-[rgba(120,135,255,0.3)] dark:bg-[rgba(91,112,255,0.14)] dark:text-white' : 'border border-white/70 bg-white text-[rgba(30,39,67,0.92)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.88)]'">
                  <div class="assistant-markdown" v-html="renderMarkdown(message.content)" />
                </div>
                <div v-else class="w-full max-w-[90%] rounded-[22px] border border-[#ece7e3] bg-[#fbfaf8] px-5 py-4 shadow-[0_12px_26px_rgba(138,150,185,0.06)] dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(255,255,255,0.04)]">
                  <div class="flex items-center justify-between gap-3">
                    <div class="min-w-0">
                      <div class="text-[14px] font-medium text-[rgba(30,39,67,0.92)] dark:text-[rgba(255,255,255,0.88)]">
                        {{ message.toolName }}
                      </div>
                      <div class="mt-1 text-[12px] text-[rgba(71,83,120,0.56)] dark:text-[rgba(255,255,255,0.45)]">
                        {{ message.toolStatus === 'completed' ? text.toolCompleted : text.toolRunning }}
                      </div>
                    </div>
                    <div class="h-2.5 w-2.5 rounded-full" :class="message.toolStatus === 'completed' ? 'bg-[#52c41a]' : 'bg-[#faad14]'" />
                  </div>
                  <pre v-if="message.content" class="mt-3 max-h-[220px] overflow-auto rounded-[16px] bg-[#f4f1ed] px-4 py-3 text-[12px] leading-[20px] whitespace-pre-wrap break-words text-[rgba(0,0,0,0.72)] dark:bg-[rgba(0,0,0,0.22)] dark:text-[rgba(255,255,255,0.78)]">{{ message.content }}</pre>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="flex-1 min-h-0 overflow-auto">
            <div class="mx-auto flex w-full max-w-[980px] flex-col items-center px-4 pt-8 pb-4">
              <div class="rounded-full border border-white/80 bg-white/80 px-4 py-2 text-[12px] font-medium tracking-[0.18em] text-[rgba(87,101,148,0.72)] uppercase shadow-[0_10px_18px_rgba(138,150,185,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.55)]">
                {{ text.heroLabel }}
              </div>
              <div class="mt-6 flex flex-wrap items-center justify-center gap-5">
                <div class="flex h-[84px] w-[84px] items-center justify-center rounded-[28px] bg-[linear-gradient(135deg,#ff7e66,#ffb56b)] text-white shadow-[0_20px_30px_rgba(255,149,111,0.28)]">
                  <rpa-icon name="robot" class="text-[42px]" />
                </div>
                <div class="text-center sm:text-left">
                  <div class="bg-[linear-gradient(120deg,#293a8a_0%,#5c72ff_42%,#d96ea0_100%)] bg-clip-text text-[52px] leading-none font-black tracking-[-0.06em] text-transparent sm:text-[72px]">
                    ASTRON
                  </div>
                  <div class="mt-2 text-[15px] font-medium text-[rgba(71,83,120,0.68)] dark:text-[rgba(255,255,255,0.55)]">
                    {{ heroTitle }}
                  </div>
                </div>
              </div>
              <div class="mt-4 text-center text-[14px] leading-[24px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]">
                {{ heroDescription }}
              </div>
              <div class="mt-4 inline-flex items-center gap-3 rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[13px] shadow-[0_10px_18px_rgba(138,150,185,0.08)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]">
                <span class="text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.48)]">{{ text.workspaceLabel }}：</span><span class="font-medium text-[rgba(30,39,67,0.92)] dark:text-[rgba(255,255,255,0.9)]">{{ workspaceName }}</span><span class="text-[12px] font-medium" :class="connectionStatusClass">{{ connectionStatusText }}</span>
              </div>
              <div v-if="contextError || errorText" class="mt-8 w-full max-w-[860px] rounded-[18px] border border-[#ffd6d1] bg-[#fff6f4] px-4 py-3 text-[13px] text-[#b44737] dark:border-[rgba(255,120,102,0.28)] dark:bg-[rgba(255,120,102,0.12)] dark:text-[#ffb2a5]">
                {{ errorText || contextError }}
              </div>
              <div class="mt-8 w-full max-w-[860px] rounded-[28px] border border-white/80 bg-white/92 p-4 shadow-[0_20px_40px_rgba(138,150,185,0.12)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]">
                <a-textarea :key="textareaKey" v-model:value="input" :placeholder="props.placeholder || text.placeholder" :auto-size="{ minRows: 3, maxRows: 6 }" :disabled="sending" class="assistant-textarea" @keydown="handleKeydown" />
                <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
                  <div class="flex items-center gap-2">
                    <button type="button" class="assistant-round-btn" @click="handleQuickAction('context')">
                      <PlusOutlined />
                    </button>
                    <button type="button" class="assistant-round-btn" @click="handleQuickAction('skills')">
                      <ThunderboltOutlined />
                    </button>
                  </div>
                  <div class="flex items-center gap-3">
                    <button type="button" class="assistant-select-btn" @click="showSettings = true">
                      <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                    </button>
                    <a-button type="primary" shape="circle" :disabled="!canSend" :loading="sending" @click="send">
                      <template #icon>
                        <SendOutlined />
                      </template>
                    </a-button>
                  </div>
                </div>
              </div>
              <div class="mt-10 w-full max-w-[980px]">
                <div class="flex flex-wrap items-center gap-3">
                  <span class="text-[16px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]">{{ starterTitle }}</span>
                  <button v-for="filter in starterFilters" :key="filter.key" type="button" class="rounded-full px-4 py-2 text-[13px] font-medium transition" :class="activeFilter === filter.key ? 'bg-[linear-gradient(135deg,#eef2ff,#edf5ff)] text-[rgba(45,60,106,0.92)] shadow-[0_10px_20px_rgba(138,150,185,0.1)] dark:bg-[rgba(91,112,255,0.16)] dark:text-white' : 'bg-transparent text-[rgba(71,83,120,0.62)] hover:bg-white/80 hover:text-[rgba(45,60,106,0.92)] dark:text-[rgba(255,255,255,0.5)] dark:hover:bg-[rgba(255,255,255,0.04)] dark:hover:text-white'" @click="activeFilter = filter.key">
                    {{ filter.label }}
                  </button>
                </div>
                <div class="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <button v-for="card in visibleStarterCards" :key="card.id" type="button" class="group rounded-[24px] border border-white/80 bg-white/88 p-5 text-left shadow-[0_18px_34px_rgba(138,150,185,0.1)] transition-all duration-200 hover:-translate-y-1 hover:border-[#d7ddff] hover:shadow-[0_24px_42px_rgba(117,132,180,0.16)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]" @click="applyStarterCard(card)">
                    <div class="flex h-12 w-12 items-center justify-center rounded-[16px] bg-[linear-gradient(135deg,#eef2ff,#fef0f3)] text-[rgba(62,76,120,0.9)] dark:bg-[rgba(91,112,255,0.14)] dark:text-white">
                      <component :is="card.icon" />
                    </div>
                    <div class="mt-5 text-[18px] font-semibold text-[rgba(30,39,67,0.94)] dark:text-[rgba(255,255,255,0.9)]">
                      {{ card.title }}
                    </div>
                    <div class="mt-3 text-[13px] leading-[22px] text-[rgba(71,83,120,0.62)] dark:text-[rgba(255,255,255,0.52)]">
                      {{ card.description }}
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="hasConversation" class="mx-auto mt-auto w-full max-w-[960px]">
            <div class="rounded-[26px] border border-white/80 bg-white/92 p-4 shadow-[0_20px_40px_rgba(138,150,185,0.12)] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.04)]">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div class="text-[13px] text-[rgba(71,83,120,0.58)] dark:text-[rgba(255,255,255,0.48)]">
                  {{ sending ? text.sending : `${text.workspaceLabel}：${workspaceName}` }}
                </div>
                <button type="button" class="assistant-select-btn" @click="showSettings = true">
                  <span>{{ currentModelLabel }}</span><DownOutlined class="text-[11px]" />
                </button>
              </div>
              <a-textarea :key="textareaKey" v-model:value="input" :placeholder="props.placeholder || text.placeholder" :auto-size="{ minRows: 2, maxRows: 6 }" :disabled="sending" class="assistant-textarea" @keydown="handleKeydown" />
              <div class="mt-4 flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <button type="button" class="assistant-round-btn" @click="handleQuickAction('context')">
                    <PlusOutlined />
                  </button>
                  <button type="button" class="assistant-round-btn" @click="handleQuickAction('skills')">
                    <ThunderboltOutlined />
                  </button>
                </div>
                <a-button type="primary" shape="circle" :disabled="!canSend" :loading="sending" @click="send">
                  <template #icon>
                    <SendOutlined />
                  </template>
                </a-button>
              </div>
            </div>
          </div>
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

.dark .assistant-textarea :deep(textarea.ant-input::placeholder) {
  color: rgba(255, 255, 255, 0.36);
}
</style>
