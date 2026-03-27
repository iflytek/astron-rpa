<script setup lang="ts">
import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Clock3,
  ExternalLink,
  FileText,
  FolderOpen,
  Globe,
  KeyRound,
  Link2,
  ListTodo,
  LoaderCircle,
  Mail,
  ShieldAlert,
  Sparkles,
  Table2,
  Workflow,
} from 'lucide-vue-next'
import { computed, reactive } from 'vue'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

import ArtifactPreviewSurface from './ArtifactPreviewSurface.vue'
import MarkdownMessage from './MarkdownMessage.vue'
import MessageActions from './MessageActions.vue'

import type {
  StudioAction,
  StudioArtifactPreviewPayload,
  StudioChatCard,
  StudioKnowledgeSource,
  StudioOption,
  StudioPlanStep,
  StudioToolCall,
  StudioToolStatus,
  StudioWorkItem,
} from '../types'

const props = withDefaults(defineProps<{
  card: StudioChatCard
  choiceValue?: string
  paramValues?: Record<string, string>
  pending?: boolean
  pendingActionId?: string
}>(), {
  choiceValue: '',
  paramValues: () => ({}),
  pending: false,
  pendingActionId: '',
})

const emit = defineEmits<{
  (e: 'update:choice', value: string): void
  (e: 'update:param', payload: { fieldId: string, value: string }): void
  (e: 'submit:choice', payload: { cardId: string, optionId: string }): void
  (e: 'submit:param', payload: { cardId: string, values: Record<string, string> }): void
  (e: 'submit:action', payload: { cardId: string, actionId: string }): void
  (e: 'select:suggestion', payload: { cardId: string, option: StudioOption }): void
}>()

const specialCardTitleClass = 'text-[13px] font-semibold leading-5 tracking-[-0.01em]'
const specialCardShellClass = 'overflow-hidden rounded-[22px] border-0 bg-[rgba(255,255,255,0.88)] shadow-[0_14px_30px_rgba(15,23,42,0.04)] backdrop-blur-[12px]'
const specialCardHeaderClass = 'flex items-center gap-2 px-4 py-3.5'
const specialCardDividerClass = 'mx-4 h-px bg-[linear-gradient(90deg,rgba(226,231,240,0)_0%,rgba(226,231,240,0.82)_16%,rgba(226,231,240,0.82)_84%,rgba(226,231,240,0)_100%)]'
const toolCallExpansion = reactive<Record<string, boolean>>({})

const widthClass = computed(() => {
  switch (props.card.type) {
    case 'choice-form':
    case 'param-form':
    case 'prompt-suggestions':
    case 'context-scope':
    case 'knowledge-sources':
    case 'plan':
    case 'citation-list':
    case 'schedule':
    case 'connect-auth':
    case 'error-boundary':
      return 'max-w-[498px]'
    case 'work-item-list':
    case 'meeting-recap':
    case 'draft-review':
    case 'approval':
      return 'max-w-[528px]'
    case 'code':
    case 'artifact-preview':
      return 'max-w-[560px]'
    default:
      return 'max-w-[74%]'
  }
})

function choiceOptionClass(selected: boolean) {
  return selected
    ? 'bg-[linear-gradient(180deg,rgba(247,244,255,0.98)_0%,rgba(241,239,255,0.92)_100%)] shadow-[0_10px_22px_rgba(114,111,255,0.08)] ring-1 ring-[#DDD9FF]'
    : 'bg-[rgba(250,250,252,0.88)] shadow-[0_8px_18px_rgba(15,23,42,0.025)] hover:bg-white'
}

function fieldChoiceClass(selected: boolean) {
  return selected
    ? 'border-transparent bg-[linear-gradient(135deg,#726FFF,#5E5AE8)] text-white shadow-[0_6px_14px_rgba(114,111,255,0.16)]'
    : 'border-transparent bg-[rgba(248,249,252,0.92)] text-black/58 hover:bg-white hover:text-black/72'
}

function actionVariant(action: StudioAction) {
  switch (action.tone) {
    case 'primary':
      return 'default'
    case 'ghost':
      return 'ghost'
    case 'soft':
      return 'soft'
    default:
      return 'secondary'
  }
}

function actionClass(action: StudioAction) {
  if (action.tone === 'danger')
    return 'h-8 rounded-[10px] border-[#FECACA] bg-[#FEF2F2] px-3 text-[11px] text-[#DC2626] shadow-none hover:bg-[#FEE2E2] hover:translate-y-0'
  if (action.tone === 'primary')
    return 'h-8 rounded-[10px] px-3 text-[11px] shadow-[0_6px_14px_rgba(114,111,255,0.22)]'
  if (action.tone === 'soft')
    return 'h-8 rounded-[10px] border-0 bg-[#F0EFFF] px-3 text-[11px] text-[#726FFF] shadow-none hover:bg-[#E9E7FF] hover:translate-y-0'
  if (action.tone === 'ghost')
    return 'h-8 rounded-[10px] border-0 bg-transparent px-3 text-[11px] text-black/52 shadow-none hover:bg-[#F5F7FB] hover:translate-y-0'
  return 'h-8 rounded-[10px] border-[#E5E7EB] bg-white px-3 text-[11px] text-black/58 shadow-none hover:bg-[#F9FAFB] hover:translate-y-0'
}

function normalizeAction(action: StudioAction | string): StudioAction {
  if (typeof action !== 'string')
    return action

  if (action.includes('允许执行'))
    return { id: action, label: action, tone: 'primary' }
  if (action.includes('始终允许'))
    return { id: action, label: action, tone: 'soft' }
  if (action.includes('拒绝'))
    return { id: action, label: action, tone: 'danger' }
  return { id: action, label: action, tone: 'secondary' }
}

function toolStatusLabel(status: StudioToolStatus) {
  if (status === 'running')
    return '执行中'
  if (status === 'done')
    return '完成'
  if (status === 'failed')
    return '失败'
  return '待处理'
}

function toolStatusTone(status: StudioToolStatus) {
  if (status === 'running')
    return 'border-[#DDD9FF] bg-[#F5F3FF] text-[#726FFF]'
  if (status === 'failed')
    return 'border-[#FECACA] bg-[#FEF2F2] text-[#DC2626]'
  return 'border-[#E5E7EB] bg-[#F8FAFC] text-black/54'
}

function toolStatusTextTone(status: StudioToolStatus) {
  if (status === 'running')
    return 'text-[#726FFF]'
  if (status === 'failed')
    return 'text-[#DC2626]'
  if (status === 'done')
    return 'text-black/48'
  return 'text-black/32'
}

function toolCallKey(cardId: string, index: number) {
  return `${cardId}-${index}`
}

function isToolCallExpanded(cardId: string, index: number, status: StudioToolStatus) {
  const key = toolCallKey(cardId, index)
  if (key in toolCallExpansion)
    return toolCallExpansion[key]
  return status === 'running' || status === 'failed'
}

function toggleToolCall(cardId: string, index: number, status: StudioToolStatus) {
  const key = toolCallKey(cardId, index)
  toolCallExpansion[key] = !isToolCallExpanded(cardId, index, status)
}

function toolCallDescription(name: string) {
  if (name.includes('read'))
    return '读取所需上下文并整理输入数据。'
  if (name.includes('scan') || name.includes('profile'))
    return '扫描相关链路，定位风险点与瓶颈位置。'
  if (name.includes('compose') || name.includes('draft'))
    return '生成当前阶段的草稿、补丁或结构化输出。'
  if (name.includes('generate'))
    return '根据当前上下文生成可视化或结构化产物。'
  return '执行当前步骤并同步状态。'
}

function toolCallSteps(name: string) {
  if (name.includes('read'))
    return ['定位目标文件', '抽取关键字段', '同步到会话上下文']
  if (name.includes('scan') || name.includes('profile'))
    return ['扫描相关文件', '对比上下游依赖', '标记异常路径']
  if (name.includes('compose') || name.includes('draft'))
    return ['汇总当前上下文', '生成结构化草稿', '写回工作空间产物']
  if (name.includes('generate'))
    return ['分析输入参数', '生成目标内容', '准备预览结果']
  return ['读取上下文', '执行当前步骤', '回写执行结果']
}

function toolCallHeadline(call: StudioToolCall) {
  return call.name.replace(/[_-]+/g, ' ')
}

function toolCallOutput(call: StudioToolCall) {
  const lines: string[] = []

  if (call.arg)
    lines.push(`target: ${call.arg}`)

  lines.push(call.detail || toolCallDescription(call.name))

  if (call.result)
    lines.push(`result: ${call.result}`)

  if (call.duration)
    lines.push(`duration: ${call.duration}`)

  const steps = call.steps?.length ? call.steps : toolCallSteps(call.name)
  if (steps.length) {
    lines.push('')
    steps.forEach((step, index) => {
      lines.push(`${index + 1}. ${step}`)
    })
  }

  return lines.join('\n')
}

function planStepDot(step: StudioPlanStep) {
  if (step.status === 'done')
    return 'bg-[#10B981]'
  if (step.status === 'running')
    return 'bg-[#726FFF]'
  if (step.status === 'failed')
    return 'bg-[#EF4444]'
  return 'bg-[#D1D5DB]'
}

function knowledgeSourceTone(source: StudioKnowledgeSource) {
  if (source.status === 'needs-auth')
    return 'bg-[rgba(255,247,237,0.92)] text-[#C2410C]'
  if (source.status === 'blocked')
    return 'bg-[rgba(254,242,242,0.92)] text-[#DC2626]'
  if (source.status === 'retrieved' || source.status === 'indexed')
    return 'bg-[rgba(240,253,244,0.92)] text-[#15803D]'
  return 'bg-[rgba(243,244,246,0.92)] text-black/56'
}

function knowledgeSourceLabel(source: StudioKnowledgeSource) {
  if (source.status === 'needs-auth')
    return '待授权'
  if (source.status === 'blocked')
    return '受限'
  if (source.status === 'indexed')
    return '已索引'
  if (source.status === 'retrieved')
    return '已引用'
  return '已连接'
}

function workItemTone(item: StudioWorkItem) {
  if (item.status === 'done')
    return 'bg-[rgba(240,253,244,0.92)] text-[#15803D]'
  if (item.status === 'in-progress')
    return 'bg-[rgba(245,243,255,0.96)] text-[#726FFF]'
  if (item.status === 'blocked')
    return 'bg-[rgba(254,242,242,0.92)] text-[#DC2626]'
  return 'bg-[rgba(243,244,246,0.92)] text-black/56'
}

function workItemLabel(item: StudioWorkItem) {
  if (item.status === 'done')
    return '已完成'
  if (item.status === 'in-progress')
    return '进行中'
  if (item.status === 'blocked')
    return '阻塞'
  return '待办'
}

function updateChoice(value: string) {
  emit('update:choice', value)
}

function updateParam(fieldId: string, value: string) {
  emit('update:param', { fieldId, value })
}

function handleParamInput(fieldId: string, event: Event) {
  const target = event.target as HTMLInputElement | null
  updateParam(fieldId, target?.value || '')
}

function isParamReady() {
  if (props.card.type !== 'param-form')
    return false
  return props.card.fields.every(field => !field.required || props.paramValues[field.id])
}

function submitChoice() {
  if (props.card.type !== 'choice-form' || !props.choiceValue || props.pending)
    return
  emit('submit:choice', {
    cardId: props.card.id,
    optionId: props.choiceValue,
  })
}

function submitParam() {
  if (props.card.type !== 'param-form' || !isParamReady() || props.pending)
    return
  emit('submit:param', {
    cardId: props.card.id,
    values: { ...props.paramValues },
  })
}

function submitAction(action: StudioAction | string) {
  if (props.pending)
    return
  const normalized = normalizeAction(action)
  emit('submit:action', {
    cardId: props.card.id,
    actionId: normalized.id,
  })
}

function selectSuggestion(option: StudioOption) {
  if (props.card.type !== 'prompt-suggestions' || props.pending)
    return
  emit('select:suggestion', {
    cardId: props.card.id,
    option,
  })
}

function isActionBusy(actionId: string) {
  return props.pending && props.pendingActionId === actionId
}

function cardTestId(type: StudioChatCard['type']) {
  switch (type) {
    case 'thinking':
      return 'thinking-card-shell'
    case 'choice-form':
      return 'choice-card-shell'
    case 'param-form':
      return 'param-card-shell'
    case 'prompt-suggestions':
      return 'prompt-suggestion-card-shell'
    case 'code':
      return 'code-card-shell'
    case 'artifact-preview':
      return 'artifact-preview-shell'
    case 'approval':
      return 'approval-card-shell'
    case 'context-scope':
      return 'context-card-shell'
    case 'knowledge-sources':
      return 'knowledge-card-shell'
    case 'plan':
      return 'plan-card-shell'
    case 'tool-call-list':
      return 'tool-call-card-shell'
    case 'citation-list':
      return 'citation-card-shell'
    case 'draft-review':
      return 'draft-card-shell'
    case 'work-item-list':
      return 'work-item-card-shell'
    case 'meeting-recap':
      return 'meeting-card-shell'
    case 'schedule':
      return 'schedule-card-shell'
    case 'connect-auth':
      return 'connect-card-shell'
    case 'error-boundary':
      return 'error-card-shell'
    default:
      return undefined
  }
}

function resolveArtifactPreview(card: Extract<StudioChatCard, { type: 'artifact-preview' }>): StudioArtifactPreviewPayload {
  if (card.preview)
    return card.preview

  return {
    kind: 'chart',
    fileName: card.fileName || 'artifact-preview',
    status: card.tag || '已生成',
    title: card.previewTitle || card.fileName || '产物预览',
    chartRows: card.chartRows || [],
    legend: card.legend,
  }
}
</script>

<template>
  <div class="max-w-[74%]" :class="widthClass">
    <template v-if="card.type === 'thinking'">
      <div :data-testid="cardTestId(card.type)" class="px-1 py-1">
        <div class="inline-flex max-w-full items-center gap-2 rounded-full bg-[rgba(255,255,255,0.58)] px-3 py-1.5 text-[12px] leading-4 text-black/48 shadow-[0_8px_18px_rgba(15,23,42,0.02)] backdrop-blur-[8px]">
          <LoaderCircle class="h-3.5 w-3.5 animate-spin text-[#726FFF]" />
          <span data-testid="special-card-title" class="font-medium text-[#4E46A8]">{{ card.title }}</span>
          <span class="text-black/28">·</span>
          <span>思考中</span>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'context-scope'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass" class="bg-[linear-gradient(180deg,rgba(252,252,255,0.96)_0%,rgba(247,248,253,0.92)_100%)]">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <Workflow class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">
            {{ card.description }}
          </div>
          <div class="grid gap-2 sm:grid-cols-2">
            <div v-for="field in card.fields" :key="field.label" class="rounded-[16px] bg-[rgba(250,250,252,0.86)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
              <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">{{ field.label }}</div>
              <div class="mt-1.5 text-[12px] font-medium leading-5 text-black/74">{{ field.value }}</div>
            </div>
          </div>
          <div v-if="card.tags?.length" class="flex flex-wrap items-center gap-2">
            <span v-for="tag in card.tags" :key="tag" class="rounded-full bg-[#F0EFFF] px-2.5 py-1 text-[10px] leading-3 text-[#726FFF]">{{ tag }}</span>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'knowledge-sources'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <Link2 class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-2.5 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">
            {{ card.description }}
          </div>
          <div
            v-for="source in card.sources"
            :key="source.id"
            class="flex items-start gap-3 rounded-[16px] bg-[rgba(250,250,252,0.86)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]"
          >
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-[12px] bg-white text-[#726FFF] shadow-[0_4px_10px_rgba(15,23,42,0.04)]">
              <FolderOpen v-if="source.type === 'workspace'" class="h-4 w-4" />
              <FileText v-else-if="source.type === 'file'" class="h-4 w-4" />
              <Globe v-else-if="source.type === 'web'" class="h-4 w-4" />
              <Link2 v-else class="h-4 w-4" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-[12px] font-medium leading-4 text-black/74">{{ source.label }}</div>
              <div v-if="source.detail" class="mt-1 text-[11px] leading-4 text-black/42">{{ source.detail }}</div>
            </div>
            <span :data-testid="`knowledge-source-status-${source.id}`" class="rounded-full px-2.5 py-1 text-[10px] font-medium leading-3" :class="knowledgeSourceTone(source)">{{ knowledgeSourceLabel(source) }}</span>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'plan'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <Sparkles class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div class="space-y-3">
            <div v-for="step in card.steps" :key="step.id" class="flex items-start gap-3">
              <div class="mt-1 flex flex-col items-center">
                <div class="h-2.5 w-2.5 rounded-full" :class="planStepDot(step)" />
                <div class="mt-1 h-6 w-px bg-[#E5E7EB]" />
              </div>
              <div class="min-w-0 flex-1 pb-1">
                <div class="flex items-center gap-2">
                  <div class="text-[12px] font-medium leading-4 text-black/74">{{ step.title }}</div>
                  <span class="rounded-full px-2 py-0.5 text-[10px] leading-3" :class="toolStatusTone(step.status)">{{ toolStatusLabel(step.status) }}</span>
                </div>
                <div v-if="step.description" class="mt-1 text-[11px] leading-4 text-black/42">{{ step.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'tool-call-list'">
      <div :data-testid="cardTestId(card.type)" class="space-y-2 px-1 py-1">
        <div class="flex items-center gap-2 px-1">
          <Sparkles class="h-3.5 w-3.5 text-black/22" />
          <span data-testid="special-card-title" class="text-[11px] font-medium leading-4 text-black/44">{{ card.title || '工具执行' }}</span>
          <span class="text-[10px] leading-4 text-black/26">{{ card.calls.length }} 步</span>
        </div>
        <div class="overflow-hidden rounded-[18px] bg-[rgba(255,255,255,0.18)] px-1.5 backdrop-blur-[4px]">
          <div
            v-for="(call, index) in card.calls"
            :key="`${card.id}-${call.name}-${call.arg}`"
            class="border-b border-[rgba(15,23,42,0.05)] last:border-b-0"
          >
            <button
              :data-testid="`tool-call-toggle-${card.id}-${index}`"
              type="button"
              class="flex w-full items-center gap-2.5 px-2.5 py-2.5 text-left transition-colors hover:bg-white/30"
              @click="toggleToolCall(card.id, index, call.status)"
            >
              <LoaderCircle v-if="call.status === 'running'" class="h-3.5 w-3.5 shrink-0 animate-spin text-[#726FFF]" />
              <CheckCircle2 v-else-if="call.status === 'done'" class="h-3.5 w-3.5 shrink-0 text-[#9CA3AF]" />
              <AlertTriangle v-else-if="call.status === 'failed'" class="h-3.5 w-3.5 shrink-0 text-[#DC2626]" />
              <Clock3 v-else class="h-3.5 w-3.5 shrink-0 text-black/26" />

              <div class="min-w-0 flex-1 truncate text-[12px] leading-5 text-black/64">
                <span class="font-medium">{{ toolCallHeadline(call) }}</span>
                <span class="px-1 text-black/18">·</span>
                <span class="font-mono text-[10px] text-black/32">{{ call.name }}</span>
                <span v-if="call.duration" class="px-1 text-black/18">·</span>
                <span v-if="call.duration" class="text-[10px] text-black/34">{{ call.duration }}</span>
              </div>

              <span
                data-testid="tool-call-status"
                class="text-[10px] font-medium leading-4"
                :class="toolStatusTextTone(call.status)"
              >
                {{ toolStatusLabel(call.status) }}
              </span>
              <ChevronDown class="h-3.5 w-3.5 shrink-0 text-black/22 transition-transform" :class="isToolCallExpanded(card.id, index, call.status) ? 'rotate-180' : ''" />
            </button>

            <div
              v-if="isToolCallExpanded(card.id, index, call.status)"
              :data-testid="`tool-call-detail-${card.id}-${index}`"
              class="px-2.5 pb-2.5 pt-0.5"
            >
              <pre class="overflow-x-auto rounded-[14px] bg-[rgba(245,247,251,0.92)] px-3 py-2.5 text-[11px] leading-5 text-black/58 shadow-[inset_0_0_0_1px_rgba(229,231,235,0.7)]"><code>{{ toolCallOutput(call) }}</code></pre>
              <div v-if="false" class="space-y-1.5 text-[11px] leading-4 text-black/54">
                <div>
                  <span class="text-black/32">调用：</span>
                  <span>{{ call.detail || toolCallDescription(call.name) }}</span>
                </div>
                <div>
                  <span class="text-black/32">目标：</span>
                  <span>{{ call.arg }}</span>
                </div>
                <div v-if="call.duration">
                  <span class="text-black/32">耗时：</span>
                  <span>{{ call.duration }}</span>
                </div>
                <div v-if="call.result">
                  <span class="text-black/32">结果：</span>
                  <span class="text-black/66">{{ call.result }}</span>
                </div>
              </div>

              <div v-if="false" class="space-y-1">
                <div class="text-[10px] font-medium leading-4 text-black/30">执行过程</div>
                <div
                  v-for="(step, stepIndex) in call.steps || toolCallSteps(call.name)"
                  :key="`${card.id}-${index}-${stepIndex}`"
                  class="flex items-start gap-2 text-[10px] leading-4 text-black/42"
                >
                  <div class="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-black/20" />
                  <span>{{ step }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'choice-form'">
      <Card :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <CardHeader class="px-4 pb-2 pt-4">
          <CardTitle data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/86">{{ card.title }}</CardTitle>
          <div v-if="card.description" class="pt-1 text-[11px] leading-5 text-black/42">{{ card.description }}</div>
        </CardHeader>
        <CardContent class="px-3 pb-3 pt-1">
          <RadioGroup :model-value="choiceValue" class="space-y-2" @update:model-value="updateChoice">
            <label
              v-for="option in card.options"
              :key="option.id"
              :data-testid="`choice-option-${card.id}-${option.id}`"
              class="flex cursor-pointer items-start gap-3 rounded-[18px] px-4 py-3 transition-all"
              :class="choiceOptionClass(choiceValue === option.id)"
            >
              <RadioGroupItem data-testid="choice-option-radio" :value="option.id" class="mt-0.5" />
              <div class="min-w-0 flex-1">
                <div class="text-[13px] font-medium leading-5" :class="choiceValue === option.id ? 'text-[#726FFF]' : 'text-black/78'">
                  {{ option.label }}
                </div>
                <div class="mt-0.5 text-[11px] leading-4 text-black/40">{{ option.description }}</div>
              </div>
            </label>
          </RadioGroup>
        </CardContent>
        <CardFooter class="px-3 pb-3 pt-0">
          <Button
            :data-testid="`card-submit-${card.id}`"
            :disabled="!choiceValue || pending"
            :variant="choiceValue && !pending ? 'default' : 'secondary'"
            :class="choiceValue && !pending ? 'border-0 shadow-[0_6px_16px_rgba(114,111,255,0.18)]' : 'border-0 bg-[#F3F4F6] text-black/28 shadow-none hover:bg-[#F3F4F6] hover:translate-y-0'"
            class="h-9 w-full rounded-[14px] text-[12px]"
            @click="submitChoice"
          >
            {{ pending ? '处理中...' : card.confirmLabel }}
          </Button>
        </CardFooter>
      </Card>
    </template>

    <template v-else-if="card.type === 'prompt-suggestions'">
      <div :data-testid="cardTestId(card.type)" class="mt-3 space-y-2 px-1 pt-3">
        <div class="h-px w-full bg-[linear-gradient(90deg,rgba(207,216,235,0)_0%,rgba(207,216,235,0.88)_12%,rgba(207,216,235,0.88)_88%,rgba(207,216,235,0)_100%)]" />
        <div data-testid="special-card-title" class="px-1 pt-0.5 text-[12px] font-semibold leading-4 text-[#1F2940]">
          建议追问
        </div>
        <button
          v-for="suggestion in card.suggestions"
          :key="suggestion.id"
          :data-testid="`prompt-suggestion-${suggestion.id}`"
          class="flex w-full items-center gap-2 rounded-[14px] border border-[rgba(222,228,240,0.82)] bg-[rgba(255,255,255,0.72)] px-3 py-2.5 text-left text-[12px] leading-5 text-black/56 shadow-[0_8px_18px_rgba(15,23,42,0.018)] transition-all hover:-translate-y-[1px] hover:bg-white hover:text-[#1F2940] hover:shadow-[0_12px_24px_rgba(15,23,42,0.03)]"
          @click="selectSuggestion(suggestion)"
        >
          <Sparkles class="h-3.5 w-3.5 shrink-0 text-[#8B90A7]" />
          <span class="min-w-0 flex-1 truncate">{{ suggestion.title }}</span>
          <span class="shrink-0 text-black/18">›</span>
        </button>
      </div>
    </template>

    <template v-else-if="card.type === 'param-form'">
      <Card :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <CardHeader class="px-4 pb-2 pt-4">
          <CardTitle data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/86">{{ card.title }}</CardTitle>
          <div v-if="card.description" class="pt-1 text-[11px] leading-4 text-black/42">{{ card.description }}</div>
        </CardHeader>
        <CardContent class="space-y-3 px-4 pb-3 pt-1">
          <div v-for="field in card.fields" :key="field.id" class="space-y-2 rounded-[18px] bg-[rgba(250,250,252,0.84)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <label class="text-[11px] font-medium leading-4 text-black/72">
              {{ field.label }}
              <span v-if="field.required" class="text-[#EF4444]">*</span>
            </label>
            <Input
              v-if="field.type === 'date'"
              :data-testid="`field-input-${card.id}-${field.id}`"
              :model-value="paramValues[field.id] || ''"
              type="date"
              class="h-10 rounded-[14px] border-0 bg-white text-[12px] shadow-[inset_0_0_0_1px_rgba(229,231,235,0.7)]"
              @input="handleParamInput(field.id, $event)"
            />
            <div v-else class="flex flex-wrap gap-2">
              <button
                v-for="choice in field.choices || []"
                :key="choice.id"
                :data-testid="`field-choice-${card.id}-${field.id}-${choice.id}`"
                type="button"
                class="rounded-[12px] border px-3 py-1.5 text-[11px] leading-4 transition-all"
                :class="fieldChoiceClass((paramValues[field.id] || '') === choice.id)"
                @click="updateParam(field.id, choice.id)"
              >
                {{ choice.label }}
              </button>
            </div>
          </div>
        </CardContent>
        <CardFooter class="px-3 pb-3 pt-0">
          <Button
            :data-testid="`card-submit-${card.id}`"
            :disabled="!isParamReady() || pending"
            :variant="isParamReady() && !pending ? 'default' : 'secondary'"
            :class="isParamReady() && !pending ? 'border-0 shadow-[0_6px_16px_rgba(114,111,255,0.18)]' : 'border-0 bg-[#F3F4F6] text-black/28 shadow-none hover:bg-[#F3F4F6] hover:translate-y-0'"
            class="h-9 w-full rounded-[14px] text-[12px]"
            @click="submitParam"
          >
            {{ pending ? '处理中...' : card.confirmLabel }}
          </Button>
        </CardFooter>
      </Card>
    </template>

    <template v-else-if="card.type === 'citation-list'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <ExternalLink class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-2.5 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div
            v-for="citation in card.citations"
            :key="citation.id"
            class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]"
          >
            <div class="flex items-center gap-2">
              <span class="text-[12px] font-medium leading-4 text-black/76">{{ citation.title }}</span>
              <span v-if="citation.meta" class="text-[10px] leading-3 text-black/36">{{ citation.meta }}</span>
            </div>
            <div class="mt-1.5 text-[12px] leading-5 text-black/68">“{{ citation.excerpt }}”</div>
            <div class="mt-2 flex items-center gap-1 text-[10px] leading-3 text-[#726FFF]">
              <Link2 class="h-3 w-3" />
              {{ citation.source }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'draft-review'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <Mail v-if="card.draftKind === 'email'" class="h-3 w-3" />
            <FileText v-else class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
          <span class="rounded-full bg-[#F0EFFF] px-2 py-0.5 text-[10px] leading-3 text-[#726FFF]">{{ card.draftKind === 'email' ? '邮件草稿' : card.draftKind === 'reply' ? '回复草稿' : '文档草稿' }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div v-if="card.subject" class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">主题</div>
            <div class="mt-1.5 text-[12px] font-medium leading-5 text-black/74">{{ card.subject }}</div>
          </div>
          <div v-if="card.recipients?.length" class="flex flex-wrap items-center gap-2">
            <span v-for="recipient in card.recipients" :key="recipient" class="rounded-full bg-[rgba(250,250,252,0.9)] px-2.5 py-1 text-[10px] leading-3 text-black/54 shadow-[0_6px_12px_rgba(15,23,42,0.02)]">
              {{ recipient }}
            </span>
          </div>
          <div class="space-y-2">
            <div v-for="section in card.sections" :key="section.label" class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
              <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">{{ section.label }}</div>
              <div class="mt-1.5 text-[12px] leading-5 text-black/68">{{ section.value }}</div>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <Button
              v-for="action in card.actions"
              :key="action.id"
              :data-action-id="action.id"
              :data-testid="`card-action-${action.id}`"
              :disabled="pending"
              :variant="actionVariant(action)"
              :class="actionClass(action)"
              @click="submitAction(action)"
            >
              {{ isActionBusy(action.id) ? '处理中...' : action.label }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'code'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div class="flex items-center justify-between px-3.5 py-3">
          <div class="flex items-center gap-2">
            <div class="flex h-5 w-5 items-center justify-center rounded-md bg-[#F0EFFF] px-1 text-[10px] font-semibold text-[#726FFF]">代码</div>
            <span class="text-[11px] font-medium leading-4 text-black/70">{{ card.fileName }}</span>
            <span v-if="card.tag" class="rounded-[4px] bg-[#F0EFFF] px-1.5 py-px text-[9px] font-medium leading-3 text-[#726FFF]">{{ card.tag }}</span>
          </div>
          <span class="text-[10px] leading-3 text-black/34">{{ card.language?.toUpperCase() || 'CODE' }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="overflow-x-auto bg-[#1E1E2E] p-4">
          <pre class="whitespace-pre text-[11px] leading-5 text-[#CDD6F4]"><code>{{ card.code }}</code></pre>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'artifact-preview'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div class="flex items-center justify-between px-3.5 py-3">
          <div class="flex items-center gap-2">
            <div class="flex h-5 w-5 items-center justify-center rounded-md bg-[#F0EFFF] text-[10px] font-semibold text-[#726FFF]">
              <Table2 v-if="resolveArtifactPreview(card).kind === 'table'" class="h-3 w-3" />
              <FileText v-else class="h-3 w-3" />
            </div>
            <span class="text-[11px] font-medium leading-4 text-black/70">{{ resolveArtifactPreview(card).fileName }}</span>
            <span v-if="resolveArtifactPreview(card).tag" class="rounded-[4px] bg-[#F0EFFF] px-1.5 py-px text-[9px] font-medium leading-3 text-[#726FFF]">{{ resolveArtifactPreview(card).tag }}</span>
          </div>
          <span class="text-[10px] leading-3 text-black/34">{{ resolveArtifactPreview(card).status }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <ArtifactPreviewSurface :preview="resolveArtifactPreview(card)" compact />
      </div>
    </template>

    <template v-else-if="card.type === 'work-item-list'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <ListTodo class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-2.5 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div
            v-for="item in card.items"
            :key="item.id"
            class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]"
          >
            <div class="flex items-center gap-2">
              <div class="text-[12px] font-medium leading-4 text-black/76">{{ item.title }}</div>
              <span class="ml-auto rounded-full px-2.5 py-1 text-[10px] leading-3" :class="workItemTone(item)">{{ workItemLabel(item) }}</span>
            </div>
            <div v-if="item.detail" class="mt-1.5 text-[11px] leading-4 text-black/42">{{ item.detail }}</div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[10px] leading-3 text-black/38">
              <span v-if="item.owner" class="rounded-full bg-white px-2 py-1 shadow-[0_4px_10px_rgba(15,23,42,0.03)]">负责人 {{ item.owner }}</span>
              <span v-if="item.due" class="rounded-full bg-white px-2 py-1 shadow-[0_4px_10px_rgba(15,23,42,0.03)]">截止 {{ item.due }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'meeting-recap'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <CalendarDays class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div v-if="card.participants?.length" class="flex flex-wrap items-center gap-2">
            <span v-for="participant in card.participants" :key="participant" class="rounded-full bg-[rgba(250,250,252,0.9)] px-2.5 py-1 text-[10px] leading-3 text-black/54 shadow-[0_6px_12px_rgba(15,23,42,0.02)]">
              {{ participant }}
            </span>
          </div>
          <div class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">已确认结论</div>
            <div class="mt-2 space-y-2">
              <div v-for="decision in card.decisions" :key="decision" class="flex items-start gap-2 text-[12px] leading-5 text-black/68">
                <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#726FFF]" />
                <span>{{ decision }}</span>
              </div>
            </div>
          </div>
          <div v-if="card.openQuestions?.length" class="rounded-[16px] bg-[rgba(255,250,240,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">待确认问题</div>
            <div class="mt-2 space-y-2">
              <div v-for="question in card.openQuestions" :key="question" class="flex items-start gap-2 text-[12px] leading-5 text-black/68">
                <Clock3 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#F59E0B]" />
                <span>{{ question }}</span>
              </div>
            </div>
          </div>
          <div v-if="card.actionItems?.length" class="space-y-2">
            <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">会后动作</div>
            <div
              v-for="item in card.actionItems"
              :key="item.id"
              class="rounded-[14px] bg-white/88 px-3 py-2.5 shadow-[0_6px_14px_rgba(15,23,42,0.02)]"
            >
              <div class="text-[12px] font-medium leading-4 text-black/72">{{ item.title }}</div>
              <div class="mt-1 text-[10px] leading-3 text-black/38">{{ item.owner }} · {{ item.due }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'schedule'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF2FF] text-[#726FFF]">
            <CalendarDays class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
          <span :data-testid="`card-status-${card.id}`" class="ml-auto rounded-full bg-[#F0EFFF] px-2 py-0.5 text-[10px] leading-3 text-[#726FFF]">{{ card.statusTag }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div v-if="card.description" class="text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          <div class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <div class="flex items-center gap-2 text-[12px] font-medium leading-4 text-black/74">
              <Clock3 class="h-3.5 w-3.5 text-[#726FFF]" />
              {{ card.scheduleLabel }}
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[10px] leading-3 text-black/40">
              <span class="rounded-full bg-white px-2 py-1 shadow-[0_4px_10px_rgba(15,23,42,0.03)]">下次 {{ card.nextRun }}</span>
              <span v-if="card.deliveryChannel" class="rounded-full bg-white px-2 py-1 shadow-[0_4px_10px_rgba(15,23,42,0.03)]">{{ card.deliveryChannel }}</span>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <Button
              v-for="action in card.actions"
              :key="action.id"
              :data-action-id="action.id"
              :data-testid="`card-action-${action.id}`"
              :disabled="pending"
              :variant="actionVariant(action)"
              :class="actionClass(action)"
              @click="submitAction(action)"
            >
              {{ isActionBusy(action.id) ? '处理中...' : action.label }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'connect-auth'">
      <div :data-testid="cardTestId(card.type)" :class="specialCardShellClass">
        <div :class="specialCardHeaderClass">
          <div class="flex h-5 w-5 items-center justify-center rounded-full bg-[#FFF7ED] text-[#EA580C]">
            <KeyRound class="h-3 w-3" />
          </div>
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-black/82">{{ card.title }}</span>
          <span :data-testid="`card-status-${card.id}`" class="ml-auto rounded-full bg-[#FFF7ED] px-2 py-0.5 text-[10px] leading-3 text-[#C2410C]">{{ card.statusTag }}</span>
        </div>
        <div :class="specialCardDividerClass" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div class="rounded-[16px] bg-[rgba(250,250,252,0.88)] px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.022)]">
            <div class="flex items-center gap-2 text-[12px] font-medium leading-4 text-black/74">
              <Link2 class="h-3.5 w-3.5 text-[#726FFF]" />
              {{ card.provider }}
            </div>
            <div class="mt-2 text-[12px] leading-5 text-black/54">{{ card.description }}</div>
          </div>
          <div class="space-y-2">
            <div class="text-[10px] uppercase tracking-[0.06em] text-black/34">所需权限</div>
            <div class="flex flex-wrap items-center gap-2">
              <span v-for="scope in card.scopes" :key="scope" class="rounded-full bg-white px-2.5 py-1 text-[10px] leading-3 text-black/56 shadow-[0_4px_10px_rgba(15,23,42,0.03)]">
                {{ scope }}
              </span>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <Button
              v-for="action in card.actions"
              :key="action.id"
              :data-action-id="action.id"
              :data-testid="`card-action-${action.id}`"
              :disabled="pending"
              :variant="actionVariant(action)"
              :class="actionClass(action)"
              @click="submitAction(action)"
            >
              {{ isActionBusy(action.id) ? '处理中...' : action.label }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'error-boundary'">
      <div :data-testid="cardTestId(card.type)" class="overflow-hidden rounded-[22px] bg-[linear-gradient(180deg,rgba(255,251,245,0.98)_0%,rgba(255,255,255,0.94)_100%)] shadow-[0_14px_30px_rgba(245,158,11,0.08)] backdrop-blur-[10px]">
        <div class="flex items-center gap-2 px-4 py-3">
          <ShieldAlert class="h-4 w-4 text-[#D97706]" />
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-[#B45309]">{{ card.title }}</span>
          <div class="ml-auto rounded-full bg-[#FEF3C7] px-2 py-px text-[10px] leading-3 text-[#B45309]">{{ card.severity === 'critical' ? '需要处理' : '权限提醒' }}</div>
        </div>
        <div class="mx-4 h-px bg-[linear-gradient(90deg,rgba(252,211,77,0)_0%,rgba(252,211,77,0.78)_16%,rgba(252,211,77,0.78)_84%,rgba(252,211,77,0)_100%)]" />
        <div class="space-y-3 px-4 pb-4 pt-3">
          <div class="text-[12px] leading-5 text-black/68">{{ card.description }}</div>
          <div v-if="card.blockedBy" class="rounded-[14px] bg-white/88 px-3 py-2.5 text-[11px] leading-4 text-black/56 shadow-[0_6px_14px_rgba(15,23,42,0.02)]">
            受限原因：{{ card.blockedBy }}
          </div>
          <div class="space-y-2">
            <div v-for="suggestion in card.suggestions" :key="suggestion" class="flex items-start gap-2 text-[11px] leading-4 text-black/56">
              <AlertTriangle class="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#D97706]" />
              <span>{{ suggestion }}</span>
            </div>
          </div>
          <div v-if="card.actions?.length" class="flex flex-wrap items-center gap-2">
            <Button
              v-for="action in card.actions"
              :key="action.id"
              :data-action-id="action.id"
              :data-testid="`card-action-${action.id}`"
              :disabled="pending"
              :variant="actionVariant(action)"
              :class="actionClass(action)"
              @click="submitAction(action)"
            >
              {{ isActionBusy(action.id) ? '处理中...' : action.label }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="card.type === 'approval'">
      <div :data-testid="cardTestId(card.type)" class="overflow-hidden rounded-[22px] bg-[linear-gradient(180deg,rgba(255,250,250,0.98)_0%,rgba(255,255,255,0.94)_100%)] shadow-[0_14px_30px_rgba(239,68,68,0.08)] backdrop-blur-[10px]">
        <div class="flex items-center gap-2 px-4 py-3">
          <div class="h-1.5 w-1.5 rounded-full bg-[#EF4444] animate-pulse" />
          <span data-testid="special-card-title" :class="specialCardTitleClass" class="text-[#B91C1C]">{{ card.title }}</span>
          <div class="ml-auto rounded-full border border-[#FCA5A5] bg-[#FEE2E2] px-2 py-px text-[10px] leading-3 text-[#DC2626]">{{ card.levelTag }}</div>
        </div>
        <div class="mx-4 h-px bg-[linear-gradient(90deg,rgba(252,165,165,0)_0%,rgba(252,165,165,0.72)_16%,rgba(252,165,165,0.72)_84%,rgba(252,165,165,0)_100%)]" />
        <div class="space-y-2.5 px-4 pb-4 pt-3">
          <div class="text-[12px] leading-5 text-black/68">{{ card.description }}</div>
          <div class="flex flex-wrap items-center gap-2">
            <Button
              v-for="action in card.actions"
              :key="normalizeAction(action).id"
              :data-action-id="normalizeAction(action).id"
              :data-testid="`card-action-${normalizeAction(action).id}`"
              :disabled="pending"
              :variant="actionVariant(normalizeAction(action))"
              :class="actionClass(normalizeAction(action))"
              @click="submitAction(action)"
            >
              {{ isActionBusy(normalizeAction(action).id) ? '处理中...' : normalizeAction(action).label }}
            </Button>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="flex flex-col gap-1">
        <div class="rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] bg-[rgba(255,255,255,0.64)] px-4 py-3 shadow-[0_6px_14px_rgba(15,23,42,0.04)]">
          <MarkdownMessage :content="card.content" tone="assistant" />
        </div>
        <MessageActions
          :message-id="card.id"
          :content="card.content"
          tone="assistant"
        />
      </div>
    </template>
  </div>
</template>
