<script setup lang="ts">
import { message } from 'ant-design-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import {
  getOpenClawManagerBaseUrl,
  getOpenClawManagerOptions,
  getOpenClawManagerStatus,
  submitOpenClawOnboard,
  type OpenClawManagerCurrentConfig,
  type OpenClawManagerOnboardResult,
  type OpenClawManagerProvider,
} from '@/api/openclaw-manager'

const text = {
  intro: '在这里配置 Astron 助理使用的 OpenClaw 大模型供应商。请求地址会跟随引擎回传的 route_port，自动访问本地 /openclaw/onboard 接口。',
  docs: 'OpenClaw Onboard 文档',
  serviceAddress: '服务地址',
  refresh: '刷新',
  provider: '模型供应商',
  providerPlaceholder: '请选择模型供应商',
  apiKey: 'API Key',
  apiKeyPlaceholder: '请输入 API Key',
  apiKeyOptionalPlaceholder: '如有需要可填写 API Key',
  secretMode: '密钥存储方式',
  secretPlaintext: '明文',
  secretRef: 'Ref',
  customBaseUrl: '自定义 Base URL',
  customBaseUrlPlaceholder: 'https://llm.example.com/v1',
  customModelId: '模型 ID',
  customModelIdPlaceholder: '例如 gpt-4.1 / qwen3.5:32b',
  customProviderId: 'Provider ID',
  customProviderIdPlaceholder: '可选，默认自动推导',
  compatibility: '兼容协议',
  restart: '如 OpenClaw 正在运行则自动重启',
  save: '保存模型配置',
  saving: '正在保存配置...',
  reset: '重置表单',
  currentConfig: '当前配置',
  currentModel: '主模型',
  currentProviders: '已配置 Provider',
  workspace: '工作区',
  notConfigured: '尚未配置',
  command: '执行命令',
  stdout: '标准输出',
  stderr: '错误输出',
  noCommandOutput: '暂无执行结果',
  loadFailed: '加载配置失败',
  saveSuccess: '模型配置已保存',
  customProviderHint: '自定义 Provider 和 Ollama 支持额外的模型/地址参数。',
  emptyProviders: '当前未获取到可用供应商选项',
} as const

const loading = ref(false)
const saving = ref(false)
const providers = ref<OpenClawManagerProvider[]>([])
const currentConfig = ref<OpenClawManagerCurrentConfig | null>(null)
const docsUrl = ref('https://docs.openclaw.ai/cli/onboard')
const lastResult = ref<OpenClawManagerOnboardResult | null>(null)
const loadError = ref('')
const serviceUrl = computed(() => getOpenClawManagerBaseUrl())

const formState = reactive({
  authChoice: '',
  apiKey: '',
  secretInputMode: 'plaintext' as 'plaintext' | 'ref',
  customBaseUrl: '',
  customModelId: '',
  customProviderId: '',
  customCompatibility: 'openai' as 'openai' | 'anthropic',
  restartIfRunning: true,
})

const providerOptions = computed(() => {
  return providers.value.map(provider => ({
    label: provider.label,
    value: provider.id,
  }))
})

const selectedProvider = computed(() => {
  return providers.value.find(provider => provider.id === formState.authChoice) || null
})

const selectedProviderApiKeyLabel = computed(() => {
  return selectedProvider.value?.api_key_label || text.apiKey
})

const showApiKey = computed(() => {
  return Boolean(selectedProvider.value?.requires_api_key || selectedProvider.value?.id === 'custom-api-key')
})

const showCustomFields = computed(() => {
  return Boolean(selectedProvider.value?.supports_custom_model)
})

const showCustomProviderId = computed(() => {
  return selectedProvider.value?.id === 'custom-api-key'
})

const showCompatibility = computed(() => {
  return selectedProvider.value?.id === 'custom-api-key'
})

const currentProviderTags = computed(() => currentConfig.value?.providers || [])

function resetForm() {
  formState.apiKey = ''
  formState.secretInputMode = 'plaintext'
  formState.customBaseUrl = ''
  formState.customModelId = ''
  formState.customProviderId = ''
  formState.customCompatibility = 'openai'
  formState.restartIfRunning = true
}

async function loadData() {
  loading.value = true
  loadError.value = ''

  try {
    const [options, status] = await Promise.all([
      getOpenClawManagerOptions(),
      getOpenClawManagerStatus(),
    ])

    providers.value = options.providers || []
    docsUrl.value = options.docs_url || docsUrl.value
    currentConfig.value = status.configured || options.current

    if (!formState.authChoice && providers.value.length > 0) {
      const preferredProvider = currentConfig.value?.providers?.[0]
      formState.authChoice = providers.value.some(item => item.id === preferredProvider)
        ? preferredProvider
        : providers.value[0].id
    }
  }
  catch (error: any) {
    const reason = error?.message || text.loadFailed
    loadError.value = reason
    message.error(reason)
  }
  finally {
    loading.value = false
  }
}

async function saveConfig() {
  if (!formState.authChoice) {
    message.warning(text.providerPlaceholder)
    return
  }

  saving.value = true

  try {
    const result = await submitOpenClawOnboard({
      auth_choice: formState.authChoice,
      api_key: formState.apiKey.trim() || undefined,
      custom_base_url: formState.customBaseUrl.trim() || undefined,
      custom_model_id: formState.customModelId.trim() || undefined,
      custom_provider_id: formState.customProviderId.trim() || undefined,
      custom_compatibility: formState.customCompatibility,
      secret_input_mode: formState.secretInputMode,
      restart_if_running: formState.restartIfRunning,
    })

    lastResult.value = result
    currentConfig.value = result.configured
    formState.apiKey = ''
    message.success(text.saveSuccess)
  }
  catch (error: any) {
    message.error(error?.message || text.loadFailed)
  }
  finally {
    saving.value = false
  }
}

watch(() => formState.authChoice, () => {
  formState.apiKey = ''
  formState.customBaseUrl = ''
  formState.customModelId = ''
  formState.customProviderId = ''
  formState.customCompatibility = 'openai'
})

onMounted(() => {
  void loadData()
})
</script>

<template>
  <a-spin :spinning="loading || saving" :tip="saving ? text.saving : undefined">
    <div class="space-y-4">
      <div class="rounded-[12px] bg-[#f7f8fc] px-4 py-3 text-[13px] leading-[22px] text-[rgba(0,0,0,0.65)] dark:bg-[rgba(255,255,255,0.04)] dark:text-[rgba(255,255,255,0.65)]">
        {{ text.intro }}
        <a class="ml-2 inline-flex" :href="docsUrl" target="_blank">
          {{ text.docs }}
        </a>
      </div>

      <a-alert
        v-if="loadError"
        type="error"
        show-icon
        :message="text.loadFailed"
        :description="loadError"
      />

      <a-form layout="vertical">
        <a-form-item :label="text.serviceAddress">
          <div class="flex gap-2">
            <a-input :value="serviceUrl" readonly />
            <a-button @click="loadData">
              {{ text.refresh }}
            </a-button>
          </div>
        </a-form-item>

        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <a-form-item :label="text.provider">
            <a-select
              v-model:value="formState.authChoice"
              :options="providerOptions"
              :placeholder="text.providerPlaceholder"
              show-search
              option-filter-prop="label"
            />
          </a-form-item>

          <a-form-item :label="text.secretMode">
            <a-select
              v-model:value="formState.secretInputMode"
              :options="[
                { label: text.secretPlaintext, value: 'plaintext' },
                { label: text.secretRef, value: 'ref' },
              ]"
            />
          </a-form-item>
        </div>

        <a-form-item v-if="showApiKey" :label="selectedProviderApiKeyLabel">
          <a-input-password
            v-model:value="formState.apiKey"
            :placeholder="selectedProvider?.requires_api_key ? text.apiKeyPlaceholder : text.apiKeyOptionalPlaceholder"
          />
        </a-form-item>

        <div v-if="showCustomFields" class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <a-form-item :label="text.customBaseUrl">
            <a-input v-model:value="formState.customBaseUrl" :placeholder="text.customBaseUrlPlaceholder" />
          </a-form-item>

          <a-form-item :label="text.customModelId">
            <a-input v-model:value="formState.customModelId" :placeholder="text.customModelIdPlaceholder" />
          </a-form-item>

          <a-form-item v-if="showCustomProviderId" :label="text.customProviderId">
            <a-input v-model:value="formState.customProviderId" :placeholder="text.customProviderIdPlaceholder" />
          </a-form-item>

          <a-form-item v-if="showCompatibility" :label="text.compatibility">
            <a-select
              v-model:value="formState.customCompatibility"
              :options="[
                { label: 'OpenAI', value: 'openai' },
                { label: 'Anthropic', value: 'anthropic' },
              ]"
            />
          </a-form-item>
        </div>

        <div
          v-if="showCustomFields"
          class="mb-4 rounded-[10px] border border-dashed border-[#d6d9e6] px-3 py-2 text-[12px] text-[rgba(0,0,0,0.58)] dark:border-[rgba(255,255,255,0.12)] dark:text-[rgba(255,255,255,0.58)]"
        >
          {{ text.customProviderHint }}
        </div>

        <a-form-item>
          <a-switch v-model:checked="formState.restartIfRunning" />
          <span class="ml-2 text-[13px] text-[rgba(0,0,0,0.68)] dark:text-[rgba(255,255,255,0.68)]">
            {{ text.restart }}
          </span>
        </a-form-item>
      </a-form>

      <div class="rounded-[12px] border border-[#edf1f6] bg-[#fff] p-4 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.02)]">
        <div class="mb-3 text-[14px] font-medium text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
          {{ text.currentConfig }}
        </div>
        <div class="grid grid-cols-1 gap-3 text-[13px] md:grid-cols-3">
          <div>
            <div class="text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
              {{ text.currentModel }}
            </div>
            <div class="mt-1 break-all text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
              {{ currentConfig?.primary_model || text.notConfigured }}
            </div>
          </div>
          <div>
            <div class="text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
              {{ text.currentProviders }}
            </div>
            <div class="mt-1 flex flex-wrap gap-2">
              <a-tag v-for="provider in currentProviderTags" :key="provider">
                {{ provider }}
              </a-tag>
              <span v-if="currentProviderTags.length === 0" class="text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
                {{ text.notConfigured }}
              </span>
            </div>
          </div>
          <div>
            <div class="text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
              {{ text.workspace }}
            </div>
            <div class="mt-1 break-all text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
              {{ currentConfig?.workspace || text.notConfigured }}
            </div>
          </div>
        </div>
      </div>

      <a-empty
        v-if="!loading && providers.length === 0"
        :description="text.emptyProviders"
      />

      <div v-if="lastResult" class="rounded-[12px] bg-[#101828] p-3 text-[12px] text-[#d1e9ff]">
        <div class="space-y-3">
          <div>
            <div class="mb-1 font-medium">
              {{ text.command }}
            </div>
            <pre class="m-0 whitespace-pre-wrap break-words">{{ lastResult.command.join(' ') || text.noCommandOutput }}</pre>
          </div>
          <div v-if="lastResult.stdout">
            <div class="mb-1 font-medium">
              {{ text.stdout }}
            </div>
            <pre class="m-0 max-h-[160px] overflow-auto whitespace-pre-wrap break-words">{{ lastResult.stdout }}</pre>
          </div>
          <div v-if="lastResult.stderr">
            <div class="mb-1 font-medium">
              {{ text.stderr }}
            </div>
            <pre class="m-0 max-h-[160px] overflow-auto whitespace-pre-wrap break-words">{{ lastResult.stderr }}</pre>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <a-button @click="resetForm">
          {{ text.reset }}
        </a-button>
        <a-button type="primary" :loading="saving" @click="saveConfig">
          {{ text.save }}
        </a-button>
      </div>
    </div>
  </a-spin>
</template>
