<script setup lang="ts">
import { CloseOutlined, LoadingOutlined, RightOutlined, SaveOutlined, StopOutlined, ZoomInOutlined } from '@ant-design/icons-vue'
import { invoke } from '@tauri-apps/api/tauri'
import { message } from 'ant-design-vue'
import { nanoid } from 'nanoid'
import PDF from 'pdf-vue3'
import { computed, h, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { getBaseURL } from '@/api/http/env'
import { sseRequest } from '@/api/sse'
import { utilsManager, windowManager } from '@/platform'
import type { chatItem } from '@/types/chat'

const FILE_TYPE_IMG = {
  doc: new URL('../../assets/img/doc.png', import.meta.url).href,
  docx: new URL('../../assets/img/doc.png', import.meta.url).href,
  txt: new URL('../../assets/img/txt.png', import.meta.url).href,
  pdf: new URL('../../assets/img/pdf.png', import.meta.url).href,
}

let controller = null

const chatType = ref('multi') // 交互类型 multi:多轮对话,file:知识问答
const title = ref('AI Chat组件')
const showSave = ref(true) // 是否显示保存按钮
const limitTurns = ref(20) // 最大轮数
const isMultiTurnLimit = computed(() => chatDataList.value.length >= limitTurns.value) // 是否置灰输入框

const prompt = ref('')
const isThinking = ref(false) // 是否在思考中
const chatDataList = ref([]) // 回答信息
const messagingId = ref('') // 当前消息ID
const isSave = ref(false) // 是否在保存过程中
const saveQAIds = ref([]) // 保存的promptIds
const fileInfo = ref({
  path: '',
  name: '',
  suffix: '',
  content: '' as any, // 文件内容
  previewContent: '' as any, // 预览内容
}) // 文件信息
const presetList = ref([]) // 预设列表
const showPreview = ref(false) // 是否显示预览弹窗，默认不显示
const model = ref('deepseek-chat')

// 初始化信息
const targetInfo = new URL(location.href).searchParams
title.value = targetInfo.get('title') || 'AI Chat组件'
showSave.value = ['1', 1].includes(targetInfo.get('is_save'))
limitTurns.value = Number(targetInfo.get('max_turns')) || 20
presetList.value = targetInfo.get('questions')?.split('$-$') || []
const filePath = targetInfo.get('file_path')
if (filePath) {
  chatType.value = 'file'
  fileInfo.value.path = filePath
  fileInfo.value.name = filePath.split('\\').pop()
  fileInfo.value.suffix = filePath.split('.').pop()
  utilsManager.readFile(`AppData\\Roaming\\iflyrpa\\Cache\\chatData\\${fileInfo.value.name}`).then((res: any) => {
    fileInfo.value.previewContent = fileInfo.value.suffix === 'txt' ? new TextDecoder().decode(res) : res
  })
  title.value = '知识问答'
}
utilsManager.listenEvent('render-ready', (eventMsg) => {
  const msgObj = JSON.parse(eventMsg)
  const { content } = msgObj
  fileInfo.value.content = content
})

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
  invoke('page_handler', {
    operType: 'AISave',
    data: JSON.stringify(filterArr),
  }).then(() => {
    handleClose()
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

function createSSE(url, query) {
  const queryLst = []
  if (chatType.value === 'multi') {
    chatDataList.value.forEach((item: chatItem) => {
      queryLst.push({ role: 'user', content: item.query })
      queryLst.push({ role: 'assistant', content: item.answer })
    })
    queryLst.push({ role: 'user', content: query })
  }
  if (chatType.value === 'file') {
    queryLst.push({ role: 'user', content: fileInfo.value.content })
    queryLst.push({ role: 'user', content: query })
  }
  controller = new AbortController()
  sseRequest(url, chatType.value === 'multi'
    ? {
        messages: queryLst,
        model: model.value,
        stream: true,
      }
    : queryLst, { signal: controller.signal }, (res) => {
    if (res) {
    // if (res.data) {
      // const { data } = res // <$start>end<$end>
      // if (data.includes(' ')) {
      //   console.log('newData空格', data) // 后端返回的数据有空格
      // }
      // const newData = data.trim().replace(/<\$start>/g, '').replace(/<\$end>/g, '').replace(/\r\n/g, '<br/>').replace(/\\n/g, '<br/>').replace(/\n/g, '<br/>')
      console.log('res', res)
      const newData = JSON.parse(res.data).choices[0].delta.content
      console.log('newData', newData)
      if (newData.includes('start')) {
        return
      }
      // if (newData.includes('end')) {
      if (newData.includes('[DONE]')) {
        handleEnd()
        return
      }
      if (newData) {
        isThinking.value = false
        updateMessagingChat('answer', newData)
        handleScrollToBottom()
      }
    }
  }, () => {
    handleEnd() // 错误处理
    updateMessagingChat('answer', '异常无法响应')
  })
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
    // createSSE('http://localhost:8003/server/api/rpaai-service/chat', promptValue)
    createSSE(`${getBaseURL()}/rpa-ai-service/v1/chat/completions`, promptValue)
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
  if (['doc', 'docx'].includes(fileInfo.value.suffix))
    return false
  showPreview.value = true
}
function handleClose() {
  windowManager.closeWindow()
}

onMounted(() => {
  setTimeout(async () => { // 通知主进程渲染进程准备就绪
    await invoke('render_ready')
  }, 1000)
})
onBeforeUnmount(() => {
  clearAllData()
})
</script>

<template>
  <div data-tauri-drag-region class="chatModal">
    <div v-show="showPreview" data-tauri-drag-region class="chat-side">
      <CloseOutlined style="position: absolute; right: 15px; top: 10px; z-index: 999;" @click="() => { showPreview = false }" />
      <div v-if="fileInfo.suffix === 'txt'" class="txt">
        <p>{{ fileInfo.previewContent }}</p>
      </div>
      <div v-if="fileInfo.suffix === 'pdf'">
        <PDF :src="fileInfo.previewContent" />
      </div>
    </div>
    <div data-tauri-drag-region class="chat-main" :style="`width: ${showPreview ? '480px;' : '800px;'}`">
      <div class="chat-header">
        {{ title }}
        <CloseOutlined style="float: right;" @click="handleClose" />
      </div>
      <div class="chat-content">
        <div v-if="chatType === 'file'" class="chat-list-preset">
          <div class="basic preset-file" @click="handlePreview">
            <div class="filename">
              <img :width="40" :height="40" style="margin-right: 10px;" :src="FILE_TYPE_IMG[fileInfo.suffix]">
              <a-tooltip :title="fileInfo.path">
                {{ fileInfo.name }}
              </a-tooltip>
            </div>
            <a-tooltip v-if="!['doc', 'docx'].includes(fileInfo.suffix)" title="查看文档">
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
          <div class="copyright">
            内容由<img width="16" height="16" src="@/assets/img/xinghuo.png" alt="">星火大模型生成
          </div>
        </div>
        <div v-if="chatDataList?.length > 0" class="chat-list">
          <div v-for="item in chatDataList" :key="item.id" :data-id="item.id" class="listitem">
            <a-checkbox v-if="isSave" style="margin-right: 5px;" @change="(e) => handleCheckboxChange(e.target.checked, item.id)" />
            <div :style="`width: 100%;${isSave ? 'padding: 10px; border: 1px solid #d9d9d9d9; border-radius: 4px;' : ''}`">
              <div class="question">
                <span class="promptText">{{ item.query }}</span>
              </div>
              <div class="answer">
                <span v-if="item.answer" class="message" v-html="item.answer" />
                <span v-if="isThinking && messagingId === item.id" class="thinking">
                  <LoadingOutlined />思考中...
                </span>
              </div>
              <a-button v-if="messagingId === item.id" size="small" class="stopBtn" :icon="h(StopOutlined)" type="primary" ghost @click="handleEnd">
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
        <a-input v-if="!isSave" v-model:value="prompt" :placeholder="`${isMultiTurnLimit ? '已达到最大对话轮次，请选择需要保存的对话结果' : '输入指令，让AI帮你完成'}`" :disabled="isMultiTurnLimit" class="promptInput" @press-enter="handleSend">
          <template #suffix>
            <img width="24" height="24" src="@/assets/img/promptSend.png" alt="" @click="handleSend">
          </template>
        </a-input>
        <a-button v-else @click="handleCancel">
          取消
        </a-button>
        <a-tooltip title="保存为输出参数">
          <a-button v-if="showSave" :type="isSave ? 'primary' : 'default'" :icon="h(SaveOutlined)" class="saveBtn" @click="handleSave">
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
