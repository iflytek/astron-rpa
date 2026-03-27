<script setup lang="ts">
import { message, Switch } from 'ant-design-vue'
import { ArrowLeft, CalendarDays, Clock3, FolderOpen, Pencil, Play, ScrollText, TimerReset, Trash2, X, Zap } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import { aiStudioWorkspaceSuggestions } from '../registry'
import ModalActionBar from './ModalActionBar.vue'
import SegmentedPills from './SegmentedPills.vue'
import WorkspacePickerField from './WorkspacePickerField.vue'

type AutomationTask = {
  id: string
  title: string
  workspace: string
  nextRun: string
  frequency: string
  enabled: boolean
  lastRun?: string
  icon: string
}

type RunLog = {
  time: string
  status: 'success' | 'error'
  duration: string
  message: string
}

type ScheduleMode = 'daily' | 'workday' | 'weekly'

const emit = defineEmits<{
  (e: 'close'): void
}>()

const tasks = ref<AutomationTask[]>([
  {
    id: 'competitor-watch',
    title: '竞品动态监控（影刃 & 实在智能）',
    workspace: '市场调研',
    nextRun: '今天 12:00',
    frequency: '每天 12:00',
    enabled: true,
    lastRun: '昨天 12:01',
    icon: '监',
  },
  {
    id: 'finance-push',
    title: '每日财报数据推送',
    workspace: '财务助手',
    nextRun: '今天 08:30',
    frequency: '每天 08:30（工作日）',
    enabled: true,
    lastRun: '昨天 08:31',
    icon: '财',
  },
  {
    id: 'weekly-report',
    title: '周报自动生成',
    workspace: '数据分析师',
    nextRun: '周一 09:00',
    frequency: '每周一 09:00',
    enabled: false,
    lastRun: '上周一 09:02',
    icon: '报',
  },
])

const showAddTask = ref(false)
const activeLogTask = ref<AutomationTask | null>(null)
const editingTask = ref<AutomationTask | null>(null)
const runningTaskId = ref<string | null>(null)

const prompt = ref('')
const workspace = ref('~/Documents')
const time = ref('09:30')
const scheduleMode = ref<ScheduleMode>('workday')
const selectedWeekdays = ref<number[]>([1])

const weekdayOptions = [
  { id: 1, label: 'Mo', fullLabel: 'Monday' },
  { id: 2, label: 'Tu', fullLabel: 'Tuesday' },
  { id: 3, label: 'We', fullLabel: 'Wednesday' },
  { id: 4, label: 'Th', fullLabel: 'Thursday' },
  { id: 5, label: 'Fr', fullLabel: 'Friday' },
  { id: 6, label: 'Sa', fullLabel: 'Saturday' },
  { id: 0, label: 'Su', fullLabel: 'Sunday' },
] as const

const scheduleModeOptions = [
  { value: 'daily', label: '每天' },
  { value: 'workday', label: '工作日' },
  { value: 'weekly', label: '自定义' },
] as const

const enabledCount = computed(() => tasks.value.filter(task => task.enabled).length)
const canSubmit = computed(() => prompt.value.trim().length > 0)
const nextTask = computed(() => tasks.value.find(task => task.enabled))
const latestTriggeredTask = computed(() => tasks.value.find(task => task.lastRun === '刚刚'))
const recentRunText = computed(() => latestTriggeredTask.value ? '刚刚触发' : (nextTask.value?.nextRun || '暂无计划'))
const recentRunHint = computed(() => latestTriggeredTask.value ? latestTriggeredTask.value.title : '下一个运行窗口')
const recentWorkspaceSuggestions = computed(() => aiStudioWorkspaceSuggestions.slice(0, 3))
const logSuccessCount = computed(() => activeLogTask.value ? logItems(activeLogTask.value).filter(log => log.status === 'success').length : 0)
const logErrorCount = computed(() => activeLogTask.value ? logItems(activeLogTask.value).filter(log => log.status === 'error').length : 0)

const schedulePreview = computed(() => formatFrequency(scheduleMode.value, time.value, selectedWeekdays.value))
const nextRunPreview = computed(() => formatNextRun(scheduleMode.value, time.value, selectedWeekdays.value))
const scheduleSummary = computed(() => scheduleMode.value === 'weekly'
  ? '选择每周触发的日期后，在固定时间运行任务。'
  : scheduleMode.value === 'workday'
    ? '仅在工作日触发，适合日报、巡检和例行同步。'
    : '每天固定时间执行，适合高频自动化任务。')

function toggleWeekday(day: number) {
  selectedWeekdays.value = selectedWeekdays.value.includes(day)
    ? selectedWeekdays.value.filter(item => item !== day)
    : [...selectedWeekdays.value, day].sort((a, b) => a - b)
}

function formatFrequency(mode: ScheduleMode, scheduleTime: string, weekdays: number[]) {
  if (mode === 'daily')
    return `每天 ${scheduleTime}`
  if (mode === 'workday')
    return `工作日 ${scheduleTime}`
  const selected = weekdayOptions
    .filter(option => weekdays.includes(option.id))
    .map(option => option.fullLabel)
    .join('、')
  return `${selected ? `${selected} ` : ''}${scheduleTime}`
}

function formatNextRun(mode: ScheduleMode, scheduleTime: string, weekdays: number[]) {
  if (mode === 'daily' || mode === 'workday')
    return `今天 ${scheduleTime}`

  const firstSelected = weekdayOptions.find(option => weekdays.includes(option.id))
  return `${firstSelected?.fullLabel || '下次'} ${scheduleTime}`
}

function resetTaskForm() {
  prompt.value = ''
  workspace.value = '~/Documents'
  time.value = '09:30'
  scheduleMode.value = 'workday'
  selectedWeekdays.value = [1]
}

function removeTask(id: string) {
  tasks.value = tasks.value.filter(task => task.id !== id)
  void message.success('自动化任务已删除')
}

function createTask() {
  if (!canSubmit.value)
    return

  tasks.value.unshift({
    id: `task-${Date.now()}`,
    title: prompt.value.trim().slice(0, 24),
    workspace: workspace.value.trim() || '~/Documents',
    nextRun: `今天 ${time.value}`,
    frequency: `每天 ${time.value}`,
    enabled: true,
    lastRun: '未运行',
    icon: '新',
  })

  tasks.value[0].nextRun = formatNextRun(scheduleMode.value, time.value, selectedWeekdays.value)
  tasks.value[0].frequency = formatFrequency(scheduleMode.value, time.value, selectedWeekdays.value)
  resetTaskForm()
  showAddTask.value = false
}

function toggleTask(task: AutomationTask) {
  task.enabled = !task.enabled
}

function openEditTask(task: AutomationTask) {
  editingTask.value = { ...task }
}

function saveTaskEdit() {
  if (!editingTask.value)
    return

  tasks.value = tasks.value.map(task =>
    task.id === editingTask.value?.id
      ? { ...editingTask.value }
      : task,
  )

  editingTask.value = null
}

function runNow(task: AutomationTask) {
  runningTaskId.value = task.id
  task.lastRun = '刚刚'

  setTimeout(() => {
    runningTaskId.value = null
  }, 1800)
}

function logItems(task: AutomationTask): RunLog[] {
  return [
    { time: task.lastRun || '刚刚', status: 'success', duration: '2m 14s', message: '任务执行完成，共处理 12 项数据。' },
    { time: '昨天同一时段', status: 'success', duration: '1m 58s', message: '任务执行完成，产出已同步到工作区。' },
    { time: '前天同一时段', status: 'error', duration: '0m 43s', message: '网络超时，重试 3 次后失败。' },
  ]
}
</script>

<template>
  <div class="relative flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-[linear-gradient(180deg,#FBFCFF_0%,#F8FAFF_100%)]">
    <div class="flex shrink-0 items-center justify-between border-b border-[#E8E8E8] px-6 py-3.5">
        <div class="flex items-center gap-3">
          <button
            aria-label="关闭自动化任务"
            class="flex h-7 w-7 items-center justify-center rounded-lg border border-[#E5E7EB] bg-white transition-colors hover:bg-[#F6F8FF]"
          @click="emit('close')"
        >
          <ArrowLeft class="h-3.5 w-3.5 text-black/56" />
        </button>
        <div class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#F0EFFF] text-[var(--color-primary)]">
            <Zap class="h-3.5 w-3.5" />
          </div>
          <span class="text-[14px] font-semibold leading-5 text-[#1A1A2E]">自动化任务</span>
        </div>
        <div class="h-4 w-px bg-[#E5E7EB]" />
        <div class="flex items-center gap-1.5">
          <div class="h-1.5 w-1.5 rounded-full bg-[var(--color-primary)]" />
          <span class="text-[11px] leading-4 text-[var(--color-primary)]">{{ enabledCount }} 个运行中</span>
        </div>
        <span class="text-[11px] leading-4 text-black/28">共 {{ tasks.length }} 个</span>
      </div>

      <Button
        data-testid="automation-add-task-trigger"
        size="sm"
        class="h-9 rounded-[12px] px-4"
        @click="showAddTask = true"
      >
        <Zap class="h-3.5 w-3.5" />
        <span class="text-[12px] font-medium leading-4">新增任务</span>
      </Button>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto">
      <div class="grid grid-cols-3 gap-3 border-b border-[#EEF0F5] bg-[#FCFCFE] px-6 py-4">
        <div data-testid="automation-metric-enabled" class="rounded-[18px] border border-[#E7EAF2] bg-[linear-gradient(180deg,#FFFFFF_0%,#FCFDFF_100%)] px-4 py-3.5 shadow-[0_10px_24px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">启用中</div>
              <div class="mt-1 text-[24px] font-semibold leading-7 text-[#1A1A2E]">{{ enabledCount }}</div>
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[linear-gradient(135deg,#F0EFFF,#E7E6FF)] text-[var(--color-primary)]">
              <Zap class="h-4 w-4" />
            </div>
          </div>
          <div class="mt-2 flex items-center justify-between gap-3">
            <div class="text-[11px] leading-4 text-black/42">当前正在运行的自动化任务数量</div>
            <span class="rounded-full bg-[#EEF7F1] px-2 py-1 text-[10px] font-medium leading-3 text-[#16A34A]">活跃</span>
          </div>
        </div>
        <div data-testid="automation-metric-recent" class="rounded-[18px] border border-[#E7EAF2] bg-[linear-gradient(180deg,#FFFFFF_0%,#FCFDFF_100%)] px-4 py-3.5 shadow-[0_10px_24px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">最近触发</div>
              <div class="mt-1 text-[18px] font-semibold leading-6 text-[#1A1A2E]">{{ recentRunText }}</div>
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[linear-gradient(135deg,#EEF5FF,#E2ECFF)] text-[#4D78FF]">
              <TimerReset class="h-4 w-4" />
            </div>
          </div>
          <div class="mt-2 text-[11px] leading-4 text-black/42">{{ recentRunHint }}</div>
          <div class="mt-2 inline-flex items-center gap-1 rounded-full bg-[#F5F7FB] px-2 py-1 text-[10px] leading-3 text-black/42">
            <Clock3 class="h-3 w-3 text-black/34" />
            贴近实际调度窗口
          </div>
        </div>
        <div data-testid="automation-metric-workspace" class="rounded-[18px] border border-[#E7EAF2] bg-[linear-gradient(180deg,#FFFFFF_0%,#FCFDFF_100%)] px-4 py-3.5 shadow-[0_10px_24px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">默认工作区</div>
              <div class="mt-1 truncate text-[15px] font-semibold leading-5 text-[#1A1A2E]">~/Documents</div>
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[linear-gradient(135deg,#FFF6E8,#FFF1D8)] text-[#D97706]">
              <FolderOpen class="h-4 w-4" />
            </div>
          </div>
          <div class="mt-2 text-[11px] leading-4 text-black/42">新增任务默认在该目录执行</div>
        </div>
      </div>

      <template v-if="tasks.length > 0">
        <table class="w-full border-collapse">
          <thead>
            <tr class="border-b border-[#F0F0F0]">
              <th class="px-5 py-2.5 text-left text-[10px] font-medium uppercase tracking-[0.12em] text-black/32">任务</th>
              <th class="px-3 py-2.5 text-left text-[10px] font-medium uppercase tracking-[0.12em] text-black/32">执行计划</th>
              <th class="px-3 py-2.5 text-left text-[10px] font-medium uppercase tracking-[0.12em] text-black/32">状态</th>
              <th class="px-5 py-2.5 text-left text-[10px] font-medium uppercase tracking-[0.12em] text-black/32" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="task in tasks"
              :key="task.id"
              class="group border-b border-[#F1F3F7] transition-colors hover:bg-[#FCFCFE]"
            >
              <td class="px-5 py-3">
                <div class="flex items-start gap-3">
                  <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-[11px] bg-[linear-gradient(135deg,#F2EFFF,#EAE7FF)] text-[var(--color-primary)] ring-1 ring-[#DCD8FF]">
                    <span class="text-[12px] font-semibold">{{ task.icon }}</span>
                  </div>
                  <div class="min-w-0">
                    <div class="text-[13px] font-medium leading-5 text-black/82">{{ task.title }}</div>
                    <div class="mt-0.5 text-[11px] leading-4 text-black/38">{{ task.workspace }}</div>
                  </div>
                </div>
              </td>
              <td class="px-3 py-3">
                <div class="flex flex-col gap-0.5">
                  <div class="flex items-center gap-2 text-[11px] leading-4 text-black/56">
                    <Clock3 class="h-3.5 w-3.5" />
                    <span>{{ task.frequency }}</span>
                  </div>
                  <div class="text-[10px] leading-3 text-black/36">
                    {{ task.enabled ? `下次 ${task.nextRun}` : '已暂停' }}
                  </div>
                </div>
              </td>
              <td class="px-3 py-3">
                <div :data-testid="`automation-task-switch-${task.id}`" class="flex items-center gap-2">
                  <Switch
                    size="small"
                    :checked="task.enabled"
                    @change="toggleTask(task)"
                  />
                  <div v-if="runningTaskId === task.id" class="h-2.5 w-2.5 rounded-full border-[1.5px] border-[var(--color-primary)] border-t-transparent animate-spin" />
                </div>
              </td>
              <td class="px-5 py-3">
                <div class="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <button class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#EEF2FF] hover:text-[var(--color-primary)]" @click="runNow(task)">
                    <Play class="h-3.5 w-3.5" />
                  </button>
                  <button :data-testid="`automation-log-trigger-${task.id}`" class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#EEF2FF] hover:text-[var(--color-primary)]" @click="activeLogTask = task">
                    <ScrollText class="h-3.5 w-3.5" />
                  </button>
                  <button class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#EEF2FF] hover:text-[var(--color-primary)]" @click="openEditTask(task)">
                    <Pencil class="h-3.5 w-3.5" />
                  </button>
                  <a-popconfirm
                    placement="leftTop"
                    title="删除任务"
                    description="删除后将停止该自动化任务的后续调度。"
                    ok-text="删除任务"
                    cancel-text="取消"
                    @confirm="removeTask(task.id)"
                  >
                    <button
                      :data-testid="`automation-delete-trigger-${task.id}`"
                      class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#FEF2F2] hover:text-[#EF4444]"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </button>
                  </a-popconfirm>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </template>

      <template v-else>
        <div class="flex flex-col items-center justify-center gap-3 py-32">
          <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F3F4F6]">
            <Zap class="h-6 w-6 text-black/22" />
          </div>
          <div class="text-[13px] font-medium leading-5 text-black/70">暂无自动化任务</div>
          <div class="text-[12px] leading-4 text-black/36">点击“新增任务”创建你的第一个自动化任务</div>
        </div>
      </template>
    </div>

    <div
      v-if="showAddTask"
      class="absolute inset-0 z-10 flex items-center justify-center bg-[rgba(10,10,20,0.32)] px-4 py-4 backdrop-blur-[4px]"
      @click.self="showAddTask = false"
    >
      <div data-testid="automation-add-task-modal" class="flex w-[560px] max-h-[calc(100%-24px)] max-w-[calc(100%-32px)] flex-col overflow-hidden rounded-[26px] bg-[rgba(255,255,255,0.98)] shadow-[0_28px_90px_rgba(15,23,42,0.18)] backdrop-blur-[18px]">
        <div class="flex items-center justify-between border-b border-[#F0F0F0] px-6 py-4">
          <div class="flex items-center gap-2.5">
            <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#F0EFFF] text-[var(--color-primary)]">
              <Zap class="h-3.5 w-3.5" />
            </div>
            <div class="text-[13px] font-semibold leading-5 text-[#1A1A2E]">新增自动化任务</div>
          </div>
          <button
            aria-label="关闭新增任务"
            class="flex h-7 w-7 items-center justify-center rounded-lg transition-colors hover:bg-[#F3F4F6]"
            @click="showAddTask = false"
          >
            <X class="h-3.5 w-3.5 text-black/56" />
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <div class="space-y-4 px-6 py-5">
            <div>
              <label class="mb-1.5 block text-[12px] font-medium leading-4 text-black/76">任务描述 <span class="text-[#EF4444]">*</span></label>
              <textarea
                v-model="prompt"
                rows="4"
                class="w-full resize-none rounded-[16px] border-0 bg-[var(--ai-surface-soft)] px-3.5 py-3 text-[13px] leading-[22px] text-black/76 shadow-[inset_0_0_0_1px_rgba(215,224,239,0.9)] outline-none transition-all placeholder:text-black/28 focus:ring-4 focus:ring-[var(--color-primary)]/8"
                placeholder="例如：每天同步最新 AI 助手页面截图，对比参考设计并输出差异清单。"
              />
            </div>

            <WorkspacePickerField
              v-model="workspace"
              label="工作目录"
              test-id-prefix="automation"
              :suggestions="recentWorkspaceSuggestions"
            />

            <div>
              <label class="mb-1.5 block text-[12px] font-medium leading-4 text-black/76">执行时间</label>
              <div class="rounded-[20px] bg-[linear-gradient(180deg,rgba(247,248,253,0.96)_0%,rgba(252,252,255,0.98)_100%)] px-4 py-4 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.9)]">
                <SegmentedPills
                  v-model="scheduleMode"
                  test-id="automation-schedule-tabs"
                  :options="scheduleModeOptions"
                />

                <div class="mt-3 flex flex-wrap items-center gap-3">
                  <div data-testid="automation-time-field" class="flex items-center gap-2 rounded-[14px] bg-white px-3 py-2 shadow-[0_10px_20px_rgba(15,23,42,0.04)]">
                    <Clock3 class="h-3.5 w-3.5 text-[var(--color-primary)]" />
                    <input
                      v-model="time"
                      type="time"
                      class="min-w-[108px] bg-transparent text-[12px] font-medium leading-4 text-black/72 outline-none"
                    >
                  </div>

                  <div v-if="scheduleMode === 'weekly'" class="flex flex-wrap gap-1.5">
                    <button
                      v-for="day in weekdayOptions"
                      :key="day.id"
                      type="button"
                      class="flex h-8 w-8 items-center justify-center rounded-full text-[11px] font-medium transition-all"
                      :class="selectedWeekdays.includes(day.id)
                        ? 'bg-[var(--color-primary)] text-white shadow-[0_8px_18px_rgba(114,111,255,0.22)]'
                        : 'bg-white text-black/48 shadow-[0_6px_14px_rgba(15,23,42,0.04)] hover:text-black/66'"
                      @click="toggleWeekday(day.id)"
                    >
                      {{ day.label }}
                    </button>
                  </div>
                  <div v-else class="inline-flex items-center gap-1 rounded-full bg-white/84 px-2.5 py-1 text-[11px] leading-4 text-black/48 shadow-[0_6px_14px_rgba(15,23,42,0.03)]">
                    <CalendarDays class="h-3.5 w-3.5 text-[var(--color-primary)]" />
                    {{ scheduleSummary }}
                  </div>
                </div>

                <div class="mt-3 rounded-[14px] bg-white/82 px-3 py-2.5 text-[11px] leading-4 text-black/52 shadow-[0_8px_18px_rgba(15,23,42,0.03)]">
                  <div class="font-medium text-black/64">{{ schedulePreview }}</div>
                  <div class="mt-1 text-black/40">{{ nextRunPreview }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <ModalActionBar
          test-id="automation"
          submit-label="添加任务"
          :submit-disabled="!canSubmit"
          @cancel="showAddTask = false"
          @submit="createTask"
        />
      </div>
    </div>

    <div
      v-if="activeLogTask"
      class="absolute inset-0 z-20 flex items-center justify-center bg-[rgba(10,10,20,0.35)] backdrop-blur-[4px]"
      @click.self="activeLogTask = null"
    >
      <div data-testid="automation-log-modal" class="flex w-[620px] max-h-[82vh] flex-col overflow-hidden rounded-[24px] bg-[rgba(255,255,255,0.98)] shadow-[0_28px_80px_rgba(15,23,42,0.18)]">
        <div class="flex items-center justify-between border-b border-[#EBEBEB] px-5 py-4">
          <div class="flex items-center gap-2.5">
            <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#F0EFFF] text-[var(--color-primary)]">
              <ScrollText class="h-3.5 w-3.5" />
            </div>
            <div>
              <div class="text-[13px] font-semibold leading-4 text-[#1A1A2E]">运行日志</div>
              <div class="mt-0.5 max-w-[320px] truncate text-[10px] leading-3.5 text-black/36">{{ activeLogTask.title }}</div>
            </div>
          </div>
          <button
            aria-label="关闭运行日志"
            class="flex h-7 w-7 items-center justify-center rounded-lg transition-colors hover:bg-[#F3F4F6]"
            @click="activeLogTask = null"
          >
            <X class="h-3.5 w-3.5 text-black/56" />
          </button>
        </div>
        <div data-testid="automation-log-summary" class="grid grid-cols-3 gap-3 border-b border-[#EEF0F5] bg-[#FCFCFE] px-5 py-4">
          <div class="rounded-[16px] border border-[#E8EBF3] bg-white px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.035)]">
            <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">最近结果</div>
            <div class="mt-1 text-[14px] font-semibold leading-5 text-[#1A1A2E]">{{ activeLogTask?.lastRun || '刚刚' }}</div>
            <div class="mt-1 text-[11px] leading-4 text-black/42">最近一次执行时间</div>
          </div>
          <div class="rounded-[16px] border border-[#E8EBF3] bg-white px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.035)]">
            <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">成功 / 失败</div>
            <div class="mt-1 text-[14px] font-semibold leading-5 text-[#1A1A2E]">{{ logSuccessCount }} / {{ logErrorCount }}</div>
            <div class="mt-1 text-[11px] leading-4 text-black/42">最近三次执行样本</div>
          </div>
          <div class="rounded-[16px] border border-[#E8EBF3] bg-white px-3.5 py-3 shadow-[0_8px_18px_rgba(15,23,42,0.035)]">
            <div class="text-[10px] font-medium tracking-[0.08em] text-black/32">任务状态</div>
            <div class="mt-1 text-[14px] font-semibold leading-5 text-[#1A1A2E]">{{ activeLogTask?.enabled ? '已启用' : '已暂停' }}</div>
            <div class="mt-1 text-[11px] leading-4 text-black/42">调度状态与当前任务联动</div>
          </div>
        </div>
        <div class="grow overflow-y-auto p-5">
          <div data-testid="automation-log-list" class="space-y-2.5">
            <div
              v-for="(log, index) in logItems(activeLogTask)"
              :key="`${activeLogTask.id}-${index}`"
              class="flex items-start gap-3 rounded-[16px] border border-[#EBEBEB] bg-[linear-gradient(180deg,#FFFFFF_0%,#FAFBFD_100%)] px-4 py-3.5 shadow-[0_8px_18px_rgba(15,23,42,0.03)]"
            >
              <div class="flex flex-col items-center pt-0.5">
                <div class="h-2.5 w-2.5 shrink-0 rounded-full" :class="log.status === 'success' ? 'bg-[#726FFF]' : 'bg-[#EF4444]'" />
                <div v-if="index < logItems(activeLogTask).length - 1" class="mt-1 h-10 w-px bg-[#E7EBF4]" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="mb-1 flex items-center gap-2">
                  <span class="text-[11px] font-medium leading-4 text-black/68">{{ log.time }}</span>
                  <span class="rounded-full px-2 py-0.5 text-[9px] font-medium leading-3" :class="log.status === 'success' ? 'bg-[#F3F1FF] text-[#726FFF]' : 'bg-[#FEF2F2] text-[#EF4444]'">
                    {{ log.status === 'success' ? '成功' : '失败' }}
                  </span>
                  <span class="ml-auto rounded-full bg-[#F5F7FB] px-2 py-0.5 text-[10px] leading-3 text-black/34">{{ log.duration }}</span>
                </div>
                <div class="text-[11px] leading-4 text-black/56">{{ log.message }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="editingTask"
      class="absolute inset-0 z-20 flex items-center justify-center bg-[rgba(10,10,20,0.35)] px-4 py-4 backdrop-blur-[4px]"
      @click.self="editingTask = null"
    >
      <div class="flex w-[540px] max-h-[calc(100%-24px)] max-w-[calc(100%-32px)] flex-col overflow-hidden rounded-2xl bg-white shadow-[0_24px_70px_rgba(0,0,0,0.16)]">
        <div class="flex items-center justify-between border-b border-[#EBEBEB] px-5 py-4">
          <div class="flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#F0EFFF] text-[var(--color-primary)]">
              <Pencil class="h-4 w-4" />
            </div>
            <div>
              <div class="text-[13px] font-semibold leading-4 text-[#1A1A2E]">编辑自动化任务</div>
              <div class="mt-0.5 text-[10px] leading-3.5 text-black/36">{{ editingTask.title }}</div>
            </div>
          </div>
          <button class="flex h-7 w-7 items-center justify-center rounded-lg transition-colors hover:bg-[#F3F4F6]" @click="editingTask = null">
            <X class="h-3.5 w-3.5 text-black/56" />
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <div class="space-y-4 p-5">
            <div>
              <label class="mb-1.5 block text-[12px] font-medium leading-4 text-black/76">任务名称</label>
              <Input v-model="editingTask.title" class="h-10 rounded-[12px] border-[#E5E7EB] bg-[#F9FAFB] text-[13px]" />
            </div>
            <WorkspacePickerField
              v-model="editingTask.workspace"
              label="工作目录"
              test-id-prefix="automation-edit"
              :suggestions="aiStudioWorkspaceSuggestions"
            />
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="mb-1.5 block text-[12px] font-medium leading-4 text-black/76">下次执行</label>
                <Input v-model="editingTask.nextRun" class="h-10 rounded-[12px] border-[#E5E7EB] bg-[#F9FAFB] text-[13px]" />
              </div>
              <div>
                <label class="mb-1.5 block text-[12px] font-medium leading-4 text-black/76">执行计划</label>
                <Input v-model="editingTask.frequency" class="h-10 rounded-[12px] border-[#E5E7EB] bg-[#F9FAFB] text-[13px]" />
              </div>
            </div>
          </div>
        </div>

        <ModalActionBar
          test-id="automation-edit"
          submit-label="保存修改"
          @cancel="editingTask = null"
          @submit="saveTaskEdit"
        />
      </div>
    </div>
  </div>
</template>
