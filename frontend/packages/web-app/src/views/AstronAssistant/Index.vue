<script setup lang="ts">
import { computed, onActivated, onBeforeUnmount, onMounted, ref } from 'vue'

import {
  clearStoredManualOpenClawToken,
  getStoredManualOpenClawToken,
  resolveOpenClawToken,
  storeManualOpenClawToken,
} from '@/api/openclaw-auth'
import { probeOpenClawReadiness } from '@/api/openclaw-health'
import { getOpenClawManagerStatus, launchOpenClaw } from '@/api/openclaw-manager'
import ChatPanel from '@/components/AstronAssistant/ChatPanel.vue'

const STARTUP_RETRY_INTERVAL_MS = 2000
const STARTUP_TIMEOUT_MS = 10000

type StartupPhase = 'checking' | 'timeout' | 'ready'

let launchingPromise: Promise<void> | null = null
const startupPhase = ref<StartupPhase>('checking')
const startupAttempts = ref(0)
const startupError = ref('')
const manualGatewayToken = ref('')

const startupTitle = computed(() => {
  return startupPhase.value === 'timeout'
    ? '仍未连接到 OpenClaw'
    : '正在启动 OpenClaw'
})

const startupDescription = computed(() => {
  return startupPhase.value === 'timeout'
    ? 'OpenClaw 还没有完成启动。页面会继续自动探测，你也可以立即手动重试。'
    : '助手页面会在 OpenClaw 真正可用后自动进入主界面。'
})

const showGatewayTokenForm = computed(() => {
  const error = startupError.value.trim().toLowerCase()
  if (!error)
    return false

  return error.includes('unauthorized') || error.includes('gateway token')
})

let startupStartedAtMs = Date.now()
let retryTimer: number | undefined
let currentProbeToken = 0
let disposed = false

function hasElectronOpenClawBridge() {
  return typeof (window as any)?.electron?.openclaw?.chatCompletions === 'function'
}

async function ensureOpenClawLaunched() {
  if (launchingPromise)
    return await launchingPromise

  launchingPromise = (async () => {
    try {
      await launchOpenClaw()
    }
    catch (error) {
      console.warn('Failed to auto launch OpenClaw:', error)
    }
    finally {
      launchingPromise = null
    }
  })()

  return await launchingPromise
}

function clearRetryTimer() {
  if (retryTimer != null) {
    window.clearTimeout(retryTimer)
    retryTimer = undefined
  }
}

function scheduleNextProbe() {
  clearRetryTimer()
  retryTimer = window.setTimeout(() => {
    void runStartupProbe()
  }, STARTUP_RETRY_INTERVAL_MS)
}

async function runStartupProbe(tokenOverride?: string) {
  if (disposed || startupPhase.value === 'ready')
    return

  const probeToken = ++currentProbeToken
  startupAttempts.value += 1

  try {
    const status = await getOpenClawManagerStatus()
    if (disposed || probeToken !== currentProbeToken)
      return

    if (!status.process_alive)
      throw new Error('OpenClaw is still starting.')

    if (hasElectronOpenClawBridge()) {
      clearRetryTimer()
      startupError.value = ''
      startupPhase.value = 'ready'
      return
    }

    const token = tokenOverride ?? await resolveOpenClawToken()
    if (disposed || probeToken !== currentProbeToken)
      return

    await probeOpenClawReadiness(token ? { token } : undefined)
    if (disposed || probeToken !== currentProbeToken)
      return

    clearRetryTimer()
    startupError.value = ''
    startupPhase.value = 'ready'
  }
  catch (error) {
    if (disposed || probeToken !== currentProbeToken)
      return

    startupError.value = error instanceof Error ? error.message : String(error)
    startupPhase.value = Date.now() - startupStartedAtMs >= STARTUP_TIMEOUT_MS
      ? 'timeout'
      : 'checking'
    scheduleNextProbe()
  }
}

function retryStartupProbe(tokenOverride?: string) {
  startupStartedAtMs = Date.now()
  startupPhase.value = 'checking'
  startupError.value = ''
  clearRetryTimer()
  void runStartupProbe(tokenOverride)
}

function saveGatewayToken() {
  const token = manualGatewayToken.value.trim()
  if (!token) {
    clearStoredManualOpenClawToken()
    retryStartupProbe()
    return
  }

  storeManualOpenClawToken(token)
  retryStartupProbe(token)
}

function clearGatewayToken() {
  manualGatewayToken.value = ''
  clearStoredManualOpenClawToken()
  retryStartupProbe()
}

async function startAssistant() {
  await ensureOpenClawLaunched()
  if (disposed)
    return

  manualGatewayToken.value = getStoredManualOpenClawToken() ?? ''
  startupStartedAtMs = Date.now()
  startupPhase.value = 'checking'
  startupError.value = ''
  startupAttempts.value = 0
  clearRetryTimer()
  void runStartupProbe()
}

onMounted(() => {
  void startAssistant()
})

onActivated(() => {
  if (startupPhase.value !== 'ready')
    void startAssistant()
})

onBeforeUnmount(() => {
  disposed = true
  currentProbeToken += 1
  clearRetryTimer()
})
</script>

<template>
  <div class="w-full h-full bg-[#f6f8ff] dark:bg-[#141414]">
    <div class="h-full min-h-0 p-4">
      <div
        v-if="startupPhase === 'ready'"
        class="h-full"
      >
        <ChatPanel />
      </div>
      <div
        v-else
        class="flex h-full items-center justify-center"
      >
        <section class="startup-shell">
          <div class="startup-shell__badge">
            OpenClaw Gateway
          </div>
          <div class="startup-shell__spinner" aria-hidden="true" />
          <h1 class="startup-shell__title">
            {{ startupTitle }}
          </h1>
          <p class="startup-shell__description">
            {{ startupDescription }}
          </p>
          <p class="startup-shell__meta">
            已发起 {{ startupAttempts }} 次探测
          </p>
          <p v-if="startupError" class="startup-shell__error">
            {{ startupError }}
          </p>
          <div v-if="showGatewayTokenForm" class="startup-shell__token-form">
            <label class="startup-shell__token-label" for="gateway-token-input">
              Gateway Token
            </label>
            <input
              id="gateway-token-input"
              v-model="manualGatewayToken"
              type="password"
              class="startup-shell__token-input"
              placeholder="Paste your OpenClaw gateway token"
            >
            <div class="startup-shell__token-actions">
              <button
                type="button"
                class="startup-shell__button"
                @click="saveGatewayToken"
              >
                保存并重试
              </button>
              <button
                type="button"
                class="startup-shell__button startup-shell__button--secondary"
                @click="clearGatewayToken"
              >
                清除
              </button>
            </div>
          </div>
          <button
            v-if="startupPhase === 'timeout'"
            type="button"
            class="startup-shell__button"
            @click="retryStartupProbe"
          >
            重试连接
          </button>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.startup-shell {
  display: flex;
  width: min(560px, 100%);
  flex-direction: column;
  align-items: center;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(241, 246, 255, 0.96));
  padding: 40px 36px;
  text-align: center;
  box-shadow: 0 24px 60px rgba(127, 145, 193, 0.16);
}

.startup-shell__badge {
  border-radius: 9999px;
  background: rgba(91, 112, 255, 0.12);
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #4f46e5;
  text-transform: uppercase;
}

.startup-shell__spinner {
  margin-top: 24px;
  height: 56px;
  width: 56px;
  border-radius: 9999px;
  border: 4px solid rgba(91, 112, 255, 0.12);
  border-top-color: #5b70ff;
  animation: startup-spin 1s linear infinite;
}

.startup-shell__title {
  margin: 24px 0 0;
  font-size: 28px;
  line-height: 1.2;
  font-weight: 700;
  color: rgba(30, 39, 67, 0.96);
}

.startup-shell__description {
  margin: 14px 0 0;
  max-width: 420px;
  font-size: 14px;
  line-height: 24px;
  color: rgba(71, 83, 120, 0.68);
}

.startup-shell__meta {
  margin: 14px 0 0;
  font-size: 13px;
  color: rgba(71, 83, 120, 0.58);
}

.startup-shell__error {
  margin: 18px 0 0;
  width: 100%;
  border-radius: 18px;
  border: 1px solid #ffd6d1;
  background: #fff6f4;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 22px;
  color: #b44737;
  text-align: left;
  word-break: break-word;
}

.startup-shell__token-form {
  margin-top: 18px;
  width: 100%;
  text-align: left;
}

.startup-shell__token-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(30, 39, 67, 0.88);
}

.startup-shell__token-input {
  width: 100%;
  border-radius: 14px;
  border: 1px solid #d7def7;
  background: #fff;
  padding: 12px 14px;
  font-size: 14px;
  color: rgba(30, 39, 67, 0.92);
  outline: none;
}

.startup-shell__token-input:focus {
  border-color: #5b70ff;
  box-shadow: 0 0 0 3px rgba(91, 112, 255, 0.12);
}

.startup-shell__token-actions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}

.startup-shell__button {
  border: none;
  border-radius: 9999px;
  background: linear-gradient(135deg, #5b70ff, #7a8cff);
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.startup-shell__button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(91, 112, 255, 0.22);
}

.startup-shell__button--secondary {
  background: rgba(255, 255, 255, 0.9);
  color: rgba(30, 39, 67, 0.88);
  box-shadow: inset 0 0 0 1px rgba(125, 141, 188, 0.16);
}

.dark .startup-shell {
  border-color: rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(25, 27, 35, 0.96), rgba(17, 19, 27, 0.98));
}

.dark .startup-shell__badge {
  background: rgba(91, 112, 255, 0.18);
  color: #c7d2fe;
}

.dark .startup-shell__title {
  color: rgba(255, 255, 255, 0.92);
}

.dark .startup-shell__description,
.dark .startup-shell__meta {
  color: rgba(255, 255, 255, 0.58);
}

.dark .startup-shell__error {
  border-color: rgba(255, 120, 102, 0.28);
  background: rgba(255, 120, 102, 0.12);
  color: #ffb2a5;
}

.dark .startup-shell__token-label {
  color: rgba(255, 255, 255, 0.88);
}

.dark .startup-shell__token-input {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.88);
}

.dark .startup-shell__button--secondary {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.88);
  box-shadow: none;
}

@keyframes startup-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
