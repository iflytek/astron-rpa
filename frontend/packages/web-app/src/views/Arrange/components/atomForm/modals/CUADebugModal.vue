<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { CloseOutlined, MinusOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

import { fileRead, fileWrite } from '@/api/resource'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { blob2Text } from '@/utils/common'
import { CUA_DEBUG_STANDALONE_RUN_KEY, WINDOW_NAME } from '@/constants'
import { windowManager } from '@/platform'

const CUA_DEBUG_LOG_PATH = './.cua_debug_runs.jsonl'
const CUA_DEBUG_CONFIG_PATH = './.cua_debug_config.json'
const STANDALONE_EXPANDED_SIZE = { width: 360, height: 520 }
const STANDALONE_COLLAPSED_SIZE = { width: 320, height: 300 }

interface CuaDebugEvent {
  event: string
  step?: number
  thought?: string
  screenshot?: string
  status?: string
  message?: string
  instruction?: string
  action_type?: string
  error?: string
}

interface DebugEntry {
  id: string
  kind: 'status' | 'step'
  text: string
  status?: string
  step?: number
  screenshotPath?: string
  screenshotUrl?: string
  timestamp: string
}

const props = defineProps<{
  atomId: string
  initialInstruction: string
  atomSnapshot?: RPA.Atom
  currentLine?: number
  projectId?: string
  processId?: string
  project?: {
    id: string
    name: string
    version: number
  }
}>()

const standaloneWindow = window.location.pathname.endsWith('/cuadebug.html') || window.location.pathname.endsWith('cuadebug.html')
const modal = standaloneWindow
  ? { visible: true, hide: () => {}, resolveHide: () => {}, remove: () => {} }
  : NiceModal.useModal()
const flowStore = useFlowStore()
const processStore = useProcessStore()
const runningStore = useRunningStore()

const instruction = ref(props.initialInstruction || '')
const collapsed = ref(false)
const loading = ref(false)
const entries = ref<DebugEntry[]>([])
const logListRef = ref<HTMLElement | null>(null)
const isSelfRunning = ref(false)
const currentRunId = ref('')
const runStartedAt = ref('')
const finalizedRunId = ref('')
const streamLineCount = ref(0)
const awaitingFirstLog = ref(false)
const pollTimer = ref<number | null>(null)

const currentAtom = computed(() => flowStore.simpleFlowUIData.find(item => item.id === props.atomId) ?? flowStore.activeAtom ?? props.atomSnapshot)
const currentLine = computed(() => props.currentLine || flowStore.simpleFlowUIData.findIndex(item => item.id === props.atomId) + 1)
const instructionItem = computed(() => currentAtom.value?.inputList?.find(item => item.key === 'instruction'))
const resolvedProjectId = computed(() => props.projectId || props.project?.id || processStore.project.id)
const resolvedProcessId = computed(() => props.processId || processStore.activeProcessId)
const isRunning = computed(() => isSelfRunning.value && ['run', 'debug'].includes(runningStore.running))
const runButtonText = computed(() => (isRunning.value ? '停止' : '运行'))
const debugStreamPath = computed(() => `./venvs/${resolvedProjectId.value}/astron/.cua_debug_stream.jsonl`)
const collapseButtonText = computed(() => (collapsed.value ? 'Expand' : 'Collapse'))
const panelWidth = computed(() => (collapsed.value ? 360 : 460))
const isStandaloneWindow = computed(() => standaloneWindow)
const debugPanelTitle = computed(() => currentAtom.value?.title || '调试模式')

if (props.project) {
  processStore.setProject(props.project)
}
else if (props.projectId) {
  processStore.setProject({ ...processStore.project, id: props.projectId })
}

if (props.processId) {
  processStore.activeProcessId = props.processId
}

if (props.atomSnapshot) {
  flowStore.setActiveAtom(props.atomSnapshot, false)
}

const EVENT_MESSAGE_MAP: Record<string, string> = {
  debug_started: 'Debug started',
  waiting_for_valid_action: 'Waiting for a valid action',
  run_finished: 'Run finished',
  max_steps_reached: 'Max steps reached',
  debug_stopped: 'Debug stopped',
  run_failed: 'Run failed',
}


function buildInstructionValue(value: string) {
  const source = instructionItem.value?.value
  if (Array.isArray(source) && source.length > 0) {
    return source.map((item, index) => (index === 0 ? { ...item, value } : item))
  }

  return [{ type: 'str', value }]
}

function syncStandaloneRunState(running: boolean) {
  if (!isStandaloneWindow.value) {
    return
  }

  windowManager.emitTo({
    from: WINDOW_NAME.CUA_DEBUG,
    target: WINDOW_NAME.MAIN,
    type: 'cua-debug-run-state',
    data: { running },
  })
}

function requestProjectSave() {
  if (!isStandaloneWindow.value) {
    return
  }

  windowManager.emitTo({
    from: WINDOW_NAME.CUA_DEBUG,
    target: WINDOW_NAME.MAIN,
    type: 'cua-debug-save-project',
    data: {
      atomId: currentAtom.value?.id,
      processId: resolvedProcessId.value,
      value: buildInstructionValue(instruction.value),
    },
  })
}

async function syncInstructionToAtom() {
  if (!currentAtom.value) {
    return
  }

  const value = buildInstructionValue(instruction.value)

  if (isStandaloneWindow.value) {
    await windowManager.emitTo({
      from: WINDOW_NAME.CUA_DEBUG,
      target: WINDOW_NAME.MAIN,
      type: 'cua-debug-sync-instruction',
      data: { atomId: currentAtom.value.id, value },
    })
    return
  }

  flowStore.setFormItemValue('instruction', value, currentAtom.value.id)
}


function revokeScreenshotUrls() {
  entries.value.forEach((entry) => {
    if (entry.screenshotUrl) {
      URL.revokeObjectURL(entry.screenshotUrl)
    }
  })
}

function resetRunEntries() {
  revokeScreenshotUrls()
  entries.value = []
  streamLineCount.value = 0
  loading.value = false
  awaitingFirstLog.value = false
  currentRunId.value = ''
  runStartedAt.value = ''
}

async function loadScreenshotUrl(path: string) {
  try {
    const { data } = await fileRead({ path })
    return URL.createObjectURL(data)
  }
  catch (error) {
    console.error('Failed to load screenshot:', error)
    return ''
  }
}

async function hydrateScreenshotUrls() {
  if (collapsed.value) {
    return
  }

  for (const entry of entries.value) {
    if (entry.screenshotPath && !entry.screenshotUrl) {
      entry.screenshotUrl = await loadScreenshotUrl(entry.screenshotPath)
    }
  }
}

function appendEntry(entry: Omit<DebugEntry, 'id' | 'timestamp'> & { timestamp?: string }) {
  awaitingFirstLog.value = false
  entries.value.push({
    id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
    timestamp: entry.timestamp || dayjs().format('YYYY-MM-DD HH:mm:ss'),
    ...entry,
  })
  nextTick(() => {
    if (logListRef.value) {
      logListRef.value.scrollTop = logListRef.value.scrollHeight
    }
  })
}

function formatEventMessage(event: CuaDebugEvent) {
  if (event.message && EVENT_MESSAGE_MAP[event.message]) {
    return EVENT_MESSAGE_MAP[event.message]
  }
  if (event.message === 'Debug started') return '开始调试'
  if (event.message === 'Waiting for a valid action') return '等待有效操作'
  if (event.message === 'Run finished') return '运行完成'
  if (event.message === 'Max steps reached') return '达到最大步数'
  if (event.message === 'Debug stopped') return '调试停止'
  if (event.message === 'Run failed') return '运行失败'

  if (event.error) {
    return event.error
  }

  return event.message || '完成'
}

async function appendEventLog(event: CuaDebugEvent, timestamp: string) {
  const terminalMessages: Record<string, string> = {
    run_finished: 'runSuccess',
    max_steps_reached: 'maxStepsReached',
    debug_stopped: 'manual_stop',
    run_failed: 'runFailed',
  }
  const suppressedMessages = new Set(['run_finished'])
  loading.value = false

  const messageKey = event.message || event.status
  const formatted = formatEventMessage(event)
  if ((messageKey && suppressedMessages.has(messageKey)) || /run finished/i.test(formatted) || formatted.includes('运行完成')) {
    return
  }

  if (event.event === 'step') {
    loading.value = false
    appendEntry({
      kind: 'step',
      status: event.status,
      step: event.step,
      text: event.thought || formatEventMessage(event) || 'No thought captured',
      screenshotPath: event.screenshot || '',
      timestamp,
    })

    if (!collapsed.value && event.screenshot) {
      const target = entries.value[entries.value.length - 1]
      target.screenshotUrl = await loadScreenshotUrl(event.screenshot)
    }
    return
  }

  const terminalStatus = event.message ? terminalMessages[event.message] : undefined
  if (!(isStandaloneWindow.value && terminalStatus)) {
    loading.value = false
    appendEntry({
      kind: 'status',
      status: event.status,
      text: formatEventMessage(event),
      timestamp,
    })
  }

  if (isStandaloneWindow.value && terminalStatus) {
    await finalizeRun(terminalStatus, false)
  }
}


async function pollDebugStream() {
  try {
    const { data } = await fileRead({ path: debugStreamPath.value })
    const content = await blob2Text<string>(data)
    const lines = content.split(/\r?\n/).filter(Boolean)
    const nextLines = lines.slice(streamLineCount.value)
    streamLineCount.value = lines.length

    for (const line of nextLines) {
      try {
        const event = JSON.parse(line) as CuaDebugEvent & { timestamp?: string }
        await appendEventLog(event, event.timestamp || dayjs().format('YYYY-MM-DD HH:mm:ss'))
      }
      catch (error) {
        console.error('Failed to parse stream event:', error, line)
      }
    }
  }
  catch {
    // The stream file may not exist before the first step is written.
  }
}

function startPollingDebugStream() {
  stopPollingDebugStream()
  pollTimer.value = window.setInterval(() => {
    void pollDebugStream()
  }, 500)
}

function stopPollingDebugStream() {
  if (pollTimer.value !== null) {
    window.clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

async function persistCurrentRun(status: string) {
  if (!currentRunId.value) {
    return
  }

  const payload = {
    runId: currentRunId.value,
    projectId: resolvedProjectId.value,
    processId: resolvedProcessId.value,
    atomId: props.atomId,
    atomKey: currentAtom.value?.key || '',
    instruction: instruction.value,
    status,
    startedAt: runStartedAt.value,
    finishedAt: new Date().toISOString(),
    entries: entries.value.map(({ screenshotUrl, ...entry }) => entry),
  }

  try {
    await fileWrite({
      path: CUA_DEBUG_LOG_PATH,
      mode: 'a',
      content: `${JSON.stringify(payload)}
`,
    })
  }
  catch (error) {
    console.error('Failed to persist CUA debug log:', error)
  }
}

async function finalizeRun(status: string, syncStream = true) {
  if (!isSelfRunning.value || finalizedRunId.value === currentRunId.value) {
    return
  }

  loading.value = false
  appendEntry({ kind: 'status', text: '完成', status })
  stopPollingDebugStream()
  if (syncStream) {
    await pollDebugStream()
  }
  await persistCurrentRun(status)
  finalizedRunId.value = currentRunId.value
  isSelfRunning.value = false
}

async function stopCurrentRun(status = 'manual_stop') {
  if (!isSelfRunning.value) {
    return
  }

  await finalizeRun(status)

  if (['run', 'debug'].includes(runningStore.running)) {
    runningStore.stop(resolvedProjectId.value)
  }
}

async function handleRunOrStop() {
  if (isRunning.value) {
    await stopCurrentRun()
    return
  }

  if (runningStore.running !== 'free') {
    message.warning('Another task is running.')
    return
  }

  if (!currentAtom.value || currentLine.value <= 0) {
    message.warning('Current atom is unavailable.')
    return
  }

  await syncInstructionToAtom()

  if (!resolvedProjectId.value || !resolvedProcessId.value || currentLine.value <= 0) {
    message.error('Debug context is incomplete. Please reopen the debug window from the editor.')
    return
  }

  if (isStandaloneWindow.value) {
    requestProjectSave()
  }

  if (!isStandaloneWindow.value) {
    try {
      await processStore.saveProject()
    }
    catch {
      message.error('Failed to save before debug run.')
      return
    }
  }

  try {
    resetRunEntries()
    localStorage.setItem(CUA_DEBUG_STANDALONE_RUN_KEY, '1')
    syncStandaloneRunState(true)
    await fileWrite({
      path: CUA_DEBUG_CONFIG_PATH,
      mode: 'w',
      content: JSON.stringify({ streamPath: debugStreamPath.value }),
    })
    await fileWrite({ path: debugStreamPath.value, mode: 'w', content: '' })
    streamLineCount.value = 0
    loading.value = true
    isSelfRunning.value = true
    awaitingFirstLog.value = true
    currentRunId.value = `${Date.now()}`
    runStartedAt.value = new Date().toISOString()
    finalizedRunId.value = ''

    startPollingDebugStream()

    runningStore.startRun(
      resolvedProjectId.value,
      resolvedProcessId.value,
      currentLine.value,
      currentLine.value,
      { minimizeWindow: false, hideLogWindow: true },
    )
  }
  catch (error) {
    console.error('Failed to start CUA debug run:', error)
    localStorage.removeItem(CUA_DEBUG_STANDALONE_RUN_KEY)
    syncStandaloneRunState(false)
    stopPollingDebugStream()
    loading.value = false
    isSelfRunning.value = false
    message.error('Failed to start CUA debug run')
  }
}

async function closePanel(forceStop = false) {
  await syncInstructionToAtom()
  if (forceStop) {
    await stopCurrentRun()
  }
  if (isStandaloneWindow.value) {
    localStorage.removeItem(CUA_DEBUG_STANDALONE_RUN_KEY)
    if (!isRunning.value) {
      syncStandaloneRunState(false)
    }
    windowManager.closeWindow(WINDOW_NAME.CUA_DEBUG)
    windowManager.showWindow()
    return
  }
  modal.hide()
}

function handleBack() {
  void closePanel(isRunning.value)
}

function handleClose() {
  void closePanel(isRunning.value)
}

function handleAfterOpenChange(open: boolean) {
  if (!open) {
    stopPollingDebugStream()
    if (!isStandaloneWindow.value) {
      modal.resolveHide()
      modal.remove()
    }
  }
}


watch(() => runningStore.running, (newVal, oldVal) => {
  if (oldVal === 'run' && newVal === 'free' && isSelfRunning.value) {
    void finalizeRun(runningStore.status || 'runSuccess')
  }
})

watch(collapsed, async (value) => {
  if (!value) {
    void hydrateScreenshotUrls()
  }

  if (isStandaloneWindow.value) {
    const targetSize = value ? STANDALONE_COLLAPSED_SIZE : STANDALONE_EXPANDED_SIZE
    await windowManager.setWindowSize(targetSize)
  }
})

onBeforeUnmount(() => {
  stopPollingDebugStream()
  revokeScreenshotUrls()
})
</script>

<template>
  <div v-if="isStandaloneWindow || modal.visible" class="cua-debug-overlay" :class="{ 'cua-debug-overlay--standalone': isStandaloneWindow }">
    <div class="cua-debug-panel" :class="{ 'cua-debug-panel--standalone': isStandaloneWindow }" :style="isStandaloneWindow ? undefined : { width: `${panelWidth}px` }">
      <div class="panel-header">
        <div class="panel-header__title">{{ debugPanelTitle }}</div>
        <div class="panel-header__actions">
          <a-tooltip :title="collapseButtonText">
            <a-button size="small" class="panel-header__icon-btn" @click="collapsed = !collapsed">
              <template #icon>
                <component :is="collapsed ? PlusOutlined : MinusOutlined" />
              </template>
            </a-button>
          </a-tooltip>
          <a-tooltip title="Close">
            <a-button size="small" class="panel-header__icon-btn" @click="handleClose">
              <template #icon>
                <CloseOutlined />
              </template>
            </a-button>
          </a-tooltip>
        </div>
      </div>

      <div class="cua-debug-modal">
        <section v-if="!collapsed" class="instruction-panel">
          <div class="panel-title">用户指令</div>
          <a-textarea
            v-model:value="instruction"
            :auto-size="{ minRows: 3, maxRows: 6 }"
            placeholder="Enter a CUA instruction"
          />
        </section>

        <section class="log-panel">
          <div class="panel-title">日志</div>
          <div v-if="loading && entries.length === 0" class="log-loading">
            <a-spin />
            <span>思考中...</span>
          </div>

          <div v-else-if="entries.length === 0" class="log-empty">
            暂无日志，请点击运行后再查看
          </div>

          <div v-else class="log-list" ref="logListRef">
            <div
              v-for="entry in entries"
              :key="entry.id"
              class="log-entry"
              :class="entry.kind === 'step' ? 'log-entry__step' : 'log-entry__status'"
            >
              <div class="log-entry__meta">
                <span v-if="entry.step">Step {{ entry.step }}</span>
              </div>
              <div class="log-entry__text">{{ entry.text }}</div>
              <img
                v-if="!collapsed && entry.screenshotUrl"
                :src="entry.screenshotUrl"
                alt="CUA debug screenshot"
                class="log-entry__image"
              >
            </div>
          </div>
        </section>

        <section class="footer-actions">
          <a-button class="footer-actions__run" :danger="isRunning" type="primary" @click="handleRunOrStop">
            {{ runButtonText }}
          </a-button>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.cua-debug-overlay {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 2100;
}

.cua-debug-overlay--standalone {
  position: static;
  inset: auto;
  width: 100%;
  height: 100vh;
}

.cua-debug-panel {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

.cua-debug-panel--standalone {
  width: 100%;
  height: 100vh;
  min-height: 0;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8fafc;
}

.panel-header__title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.88);
}

.panel-header__actions {
  display: flex;
  gap: 6px;
}

.panel-header__icon-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cua-debug-modal {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
}

.panel-title {
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.72);
}

.instruction-panel {
  flex: 0 0 auto;
}

.log-panel {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
}


.log-loading,
.log-empty {
  flex: 1;
  min-height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.45);
  background: #f7f7f9;
  border-radius: 12px;
}

.log-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 4px;
}

.log-entry {
  padding: 8px;
  border-radius: 12px;
  background: #f7f7f9;
}

.log-entry__meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.log-entry__text {
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(0, 0, 0, 0.85);
  font-size: 13px;
  line-height: 1.5;
}

.log-entry__image {
  display: block;
  width: 100%;
  max-height: 160px;
  object-fit: cover;
  margin-top: 10px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.footer-actions {
  display: flex;
  align-items: center;
  margin-top: auto;
  padding-top: 2px;
}

.footer-actions__run {
  width: 100%;
}
</style>



