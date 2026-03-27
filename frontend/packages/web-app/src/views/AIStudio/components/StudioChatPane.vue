<script setup lang="ts">
import {
  AtSign,
  Check,
  ChevronDown,
  Circle,
  FileText,
  FolderOpen,
  LoaderCircle,
  Paperclip,
  Plus,
  Send,
  UserPlus,
  WandSparkles,
  X,
} from 'lucide-vue-next'
import { computed, nextTick, reactive, ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'

import StudioChatCardRenderer from './StudioChatCardRenderer.vue'
import MarkdownMessage from './MarkdownMessage.vue'
import MessageActions from './MessageActions.vue'

import type { StudioChatCard, StudioSessionDetail } from '../types'

const props = defineProps<{
  session: StudioSessionDetail
  workspaceOpen: boolean
  invitedAssistants: string[]
  sessionPending: boolean
  isAiTyping?: boolean
  isCardPending: (cardId: string) => boolean
  isActionPending: (actionId: string) => boolean
}>()

const emit = defineEmits<{
  (e: 'open-invite'): void
  (e: 'send-message', payload: { content: string, attachments: string[], mentions?: string[], skills?: string[] }): void
  (e: 'submit-choice', payload: { cardId: string, optionId: string }): void
  (e: 'submit-param', payload: { cardId: string, values: Record<string, string> }): void
  (e: 'submit-action', payload: { cardId: string, actionId: string }): void
  (e: 'toggle-workspace'): void
}>()

interface ComposerMentionOption {
  id: string
  label: string
  badge: string
  description: string
}

interface ComposerSkillOption {
  id: string
  label: string
  badge: string
  description: string
}

interface ComposerTriggerState {
  type: 'mention' | 'skill'
  start: number
  query: string
  signature: string
}

interface TaskProgressStep {
  id: string
  title: string
  status: 'done' | 'running' | 'pending' | 'failed'
}

interface TaskProgressStrip {
  headline: string
  status: 'done' | 'running' | 'pending' | 'failed'
  metrics?: string
  steps: TaskProgressStep[]
}

const choiceValues = reactive<Record<string, string>>({})
const paramValues = reactive<Record<string, Record<string, string>>>({})
const draft = ref('')
const localAttachments = ref<string[]>([])
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const activeTrigger = ref<ComposerTriggerState | null>(null)
const activeMenuIndex = ref(0)
const dismissedTriggerSignature = ref('')
const isComposerFocused = ref(false)
const taskProgressExpanded = ref(false)

const skillOptions: ComposerSkillOption[] = [
  { id: 'summary', label: '总结', badge: '总', description: '快速归纳当前会话重点、风险与下一步。' },
  { id: 'report', label: '生成报告', badge: '报', description: '整理结构化报告、recap 或对外摘要。' },
  { id: 'code', label: '分析代码', badge: '码', description: '聚焦代码、日志与修复建议的分析路径。' },
]

const mentionOptions: ComposerMentionOption[] = [
  { id: 'office', label: '办公助手', badge: '办', description: '会议纪要、邮件草稿和行动项整理。' },
  { id: 'finance', label: '财务助手', badge: '财', description: '财务分析、报表和异常项核对。' },
  { id: 'code', label: '代码助手', badge: '代', description: '接口、Bug、补丁和代码审查。' },
  { id: 'data', label: '数据分析师', badge: '数', description: '增长分析、漏斗拆解和图表洞察。' },
]

const displayedMessages = computed(() => props.session.messages)
const displayedTimeline = computed(() => {
  const messageItems = props.session.messages
    .filter(item => item.role === 'user')
    .map((message, index) => ({
      kind: 'user-message' as const,
      id: message.id,
      order: message.order ?? index,
      message,
    }))

  const cardBase = props.session.messages.length
  const cardItems = (props.session.chatCards || []).map((card, index) => ({
    kind: 'card' as const,
    id: card.id,
    order: card.order ?? (cardBase + index),
    card,
  }))

  return [...messageItems, ...cardItems].sort((left, right) => left.order - right.order)
})
const displayedAttachments = computed(() => localAttachments.value)
const canSend = computed(() => draft.value.trim().length > 0 || displayedAttachments.value.length > 0)
const composerInteractive = computed(() =>
  isComposerFocused.value
  || !!activeTrigger.value
  || draft.value.length > 0
  || displayedAttachments.value.length > 0
  || selectedMentionOptions.value.length > 0
  || selectedSkillOptions.value.length > 0,
)
const inputPlaceholder = computed(() => props.session.inputPlaceholder || '输入消息，或使用 / 技能、@ 提及助手')
const composerPlaceholder = computed(() => '输入消息')
const groupParticipants = computed(() => [...new Set([...participantIds(), ...props.invitedAssistants])])
const groupHeaderParticipants = computed(() => groupParticipants.value.slice(0, 2))
const groupInlineParticipants = computed(() => groupParticipants.value.slice(0, 3))
const groupCoordinatorSummary = computed(() => {
  if (props.session.mode !== 'group')
    return ''
  return '主 Agent：通用协调器（仅调度）'
})
const groupModeSummary = computed(() => {
  if (props.session.mode !== 'group')
    return ''
  return `协作模式：${collaborationModeLabel(props.session.collaborationMode)}`
})
const taskProgressStrip = computed<TaskProgressStrip | null>(() => {
  const cards = props.session.chatCards || []
  const run = props.session.run
  const planCard = [...cards].reverse().find(card => card.type === 'plan')
  const toolCard = [...cards].reverse().find(card => card.type === 'tool-call-list')

  if (!run && !planCard && !toolCard)
    return null

  const steps = planCard?.steps?.map(step => ({
    id: step.id,
    title: step.title,
    status: step.status,
  })) || toolCard?.calls?.slice(0, 4).map((call, index) => ({
    id: `${toolCard.id}-${index}`,
    title: /^[\w-]+\.[a-z0-9]+$/i.test(call.arg) ? call.arg : call.name,
    status: call.status,
  })) || []

  const doneCount = steps.filter(step => step.status === 'done').length
  const metrics = steps.length > 0 ? `${doneCount}/${steps.length}` : undefined
  const runningStep = steps.find(step => step.status === 'running')
  const failedStep = steps.find(step => step.status === 'failed')
  const pendingStep = steps.find(step => step.status === 'pending')
  const doneStep = [...steps].reverse().find(step => step.status === 'done')
  const status = steps.find(step => step.status === 'running')?.status
    || steps.find(step => step.status === 'failed')?.status
    || (doneCount === steps.length && steps.length > 0 ? 'done' : 'pending')
  const headline = runningStep?.title
    || failedStep?.title
    || pendingStep?.title
    || doneStep?.title
    || run?.label
    || '当前任务进度'

  return {
    headline,
    status,
    metrics,
    steps,
  }
})

const filteredMentionOptions = computed(() => {
  if (activeTrigger.value?.type !== 'mention')
    return []

  const query = activeTrigger.value.query.trim().toLocaleLowerCase()
  return mentionOptions.filter(option =>
    !query
    || option.label.toLocaleLowerCase().includes(query)
    || option.id.includes(query),
  )
})

const filteredSkillOptions = computed(() => {
  if (activeTrigger.value?.type !== 'skill')
    return []

  const query = activeTrigger.value.query.trim().toLocaleLowerCase()
  return skillOptions.filter(option =>
    !query
    || option.label.toLocaleLowerCase().includes(query)
    || option.description.toLocaleLowerCase().includes(query)
    || option.id.includes(query),
  )
})

const activeMenuOptions = computed(() => activeTrigger.value?.type === 'mention'
  ? filteredMentionOptions.value
  : filteredSkillOptions.value)

const selectedMentionOptions = computed(() => mentionOptions.filter(option =>
  extractComposerTokenIds(mentionOptions, value => `@${value.label}`).includes(option.id),
))

const selectedSkillOptions = computed(() => skillOptions.filter(option =>
  extractComposerTokenIds(skillOptions, value => `/${value.label}`).includes(option.id),
))

watch(
  () => props.session.id,
  async () => {
    for (const key of Object.keys(choiceValues))
      delete choiceValues[key]
    for (const key of Object.keys(paramValues))
      delete paramValues[key]
    draft.value = ''
    localAttachments.value = [...(props.session.attachments || [])]
    activeTrigger.value = null
    activeMenuIndex.value = 0
    dismissedTriggerSignature.value = ''
    taskProgressExpanded.value = false
    await nextTick()
    resizeTextarea()
  },
  { immediate: true },
)

watch(draft, async () => {
  await nextTick()
  resizeTextarea()
})

watch(activeMenuOptions, (options) => {
  if (activeMenuIndex.value >= options.length)
    activeMenuIndex.value = 0
})

function resizeTextarea() {
  if (!textareaRef.value)
    return
  textareaRef.value.style.height = '0px'
  textareaRef.value.style.height = `${Math.min(Math.max(textareaRef.value.scrollHeight, 44), 128)}px`
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function extractComposerTokenIds<T extends { id: string }>(
  options: T[],
  resolveToken: (option: T) => string,
) {
  return options
    .filter(option => new RegExp(`(^|[\\s\\n])${escapeRegExp(resolveToken(option))}(?=$|[\\s\\n])`).test(draft.value))
    .map(option => option.id)
}

function detectComposerTrigger(value: string, cursor: number): ComposerTriggerState | null {
  const beforeCursor = value.slice(0, cursor)
  const match = beforeCursor.match(/(^|[\s\n])([@/])([^\s\n]*)$/)

  if (!match)
    return null

  const type = match[2] === '@' ? 'mention' : 'skill'
  const query = match[3] || ''
  const start = beforeCursor.length - query.length - 1
  const signature = `${type}:${start}:${query}`

  if (dismissedTriggerSignature.value === signature)
    return null

  return {
    type,
    start,
    query,
    signature,
  }
}

function syncComposerTrigger(resetDismissed = false) {
  if (resetDismissed)
    dismissedTriggerSignature.value = ''

  const textarea = textareaRef.value
  const cursor = textarea?.selectionStart ?? draft.value.length
  const nextTrigger = detectComposerTrigger(draft.value, cursor)
  const previousSignature = activeTrigger.value?.signature

  activeTrigger.value = nextTrigger
  if (nextTrigger?.signature !== previousSignature)
    activeMenuIndex.value = 0
}

function focusTextarea(position = draft.value.length) {
  nextTick(() => {
    if (!textareaRef.value)
      return
    textareaRef.value.focus()
    textareaRef.value.setSelectionRange(position, position)
  })
}

function openComposerPicker(type: 'mention' | 'skill') {
  if (props.sessionPending)
    return

  const marker = type === 'mention' ? '@' : '/'
  const textarea = textareaRef.value
  const cursor = textarea?.selectionStart ?? draft.value.length
  const before = draft.value.slice(0, cursor)
  const after = draft.value.slice(cursor)
  const needsLeadingGap = before.length > 0 && !/[\s\n]$/.test(before)
  const nextCursor = cursor + (needsLeadingGap ? 1 : 0) + 1

  draft.value = `${before}${needsLeadingGap ? ' ' : ''}${marker}${after}`

  nextTick(() => {
    if (!textareaRef.value)
      return
    textareaRef.value.focus()
    textareaRef.value.setSelectionRange(nextCursor, nextCursor)
    syncComposerTrigger(true)
  })
}

function insertComposerOption(option: ComposerMentionOption | ComposerSkillOption) {
  if (!activeTrigger.value)
    return

  const textarea = textareaRef.value
  const cursor = textarea?.selectionStart ?? draft.value.length
  let tokenEnd = cursor
  while (tokenEnd < draft.value.length && !/[\s\n]/.test(draft.value[tokenEnd]))
    tokenEnd += 1

  const before = draft.value.slice(0, activeTrigger.value.start)
  const after = draft.value.slice(tokenEnd)
  const token = activeTrigger.value.type === 'mention'
    ? `@${option.label}`
    : `/${option.label}`
  const needsTrailingGap = after.length === 0 || !/^[\s\n]/.test(after)
  const nextValue = `${before}${token}${needsTrailingGap ? ' ' : ''}${after}`
  const nextCursor = before.length + token.length + (needsTrailingGap ? 1 : 0)

  draft.value = nextValue
  activeTrigger.value = null
  activeMenuIndex.value = 0
  dismissedTriggerSignature.value = ''

  focusTextarea(nextCursor)
}

function onDraftInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  draft.value = target.value
  syncComposerTrigger(true)
}

function onDraftInteraction() {
  if (props.sessionPending)
    return
  syncComposerTrigger()
}

function onDraftFocus() {
  isComposerFocused.value = true
  syncComposerTrigger()
}

function onDraftBlur() {
  isComposerFocused.value = false
  window.setTimeout(() => {
    activeTrigger.value = null
  }, 120)
}

function skillButtonActive() {
  return activeTrigger.value?.type === 'skill' || selectedSkillOptions.value.length > 0
}

function mentionButtonActive() {
  return activeTrigger.value?.type === 'mention' || selectedMentionOptions.value.length > 0
}

function mentionBadgeTone(id: string) {
  if (id === 'office')
    return 'bg-[#DBEAFE] text-[#1D4ED8]'
  if (id === 'code')
    return 'bg-[#F3F4F6] text-black/66'
  if (id === 'data')
    return 'bg-[#FFEDD5] text-[#EA580C]'
  return 'bg-[#EEF2FF] text-[#726FFF]'
}

function mentionTokenTone(id: string) {
  if (id === 'office')
    return 'bg-[#EEF5FF] text-[#1D4ED8] ring-[#BFDBFE]'
  if (id === 'code')
    return 'bg-[#F4F6F8] text-black/66 ring-[#E2E8F0]'
  if (id === 'data')
    return 'bg-[#FFF3E8] text-[#C2410C] ring-[#FED7AA]'
  return 'bg-[#F3F1FF] text-[#5E5AE8] ring-[#D9D6FF]'
}

function skillBadgeTone(id: string) {
  if (id === 'code')
    return 'bg-[#ECFDF5] text-[#059669]'
  if (id === 'report')
    return 'bg-[#EEF2FF] text-[#726FFF]'
  return 'bg-[#EFF6FF] text-[#2563EB]'
}

function skillTokenTone(id: string) {
  if (id === 'code')
    return 'bg-[#EDFDF5] text-[#059669] ring-[#BBF7D0]'
  if (id === 'report')
    return 'bg-[#F3F1FF] text-[#5E5AE8] ring-[#D9D6FF]'
  return 'bg-[#EEF5FF] text-[#2563EB] ring-[#BFDBFE]'
}

function taskProgressStatusTone(status: TaskProgressStrip['status']) {
  if (status === 'running')
    return 'text-[#726FFF]'
  if (status === 'done')
    return 'text-[#059669]'
  if (status === 'failed')
    return 'text-[#DC2626]'
  return 'text-black/42'
}

function taskProgressDotTone(status: TaskProgressStep['status']) {
  if (status === 'running')
    return 'text-black/46'
  if (status === 'done')
    return 'text-[#22C55E]'
  if (status === 'failed')
    return 'text-[#EF4444]'
  return 'text-black/24'
}

function taskProgressStatusLabel(status: TaskProgressStrip['status']) {
  if (status === 'running')
    return '进行中'
  if (status === 'done')
    return '已完成'
  if (status === 'failed')
    return '需处理'
  return '待继续'
}

function isGroupSession() {
  return props.session.mode === 'group'
}

function participantIds() {
  return props.session.participantAssistantIds || []
}

function participantName(id: string) {
  if (id === 'coordinator')
    return '主 Agent'
  if (id === 'office')
    return '办公助手'
  if (id === 'finance')
    return '财务助手'
  if (id === 'code')
    return '代码助手'
  if (id === 'data')
    return '数据分析师'
  if (id === 'audit-group')
    return '年报审计协作'
  return '页面助手'
}

function participantBadge(id: string) {
  if (id === 'office')
    return '办'
  if (id === 'finance')
    return '财'
  if (id === 'code')
    return '码'
  if (id === 'data')
    return '数'
  if (id === 'audit-group')
    return '协'
  return '页'
}

function participantAvatarTone(id: string) {
  if (id === 'code')
    return 'bg-[#4B5563] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
  if (id === 'data')
    return 'bg-[#EA580C] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
  if (id === 'office')
    return 'bg-[#1D4ED8] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
  return 'bg-[#726FFF] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
}

function collaborationModeLabel(mode?: StudioSessionDetail['collaborationMode']) {
  if (mode === 'pipeline')
    return '流水线'
  if (mode === 'race')
    return '赛马'
  if (mode === 'debate')
    return '会审'
  return '自动'
}

function ensureParamState(cardId: string, fieldId: string) {
  if (!paramValues[cardId])
    paramValues[cardId] = {}
  if (!paramValues[cardId][fieldId])
    paramValues[cardId][fieldId] = ''
}

function setParamValue(cardId: string, fieldId: string, value: string) {
  ensureParamState(cardId, fieldId)
  paramValues[cardId][fieldId] = value
}

function cardAssistantName(card: StudioChatCard) {
  return card.assistantName || props.session.assistantName
}

function cardAssistantBadge(card: StudioChatCard) {
  return card.assistantBadge || props.session.headerBadge
}

function cardAssistantId(card: StudioChatCard) {
  return card.assistantId || 'finance'
}

function cardMetaTone(card: StudioChatCard) {
  if (cardAssistantId(card) === 'code')
    return 'bg-[#F3F4F6] text-black/60'
  if (cardAssistantId(card) === 'office')
    return 'bg-[#DBEAFE] text-[#1D4ED8]'
  return 'bg-[#EEF2FF] text-[#726FFF]'
}

function cardNameTone(card: StudioChatCard) {
  if (cardAssistantId(card) === 'code')
    return 'text-black/68'
  if (cardAssistantId(card) === 'office')
    return 'text-[#1D4ED8]'
  return 'text-[#726FFF]'
}

function attachmentPool() {
  if (props.session.id.startsWith('office'))
    return ['meeting-notes.md', 'sales-weekly.xlsx', 'follow-up-email.eml']
  if (props.session.id.startsWith('code'))
    return ['error-log.txt', 'login-page.png', 'trace-export.json']
  if (props.session.id.startsWith('data'))
    return ['weekly-growth.xlsx', 'channel-breakdown.csv', 'retention-cohort.png']
  return ['Q3_finance_data.xlsx', 'budget_detail.csv', 'review-note.docx']
}

function addAttachment() {
  const next = attachmentPool().find(item => !localAttachments.value.includes(item))
  if (next)
    localAttachments.value.push(next)
}

function removeAttachment(name: string) {
  localAttachments.value = localAttachments.value.filter(item => item !== name)
}

function resolvePendingActionId(card: StudioChatCard) {
  if (card.type === 'approval')
    return card.actions.map(action => typeof action === 'string' ? action : action.id).find(props.isActionPending) || ''
  if (card.type === 'draft-review' || card.type === 'schedule' || card.type === 'connect-auth' || card.type === 'error-boundary')
    return card.actions.map(action => action.id).find(props.isActionPending) || ''
  return ''
}

function sendMessage() {
  if (!canSend.value || props.sessionPending)
    return

  const mentions = selectedMentionOptions.value.map(option => option.id)
  const skills = selectedSkillOptions.value.map(option => option.id)
  const attachmentSummary = displayedAttachments.value.length
    ? `已附带：${displayedAttachments.value.join('、')}`
    : ''

  const content = [draft.value.trim(), attachmentSummary].filter(Boolean).join('。')

  emit('send-message', {
    content,
    attachments: [...displayedAttachments.value],
    mentions,
    skills,
  })

  draft.value = ''
  localAttachments.value = []
  activeTrigger.value = null
  activeMenuIndex.value = 0
  dismissedTriggerSignature.value = ''

  nextTick(() => {
    resizeTextarea()
  })
}

function sendSuggestedPrompt(content: string) {
  if (props.sessionPending)
    return

  emit('send-message', {
    content,
    attachments: [],
    mentions: [],
    skills: [],
  })

  draft.value = ''
  localAttachments.value = []
  activeTrigger.value = null
  activeMenuIndex.value = 0
  dismissedTriggerSignature.value = ''
  nextTick(() => {
    resizeTextarea()
  })
}

function onDraftKeydown(event: KeyboardEvent) {
  if (props.sessionPending)
    return

  if (activeTrigger.value && activeMenuOptions.value.length > 0) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      activeMenuIndex.value = (activeMenuIndex.value + 1) % activeMenuOptions.value.length
      return
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault()
      activeMenuIndex.value = (activeMenuIndex.value - 1 + activeMenuOptions.value.length) % activeMenuOptions.value.length
      return
    }

    if ((event.key === 'Enter' || event.key === 'Tab') && !event.shiftKey) {
      event.preventDefault()
      const option = activeMenuOptions.value[activeMenuIndex.value]
      if (option)
        insertComposerOption(option)
      return
    }

    if (event.key === 'Escape') {
      event.preventDefault()
      dismissedTriggerSignature.value = activeTrigger.value.signature
      activeTrigger.value = null
      return
    }
  }

  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <section class="relative flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-[linear-gradient(180deg,rgba(255,255,255,0.24)_0%,rgba(250,251,255,0.34)_100%)]" style="font-family: var(--font-sans-ui);">
    <template v-if="isGroupSession()">
      <div class="shrink-0 px-4 pb-2 pt-3">
        <div data-testid="chat-header-shell" class="overflow-hidden rounded-[18px] bg-[rgba(255,255,255,0.54)] shadow-[0_8px_24px_rgba(15,23,42,0.022)] backdrop-blur-[10px]">
          <div class="flex items-center justify-between px-4 py-3">
            <div class="flex items-center gap-3">
              <div class="relative h-8 w-10 shrink-0">
                <div
                  v-for="(assistantId, index) in groupHeaderParticipants"
                  :key="`${assistantId}-${index}`"
                  :class="participantAvatarTone(assistantId)"
                  :style="{ left: `${index * 15}px`, top: index === 0 ? '0px' : '6px' }"
                  class="absolute flex h-7 w-7 items-center justify-center rounded-[10px] text-[10px] font-semibold"
                >
                  {{ participantBadge(assistantId) }}
                </div>
              </div>
              <div class="min-w-0">
                <span class="block truncate text-sm font-semibold leading-[18px] text-[#1A1A2E]">{{ session.headerTitle }}</span>
                <span
                  v-if="groupCoordinatorSummary"
                  class="mt-0.5 block truncate text-[11px] leading-4 text-black/48"
                >
                  {{ groupCoordinatorSummary }}
                </span>
                <span
                  v-if="groupModeSummary"
                  class="block truncate text-[10px] leading-4 text-black/34"
                >
                  {{ groupModeSummary }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div
                v-if="session.collaborationSummary"
                class="rounded-full bg-[rgba(255,255,255,0.72)] px-2.5 py-1 text-[10px] leading-3 text-black/52"
              >
                {{ `进行中 ${session.collaborationSummary.activeTasks} · 完成 ${session.collaborationSummary.completedTasks}` }}
              </div>
              <div
                v-if="groupParticipants.length > 0"
                data-testid="group-participants-inline"
                class="flex items-center rounded-full bg-[rgba(255,255,255,0.72)] px-1.5 py-1 shadow-[0_6px_16px_rgba(15,23,42,0.03)]"
              >
                <div class="flex items-center">
                  <div
                    v-for="(assistantId, index) in groupInlineParticipants"
                    :key="`inline-${assistantId}-${index}`"
                    :class="participantAvatarTone(assistantId)"
                    class="-ml-1 first:ml-0 flex h-5 w-5 items-center justify-center rounded-[8px] text-[8px] font-semibold"
                  >
                    {{ participantBadge(assistantId) }}
                  </div>
                </div>
                <span
                  v-if="groupParticipants.length > groupInlineParticipants.length"
                  class="ml-1 rounded-full bg-white px-1.5 py-0.5 text-[10px] font-medium leading-3 text-black/42"
                >
                  +{{ groupParticipants.length - groupInlineParticipants.length }}
                </span>
              </div>
              <button data-testid="workspace-trigger" class="flex items-center gap-1.5 rounded-full bg-[rgba(255,255,255,0.72)] px-2.5 py-1.5 transition-colors hover:bg-[rgba(255,255,255,0.94)]" @click="emit('toggle-workspace')">
                <FolderOpen class="h-3.5 w-3.5" :class="workspaceOpen ? 'text-[#726FFF]' : 'text-black/46'" />
                <span class="text-xs leading-4" :class="workspaceOpen ? 'text-[#726FFF]' : 'text-black/58'">工作空间</span>
              </button>
              <button class="flex items-center gap-1.5 rounded-full bg-[rgba(240,239,255,0.88)] px-2.5 py-1.5 transition-colors hover:bg-[#F0EFFF]" @click="emit('open-invite')">
                <Plus class="h-3.5 w-3.5 text-[#726FFF]" />
                <span class="text-xs font-medium leading-4 text-[#726FFF]">邀请助手</span>
              </button>
            </div>
          </div>
        </div>
        <div v-if="false" class="flex items-center gap-2 px-4 pb-3 pt-1.5">
          <span class="shrink-0 text-[10px] leading-4 text-black/34">参与助手</span>
          <div v-for="assistantId in participantIds()" :key="assistantId" class="flex items-center gap-2 rounded-lg bg-[rgba(255,255,255,0.72)] px-2.5 py-1">
            <div class="flex h-4 w-4 items-center justify-center rounded-md text-[7px] font-bold" :class="assistantId === 'code' ? 'bg-[#F3F4F6] text-black/60' : assistantId === 'office' ? 'bg-[#DBEAFE] text-[#1D4ED8]' : 'bg-[#EEF2FF] text-[#726FFF]'">
              {{ participantBadge(assistantId) }}
            </div>
            <span class="text-[10px] leading-4 text-black/68">{{ participantName(assistantId) }}</span>
            <div class="h-1.5 w-1.5 rounded-full" :class="assistantId === 'finance' ? 'bg-[#6B7280] animate-pulse' : 'bg-[#D1D5DB]'" />
          </div>
          <div v-for="assistantId in invitedAssistants" :key="assistantId" class="flex items-center gap-2 rounded-lg bg-[rgba(255,255,255,0.72)] px-2.5 py-1">
            <div class="flex h-4 w-4 items-center justify-center rounded-md bg-[#F3F4F6] text-[7px] font-bold text-black/60">
              {{ participantBadge(assistantId) }}
            </div>
            <span class="text-[10px] leading-4 text-black/68">{{ participantName(assistantId) }}</span>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="shrink-0 px-4 pb-2 pt-3">
        <div data-testid="chat-header-shell" class="flex items-center justify-between rounded-[18px] bg-[rgba(255,255,255,0.54)] px-4 py-3 shadow-[0_8px_24px_rgba(15,23,42,0.022)] backdrop-blur-[10px]">
          <div class="flex items-center gap-2.5">
            <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#EEF2FF] text-xs font-semibold text-[#726FFF]">{{ session.headerBadge }}</div>
            <div class="flex items-center gap-1.5">
              <div class="text-sm font-semibold leading-[18px] text-[#1A1A2E]">{{ session.headerTitle }}</div>
              <div class="rounded-full bg-[#F3F4F6] px-2 py-0.5">
                <div class="flex items-center gap-1 text-[10px] font-medium leading-3 text-[#6B7280]">
                  <div class="h-1.5 w-1.5 rounded-full bg-[#6B7280]" :class="sessionPending ? 'animate-pulse' : ''" />
                  {{ session.headerTag }}
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button data-testid="workspace-trigger" class="flex items-center gap-1.5 rounded-full bg-[rgba(255,255,255,0.72)] px-2.5 py-1.5 transition-colors hover:bg-[rgba(255,255,255,0.94)]" @click="emit('toggle-workspace')">
              <FolderOpen class="h-3.5 w-3.5" :class="workspaceOpen ? 'text-[#726FFF]' : 'text-black/46'" />
              <span class="text-xs leading-4" :class="workspaceOpen ? 'text-[#726FFF]' : 'text-black/58'">工作空间</span>
            </button>
            <button class="flex items-center gap-1.5 rounded-full bg-[rgba(240,239,255,0.88)] px-2.5 py-1.5 transition-colors hover:bg-[#F0EFFF]" @click="emit('open-invite')">
              <UserPlus class="h-3.5 w-3.5 text-[#726FFF]" />
              <span class="text-xs font-medium leading-4 text-[#726FFF]">邀请助手</span>
            </button>
          </div>
        </div>
      </div>
    </template>

    <ScrollArea class="min-h-0 flex-1">
      <div class="mx-auto flex w-full max-w-[820px] flex-col gap-2.5 px-5 py-4">
        <div v-if="session.run?.summary && !taskProgressStrip" class="rounded-[16px] bg-[rgba(255,255,255,0.64)] px-4 py-2.5 text-[11px] leading-5 text-black/52 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
          {{ session.run.summary }}
        </div>

        <template v-for="item in displayedTimeline" :key="item.id">
          <div v-if="item.kind === 'user-message'" class="flex flex-col items-end gap-1">
            <div data-testid="user-message-bubble" class="rounded-t-[18px] rounded-bl-[18px] rounded-br-[6px] bg-[linear-gradient(180deg,rgba(244,243,255,0.9)_0%,rgba(238,240,255,0.82)_100%)] px-4 py-2.5 shadow-[0_6px_14px_rgba(114,111,255,0.05)]" :class="isGroupSession() ? 'max-w-[56%]' : 'max-w-[58%]'">
              <MarkdownMessage :content="item.message.content" tone="user" />
            </div>
            <MessageActions
              :message-id="item.message.id"
              :content="item.message.content"
              tone="user"
            />
          </div>
          <div v-else class="flex flex-col gap-1.5">
            <div class="flex items-center gap-1.5">
              <div class="flex h-5 w-5 items-center justify-center overflow-hidden rounded-md text-[8px] font-bold shadow-[0_1px_2px_rgba(15,23,42,0.05)]" :class="cardMetaTone(item.card)">
                {{ cardAssistantBadge(item.card) }}
              </div>
              <span class="text-[11px] font-medium leading-4" :class="cardNameTone(item.card)">{{ cardAssistantName(item.card) }}</span>
              <span v-if="item.card.time" class="text-[10px] leading-3 text-black/28">{{ item.card.time }}</span>
            </div>

            <StudioChatCardRenderer
              :card="item.card"
              :choice-value="choiceValues[item.card.id] || ''"
              :param-values="paramValues[item.card.id] || {}"
              :pending="isCardPending(item.card.id)"
              :pending-action-id="resolvePendingActionId(item.card)"
              @submit:action="emit('submit-action', $event)"
              @submit:choice="emit('submit-choice', $event)"
              @submit:param="emit('submit-param', $event)"
              @select:suggestion="sendSuggestedPrompt($event.option.title)"
              @update:choice="choiceValues[item.card.id] = $event"
              @update:param="setParamValue(item.card.id, $event.fieldId, $event.value)"
            />
          </div>
        </template>

        <!-- AI typing indicator -->
        <div v-if="isAiTyping" class="flex flex-col gap-1.5">
          <div class="flex items-center gap-1.5">
            <div class="flex h-5 w-5 items-center justify-center overflow-hidden rounded-md text-[8px] font-bold shadow-[0_1px_2px_rgba(15,23,42,0.05)] bg-[#EEF2FF] text-[#726FFF]">
              {{ session.headerBadge }}
            </div>
            <span class="text-[11px] font-medium leading-4 text-[#726FFF]">{{ session.assistantName }}</span>
          </div>
          <div class="flex w-fit items-center gap-[5px] rounded-[16px] bg-[rgba(255,255,255,0.64)] px-4 py-3 shadow-[0_6px_14px_rgba(15,23,42,0.04)]">
            <span class="h-1.5 w-1.5 rounded-full bg-black/32 animate-bounce [animation-delay:0ms]" />
            <span class="h-1.5 w-1.5 rounded-full bg-black/32 animate-bounce [animation-delay:160ms]" />
            <span class="h-1.5 w-1.5 rounded-full bg-black/32 animate-bounce [animation-delay:320ms]" />
          </div>
        </div>

        <div
          v-if="session.options?.length"
          data-testid="follow-up-list"
          class="mt-3 space-y-2 px-1 pt-3"
        >
          <div class="h-px w-full bg-[linear-gradient(90deg,rgba(207,216,235,0)_0%,rgba(207,216,235,0.88)_12%,rgba(207,216,235,0.88)_88%,rgba(207,216,235,0)_100%)]" />
          <div class="px-1 pt-0.5">
            <div class="text-[12px] font-semibold leading-4 text-[#1F2940]">建议追问</div>
          </div>
          <button
            v-for="option in session.options"
            :key="option.id"
            :data-testid="`follow-up-option-${option.id}`"
            class="flex w-full items-center gap-2 rounded-[14px] border border-[rgba(222,228,240,0.82)] bg-[rgba(255,255,255,0.72)] px-3 py-2.5 text-left text-[12px] leading-5 text-black/56 shadow-[0_8px_18px_rgba(15,23,42,0.018)] transition-all hover:-translate-y-[1px] hover:bg-white hover:text-[#1F2940] hover:shadow-[0_12px_24px_rgba(15,23,42,0.03)]"
            @click="sendSuggestedPrompt(option.title)"
          >
            <AtSign v-if="option.title.startsWith('@')" class="h-3.5 w-3.5 shrink-0 text-[#726FFF]" />
            <WandSparkles v-else class="h-3.5 w-3.5 shrink-0 text-[#8B90A7]" />
            <span class="min-w-0 flex-1 truncate">{{ option.title }}</span>
            <span class="shrink-0 text-black/18">›</span>
          </button>
        </div>
      </div>
    </ScrollArea>

    <div data-testid="composer-area" class="shrink-0 bg-transparent px-5 pb-5 pt-2">
      <div
        v-if="taskProgressStrip"
        data-testid="task-progress-strip"
        class="mx-auto mb-1.5 w-full max-w-[820px] overflow-hidden rounded-[20px] bg-[rgba(255,255,255,0.5)] shadow-[0_8px_20px_rgba(15,23,42,0.018)] backdrop-blur-[8px]"
      >
        <button
          data-testid="task-progress-toggle"
          class="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-white/35"
          type="button"
          @click="taskProgressExpanded = !taskProgressExpanded"
        >
          <div class="flex h-4 w-4 shrink-0 items-center justify-center">
            <Check v-if="taskProgressStrip.status === 'done'" class="h-4 w-4" :class="taskProgressDotTone('done')" />
            <LoaderCircle v-else-if="taskProgressStrip.status === 'running'" class="h-4 w-4 animate-spin" :class="taskProgressDotTone('running')" />
            <Circle v-else class="h-3.5 w-3.5" :class="taskProgressDotTone(taskProgressStrip.status === 'failed' ? 'failed' : 'pending')" />
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 text-[12px] leading-4">
              <span class="font-medium text-[#1F2940]">{{ taskProgressStrip.headline }}</span>
              <span
                class="text-[10px] font-medium leading-3"
                :class="taskProgressStatusTone(taskProgressStrip.status)"
              >
                {{ taskProgressStatusLabel(taskProgressStrip.status) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2.5 text-[11px] leading-4 text-black/34">
            <span v-if="taskProgressStrip.metrics" data-testid="task-progress-metrics">{{ taskProgressStrip.metrics }}</span>
            <ChevronDown class="h-4 w-4 transition-transform duration-200" :class="taskProgressExpanded ? 'rotate-180' : ''" />
          </div>
        </button>

        <div v-if="taskProgressExpanded" class="px-4 pb-3 pt-2.5">
          <div v-if="taskProgressStrip.steps.length" data-testid="task-progress-steps" class="space-y-1.5">
            <div
              v-for="step in taskProgressStrip.steps"
              :key="step.id"
              data-testid="task-progress-step"
              class="flex items-center gap-2.5 rounded-[12px] px-1 py-1 text-[11px] leading-4 text-black/52"
            >
              <div class="flex h-4 w-4 shrink-0 items-center justify-center">
                <Check v-if="step.status === 'done'" class="h-4 w-4 text-[#22C55E]" />
                <LoaderCircle v-else-if="step.status === 'running'" class="h-4 w-4 animate-spin text-black/42" />
                <Circle v-else class="h-3.5 w-3.5" :class="taskProgressDotTone(step.status)" />
              </div>
              <div class="min-w-0 flex-1 truncate">{{ step.title }}</div>
              <span class="shrink-0 text-[10px] leading-4" :class="taskProgressStatusTone(step.status)">
                {{ taskProgressStatusLabel(step.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        data-testid="composer-shell"
        class="rounded-[24px] px-4 py-3.5 backdrop-blur-[10px] transition-all duration-200"
        :class="composerInteractive
          ? 'bg-[rgba(255,255,255,0.72)] shadow-[0_16px_36px_rgba(15,23,42,0.05),inset_0_0_0_1px_rgba(224,229,242,0.88)]'
          : 'bg-[rgba(255,255,255,0.58)] shadow-[0_12px_30px_rgba(15,23,42,0.028),inset_0_0_0_1px_rgba(236,240,248,0.72)]'"
      >
        <div v-if="displayedAttachments.length > 0" class="mb-2.5 flex flex-wrap items-center gap-1.5">
          <div v-for="attachment in displayedAttachments" :key="attachment" class="flex items-center gap-1 rounded-full bg-[rgba(255,255,255,0.72)] px-2.5 py-1">
            <FileText class="h-3 w-3 text-black/38" />
            <div class="text-[11px] leading-4 text-black/56">{{ attachment }}</div>
            <button class="text-black/26 transition-colors hover:text-black/42" @click="removeAttachment(attachment)">
              <X class="h-3 w-3" />
            </button>
          </div>
          <button class="flex items-center gap-1 rounded-full bg-[rgba(255,255,255,0.64)] px-2.5 py-1 transition-colors hover:bg-[rgba(255,255,255,0.88)]" @click="addAttachment">
            <Plus class="h-3 w-3 text-black/34" />
            <div class="text-[11px] leading-4 text-black/40">添加附件</div>
          </button>
        </div>

        <div v-if="selectedMentionOptions.length > 0 || selectedSkillOptions.length > 0" class="mb-2.5 flex flex-wrap items-center gap-1.5">
          <div
            v-for="option in selectedMentionOptions"
            :key="`mention-${option.id}`"
            :data-testid="`composer-inline-token-mention-${option.id}`"
            class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-[11px] font-medium leading-4 ring-1 shadow-[0_8px_18px_rgba(15,23,42,0.04)]"
            :class="mentionTokenTone(option.id)"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-semibold" :class="mentionBadgeTone(option.id)">
              {{ option.badge }}
            </span>
            <span>@{{ option.label }}</span>
          </div>

          <div
            v-for="option in selectedSkillOptions"
            :key="`skill-${option.id}`"
            :data-testid="`composer-inline-token-skill-${option.id}`"
            class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-[11px] font-medium leading-4 ring-1 shadow-[0_8px_18px_rgba(15,23,42,0.04)]"
            :class="skillTokenTone(option.id)"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-semibold" :class="skillBadgeTone(option.id)">
              {{ option.badge }}
            </span>
            <span>/{{ option.label }}</span>
          </div>
        </div>

        <div class="flex items-end gap-3">
          <div class="relative min-w-0 flex-1">
            <textarea
              ref="textareaRef"
              :value="draft"
              data-testid="composer-textarea"
              :disabled="sessionPending"
              :placeholder="composerPlaceholder"
              class="ai-composer-textarea min-h-[44px] w-full resize-none border-0 bg-transparent px-0 py-0 text-[13px] leading-[22px] text-[#2F374A] outline-none disabled:cursor-not-allowed disabled:opacity-60"
              @focus="onDraftFocus"
              @blur="onDraftBlur"
              @click="onDraftInteraction"
              @input="onDraftInput"
              @keydown="onDraftKeydown"
              @keyup="onDraftInteraction"
            />

            <div
              v-if="activeTrigger?.type === 'mention' && filteredMentionOptions.length > 0"
              data-testid="composer-mention-menu"
              class="absolute bottom-[calc(100%+10px)] left-0 z-20 w-[280px] overflow-hidden rounded-[18px] bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(252,252,255,0.98)_100%)] p-1.5 shadow-[0_18px_40px_rgba(15,23,42,0.12),inset_0_0_0_1px_rgba(224,229,242,0.82)]"
            >
              <div class="px-3 pb-1.5 pt-1.5 text-[10px] font-medium leading-4 text-black/38">
                提及助手
              </div>
              <button
                v-for="(option, index) in filteredMentionOptions"
                :key="option.id"
                :data-testid="`composer-option-mention-${option.id}`"
                class="flex w-full items-center gap-3 rounded-[14px] px-3 py-2.5 text-left transition-all duration-150"
                :class="index === activeMenuIndex ? 'bg-[rgba(114,111,255,0.10)] text-[#5E5AE8]' : 'text-black/68 hover:bg-white/78 hover:text-black/82'"
                @mousedown.prevent="insertComposerOption(option)"
              >
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-[10px] text-[10px] font-semibold" :class="mentionBadgeTone(option.id)">
                  {{ option.badge }}
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-[12px] font-medium leading-4">@{{ option.label }}</span>
                  <span class="mt-1 block text-[10px] leading-4 text-black/40">{{ option.description }}</span>
                </span>
              </button>
            </div>

            <div
              v-if="activeTrigger?.type === 'skill' && filteredSkillOptions.length > 0"
              data-testid="composer-skill-menu"
              class="absolute bottom-[calc(100%+10px)] left-0 z-20 w-[280px] overflow-hidden rounded-[18px] bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(252,252,255,0.98)_100%)] p-1.5 shadow-[0_18px_40px_rgba(15,23,42,0.12),inset_0_0_0_1px_rgba(224,229,242,0.82)]"
            >
              <div class="px-3 pb-1.5 pt-1.5 text-[10px] font-medium leading-4 text-black/38">
                调用技能
              </div>
              <button
                v-for="(option, index) in filteredSkillOptions"
                :key="option.id"
                :data-testid="`composer-option-skill-${option.id}`"
                class="flex w-full items-center gap-3 rounded-[14px] px-3 py-2.5 text-left transition-all duration-150"
                :class="index === activeMenuIndex ? 'bg-[rgba(114,111,255,0.10)] text-[#5E5AE8]' : 'text-black/68 hover:bg-white/78 hover:text-black/82'"
                @mousedown.prevent="insertComposerOption(option)"
              >
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-[10px] text-[10px] font-semibold" :class="skillBadgeTone(option.id)">
                  {{ option.badge }}
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block text-[12px] font-medium leading-4">/{{ option.label }}</span>
                  <span class="mt-1 block text-[10px] leading-4 text-black/40">{{ option.description }}</span>
                </span>
              </button>
            </div>
          </div>

          <div class="flex items-center gap-1.5 self-end">
            <Button
              data-testid="composer-skill-button"
              variant="soft"
              size="sm"
              class="h-8 rounded-full border-0 px-2.5 text-[11px] shadow-none hover:translate-y-0"
              :class="skillButtonActive()
                ? 'bg-[rgba(114,111,255,0.12)] text-[#726FFF] hover:bg-[rgba(114,111,255,0.18)]'
                : 'bg-[rgba(255,255,255,0.72)] text-black/62 hover:bg-[rgba(255,255,255,0.96)] hover:text-black/74'"
              @click="openComposerPicker('skill')"
            >
              <WandSparkles class="h-3.5 w-3.5" />
              <span>/ 技能</span>
            </Button>

            <Button
              data-testid="composer-mention-button"
              variant="secondary"
              size="sm"
              class="h-8 rounded-full border-0 px-2.5 text-[11px] shadow-none hover:translate-y-0"
              :class="mentionButtonActive()
                ? 'bg-[rgba(114,111,255,0.12)] text-[#726FFF] hover:bg-[rgba(114,111,255,0.18)]'
                : 'bg-[rgba(255,255,255,0.72)] text-black/62 hover:bg-[rgba(255,255,255,0.96)] hover:text-black/74'"
              @click="openComposerPicker('mention')"
            >
              <AtSign class="h-3.5 w-3.5" />
              <span>@ 提及</span>
            </Button>

            <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full border-0 bg-[rgba(255,255,255,0.72)] text-black/56 shadow-none hover:bg-[rgba(255,255,255,0.96)] hover:text-[#726FFF] hover:translate-y-0" @click="addAttachment">
              <Paperclip class="h-3.5 w-3.5" />
            </Button>

            <Button
              data-testid="composer-send-button"
              size="icon"
              :disabled="!canSend || sessionPending"
              class="h-8 w-8 rounded-[10px] shadow-[0_6px_14px_rgba(114,111,255,0.26)] disabled:pointer-events-none disabled:opacity-45"
              @click="sendMessage"
            >
              <Send v-if="!sessionPending" class="h-3.5 w-3.5" />
              <div v-else class="h-3.5 w-3.5 rounded-full border-[1.5px] border-white border-t-transparent animate-spin" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ai-composer-textarea::placeholder {
  color: rgba(15, 23, 42, 0.28);
  opacity: 1;
}
</style>
