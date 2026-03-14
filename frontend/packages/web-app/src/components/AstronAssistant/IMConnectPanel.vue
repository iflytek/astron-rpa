<script setup lang="ts">
import { message } from 'ant-design-vue'
import { computed, onMounted, ref } from 'vue'

import { getUserSetting } from '@/api/setting'

import FeishuConnectPanel from './FeishuConnectPanel.vue'
import { readFeishuConfigFromSetting } from './feishu-config'

const open = defineModel<boolean>('open', { default: false })

type ProviderKey = 'feishu' | 'dingtalk' | 'qq' | 'wechat-work'

const text = {
  title: '\u52a9\u624b\u8bbe\u7f6e',
  tabIm: 'IM \u914d\u7f6e',
  sectionTitle: '\u96c6\u6210\u6e20\u9053',
  sectionDesc: '\u5728\u8fd9\u91cc\u7ba1\u7406 Astron \u52a9\u624b\u7684 IM \u63a5\u5165\u65b9\u5f0f\uff0c\u76ee\u524d\u5148\u5f00\u653e\u98de\u4e66\u914d\u7f6e\u3002',
  guide: '\u914d\u7f6e\u6307\u5357',
  configured: '\u5df2\u914d\u7f6e',
  notConfigured: '\u672a\u914d\u7f6e',
  configure: '\u914d\u7f6e',
  edit: '\u7f16\u8f91',
  disabled: '\u6682\u672a\u5f00\u653e',
  placeholderInfo: '\u8be5\u6e20\u9053\u5df2\u9884\u7559\uff0c\u540e\u7eed\u518d\u5f00\u653e\u914d\u7f6e\u3002',
  feishuTitle: '\u98de\u4e66\u673a\u5668\u4eba\u96c6\u6210',
  feishuDesc: '\u6ce8\u518c\u98de\u4e66\u5e94\u7528\u5e76\u586b\u5199\u51ed\u636e\uff0c\u8ba9\u7528\u6237\u53ef\u4ee5\u76f4\u63a5\u5728\u624b\u673a\u98de\u4e66\u4e2d\u4e0e Astron \u52a9\u624b\u5bf9\u8bdd\u3002',
  feishuReady: '\u98de\u4e66\u901a\u9053\u51ed\u636e\u5df2\u4fdd\u5b58\uff0c\u53ef\u7ee7\u7eed\u5b8c\u6210 OpenClaw \u901a\u9053\u6ce8\u518c\u3002',
  dingtalkTitle: '\u9489\u9489\u673a\u5668\u4eba\u96c6\u6210',
  dingtalkDesc: '\u9884\u7559 Stream Mode / Callback Mode \u63a5\u5165\u80fd\u529b\u3002',
  qqTitle: 'QQ \u673a\u5668\u4eba\u96c6\u6210',
  qqDesc: '\u9884\u7559 QQ \u673a\u5668\u4eba\u6e20\u9053\u80fd\u529b\u3002',
  weworkTitle: '\u4f01\u4e1a\u5fae\u4fe1\u96c6\u6210',
  weworkDesc: '\u9884\u7559\u4f01\u5fae\u5ba2\u670d\u548c\u673a\u5668\u4eba\u6e20\u9053\u80fd\u529b\u3002',
} as const

const activeProvider = ref<ProviderKey>('feishu')
const feishuEnabled = ref(false)
const feishuBound = ref(false)
const feishuBotName = ref('')

const providers = computed(() => [
  {
    key: 'feishu' as ProviderKey,
    title: text.feishuTitle,
    description: text.feishuDesc,
    disabled: false,
  },
  {
    key: 'dingtalk' as ProviderKey,
    title: text.dingtalkTitle,
    description: text.dingtalkDesc,
    disabled: true,
  },
  {
    key: 'qq' as ProviderKey,
    title: text.qqTitle,
    description: text.qqDesc,
    disabled: true,
  },
  {
    key: 'wechat-work' as ProviderKey,
    title: text.weworkTitle,
    description: text.weworkDesc,
    disabled: true,
  },
])

const feishuStatusText = computed(() => {
  if (feishuEnabled.value && feishuBound.value)
    return text.configured
  return text.notConfigured
})

const feishuStatusClass = computed(() => {
  if (feishuEnabled.value && feishuBound.value)
    return 'text-[#10b981]'
  return 'text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]'
})

async function loadStatus() {
  const setting = await getUserSetting()
  const feishu = readFeishuConfigFromSetting(setting)
  feishuEnabled.value = feishu.enabled
  feishuBound.value = Boolean(feishu.appId && feishu.appSecret)
  feishuBotName.value = feishu.botName || 'Astron Assistant'
}

function openProvider(providerKey: ProviderKey, disabled: boolean) {
  if (disabled) {
    message.info(text.placeholderInfo)
    return
  }
  activeProvider.value = providerKey
}

function handleSaved() {
  void loadStatus()
}

onMounted(() => {
  void loadStatus()
})
</script>

<template>
  <a-modal v-model:open="open" :title="text.title" :footer="null" :width="980" destroy-on-close>
    <a-tabs default-active-key="im">
      <a-tab-pane key="im" :tab="text.tabIm">
        <div class="rounded-[16px] border border-[#e7ebf3] bg-[#fcfcfd] dark:border-[rgba(255,255,255,0.08)] dark:bg-[#1f1f23]">
          <div class="flex items-start justify-between gap-4 border-b border-[#edf1f6] px-5 py-4 dark:border-[rgba(255,255,255,0.08)]">
            <div>
              <div class="text-[18px] font-semibold text-[rgba(0,0,0,0.88)] dark:text-[rgba(255,255,255,0.88)]">
                {{ text.sectionTitle }}
              </div>
              <div class="mt-1 text-[13px] leading-[22px] text-[rgba(0,0,0,0.5)] dark:text-[rgba(255,255,255,0.5)]">
                {{ text.sectionDesc }}
              </div>
            </div>
            <a class="text-[13px]" href="https://open.feishu.cn/document/home/index" target="_blank">
              {{ text.guide }}
            </a>
          </div>

          <div class="grid grid-cols-1 gap-3 p-5 lg:grid-cols-[360px_minmax(0,1fr)]">
            <div class="space-y-3">
              <div
                v-for="provider in providers"
                :key="provider.key"
                class="w-full rounded-[14px] border px-4 py-4 text-left transition"
                :class="[
                  provider.disabled
                    ? 'cursor-not-allowed border-[#edf1f6] bg-[#f6f7fa] opacity-65 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.03)]'
                    : activeProvider === provider.key
                      ? 'border-[#4f46e5] bg-[#eef2ff] shadow-[0_8px_20px_rgba(79,70,229,0.12)] dark:border-[#6366f1] dark:bg-[rgba(99,102,241,0.14)]'
                      : 'border-[#edf1f6] bg-[#f8faff] hover:border-[#cdd5e6] dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.03)]',
                ]"
                @click="openProvider(provider.key, provider.disabled)"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="text-[15px] font-medium text-[rgba(0,0,0,0.88)] dark:text-[rgba(255,255,255,0.88)]">{{ provider.title }}</span>
                      <span
                        v-if="provider.key === 'feishu'"
                        class="text-[12px] font-medium"
                        :class="feishuStatusClass"
                      >
                        {{ feishuStatusText }}
                      </span>
                      <span
                        v-else
                        class="rounded-full bg-[rgba(0,0,0,0.06)] px-2 py-[2px] text-[12px] text-[rgba(0,0,0,0.45)] dark:bg-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.45)]"
                      >
                        {{ text.disabled }}
                      </span>
                    </div>
                    <div class="mt-2 text-[13px] leading-[22px] text-[rgba(0,0,0,0.58)] dark:text-[rgba(255,255,255,0.58)]">
                      {{ provider.description }}
                    </div>
                  </div>

                  <a-button
                    v-if="provider.key === 'feishu'"
                    type="primary"
                    size="small"
                  >
                    {{ feishuBound ? text.edit : text.configure }}
                  </a-button>
                  <a-button
                    v-else
                    size="small"
                    disabled
                  >
                    {{ text.disabled }}
                  </a-button>
                </div>

                <div
                  v-if="provider.key === 'feishu' && feishuBound"
                  class="mt-4 rounded-[12px] border border-[#dbe4ff] bg-[#fff] px-3 py-3 text-[12px] dark:border-[rgba(99,102,241,0.28)] dark:bg-[rgba(255,255,255,0.02)]"
                >
                  <div class="font-medium text-[rgba(0,0,0,0.84)] dark:text-[rgba(255,255,255,0.84)]">
                    {{ feishuBotName }}
                  </div>
                  <div class="mt-1 text-[#10b981]">
                    {{ text.feishuReady }}
                  </div>
                </div>
              </div>
            </div>

            <div class="min-h-[420px] rounded-[16px] border border-[#edf1f6] bg-[#fff] p-5 dark:border-[rgba(255,255,255,0.08)] dark:bg-[rgba(255,255,255,0.02)]">
              <FeishuConnectPanel v-if="activeProvider === 'feishu'" @saved="handleSaved" />
            </div>
          </div>
        </div>
      </a-tab-pane>
    </a-tabs>
  </a-modal>
</template>
