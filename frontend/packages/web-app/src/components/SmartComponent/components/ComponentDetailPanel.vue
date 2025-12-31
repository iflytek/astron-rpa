<script lang="ts" setup>
import { computed } from 'vue'

import loadingSvg from '@/assets/img/loading.svg'

import { injectChatContext, useSmartComp } from '../hooks'
import type { SmartComp } from '../types'

import CollapsePanel from './CollapsePanel.vue'

const props = defineProps<{
  version: SmartComp | number
  showTime?: boolean
  isGenerating?: boolean
}>()

const smartComp = useSmartComp()
const { restoreChatHistory } = injectChatContext()
const currentVersion = computed(() => smartComp.editingSmartComp.value?.version)

const versionData = computed<SmartComp | undefined>(() => {
  if (!props.version) {
    return undefined
  }

  if (typeof props.version === 'object') {
    return props.version
  }

  if (typeof props.version === 'number') {
    return smartComp.versionList.value.find(v => v.version === props.version)
  }

  return undefined
})

function handleSwitchVersion(version: number) {
  if (version === currentVersion.value)
    return

  smartComp.switchToVersion(version)

  const targetVersion = smartComp.versionList.value.find(v => v.version === version)
  if (targetVersion?.detail?.chatHistory && targetVersion.detail.chatHistory.length > 0) {
    restoreChatHistory(targetVersion.detail.chatHistory)
  }
}
</script>

<template>
  <div v-if="isGenerating" class="flex items-center gap-2 bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08] rounded-lg p-2">
    <img :src="loadingSvg" alt="loading" class="w-4 h-4 animate-spin">
    <span>正在生成组件...</span>
  </div>
  <CollapsePanel
    v-if="versionData"
    class="bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08] hover:bg-[#D7D7FF]/[.4] dark:hover:bg-[#5D59FF]/[.35] border border-primary rounded-lg p-2 transition-colors"
    :class="{ 'border-transparent': versionData.version !== currentVersion }"
  >
    <template #title>
      <div class="flex-1 overflow-hidden">
        <div class="flex items-center">
          <div
            class="mr-2 px-2 rounded font-medium text-[12px] bg-[#D7D7FF]/[.4] dark:bg-[#5D59FF]/[.35]"
            :class="{ 'text-primary': versionData.version === currentVersion }"
          >
            v{{ versionData.version }}
          </div>
          <div class="flex-1 flex flex-col overflow-hidden">
            <span class="font-medium text-ellipsis overflow-hidden whitespace-nowrap">{{ versionData.title || '组件版本名称' }}</span>
            <span v-if="showTime" class="text-[12px] text-text-tertiary">
              {{ new Date(versionData.updateTime || versionData.createTime || Date.now()).toLocaleString('zh-CN') }}
            </span>
          </div>
          <rpa-hint-icon
            v-if="versionData.version !== currentVersion"
            name="undo"
            enable-hover-bg
            @click.stop="handleSwitchVersion(versionData.version!)"
          />
        </div>
      </div>
    </template>
    <div class="space-y-2 text-[12px]">
      <div class="flex">
        <span class="font-medium">组件功能：</span>
        <span class="flex-1 text-text-secondary">{{ versionData.comment }}</span>
      </div>
      <div class="flex">
        <span class="font-medium">输入参数：</span>
        <span class="flex-1 text-text-secondary">{{ versionData.inputList.map(item => item.title).join('、') || '无' }}</span>
      </div>
      <div class="flex">
        <span class="font-medium">输出参数：</span>
        <span class="flex-1 text-text-secondary">{{ versionData.outputList.map(item => item.title).join('、') || '无' }}</span>
      </div>
    </div>
  </CollapsePanel>
</template>
