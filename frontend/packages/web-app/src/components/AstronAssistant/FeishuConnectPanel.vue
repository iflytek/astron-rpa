<script setup lang="ts">
import { message } from 'ant-design-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { getUserSetting, setUserSetting } from '@/api/setting'

import {
  buildOpenClawFeishuConfig,
  DEFAULT_FEISHU_CONFIG,
  mergeFeishuConfigIntoSetting,
  readFeishuConfigFromSetting,
  type AstronAssistantFeishuConfig,
} from './feishu-config'

const emit = defineEmits<{
  saved: []
}>()

const text = {
  intro: '\u8f93\u5165\u98de\u4e66\u5e94\u7528\u51ed\u636e\u540e\uff0c\u5373\u53ef\u5c06\u5f53\u524d Astron \u52a9\u624b\u63a5\u5165\u98de\u4e66\u673a\u5668\u4eba\u901a\u9053\u3002',
  guide: '\u914d\u7f6e\u6307\u5357',
  enabled: '\u542f\u7528\u72b6\u6001',
  botName: '\u673a\u5668\u4eba\u540d\u79f0',
  appSecret: 'App Secret',
  domain: '\u57df\u540d',
  connectionMode: '\u8fde\u63a5\u6a21\u5f0f',
  inputSecret: '\u8f93\u5165 App Secret',
  inputVerify: '\u8f93\u5165 Verification Token',
  inputEncrypt: '\u8f93\u5165 Encrypt Key',
  preview: 'OpenClaw \u914d\u7f6e\u9884\u89c8',
  copy: '\u590d\u5236\u914d\u7f6e',
  reset: '\u91cd\u7f6e',
  save: '\u4fdd\u5b58\u98de\u4e66\u914d\u7f6e',
  saved: '\u98de\u4e66\u914d\u7f6e\u5df2\u4fdd\u5b58',
  copied: 'OpenClaw \u914d\u7f6e\u5df2\u590d\u5236',
  on: '\u542f\u7528',
  off: '\u505c\u7528',
} as const

const domainOptions = [
  { label: '\u98de\u4e66', value: 'feishu' },
  { label: 'Lark', value: 'lark' },
]

const connectionOptions = [
  { label: 'WebSocket', value: 'websocket' },
  { label: 'Webhook', value: 'webhook' },
]

const loading = ref(false)
const saving = ref(false)
const formState = reactive<AstronAssistantFeishuConfig>({ ...DEFAULT_FEISHU_CONFIG })

function patchFormState(nextState: AstronAssistantFeishuConfig) {
  Object.assign(formState, nextState)
}

async function loadSetting() {
  loading.value = true
  try {
    const setting = await getUserSetting()
    patchFormState(readFeishuConfigFromSetting(setting))
  }
  finally {
    loading.value = false
  }
}

async function saveSetting() {
  saving.value = true
  try {
    const currentSetting = await getUserSetting()
    const nextSetting = mergeFeishuConfigIntoSetting(currentSetting, { ...formState })
    await setUserSetting(nextSetting as RPA.UserSetting)
    message.success(text.saved)
    emit('saved')
  }
  finally {
    saving.value = false
  }
}

async function copyConfigPreview() {
  const content = JSON.stringify(buildOpenClawFeishuConfig({ ...formState }), null, 2)
  await navigator.clipboard.writeText(content)
  message.success(text.copied)
}

const configPreview = computed(() => JSON.stringify(buildOpenClawFeishuConfig({ ...formState }), null, 2))

watch(() => formState.connectionMode, (mode) => {
  if (mode === 'websocket') {
    formState.verificationToken = ''
    formState.encryptKey = ''
  }
})

onMounted(() => {
  void loadSetting()
})
</script>

<template>
  <a-spin :spinning="loading">
    <div class="space-y-4">
      <div class="rounded-[12px] bg-[#f7f8fc] px-4 py-3 text-[13px] leading-[22px] text-[rgba(0,0,0,0.65)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.65)]">
        {{ text.intro }}
        <a class="ml-2 inline-flex" href="https://open.feishu.cn/document/home/index" target="_blank">
          {{ text.guide }}
        </a>
      </div>

      <a-form layout="vertical">
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <a-form-item :label="text.enabled">
            <a-switch v-model:checked="formState.enabled" :checked-children="text.on" :un-checked-children="text.off" />
          </a-form-item>
          <a-form-item :label="text.botName">
            <a-input v-model:value="formState.botName" placeholder="Astron Assistant" />
          </a-form-item>
          <a-form-item label="App ID">
            <a-input v-model:value="formState.appId" placeholder="cli_xxx" />
          </a-form-item>
          <a-form-item :label="text.appSecret">
            <a-input-password v-model:value="formState.appSecret" :placeholder="text.inputSecret" />
          </a-form-item>
          <a-form-item :label="text.domain">
            <a-select v-model:value="formState.domain" :options="domainOptions" />
          </a-form-item>
          <a-form-item :label="text.connectionMode">
            <a-select v-model:value="formState.connectionMode" :options="connectionOptions" />
          </a-form-item>
        </div>

        <div v-if="formState.connectionMode === 'webhook'" class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <a-form-item label="Verification Token">
            <a-input v-model:value="formState.verificationToken" :placeholder="text.inputVerify" />
          </a-form-item>
          <a-form-item label="Encrypt Key">
            <a-input-password v-model:value="formState.encryptKey" :placeholder="text.inputEncrypt" />
          </a-form-item>
          <a-form-item label="Webhook Host">
            <a-input v-model:value="formState.webhookHost" placeholder="127.0.0.1" />
          </a-form-item>
          <a-form-item label="Webhook Port">
            <a-input-number v-model:value="formState.webhookPort" class="w-full" :min="1" :max="65535" />
          </a-form-item>
          <a-form-item class="md:col-span-2" label="Webhook Path">
            <a-input v-model:value="formState.webhookPath" placeholder="/feishu/events" />
          </a-form-item>
        </div>
      </a-form>

      <div class="rounded-[12px] bg-[#101828] p-3 text-[12px] text-[#d1e9ff]">
        <div class="mb-2 flex items-center justify-between gap-3">
          <span class="font-medium">{{ text.preview }}</span>
          <a-button size="small" ghost @click="copyConfigPreview">
            {{ text.copy }}
          </a-button>
        </div>
        <pre class="m-0 max-h-[220px] overflow-auto whitespace-pre-wrap break-words">{{ configPreview }}</pre>
      </div>

      <div class="flex justify-end gap-2">
        <a-button @click="loadSetting">
          {{ text.reset }}
        </a-button>
        <a-button type="primary" :loading="saving" @click="saveSetting">
          {{ text.save }}
        </a-button>
      </div>
    </div>
  </a-spin>
</template>
