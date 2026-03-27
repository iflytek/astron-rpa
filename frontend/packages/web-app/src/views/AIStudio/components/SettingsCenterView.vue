<script setup lang="ts">
import { Switch } from 'ant-design-vue'
import { CheckCircle2, ChevronDown, ChevronRight, Cpu, FileArchive, Key, Plug, Plus, Settings, ShieldCheck, Trash2, Upload, X, XCircle, Zap } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'

type TabId = 'model' | 'mcp' | 'skills' | 'behavior'
type McpStatus = 'connected' | 'error' | 'pending'
type BehaviorLevelId = 'high' | 'medium' | 'low'
type ProviderStatus = 'ready' | 'coming_soon'

type ProviderDefinition = {
  id: string
  name: string
  description: string
  badge: string
  accent: string
  surface: string
  popular: boolean
  status: ProviderStatus
  supportsModel: boolean
  supportsBaseUrl: boolean
  requiresBaseUrl?: boolean
  supportsDisplayName?: boolean
  comingSoonNote?: string
}

type ProviderSummary = {
  providerId: string
  label: string
  configured: boolean
  apiKeyHint: string | null
  baseUrl: string | null
  hasBaseUrl: boolean
  model: string | null
  displayName: string | null
}

type DesktopSettings = {
  providers: ProviderSummary[]
  defaultModel: {
    providerId: string | null
    model: string
    configured: boolean
  }
}

type SaveProviderInput = {
  providerId: string
  apiKey?: string | null
  model?: string | null
  baseUrl?: string | null
  displayName?: string | null
  clear?: boolean
}

type SaveDefaultModelInput = {
  providerId: string
  model: string
}

type DefaultModel = { id: string, name: string, provider: string, badge?: string }
type McpServer = { id: string, name: string, transport: string, status: McpStatus, desc: string }
type UploadedSkill = { id: string, name: string, fileName: string, size: string, enabled: boolean }
type BuiltinSkill = { name: string, desc: string, short: string }
type BehaviorLevel = { id: BehaviorLevelId, label: string, desc: string, hint: string, default?: boolean, requireGeek?: boolean }

const emit = defineEmits<{ (e: 'close'): void }>()

const PROVIDER_OPTIONS: ProviderDefinition[] = [
  { id: 'openai', name: 'OpenAI', description: 'GPT-4.1、GPT-4o 以及相关 OpenAI 模型', badge: 'OA', accent: '#111827', surface: '#f3f4f6', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'anthropic', name: 'Anthropic', description: 'Anthropic 提供的 Claude 系列模型', badge: 'AN', accent: '#a16207', surface: '#fff7ed', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'google', name: 'Google', description: 'Google 提供的 Gemini 模型', badge: 'G', accent: '#2563eb', surface: '#eff6ff', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'openrouter', name: 'OpenRouter', description: '通过单一入口访问多家模型提供商', badge: 'OR', accent: '#0f766e', surface: '#ecfeff', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'vercel', name: 'Vercel AI Gateway', description: '统一接入 AI 模型并支持智能路由', badge: 'VC', accent: '#111827', surface: '#f3f4f6', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'xai', name: 'xAI', description: 'xAI 提供的 Grok 系列模型', badge: 'xA', accent: '#7c3aed', surface: '#f5f3ff', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'deepseek', name: 'DeepSeek', description: 'DeepSeek 推理与代码模型', badge: 'DS', accent: '#1d4ed8', surface: '#eff6ff', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'azure', name: 'Azure OpenAI', description: 'Azure OpenAI 部署', badge: 'AZ', accent: '#0369a1', surface: '#ecfeff', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'groq', name: 'Groq', description: '低延迟推理模型托管服务', badge: 'GR', accent: '#dc2626', surface: '#fef2f2', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'mistral', name: 'Mistral', description: 'Mistral 托管模型端点', badge: 'MI', accent: '#ea580c', surface: '#fff7ed', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'moonshot', name: 'Moonshot AI', description: 'Kimi 系列模型与代码能力', badge: 'MS', accent: '#6d28d9', surface: '#f5f3ff', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'minimax', name: 'MiniMax', description: 'MiniMax 托管模型服务', badge: 'MM', accent: '#be123c', surface: '#fff1f2', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'z-ai', name: 'Z.AI', description: 'Z.AI / GLM 系列模型', badge: 'ZA', accent: '#065f46', surface: '#ecfdf5', popular: false, status: 'ready', supportsModel: true, supportsBaseUrl: true },
  { id: 'custom-openai-compatible', name: '自定义兼容接口', description: '接入任何 OpenAI-compatible API', badge: 'CU', accent: '#4338ca', surface: '#eef2ff', popular: true, status: 'ready', supportsModel: true, supportsBaseUrl: true, requiresBaseUrl: true, supportsDisplayName: true },
  { id: 'github-copilot', name: 'GitHub Copilot', description: '通过 GitHub 账号授权接入 Copilot 模型', badge: 'GH', accent: '#111827', surface: '#f3f4f6', popular: true, status: 'coming_soon', supportsModel: false, supportsBaseUrl: false, comingSoonNote: '这一接入方式需要 OAuth 授权流程，后续版本会补齐。' },
  { id: 'amazon-bedrock', name: 'Amazon Bedrock', description: '使用 AWS 凭证与区域配置接入 Bedrock', badge: 'AWS', accent: '#92400e', surface: '#fffbeb', popular: false, status: 'coming_soon', supportsModel: false, supportsBaseUrl: false, comingSoonNote: '这一接入方式需要 AWS 凭证链、区域和环境配置，后续版本会补齐。' },
  { id: 'google-vertex', name: 'Google Vertex', description: '通过 Google Cloud / Vertex AI 访问模型', badge: 'GV', accent: '#1d4ed8', surface: '#eff6ff', popular: false, status: 'coming_soon', supportsModel: false, supportsBaseUrl: false, comingSoonNote: '这一接入方式依赖 Google Cloud 项目与环境凭证，后续版本会补齐。' },
  { id: 'ollama', name: 'Ollama', description: '连接本地或远程 Ollama 服务', badge: 'OL', accent: '#0f766e', surface: '#ecfeff', popular: false, status: 'coming_soon', supportsModel: false, supportsBaseUrl: false, comingSoonNote: '这一接入方式需要本地模型发现与更细的连接配置，后续版本会补齐。' },
  { id: 'lmstudio', name: 'LM Studio', description: '连接 LM Studio 的本地兼容接口', badge: 'LM', accent: '#7c2d12', surface: '#fff7ed', popular: false, status: 'coming_soon', supportsModel: false, supportsBaseUrl: false, comingSoonNote: '这一接入方式需要本地模型发现与更细的连接配置，后续版本会补齐。' },
]

const currentTab = ref<TabId>('model')
const selectedDefaultModel = ref('')
const editingProviderId = ref<string | null>(null)
const providerApiKey = ref('')
const providerModel = ref('')
const providerBaseUrl = ref('')
const providerDisplayName = ref('')
const providerError = ref('')
const providerSubmitting = ref(false)
const defaultModelError = ref('')
const defaultModelSaving = ref(false)
const settingsLoading = ref(false)
const settingsError = ref('')
const settingsData = ref<DesktopSettings>({
  providers: [],
  defaultModel: {
    providerId: null,
    model: '',
    configured: false,
  },
})
const showMcpImport = ref(false)
const showSkillUpload = ref(false)
const geekMode = ref(false)
const behaviorLevel = ref<BehaviorLevelId>('medium')

const mcpJson = ref(`{
  "mcpServers": {
    "custom-api": {
      "url": "https://mcp.example.com/server",
      "transport": "streamable-http"
    }
  }
}`)

const navItems = [
  { id: 'model', label: '模型', desc: '基础推理模型配置', icon: Cpu },
  { id: 'mcp', label: 'MCP', desc: '工具协议服务管理', icon: Plug },
  { id: 'skills', label: 'Skills', desc: '能力插件开关', icon: Zap },
  { id: 'behavior', label: '行为配置', desc: '安全级别与自动化', icon: ShieldCheck },
] as const

const mcpServers = ref<McpServer[]>([
  { id: 'filesystem', name: 'filesystem', transport: 'stdio', status: 'connected', desc: '本地文件系统读写' },
  { id: 'figma', name: 'figma', transport: 'stdio', status: 'connected', desc: '设计资源读取与变量拉取' },
  { id: 'browser', name: 'browser', transport: 'streamable-http', status: 'pending', desc: '网页抓取与页面预览' },
  { id: 'postgres', name: 'postgres', transport: 'streamable-http', status: 'error', desc: '数据库查询与检索' },
])

const builtinSkills = [
  { name: '文件读写', desc: '读取本地及云端文档，支持 xlsx、csv、pdf、txt 等格式', short: 'FS' },
  { name: '邮件发送', desc: '通过 SMTP、Gmail、Outlook 发送邮件并带附件', short: 'EM' },
  { name: '数据库查询', desc: '执行 SQL 查询，连接 MySQL、PostgreSQL、SQLite', short: 'DB' },
  { name: 'API 调用', desc: '发起 REST 请求，支持 GET、POST、PUT、DELETE', short: 'API' },
  { name: '图表生成', desc: '生成 ECharts 结果并输出图像或 JSON 配置', short: 'CH' },
  { name: 'PDF 解析', desc: '抽取 PDF 文本、表格和元数据，支持 OCR 识别', short: 'PDF' },
  { name: '网页抓取', desc: '使用 Playwright 抓取动态页面内容与截图', short: 'WEB' },
  { name: '代码执行', desc: '在沙箱中运行 Python、JS 代码并拿回结果', short: 'RUN' },
  { name: '日历管理', desc: '创建、查询、删除 Google Calendar 日历事件', short: 'CAL' },
  { name: '消息通知', desc: '推送消息到 Slack、钉钉、企业微信等 IM', short: 'MSG' },
] satisfies BuiltinSkill[]

const behaviorLevels = [
  { id: 'high', label: '高', desc: '任何跨应用跳转、写文件操作均需要人工确认', hint: '最安全，每步操作都会弹出确认' },
  { id: 'medium', label: '中', desc: '仅涉及删除、外发、批量写入等敏感动作时确认', hint: '推荐默认，平衡安全与效率', default: true },
  { id: 'low', label: '低', desc: '全自动运行，仅在极客模式开启后可选择', hint: 'Agent 将完全自主执行，不弹出任何确认', requireGeek: true },
] satisfies BehaviorLevel[]

const uploadedSkills = ref<UploadedSkill[]>([])
const enabledBuiltinSkills = ref(new Set(['文件读写', '图表生成', 'PDF 解析', '代码执行']))

const activeNav = computed(() => navItems.find(item => item.id === currentTab.value) ?? navItems[0])
const providerMap = computed(() => new Map(PROVIDER_OPTIONS.map(provider => [provider.id, provider])))
const providerOptions = computed(() => PROVIDER_OPTIONS)
const defaultModels = computed<DefaultModel[]>(() =>
  settingsData.value.providers
    .filter((provider) => {
      const definition = providerMap.value.get(provider.providerId)
      return definition?.status === 'ready' && provider.configured && provider.model
    })
    .map((provider) => ({
      id: `${provider.providerId}:${provider.model}`,
      name: provider.model ?? '',
      provider: provider.label,
      badge:
        settingsData.value.defaultModel.configured
        && settingsData.value.defaultModel.providerId === provider.providerId
        && settingsData.value.defaultModel.model === provider.model
          ? '默认'
          : undefined,
    })),
)
const currentDefaultModel = computed(() => defaultModels.value.find(model => model.id === selectedDefaultModel.value) ?? defaultModels.value[0] ?? null)
const editingProvider = computed(() => providerOptions.value.find(provider => provider.id === editingProviderId.value) ?? null)
const editingProviderSummary = computed(() => settingsData.value.providers.find(provider => provider.providerId === editingProviderId.value) ?? null)
const mcpStats = computed(() => [
  { label: '已连接', value: mcpServers.value.filter(server => server.status === 'connected').length, tone: 'text-[#6B7280]' },
  { label: '失败', value: mcpServers.value.filter(server => server.status === 'error').length, tone: 'text-[#EF4444]' },
  { label: '待连接', value: mcpServers.value.filter(server => server.status === 'pending').length, tone: 'text-black/42' },
  { label: '总计', value: mcpServers.value.length, tone: 'text-[#4B5563]' },
])
const allBuiltinEnabled = computed(() => enabledBuiltinSkills.value.size === builtinSkills.length)
const selectedBehaviorMeta = computed(() => behaviorLevels.find(level => level.id === behaviorLevel.value) ?? behaviorLevels[1])

watch(defaultModels, (models) => {
  if (!models.length) {
    selectedDefaultModel.value = ''
    return
  }
  if (!models.some(model => model.id === selectedDefaultModel.value)) {
    selectedDefaultModel.value = models[0].id
  }
}, { immediate: true })

function getDesktopApi() {
  if (typeof window === 'undefined' || !window.opencodeApi) {
    throw new Error('opencodeApi 不可用')
  }
  return window.opencodeApi
}

async function loadSettings() {
  try {
    settingsLoading.value = true
    settingsError.value = ''
    const settings = await getDesktopApi().getSettings() as DesktopSettings
    settingsData.value = settings
    if (settings.defaultModel.configured && settings.defaultModel.providerId) {
      selectedDefaultModel.value = `${settings.defaultModel.providerId}:${settings.defaultModel.model}`
    }
  } catch (error) {
    settingsError.value = error instanceof Error ? error.message : '加载模型设置失败'
  } finally {
    settingsLoading.value = false
  }
}

onMounted(() => {
  void loadSettings()
})

function providerConfigured(id: string) {
  return Boolean(settingsData.value.providers.find(provider => provider.providerId === id)?.configured)
}

function providerStatusText(provider: ProviderDefinition) {
  if (provider.status === 'coming_soon') return '即将支持'
  return providerConfigured(provider.id) ? '已配置' : '点击配置'
}

function openProvider(provider: ProviderDefinition) {
  editingProviderId.value = provider.id
  providerApiKey.value = ''
  providerModel.value = editingProviderSummary.value?.model ?? ''
  providerBaseUrl.value = editingProviderSummary.value?.baseUrl ?? ''
  providerDisplayName.value = editingProviderSummary.value?.displayName ?? editingProviderSummary.value?.label ?? provider.name
  providerError.value = ''
  providerSubmitting.value = false
}

function closeProvider() {
  editingProviderId.value = null
  providerApiKey.value = ''
  providerModel.value = ''
  providerBaseUrl.value = ''
  providerDisplayName.value = ''
  providerError.value = ''
}

async function saveProvider() {
  if (!editingProvider.value || editingProvider.value.status !== 'ready') return

  if (!editingProviderSummary.value?.configured && !providerApiKey.value.trim()) {
    providerError.value = `请先为 ${editingProvider.value.name} 填写 API Key`
    return
  }
  if (editingProvider.value.supportsModel && !providerModel.value.trim()) {
    providerError.value = `请先为 ${editingProvider.value.name} 填写模型 ID`
    return
  }
  if (editingProvider.value.requiresBaseUrl && !providerBaseUrl.value.trim()) {
    providerError.value = `请先为 ${editingProvider.value.name} 填写 Base URL`
    return
  }
  if (editingProvider.value.supportsDisplayName && !providerDisplayName.value.trim()) {
    providerError.value = '请先填写显示名称'
    return
  }

  try {
    providerSubmitting.value = true
    providerError.value = ''
    await getDesktopApi().saveProvider({
      providerId: editingProvider.value.id,
      apiKey: providerApiKey.value.trim() || undefined,
      model: editingProvider.value.supportsModel ? providerModel.value.trim() || null : undefined,
      baseUrl: editingProvider.value.supportsBaseUrl ? providerBaseUrl.value.trim() || null : undefined,
      displayName: editingProvider.value.supportsDisplayName ? providerDisplayName.value.trim() : undefined,
    } satisfies SaveProviderInput)
    await loadSettings()
    closeProvider()
  } catch (error) {
    providerError.value = error instanceof Error ? error.message : '保存供应商设置失败'
  } finally {
    providerSubmitting.value = false
  }
}

async function clearProvider() {
  if (!editingProvider.value) return

  try {
    providerSubmitting.value = true
    providerError.value = ''
    await getDesktopApi().saveProvider({
      providerId: editingProvider.value.id,
      clear: true,
    } satisfies SaveProviderInput)
    await loadSettings()
    closeProvider()
  } catch (error) {
    providerError.value = error instanceof Error ? error.message : '移除供应商设置失败'
  } finally {
    providerSubmitting.value = false
  }
}

async function saveDefaultModel() {
  if (!selectedDefaultModel.value) {
    defaultModelError.value = '请先选择一个已配置模型'
    return
  }

  const [providerId, ...rest] = selectedDefaultModel.value.split(':')
  const model = rest.join(':')
  if (!providerId || !model) {
    defaultModelError.value = '默认模型格式不正确'
    return
  }

  try {
    defaultModelSaving.value = true
    defaultModelError.value = ''
    await getDesktopApi().saveDefaultModel({
      providerId,
      model,
    } satisfies SaveDefaultModelInput)
    await loadSettings()
  } catch (error) {
    defaultModelError.value = error instanceof Error ? error.message : '保存默认模型失败'
  } finally {
    defaultModelSaving.value = false
  }
}

function providerMeta(providerId: string) {
  const provider = providerMap.value.get(providerId)
  const summary = settingsData.value.providers.find(item => item.providerId === providerId)
  if (!provider) return '未识别的提供方'
  if (provider.status === 'coming_soon') return provider.comingSoonNote ?? '这一接入方式将在后续版本开放。'
  if (!summary?.configured) {
    return provider.id === 'custom-openai-compatible'
      ? '填写显示名称、Base URL、API Key 与模型后即可使用'
      : '点击配置'
  }

  const parts = [summary.apiKeyHint ?? '已保存密钥']
  if (summary.model) parts.push(`模型：${summary.model}`)
  if (summary.baseUrl) parts.push(`地址：${summary.baseUrl.length > 36 ? `${summary.baseUrl.slice(0, 33)}...` : summary.baseUrl}`)
  return parts.join(' · ')
}

function removeMcpServer(id: string) {
  mcpServers.value = mcpServers.value.filter(server => server.id !== id)
}

function importMcpConfig() {
  try {
    const parsed = JSON.parse(mcpJson.value)
    const incoming = Object.entries(parsed.mcpServers ?? {}).map(([name, config]) => ({
      id: `mcp-${name}`,
      name,
      transport: typeof config === 'object' && config && 'transport' in config ? String((config as { transport?: string }).transport || 'stdio') : 'stdio',
      status: 'pending' as const,
      desc: '从 JSON 配置导入',
    }))
    const existing = new Set(mcpServers.value.map(server => server.name))
    mcpServers.value = [...mcpServers.value, ...incoming.filter(server => !existing.has(server.name))]
    showMcpImport.value = false
  } catch {}
}

function setBuiltinSkillEnabled(name: string, enabled: boolean) {
  const next = new Set(enabledBuiltinSkills.value)
  if (enabled) next.add(name)
  else next.delete(name)
  enabledBuiltinSkills.value = next
}

function toggleAllBuiltinSkills() {
  enabledBuiltinSkills.value = allBuiltinEnabled.value ? new Set() : new Set(builtinSkills.map(skill => skill.name))
}

function confirmSkillUpload() {
  if (!uploadedSkills.value.find(skill => skill.name === 'ui-ux-pro-max')) {
    uploadedSkills.value = [{
      id: `skill-${Date.now()}`,
      name: 'ui-ux-pro-max',
      fileName: 'ui-ux-pro-max.skill.zip',
      size: '128 KB',
      enabled: true,
    }, ...uploadedSkills.value]
  }
  showSkillUpload.value = false
}

function setUploadedSkillEnabled(id: string, enabled: boolean) {
  uploadedSkills.value = uploadedSkills.value.map(skill => skill.id === id ? { ...skill, enabled } : skill)
}

function removeUploadedSkill(id: string) {
  uploadedSkills.value = uploadedSkills.value.filter(skill => skill.id !== id)
}

function setGeekMode(enabled: boolean) {
  if (!enabled && behaviorLevel.value === 'low') behaviorLevel.value = 'medium'
  geekMode.value = enabled
}

function selectBehaviorLevel(id: BehaviorLevelId) {
  const target = behaviorLevels.find(level => level.id === id)
  if (!target || (target.requireGeek && !geekMode.value)) return
  behaviorLevel.value = id
}
</script>

<template>
  <Teleport to="body">
    <div
      data-testid="settings-overlay-shell"
      class="fixed inset-0 z-[1600] flex items-center justify-center bg-[rgba(12,17,30,0.18)] p-6 backdrop-blur-[8px]"
      @click.self="emit('close')"
    >
    <div
      data-testid="settings-panel-shell"
      class="relative flex h-[620px] max-h-full w-full max-w-[880px] overflow-hidden rounded-[30px] bg-[linear-gradient(180deg,rgba(255,255,255,0.94)_0%,rgba(252,252,255,0.98)_100%)] shadow-[0_32px_80px_rgba(17,24,39,0.16)] backdrop-blur-[18px]"
    >
      <div class="pointer-events-none absolute inset-x-0 top-0 h-24 bg-[radial-gradient(circle_at_top_left,rgba(114,111,255,0.10),transparent_60%)]" />
      <div class="pointer-events-none absolute bottom-8 left-[220px] top-8 w-px bg-[linear-gradient(180deg,rgba(114,111,255,0)_0%,rgba(224,229,241,0.72)_18%,rgba(224,229,241,0.72)_82%,rgba(114,111,255,0)_100%)]" />

      <aside data-testid="settings-nav-shell" class="relative flex w-[220px] shrink-0 flex-col bg-[linear-gradient(180deg,rgba(252,252,255,0.98)_0%,rgba(246,248,255,0.92)_100%)]">
        <div class="flex items-center gap-2.5 px-4 pb-4 pt-5">
          <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-[#726FFF] text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)]"><Settings class="h-4 w-4" /></div>
          <div class="min-w-0">
            <div class="truncate text-[13px] font-semibold text-black/82">配置中心</div>
            <div class="mt-0.5 text-[10px] text-black/42">模型、工具、技能与行为策略</div>
          </div>
        </div>

        <div class="flex flex-1 flex-col gap-1.5 p-3">
          <button v-for="item in navItems" :key="item.id" :class="currentTab === item.id ? 'bg-white text-[#726FFF] shadow-[0_10px_24px_rgba(15,23,42,0.05)]' : 'bg-transparent text-black/62 hover:bg-white/72'" class="flex w-full items-center gap-2.5 rounded-[16px] px-3 py-2.5 text-left transition-all" @click="currentTab = item.id">
            <div :class="currentTab === item.id ? 'bg-[#726FFF] text-white' : 'bg-[#EEF2F8] text-black/48'" class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px] transition-colors"><component :is="item.icon" class="h-3.5 w-3.5" /></div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-[12px] font-medium">{{ item.label }}</div>
              <div class="mt-0.5 truncate text-[10px] text-black/38">{{ item.desc }}</div>
            </div>
            <ChevronRight v-if="currentTab === item.id" class="h-3.5 w-3.5 shrink-0 text-[#726FFF]" />
          </button>
        </div>

        <div class="px-3 pb-4">
          <div class="rounded-[18px] bg-[linear-gradient(135deg,rgba(248,247,255,0.9)_0%,rgba(252,251,255,0.96)_100%)] px-3.5 py-3 shadow-[0_10px_24px_rgba(114,111,255,0.06)]">
            <div class="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#726FFF]">实时生效</div>
            <div class="mt-1.5 text-[10px] leading-4.5 text-black/42">设置修改后立即对当前会话生效，无需额外刷新或重启工作室。</div>
          </div>
        </div>
      </aside>

      <section class="flex min-w-0 flex-1 flex-col bg-[linear-gradient(180deg,rgba(255,255,255,0.76)_0%,rgba(252,252,255,0.92)_100%)]">
        <header data-testid="settings-content-header" class="flex shrink-0 items-center justify-between px-6 pb-3 pt-5">
          <div class="flex min-w-0 items-center gap-2.5">
            <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px] bg-[#F0EFFF] text-[#726FFF]"><component :is="activeNav.icon" class="h-3.5 w-3.5" /></div>
            <div class="truncate text-[13px] font-semibold text-black/82">{{ activeNav.label }}</div>
            <div class="h-4 w-px shrink-0 bg-[var(--ai-line)]" />
            <div class="truncate text-[11px] text-black/40">{{ activeNav.desc }}</div>
          </div>
          <button aria-label="关闭配置中心" class="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[rgba(255,255,255,0.86)] text-black/52 shadow-[0_10px_24px_rgba(15,23,42,0.05)] transition-colors hover:bg-white" @click="emit('close')"><X class="h-4 w-4" /></button>
        </header>

        <div class="min-h-0 flex-1 overflow-y-auto px-6 pb-6 pt-3">
          <div v-if="currentTab === 'model'" class="space-y-7">
            <div class="flex items-center gap-3 border-b border-[var(--ai-line)] pb-5">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#F0EFFF] text-[#726FFF]"><Cpu class="h-4.5 w-4.5" /></div>
              <div><div class="text-[15px] font-semibold text-black/82">模型</div><div class="mt-0.5 text-[11px] text-black/40">为不同任务场景选择合适的推理模型</div></div>
            </div>

            <section class="space-y-3">
              <div class="flex items-center gap-2"><div class="text-[12px] font-semibold text-black/82">默认模型</div><div class="h-px flex-1 bg-[var(--ai-line)]" /></div>
              <div class="text-[10px] leading-4 text-black/40">用于日常对话、工具调用和任务执行</div>
              <div class="text-[11px] font-medium text-black/64">当前默认模型：{{ currentDefaultModel?.name ?? '未设置' }}</div>
              <div v-if="settingsLoading" class="rounded-[14px] border border-[#E8EAF2] bg-[#FAFAFC] px-4 py-3 text-[11px] text-black/42">
                正在加载模型设置...
              </div>
              <div v-else-if="defaultModels.length" class="space-y-1.5">
                <button v-for="model in defaultModels" :key="model.id" data-testid="default-model-option" :class="selectedDefaultModel === model.id ? 'border-[#726FFF] bg-[#F8F7FF] shadow-[0_0_0_3px_rgba(114,111,255,0.08)]' : 'border-[#E8EAF2] bg-[#FAFAFC] hover:border-[#726FFF]/36'" class="flex w-full items-center gap-3 rounded-[16px] border px-4 py-3 text-left transition-all" @click="selectedDefaultModel = model.id">
                  <div :class="selectedDefaultModel === model.id ? 'border-[#726FFF]' : 'border-[#D6D9E4]'" class="flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2"><div v-if="selectedDefaultModel === model.id" class="h-1.5 w-1.5 rounded-full bg-[#726FFF]" /></div>
                  <div class="min-w-0 flex-1"><div class="flex items-center gap-2"><span class="truncate text-[12px] font-medium text-black/82">{{ model.name }}</span><span v-if="model.badge" class="rounded-[6px] bg-[#F0EFFF] px-1.5 py-0.5 text-[9px] font-semibold text-[#726FFF]">{{ model.badge }}</span></div></div>
                  <span class="shrink-0 text-[11px] text-black/38">{{ model.provider }}</span>
                </button>
              </div>
              <div v-else class="rounded-[14px] border border-[#E8EAF2] bg-[#FAFAFC] px-4 py-3 text-[11px] leading-5 text-black/42">
                还没有可用的默认模型。请先配置任意一个支持的供应商与模型。
              </div>
              <div v-if="defaultModelError" class="rounded-[12px] bg-[#FEF2F2] px-3 py-2 text-[11px] text-[#DC2626]">
                {{ defaultModelError }}
              </div>
              <div class="flex justify-end">
                <button class="rounded-[12px] bg-[#726FFF] px-4 py-2 text-[12px] font-medium text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)] transition-colors hover:bg-[#635EF7] disabled:cursor-not-allowed disabled:opacity-60" :disabled="!defaultModels.length || defaultModelSaving" @click="saveDefaultModel">
                  {{ defaultModelSaving ? '正在保存...' : '保存默认模型' }}
                </button>
              </div>
            </section>

            <section class="space-y-3">
              <div class="flex items-center gap-2"><div class="text-[12px] font-semibold text-black/82">AI 提供商</div><div class="h-px flex-1 bg-[var(--ai-line)]" /></div>
              <div class="text-[10px] leading-4 text-black/40">已按 opencode provider registry 展开，可配置供应商和即将支持的入口都会显示。</div>
              <div v-if="settingsError" class="rounded-[12px] bg-[#FEF2F2] px-3 py-2 text-[11px] text-[#DC2626]">
                {{ settingsError }}
              </div>
              <div class="grid grid-cols-2 gap-2">
                <button v-for="provider in providerOptions" :key="provider.id" data-testid="provider-config-tile" class="group flex items-center gap-3 rounded-[16px] border border-[#E8EAF2] bg-[#FAFAFC] px-3.5 py-3 text-left transition-all hover:border-[#726FFF]/36 hover:bg-white" @click="openProvider(provider)">
                  <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-[12px] border bg-white text-[10px] font-semibold shadow-[0_4px_10px_rgba(15,23,42,0.05)]" :style="{ color: provider.accent, borderColor: `${provider.accent}26` }">{{ provider.badge }}</div>
                  <div class="min-w-0 flex-1">
                    <div class="truncate text-[11px] font-medium text-black/82">{{ provider.name }}</div>
                    <div class="mt-0.5 truncate text-[10px] text-black/38">{{ provider.description }}</div>
                    <div class="mt-1 flex items-center gap-1.5">
                      <div class="h-1.5 w-1.5 rounded-full" :class="providerConfigured(provider.id) ? 'bg-[#6B7280]' : provider.status === 'coming_soon' ? 'bg-[#F59E0B]' : 'bg-[#D1D5DB]'" />
                      <span class="truncate text-[9px] text-black/38">{{ providerStatusText(provider) }}</span>
                    </div>
                    <div class="mt-1 truncate text-[9px] text-black/30">{{ providerMeta(provider.id) }}</div>
                  </div>
                  <ChevronRight data-testid="provider-config-chevron" class="h-3.5 w-3.5 shrink-0 text-black/24 transition-colors group-hover:text-[#726FFF]" />
                </button>
              </div>
            </section>
          </div>

          <div v-else-if="currentTab === 'mcp'" class="space-y-7">
            <div class="flex items-center gap-3 border-b border-[var(--ai-line)] pb-5">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#F0EFFF] text-[#726FFF]"><Plug class="h-4.5 w-4.5" /></div>
              <div><div class="text-[15px] font-semibold text-black/82">MCP</div><div class="mt-0.5 text-[11px] text-black/40">管理 Model Context Protocol 外部工具服务</div></div>
            </div>

            <div data-testid="mcp-stats-row" class="flex items-center gap-4 rounded-[16px] border border-[#E7EAF3] bg-[#FAFAFC] px-4 py-3">
              <div v-for="(stat, index) in mcpStats" :key="stat.label" data-testid="mcp-stat-item" :class="index < mcpStats.length - 1 ? 'border-r border-[#E7EAF3] pr-4' : ''" class="flex items-center gap-2"><span :class="stat.tone" class="text-[14px] font-semibold">{{ stat.value }}</span><span class="text-[10px] text-black/38">{{ stat.label }}</span></div>
            </div>

            <div class="space-y-1.5">
              <div v-for="server in mcpServers" :key="server.id" class="flex items-center gap-3 rounded-[16px] border border-[#E8EAF2] bg-[#FAFAFC] px-4 py-3">
                <CheckCircle2 v-if="server.status === 'connected'" class="h-4 w-4 shrink-0 text-[#6B7280]" />
                <XCircle v-else-if="server.status === 'error'" class="h-4 w-4 shrink-0 text-[#EF4444]" />
                <div v-else class="h-3.5 w-3.5 shrink-0 rounded-full border border-[#D1D5DB]" />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2"><span class="text-[12px] font-medium text-black/82">{{ server.name }}</span><span :class="server.status === 'connected' ? 'bg-[#F3F4F6] text-[#6B7280]' : server.status === 'error' ? 'bg-[#FEF2F2] text-[#EF4444]' : 'bg-[#F3F4F6] text-black/40'" class="rounded-[6px] px-1.5 py-0.5 text-[9px] font-medium">{{ server.status === 'connected' ? '已连接' : server.status === 'error' ? '连接失败' : '待连接' }}</span></div>
                  <div class="mt-0.5 truncate text-[10px] text-black/38">{{ server.desc }} · {{ server.transport }}</div>
                </div>
                <button class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#FEF2F2] hover:text-[#EF4444]" @click="removeMcpServer(server.id)"><Trash2 class="h-3.5 w-3.5" /></button>
              </div>
            </div>

            <div v-if="showMcpImport" data-testid="mcp-import-panel" class="overflow-hidden rounded-[18px] border border-[#E7EAF3] bg-white">
              <div class="border-b border-[var(--ai-line)] px-4 py-3"><div class="text-[12px] font-semibold text-black/82">粘贴 JSON 添加 MCP 服务</div><div class="mt-1 text-[10px] text-black/38">支持直接粘贴参考项目里的 mcpServers 配置结构。</div></div>
              <div class="p-4"><textarea v-model="mcpJson" rows="8" class="w-full resize-none rounded-[16px] border border-[#E5E7EB] bg-[#F9FAFB] px-3.5 py-3 text-[12px] leading-5 text-black/74 outline-none transition-colors focus:border-[#726FFF]" /></div>
              <div class="flex justify-end gap-2 border-t border-[var(--ai-line)] px-4 py-3">
                <button class="rounded-[12px] border border-[#E5E7EB] bg-white px-4 py-2 text-[12px] text-black/56 transition-colors hover:bg-[#F9FAFB]" @click="showMcpImport = false">取消</button>
                <button class="rounded-[12px] bg-[#726FFF] px-4 py-2 text-[12px] font-medium text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)] transition-colors hover:bg-[#635EF7]" @click="importMcpConfig">导入配置</button>
              </div>
            </div>

            <button data-testid="mcp-import-toggle" class="flex w-full items-center justify-center gap-2 rounded-[16px] border border-dashed border-[#D1D5DB] py-3 text-[12px] font-medium text-black/46 transition-all hover:border-[#726FFF] hover:bg-[#F8F7FF] hover:text-[#726FFF]" @click="showMcpImport = !showMcpImport">
              <Plus class="h-3.5 w-3.5" /><span>展开 JSON 导入</span><ChevronDown class="h-3.5 w-3.5 transition-transform" :class="showMcpImport ? 'rotate-180' : ''" />
            </button>
          </div>

          <div v-else-if="currentTab === 'skills'" class="space-y-7">
            <div class="flex items-center gap-3 border-b border-[var(--ai-line)] pb-5">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#F0EFFF] text-[#726FFF]"><Zap class="h-4.5 w-4.5" /></div>
              <div><div class="text-[15px] font-semibold text-black/82">Skills</div><div class="mt-0.5 text-[11px] text-black/40">开关内置技能，或上传自定义技能包</div></div>
            </div>

            <div class="space-y-3">
              <button data-testid="skills-upload-expander" class="flex w-full items-center gap-2 rounded-[18px] bg-[rgba(255,255,255,0.82)] px-4 py-3 text-left shadow-[0_10px_22px_rgba(15,23,42,0.028)] transition-all hover:bg-[rgba(248,247,255,0.92)]" @click="showSkillUpload = !showSkillUpload">
                <Upload class="h-4 w-4 text-black/48" /><span class="text-[12px] font-medium text-black/74">上传技能文件包</span><ChevronDown class="ml-auto h-3.5 w-3.5 text-black/30 transition-transform" :class="showSkillUpload ? 'rotate-180' : ''" />
              </button>

              <div v-if="showSkillUpload" class="rounded-[20px] bg-[rgba(255,255,255,0.88)] p-4 shadow-[0_12px_26px_rgba(15,23,42,0.035)]">
                <div data-testid="skills-upload-dropzone" class="rounded-[18px] border-2 border-dashed border-[#E5E7EB] bg-[rgba(250,250,252,0.84)] px-5 py-8 text-center">
                  <FileArchive class="mx-auto h-5 w-5 text-black/28" />
                  <div class="mt-3 text-[12px] font-medium text-black/74">拖放或点击选择文件</div>
                  <div class="mt-1 text-[10px] text-black/38">支持 .zip、.tar.gz、.skill 格式，当前示例文件为 ui-ux-pro-max.skill.zip</div>
                </div>
                <div class="mt-3 flex justify-end"><button data-testid="skills-upload-confirm" class="rounded-[12px] bg-[#726FFF] px-4 py-2 text-[12px] font-medium text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)] transition-colors hover:bg-[#635EF7]" @click="confirmSkillUpload">确认上传</button></div>
              </div>
            </div>

            <div v-if="uploadedSkills.length" class="space-y-2">
              <div class="text-[10px] font-semibold uppercase tracking-[0.16em] text-black/36">已上传技能包</div>
              <div v-for="skill in uploadedSkills" :key="skill.id" class="flex items-center gap-3 rounded-[18px] bg-[rgba(255,255,255,0.84)] px-4 py-3 shadow-[0_10px_22px_rgba(15,23,42,0.028)]">
                <FileArchive class="h-4 w-4 shrink-0 text-black/42" />
                <div class="min-w-0 flex-1"><div class="text-[12px] font-medium text-black/82">{{ skill.name }}</div><div class="mt-0.5 text-[10px] text-black/38">{{ skill.fileName }} · {{ skill.size }}</div></div>
                <Switch
                  class="settings-switch shrink-0"
                  :checked="skill.enabled"
                  @change="setUploadedSkillEnabled(skill.id, Boolean($event))"
                />
                <button class="flex h-7 w-7 items-center justify-center rounded-[10px] text-black/28 transition-colors hover:bg-[#FEF2F2] hover:text-[#EF4444]" @click="removeUploadedSkill(skill.id)"><Trash2 class="h-3.5 w-3.5" /></button>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between"><div class="text-[10px] font-semibold uppercase tracking-[0.16em] text-black/36">内置技能</div><button class="text-[10px] font-medium text-[#726FFF] hover:underline" @click="toggleAllBuiltinSkills">{{ allBuiltinEnabled ? '全部关闭' : '全部开启' }}</button></div>
              <div class="space-y-1.5">
                <div v-for="skill in builtinSkills" :key="skill.name" data-testid="builtin-skill-row" :class="enabledBuiltinSkills.has(skill.name) ? 'bg-[rgba(255,255,255,0.92)] shadow-[0_10px_22px_rgba(15,23,42,0.03)]' : 'bg-[rgba(250,250,252,0.82)]'" class="flex items-center gap-3 rounded-[18px] px-4 py-3 transition-all">
                  <div :class="enabledBuiltinSkills.has(skill.name) ? 'bg-[#F0EFFF] text-[#726FFF]' : 'bg-[#F3F4F6] text-black/40'" class="flex h-8 w-8 shrink-0 items-center justify-center rounded-[12px] text-[10px] font-semibold">{{ skill.short }}</div>
                  <div class="min-w-0 flex-1"><div :class="enabledBuiltinSkills.has(skill.name) ? 'text-black/82' : 'text-black/42'" class="text-[12px] font-medium">{{ skill.name }}</div><div class="mt-0.5 text-[10px] leading-4 text-black/38">{{ skill.desc }}</div></div>
                  <Switch
                    class="settings-switch shrink-0"
                    :checked="enabledBuiltinSkills.has(skill.name)"
                    @change="setBuiltinSkillEnabled(skill.name, Boolean($event))"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-else class="space-y-7">
            <div class="flex items-center gap-3 border-b border-[var(--ai-line)] pb-5">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#F0EFFF] text-[#726FFF]"><ShieldCheck class="h-4.5 w-4.5" /></div>
              <div><div class="text-[15px] font-semibold text-black/82">行为配置</div><div class="mt-0.5 text-[11px] text-black/40">配置 Agent 的敏感操作级别与自动化策略</div></div>
            </div>

            <div data-testid="behavior-geek-card" class="overflow-hidden rounded-[22px] bg-[rgba(255,255,255,0.88)] shadow-[0_12px_26px_rgba(15,23,42,0.04)]">
              <div class="flex items-center justify-between px-4 py-4">
                <div class="flex items-start gap-3">
                  <div class="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[#F3F4F6] text-[15px]">⌘</div>
                  <div><div class="text-[12px] font-semibold text-black/82">极客模式</div><div class="mt-1 text-[10px] leading-4 text-black/38">解锁最低安全级别，允许 Agent 在受控范围内全自动执行任务。</div></div>
                </div>
                <Switch
                  data-testid="behavior-geek-toggle"
                  class="settings-switch shrink-0"
                  :checked="geekMode"
                  @change="setGeekMode(Boolean($event))"
                />
              </div>
              <div v-if="geekMode" class="mx-4 mb-4 rounded-[16px] bg-[#FFF8E8] px-4 py-3"><div class="text-[11px] font-semibold text-[#92400E]">极客模式已开启</div><div class="mt-1 text-[10px] leading-4 text-[#92400E]">Agent 可在更多步骤中自主继续执行，请谨慎确认工作目录与外部连接范围。</div></div>
            </div>

            <div class="space-y-3">
              <div class="text-[10px] font-semibold uppercase tracking-[0.16em] text-black/36">敏感操作安全级别</div>
              <div class="space-y-2">
                <button v-for="level in behaviorLevels" :key="level.id" data-testid="behavior-level-option" :disabled="level.requireGeek && !geekMode" :class="level.requireGeek && !geekMode ? 'cursor-not-allowed border-[#E8EAF2] bg-[#FAFAFC] opacity-45' : behaviorLevel === level.id ? 'border-[#D8DAE6] bg-white shadow-[0_10px_24px_rgba(15,23,42,0.04)]' : 'border-[#E8EAF2] bg-white hover:shadow-[0_6px_16px_rgba(15,23,42,0.04)]'" class="relative flex w-full items-start gap-3.5 rounded-[18px] border px-4 py-4 text-left transition-all" @click="selectBehaviorLevel(level.id)">
                  <div v-if="behaviorLevel === level.id" class="absolute bottom-4 left-0 top-4 w-[3px] rounded-r-full bg-[#726FFF]" />
                  <div :class="behaviorLevel === level.id ? 'border-[#726FFF]' : 'border-[#D6D9E4]'" class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2"><div v-if="behaviorLevel === level.id" class="h-1.5 w-1.5 rounded-full bg-[#726FFF]" /></div>
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2"><span :class="behaviorLevel === level.id ? 'text-[#726FFF]' : 'text-black/82'" class="text-[12px] font-semibold">{{ level.label }}</span><span v-if="level.default" class="rounded-[6px] bg-[#F3F4F6] px-1.5 py-0.5 text-[9px] font-semibold text-black/48">默认</span><span v-if="level.requireGeek" class="rounded-[6px] bg-[#F3F4F6] px-1.5 py-0.5 text-[9px] font-semibold text-black/42">需极客模式</span></div>
                    <div class="mt-1 text-[11px] leading-4.5 text-black/66">{{ level.desc }}</div>
                    <div v-if="behaviorLevel === level.id" class="mt-1.5 text-[10px] text-[#726FFF]">{{ level.hint }}</div>
                  </div>
                </button>
              </div>
            </div>

            <div class="rounded-[18px] bg-[rgba(250,250,252,0.84)] px-4 py-3 shadow-[inset_0_0_0_1px_rgba(232,234,242,0.55)]"><div class="text-[11px] font-medium text-black/72">当前生效策略</div><div class="mt-1 text-[10px] leading-4.5 text-black/40">{{ selectedBehaviorMeta.label }} 级别已生效；涉及写入、删除、外发与外部工具调用时会遵循上面的安全门槛。</div></div>
          </div>
        </div>
      </section>
    </div>

    <div v-if="editingProvider" class="absolute inset-0 z-40 flex items-center justify-center bg-[rgba(10,10,20,0.4)] backdrop-blur-[4px]" @click.self="closeProvider">
      <div class="w-[400px] overflow-hidden rounded-[24px] bg-white shadow-[0_24px_60px_rgba(0,0,0,0.16)]">
        <div class="flex items-center justify-between border-b border-[#EBEBEB] px-5 py-4">
          <div class="flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-[12px] border bg-[#F9FAFB] text-[10px] font-semibold" :style="{ color: editingProvider.accent, borderColor: `${editingProvider.accent}26` }">{{ editingProvider.badge }}</div>
            <div><div class="text-[13px] font-semibold text-black/82">配置 {{ editingProvider.name }}</div><div class="mt-0.5 text-[10px] text-black/36">{{ editingProvider.description }}</div></div>
          </div>
          <button class="flex h-7 w-7 items-center justify-center rounded-[10px] transition-colors hover:bg-[#F3F4F6]" @click="closeProvider"><X class="h-3.5 w-3.5 text-black/52" /></button>
        </div>

        <div v-if="editingProvider.status === 'coming_soon'" class="space-y-3 p-5">
          <div class="rounded-[16px] bg-[#FFF8E8] px-4 py-3 text-[11px] leading-5 text-[#92400E]">
            {{ editingProvider.comingSoonNote ?? '当前版本先展示入口，后续会补齐完整接入流程。' }}
          </div>
        </div>

        <div v-else class="space-y-4 p-5">
          <div v-if="editingProvider.supportsDisplayName">
            <label class="mb-1.5 block text-[12px] font-medium text-black/74">显示名称</label>
            <input v-model="providerDisplayName" class="h-10 w-full rounded-[12px] border border-[#E5E7EB] bg-[#F9FAFB] px-3 text-[13px] text-black/80 outline-none transition-colors focus:border-[#726FFF]" placeholder="例如：公司私有模型网关">
          </div>
          <div>
            <label class="mb-1.5 flex items-center gap-1.5 text-[12px] font-medium text-black/74"><Key class="h-3.5 w-3.5 text-[#726FFF]" />API Key</label>
            <input v-model="providerApiKey" type="password" class="h-10 w-full rounded-[12px] border border-[#E5E7EB] bg-[#F9FAFB] px-3 text-[13px] text-black/80 outline-none transition-colors focus:border-[#726FFF]" :placeholder="editingProviderSummary?.configured ? '留空可保留已保存密钥' : 'sk-...'">
          </div>
          <div v-if="editingProvider.supportsBaseUrl">
            <label class="mb-1.5 block text-[12px] font-medium text-black/74">{{ editingProvider.requiresBaseUrl ? 'Base URL' : 'Base URL（可选）' }}</label>
            <input v-model="providerBaseUrl" class="h-10 w-full rounded-[12px] border border-[#E5E7EB] bg-[#F9FAFB] px-3 text-[13px] text-black/80 outline-none transition-colors focus:border-[#726FFF]" :placeholder="editingProvider.id === 'custom-openai-compatible' ? '例如：https://api.example.com/v1' : '可留空以使用默认端点'">
          </div>
          <div v-if="editingProvider.supportsModel">
            <label class="mb-1.5 block text-[12px] font-medium text-black/74">默认模型</label>
            <input v-model="providerModel" class="h-10 w-full rounded-[12px] border border-[#E5E7EB] bg-[#F9FAFB] px-3 text-[13px] text-black/80 outline-none transition-colors focus:border-[#726FFF]" placeholder="例如：gpt-4o">
          </div>
          <div class="rounded-[14px] bg-[#F9FAFB] px-3 py-2 text-[10px] leading-4.5 text-black/42">
            {{ providerMeta(editingProvider.id) }}
          </div>
          <div v-if="providerError" class="rounded-[12px] bg-[#FEF2F2] px-3 py-2 text-[11px] text-[#DC2626]">
            {{ providerError }}
          </div>
        </div>

        <div class="flex gap-2 px-5 pb-5">
          <button v-if="editingProvider.status === 'coming_soon'" class="flex-1 rounded-[12px] bg-[#726FFF] py-2 text-[12px] font-medium text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)] transition-colors hover:bg-[#635EF7]" @click="closeProvider">知道了</button>
          <template v-else>
            <button class="flex-1 rounded-[12px] border border-[#E5E7EB] bg-white py-2 text-[12px] text-black/56 transition-colors hover:bg-[#F9FAFB] disabled:cursor-not-allowed disabled:opacity-60" :disabled="providerSubmitting" @click="editingProviderSummary?.configured ? clearProvider() : closeProvider()">
              {{ editingProviderSummary?.configured ? '移除' : '取消' }}
            </button>
            <button class="flex-1 rounded-[12px] bg-[#726FFF] py-2 text-[12px] font-medium text-white shadow-[0_10px_24px_rgba(114,111,255,0.22)] transition-colors hover:bg-[#635EF7] disabled:cursor-not-allowed disabled:opacity-60" :disabled="providerSubmitting" @click="saveProvider">
              {{ providerSubmitting ? '正在保存...' : '保存' }}
            </button>
          </template>
        </div>
      </div>
    </div>
    </div>
  </Teleport>
</template>

<style scoped>
:deep(.settings-switch.ant-switch) {
  min-width: 40px;
  height: 22px;
  background: rgba(148, 163, 184, 0.28);
  box-shadow: none;
}

:deep(.settings-switch.ant-switch:hover:not(.ant-switch-disabled)) {
  background: rgba(148, 163, 184, 0.36);
}

:deep(.settings-switch.ant-switch .ant-switch-handle) {
  top: 2px;
  inset-inline-start: 2px;
}

:deep(.settings-switch.ant-switch.ant-switch-checked) {
  background: linear-gradient(135deg, #726FFF 0%, #5E5AE8 100%);
}

:deep(.settings-switch.ant-switch.ant-switch-checked:hover:not(.ant-switch-disabled)) {
  background: linear-gradient(135deg, #6a66fb 0%, #5652e4 100%);
}
</style>
