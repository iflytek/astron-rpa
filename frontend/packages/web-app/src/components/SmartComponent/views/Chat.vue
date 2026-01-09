<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { Bubble } from 'ant-design-x-vue'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getSmartComp, optimizeQuestion } from '@/api/component'
import { clipboardManager } from '@/platform'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'

import ComponentDetailPanel from '../components/ComponentDetailPanel.vue'
import PackageBar from '../components/PackageBar.vue'
import Prompts from '../components/Prompts.vue'
import StatusBar from '../components/StatusBar.vue'
import TiptapEditor from '../components/TiptapEditor/TiptapEditor.vue'
import { SMART_COMPONENT_KEY_PREFIX } from '../config/constants'
import { injectChatContext, usePackageCheck, useSmartComp } from '../hooks'
import type { DocNode } from '../types'
import type { Message, MessageInput, MessageOutput, SmartType } from '../types/chat'
import { isAssistantMessage, isUserMessage, parseChatContent, parseOptimizedTextToDocNode, parseUserTextToDocNode } from '../utils'

const smartComp = useSmartComp()
const processStore = useProcessStore()
const flowStore = useFlowStore()
const route = useRoute()
const { colorTheme } = storeToRefs(useAppConfigStore())

const {
  realMsgs,
  promptItmes,
  senderLoading,
  rolesAsFunction,
  sendChat,
  restoreChatHistory,
} = injectChatContext()

async function restoreChat(smartId: string, targetVersion?: number) {
  try {
    if (!smartId) {
      console.error('restoreChat: smartId is undefined', smartId)
      return
    }

    const smartCompData = await getSmartComp({
      robotId: processStore.project.id,
      smartId,
    })

    if (smartCompData && smartCompData.detail?.versionList) {
      const versionList = smartCompData.detail.versionList

      const version = targetVersion || Math.max(...versionList.map(v => v.version || 0))
      const targetVersionData = versionList.find(v => v.version === version)

      if (targetVersionData) {
        // 从 simpleFlowUIData 中获取对应的原子能力数据
        const key = `${SMART_COMPONENT_KEY_PREFIX}.${smartId}`
        const flowNode = flowStore.simpleFlowUIData.find(item => item.key === key)

        // 如果存在流程节点，将表单属性同步到 editingSmartComp
        if (flowNode) {
          const mergedComp = {
            ...targetVersionData,
            inputList: flowNode.inputList || targetVersionData.inputList || [],
            outputList: flowNode.outputList || targetVersionData.outputList || [],
            advanced: flowNode.advanced || targetVersionData.advanced || [],
            exception: flowNode.exception || targetVersionData.exception || [],
            alias: flowNode.alias || targetVersionData.alias,
          }
          smartComp.initVersionList(versionList.map(v => v.version === version ? mergedComp : v), version)
        }
        else {
          smartComp.initVersionList(versionList, version)
        }
        smartComp.smartType.value = targetVersionData.smartType

        // 恢复会话历史
        if (targetVersionData.detail?.chatHistory && targetVersionData.detail.chatHistory.length > 0) {
          restoreChatHistory(targetVersionData.detail.chatHistory)
        }
      }
    }
  }
  catch (error) {
    console.error('恢复智能组件会话历史失败:', error)
  }
}

onMounted(() => {
  const smartId = route.query?.smartId as string | undefined
  const version = Number(route.query?.version)

  if (smartId) {
    restoreChat(smartId, version)
  }
  else {
    smartComp.setEditingSmartComp()
  }
})

const value = ref()
const optimizeLoading = ref(false)
const editorRef = ref<InstanceType<typeof TiptapEditor>>()

const {
  lackPackages,
  initialLackPackages,
  isInstalling,
  isInstallCompleted,
  hasLackPackages,
  installAllPackages,
} = usePackageCheck()

const showInstallConfirm = ref(false)

watch(lackPackages, (newVal) => {
  if (newVal.length > 0) {
    showInstallConfirm.value = true
  }
})

function handleCopy(content: MessageInput | MessageOutput) {
  if ('user' in content) {
    // 转换为 docNode 并复制 JSON
    const docNode = parseUserTextToDocNode(content.user, content.elements || [])
    clipboardManager.writeClipboardText(JSON.stringify(docNode, null, 2))
  }
  else {
    clipboardManager.writeClipboardText(content.text)
  }
  message.success('复制成功')
}

async function handleOptimizeQuestion(docNode: DocNode) {
  try {
    optimizeLoading.value = true
    const parsedContent = parseChatContent(docNode)
    const optimizedText = await optimizeQuestion({
      sceneCode: 'smart_optimize_input',
      user: parsedContent.user,
      elements: parsedContent.elements,
    })

    if (optimizedText) {
      const optimizedDocNode = parseOptimizedTextToDocNode(optimizedText, parsedContent.elements)
      value.value = optimizedDocNode
      message.success('优化成功')
    }
  }
  catch (error) {
    console.error('优化提问失败:', error)
  }
  finally {
    optimizeLoading.value = false
  }
}

function handlePromptClick(prompt) {
  const type = prompt.key as SmartType
  if (!editorRef.value) {
    return
  }

  if (type === 'web_auto') {
    editorRef.value.setContent([
      { type: 'text', text: '在' },
      { type: 'elementNode', attrs: { name: '元素名' } },
      { type: 'text', text: '中完成' },
      { type: 'descriptionNode', content: [{ type: 'text', text: '可见元素的自动化操作' }] },
    ])
  }
  else if (type === 'data_process') {
    editorRef.value.setContent([
      { type: 'text', text: '需求：' },
      { type: 'descriptionNode', content: [{ type: 'text', text: '需求描述' }] },
      { type: 'text', text: '示例：' },
      { type: 'descriptionNode', content: [{ type: 'text', text: '示例描述' }] },
      { type: 'text', text: '输入：' },
      { type: 'descriptionNode', content: [{ type: 'text', text: '参数' }] },
      { type: 'text', text: '输出：' },
      { type: 'descriptionNode', content: [{ type: 'text', text: '参数' }] },
    ])
  }

  smartComp.smartType.value = type
}

// 安装依赖
async function handleConfirmInstall() {
  await installAllPackages()
  showInstallConfirm.value = false
}

// 取消安装
function handleCancelInstall() {
  showInstallConfirm.value = false
}
</script>

<template>
  <div class="flex justify-center bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.08] rounded-lg" :class="[colorTheme]">
    <div class="h-full flex flex-col gap-4 w-[712px] p-4 overflow-y-hidden">
      <div class="flex-1 flex flex-col gap-4 overflow-y-auto">
        <Bubble.List
          v-if="realMsgs.length"
          :roles="rolesAsFunction"
          :items="realMsgs"
        >
          <template #header="{ item }">
            <div v-if="isAssistantMessage(item as Message)" class="flex flex-col gap-1">
              <StatusBar :is-generating="item.content.status === 'generating'" :duration="item.content.duration" />
              <ComponentDetailPanel :version="item.content.version" :is-generating="item.content.status === 'generating'" />
              <PackageBar
                v-if="item.content.version === smartComp.currentVersionIndex.value + 1"
                :lack-packages="lackPackages"
                :initial-lack-packages="initialLackPackages"
                :is-installing="isInstalling"
                :is-completed="isInstallCompleted"
              />
            </div>
          </template>
          <template #message="{ item }">
            <div>{{ item.content }}</div>
          </template>
          <template #footer="{ item }">
            <div v-if="isUserMessage(item as Message)" class="flex">
              <rpa-hint-icon name="bottom-pick-menu-copy" enable-hover-bg @click="handleCopy(item.content)" />
            </div>
          </template>
        </Bubble.List>

        <div v-else class="flex-1 flex flex-col justify-center gap-4">
          <div class="flex flex-col items-center">
            <rpa-icon name="magic-wand" size="32" class="text-primary" />
            <span class="text-primary text-[20px] font-semibold">星辰 RPA 智能组件生成助手</span>
            <span>帮助您快速创建 RPA 组件</span>
          </div>

          <Prompts
            :items="promptItmes"
            :active-key="smartComp.smartType.value"
            @item-click="handlePromptClick"
          />
        </div>
      </div>
      <div class="flex flex-col">
        <div
          v-if="showInstallConfirm && hasLackPackages"
          class="flex justify-between items-center mx-4 p-3 rounded-t-lg bg-[#D7D7FF]/[.4] dark:bg-[#5D59FF]/[.35]"
        >
          <span class="text-primary">是否安装缺失依赖库？</span>
          <div class="flex items-center gap-2">
            <a-button type="text" :disabled="isInstalling" @click="handleCancelInstall">
              取消
            </a-button>
            <a-button
              type="primary"
              :loading="isInstalling"
              @click="handleConfirmInstall"
            >
              确定
            </a-button>
          </div>
        </div>
        <TiptapEditor ref="editorRef" v-model:value="value" :loading="senderLoading" :optimize-loading="optimizeLoading" @submit="sendChat" @optimize="handleOptimizeQuestion" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-bubble-header) {
  width: 100%;
}

:deep(.ant-bubble-start .ant-bubble-content) {
  width: 100%;
}

:deep(.ant-typography) {
  p:last-child {
    margin-bottom: 0;
  }
}

:deep(.ant-bubble-content-filled) {
  background-color: #f3f3f7;

  * {
    user-select: text;
  }
}

.dark :deep(.ant-bubble-content-filled) {
  background-color: rgba(#ffffff, 0.08);
}
</style>
