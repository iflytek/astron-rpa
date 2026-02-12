<script setup lang="ts">
import { CloseOutlined, LoadingOutlined, RightOutlined, SaveOutlined, StopOutlined, ZoomInOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { nanoid } from 'nanoid'
import { computed, h, nextTick, onBeforeUnmount, ref } from 'vue'
import { useAsyncState, useToggle } from '@vueuse/core'
import { get } from 'lodash-es'
import { to } from 'await-to-js'
import { useTheme } from '@rpa/components'

import { WINDOW_NAME } from '@/constants'
import { getAPIBaseURL } from '@/api/http/env'
import { sseRequest } from '@/api/sse'
import { utilsManager, windowManager } from '@/platform'
import type { chatItem } from '@/types/chat'

import { type FileInfo, initFileInfo, FILE_TYPE_IMG } from './utils'
import Preview from './Preview.vue'
import ChatBgLightSvg from './assets/chat-bg-light.svg?component'
import ChatBgDarkSvg from './assets/chat-bg-dark.svg?component'

let controller: AbortController | null = null
// 初始化信息
const targetInfo = new URL(location.href).searchParams
// 文件路径
const filePath = targetInfo.get('file_path') || ''
const fileName = filePath.split(/[/\\]/).pop() || '';
const fileSuffix = fileName.split('.').pop()?.toLowerCase() || '';
const initFileInfoData = initFileInfo({ path: filePath, name: fileName, suffix: fileSuffix })

const title = filePath ? '知识问答' : (targetInfo.get('title') || 'AI Chat组件')
// 是否显示保存按钮
const showSave = ['1', 1].includes(targetInfo.get('is_save'))
// 最大轮数
const limitTurns = Number(targetInfo.get('max_turns')) || 20
// 预设列表
const presetList = targetInfo.get('questions')?.split('$-$') || []
// 对话模型
const model = targetInfo.get('model')
const replyBaseData = JSON.parse(targetInfo.get('reply') || '{}') ?? {}
// 交互类型 multi:多轮对话,file:知识问答
const chatType = filePath ? 'file' : 'multi'

const { isDark } = useTheme()

const ChatBgSvg = computed(() => isDark.value ? ChatBgDarkSvg : ChatBgLightSvg)
const isMultiTurnLimit = computed(() => chatDataList.value.length >= limitTurns) // 是否置灰输入框

const prompt = ref('')
const isThinking = ref(false) // 是否在思考中
const chatDataList = ref([]) // 回答信息
const messagingId = ref('') // 当前消息ID
const isSave = ref(false) // 是否在保存过程中
const saveQAIds = ref([]) // 保存的promptIds
const [showPreview, togglePreview] = useToggle(false) // 是否显示预览弹窗，默认不显示

// 文件信息
const { state: fileInfo } = useAsyncState<FileInfo>(async () => {
  if (!filePath) return initFileInfoData
  const [err, _fileContent] = await to(utilsManager.readFile(filePath, null));
  const fileContent = err ? '' : _fileContent;
  const filePreviewContent = fileSuffix === 'txt' && fileContent instanceof Uint8Array
    ? new TextDecoder().decode(fileContent)
    : fileContent;

  return {
    ...initFileInfoData,
    content: fileContent as string,
    previewContent: filePreviewContent,
  }
}, initFileInfoData)

const couldPreview = computed(() => !['doc', 'docx'].includes(fileInfo.value.suffix))

function updateMessagingChat(key: string, data: string | number) {
  chatDataList.value.forEach((item: chatItem) => {
    if (item.id === messagingId.value) {
      if (key === 'answer')
        item[key] += data
      if (key === 'timestamp')
        item[key] = data
    }
  })
}

function removeQAId(id: string) {
  saveQAIds.value = saveQAIds.value.filter(item => item !== id)
}

function clearAllData() {
  chatDataList.value = []
  messagingId.value = ''
  isSave.value = false
  saveQAIds.value = []
}

function handleCheckboxChange(checkValue: boolean, id: string) {
  checkValue ? saveQAIds.value.push(id) : removeQAId(id)
}

function handleCancel() {
  isSave.value = false
  saveQAIds.value = []
}

function handleSave() {
  if (!isSave.value) {
    isSave.value = true
    return
  }
  if (!saveQAIds.value?.length) {
    message.warning('请选择要保存的对话')
    return
  }

  const filterArr = chatDataList.value.filter(item => saveQAIds.value.includes(item.id))
  replyToMain(JSON.stringify(filterArr))
  windowManager.closeWindow()
}

function replyToMain(data: string) {
  windowManager.emitTo({
    from: WINDOW_NAME.MULTICHAT,
    target: WINDOW_NAME.MAIN,
    type: 'chatContentSave',
    data: { ...replyBaseData, data },
  })
}

function handleScrollToBottom() {
  if (messagingId.value) {
    nextTick(() => {
      document.querySelector(`.chat-list .listitem[data-id='${messagingId.value}']`)?.scrollIntoView({ behavior: 'instant', block: 'end' })
    })
  }
}

function handleEnd() {
  updateMessagingChat('timestamp', Date.now())
  isThinking.value && updateMessagingChat('answer', '已取消')
  isThinking.value = false
  messagingId.value = ''
  controller.abort()
  controller = null
}

function createSSE(url: string, query: string) {
  const queryLst = []
  if (chatType === 'multi') {
    chatDataList.value.forEach((item: chatItem) => {
      queryLst.push({ role: 'user', content: item.query })
      queryLst.push({ role: 'assistant', content: item.answer })
    })
    queryLst.push({ role: 'user', content: query })
  }
  if (chatType === 'file') {
    queryLst.push({ role: 'user', content: fileInfo.value.content })
    queryLst.push({ role: 'user', content: query })
  }

  const queryData = {
    messages: queryLst,
    stream: true,
    ...(model ? { model } : null)
  }

  controller = sseRequest.post(
    url, 
    queryData, 
    (res) => {
      console.log('res', res)
      if (!res) return;

      if (res.data === '[DONE]') {
        handleEnd()
        return
      }

      try {
        const content = get(JSON.parse(res.data), ['choices', 0, 'delta', 'content'])
        if (content) {
          isThinking.value = false
          updateMessagingChat('answer', content)
          handleScrollToBottom()
        }
      } catch (error) {
        console.error('Failed to parse SSE data:', error, res.data)
      }
    },
    () => {
      handleEnd() // 错误处理
      updateMessagingChat('answer', '异常无法响应')
    },
  )
}

function handleSend() {
  const promptValue = prompt.value
  prompt.value = ''
  setTimeout(() => {
    if (isMultiTurnLimit.value)
      return
    if (messagingId.value || isThinking.value) {
      console.log('messagingId', messagingId.value)
      message.warning('请等待上一次对话结束')
      return
    }
    if (!promptValue.trim()) {
      message.warning('请输入指令')
      return
    }
    createSSE(`${getAPIBaseURL()}/rpa-ai-service/v1/chat/completions`, promptValue)
    isThinking.value = true
    const responseId = nanoid()
    messagingId.value = responseId
    const time = (chatDataList.value[chatDataList.value.length - 1]?.time || 0) + 1 // 当前轮次
    chatDataList.value.push({
      id: responseId,
      timestamp: 0,
      time,
      query: promptValue,
      answer: '',
    })
    handleScrollToBottom()
  })
}
function handlePresetClick(item: string) {
  prompt.value = item
  handleSend()
}

function handlePreview() {
  couldPreview.value && togglePreview(true)
}

function handleClose() {
  replyToMain('')
  windowManager.closeWindow()
}

onBeforeUnmount(() => clearAllData())
</script>

<template>
  <div class="chatModal">
    <Preview
      v-show="showPreview"
      class="mr-2.5"
      :file-info="fileInfo"
      @close="togglePreview(false)"
    />
    <div class="chat-main flex-1 bg-bg-elevated relative">
      <component :is="ChatBgSvg" class="absolute top-0 left-0 w-full" />
      <div class="chat-header relative flex items-center pr-[18px]">
        <div class="drag flex-1 px-[18px] pt-[18px]">{{ title }}</div>
        <CloseOutlined @click="handleClose" />
      </div>
      <div class="chat-content relative">
        <div v-if="chatType === 'file'" class="chat-list-preset">
          <div class="basic preset-file flex items-center gap-2.5" @click="handlePreview">
            <img :width="40" :height="40" :src="FILE_TYPE_IMG[fileInfo.suffix]">
            <a-tooltip :title="fileInfo.path">
              {{ fileInfo.name }}
            </a-tooltip>
            <a-tooltip v-if="couldPreview" title="查看文档">
              <ZoomInOutlined />
            </a-tooltip>
          </div>
          <div v-if="chatDataList?.length === 0">
            <div v-for="(item, index) in presetList" :key="index">
              <span class="basic preset-item" @click="handlePresetClick(item)">
                {{ item }}
                <RightOutlined style="margin-left: 5px;" />
              </span>
            </div>
          </div>
        </div>
        <div v-if="chatType === 'multi' && chatDataList?.length === 0" class="chat-list-empty">
          <div class="title">
            你好，我可以为你做什么
          </div>
          <div class="flex items-center gap-[3px] text-text-tertiary">
            <span>内容由</span>
            <img width="16" height="16" src="@/assets/img/xinghuo.png" alt="xinghuo">
            <span>星火大模型生成</span>
          </div>
        </div>
        <div v-if="chatDataList?.length > 0" class="chat-list">
          <div v-for="item in chatDataList" :key="item.id" :data-id="item.id" class="listitem">
            <a-checkbox
              v-if="isSave"
              style="margin-right: 5px;"
              @change="(e) => handleCheckboxChange(e.target.checked, item.id)"
            />
            <div
              :style="`width: 100%;${isSave ? 'padding: 10px; border: 1px solid #d9d9d9d9; border-radius: 4px;' : ''}`"
            >
              <div class="question">
                <span class="promptText">{{ item.query }}</span>
              </div>
              <div class="answer">
                <span v-if="item.answer" class="message" v-html="item.answer" />
                <span v-if="isThinking && messagingId === item.id" class="thinking">
                  <LoadingOutlined />思考中...
                </span>
              </div>
              <a-button
                v-if="messagingId === item.id"
                size="small"
                class="stopBtn"
                :icon="h(StopOutlined)"
                type="primary"
                ghost
                @click="handleEnd"
              >
                停止响应
              </a-button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isMultiTurnLimit" class="limitTip">
        {{ `———————— 最多对话${limitTurns}轮 ————————` }}
      </div>
      <div class="chat-footer">
        <a-input
          v-if="!isSave"
          v-model:value="prompt"
          :placeholder="isMultiTurnLimit ? '已达到最大对话轮次，请选择需要保存的对话结果' : '输入指令，让AI帮你完成'"
          :disabled="isMultiTurnLimit"
          class="promptInput"
          @press-enter="handleSend"
        >
          <template #suffix>
            <img width="24" height="24" src="@/assets/img/promptSend.png" alt="" @click="handleSend">
          </template>
        </a-input>
        <a-button v-else @click="handleCancel">
          取消
        </a-button>
        <a-tooltip title="保存为输出参数" placement="topRight">
          <a-button v-if="showSave" :type="isSave ? 'primary' : 'default'" :icon="h(SaveOutlined)" class="saveBtn"
            @click="handleSave">
            {{ isSave ? '保存' : '' }}
          </a-button>
        </a-tooltip>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@import './index.scss';
</style>
