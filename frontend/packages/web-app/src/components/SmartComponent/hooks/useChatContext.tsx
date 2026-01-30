import { message, Typography } from 'ant-design-vue'
import type { BubbleProps, XRequestCallbacks } from 'ant-design-x-vue'
import { useXAgent, useXChat, XRequest } from 'ant-design-x-vue'
import markdownit from 'markdown-it'
import { computed, inject, provide, ref } from 'vue'

import { codeToMeta } from '@/api/component'
import { getAPIBaseURL } from '@/api/http/env'

import { SMART_CODE_BLOCK_REGEX, SMART_CODE_START_REGEX } from '../config/constants'
import type { DocNode, Message, MessageInput, SmartComp } from '../types'
import type { MessageOutput } from '../types/index'
import { generateComponentForm } from '../utils'
import { isAssistantMessage, isUserMessage, parseChatContent } from '../utils/chatParser'

import type { SmartCompContext } from '.'

// 创建聊天上下文
export function useChatContext(smartComp: SmartCompContext) {
  const promptItmes = [
    {
      key: 'web_auto',
      icon: 'globe',
      label: '网页自动化',
      description: '从网页抓取数据并保存到 Excel',
    },
    {
      key: 'data_process',
      icon: 'sheet',
      label: '数据处理',
      description: '从 Excel 读取数据并转换为 JSON 格式',
    },
  ]

  const md = markdownit({ html: true, breaks: true })

  const rolesAsFunction = (bubbleData: BubbleProps) => {
    switch (bubbleData.role) {
      case 'assistant':
        return {
          placement: 'start',
          typing: { step: 5, interval: 20 },
        } as const
      case 'user':
        return {
          placement: 'end',
        } as const
      default:
        return { }
    }
  }

  const senderLoading = ref(false)

  const BASE_URL = getAPIBaseURL()
  const PATH = '/rpa-ai-service/smart/chat/stream'
  // const MODEL = 'gpt-3.5-turbo';

  const exampleRequest = XRequest({
    baseURL: BASE_URL + PATH,
    // model: MODEL,
  })

  function createRequest(message: MessageInput, callbacks?: XRequestCallbacks<MessageOutput>) {
    const { onSuccess, onUpdate, onError } = callbacks
    exampleRequest.value.create(message, { onSuccess, onUpdate, onError })
  }

  // Agent for request
  const [agent] = useXAgent<MessageInput | MessageOutput, { message: MessageInput }, MessageOutput>({
    request: async ({ message }, { onSuccess, onUpdate, onError }) => {
      senderLoading.value = true

      let generateStartTime = null
      let fullText = ''
      let compMeta

      createRequest(message, {
        onSuccess: () => {},
        onUpdate: async (chunk) => {
          try {
            if ((chunk as any).data === ' [DONE]') {
              const { renderContent, extractedCode } = extractCodeAndText(fullText)

              if (extractedCode) {
                // 计算组件生成耗时（秒）
                let duration: number | undefined
                if (generateStartTime !== null) {
                  duration = (Date.now() - generateStartTime) / 1000
                }

                try {
                  compMeta = await codeToMeta({ code: extractedCode }) || {}
                }
                catch (error) {
                  console.error('解析组件元数据失败:', error)
                  compMeta = {}
                }

                const nextVersionNumber = smartComp.getNextVersionNumber()
                const finalContent = toMessageOutput(renderContent, {
                  status: 'completed',
                  smartCode: extractedCode,
                  version: nextVersionNumber,
                  duration,
                })
                onUpdate(finalContent)
                onSuccess([finalContent])

                const newVersion: SmartComp = {
                  ...generateComponentForm(compMeta, smartComp.editingSmartComp.value?.outputList),
                  version: nextVersionNumber,
                  key: smartComp.editingSmartComp.value?.key,
                  alias: smartComp.editingSmartComp.value?.alias || compMeta.title,
                  smartType: smartComp.smartType.value,
                  smartCode: extractedCode,
                  createTime: Date.now(), // 记录组件生成时间
                  detail: {
                    packages: [],
                    elements: [],
                    chatHistory: realMsgs.value.map(({ role, content }) => ({
                      role,
                      content,
                    })),
                  },
                } as SmartComp

                smartComp.addNewVersion(newVersion)
              }
              else {
                const finalContent = toMessageOutput(renderContent)
                onSuccess([finalContent])

                const currentChatHistory = realMsgs.value.map(({ role, content }) => ({
                  role,
                  content,
                }))
                smartComp.updateCurrentVersionChatHistory(currentChatHistory)
              }

              senderLoading.value = false
            }
            else {
              try {
                const data = JSON.parse((chunk as any).data)
                const deltaText = data.choices[0]?.delta?.content || ''
                fullText += deltaText

                const { renderContent, isGeneratingCode, extractedCode } = extractCodeAndText(fullText)

                // 开始生成代码,记录开始时间
                if (isGeneratingCode && generateStartTime === null) {
                  generateStartTime = Date.now()
                }

                let currentContent: MessageOutput
                if (isGeneratingCode || extractedCode) {
                  currentContent = toMessageOutput(renderContent, {
                    status: 'generating',
                  })
                }
                else {
                  currentContent = toMessageOutput(renderContent)
                }
                onUpdate(currentContent)
              }
              catch (error) {
                console.error('解析流式数据失败:', error)
              }
            }
          }
          catch (error) {
            console.error('处理消息失败:', error)
            senderLoading.value = false
          }
        },
        onError: (error) => {
          onError(error)
          senderLoading.value = false
        },
      })
    },
  })

  // Chat messages
  const { onRequest, messages } = useXChat({
    agent: agent.value,
    requestPlaceholder: toMessageOutput('正在请求...'),
    requestFallback: toMessageOutput('请求失败，请稍后再试。'),
  })

  // 渲染消息
  function messageRender(message: Message) {
    let text = ''
    isAssistantMessage(message) && (text = message.content.text)
    isUserMessage(message) && (text = message.content.user)

    return (
      <Typography>
        <div v-html={md.render(text)} />
      </Typography>
    )
  }

  function toMessageOutput(text: string, extra?: Partial<MessageOutput>): MessageOutput {
    return {
      text,
      ...extra,
    }
  }

  function extractCodeAndText(fullText: string) {
    const codeMatch = fullText.match(SMART_CODE_BLOCK_REGEX)
    const extractedCode = codeMatch?.[1]?.trim() ?? ''

    const hasStartMarker = SMART_CODE_START_REGEX.test(fullText)
    const isGeneratingCode = hasStartMarker && !extractedCode

    let renderContent = fullText
    if (isGeneratingCode) {
      renderContent = fullText.replace(SMART_CODE_START_REGEX, '').trim()
    }
    else if (extractedCode) {
      renderContent = fullText.replace(SMART_CODE_BLOCK_REGEX, '').trim()
    }

    return {
      extractedCode,
      renderContent,
      isGeneratingCode,
    }
  }

  function sendChat(text: DocNode) {
    // 解析TiptapEditor的JSON格式为服务端需要的格式
    const parsedContent = parseChatContent(text)
    console.log('解析后的内容:', parsedContent)

    if (!smartComp.smartType.value) {
      // 根据是否有 ElementNode 节点设置 smartType
      if (parsedContent.elements && parsedContent.elements.length > 0) {
        smartComp.smartType.value = 'web_auto'
      }
      else {
        smartComp.smartType.value = 'data_process'
      }
    }

    const chatHistory = smartComp.editingSmartComp.value?.detail?.chatHistory || []

    onRequest({
      sceneCode: `smart_${smartComp.smartType.value}`,
      user: parsedContent.user,
      elements: parsedContent.elements,
      chatHistory,
    } as MessageInput)
  }

  function fixCode(errorLog: RPA.LogItem & Record<'formattedContent', string>) {
    console.log('修复错误:', errorLog)

    if (senderLoading.value) {
      message.warning('智能组件生成中，请稍后再试')
      return
    }

    onRequest({
      sceneCode: `smart_${smartComp.smartType.value}`,
      user: `修复${errorLog.formattedContent}`,
      needFix: true,
      fixInfo: {
        consoleLog: errorLog.content,
        traceback: errorLog.error_traceback,
      },
      currentCode: smartComp.editingSmartComp.value?.smartCode || '',
    } as MessageInput)
  }

  const realMsgs = computed(() => {
    // 这里的 status 是组件自身内部类型，与自定义的 MessageStatus 不同
    // type MessageStatus = 'local' | 'loading' | 'success' | 'error';
    return messages.value.map(({ id, message, status }) => ({
      key: id,
      loading: status === 'loading',
      role: status === 'local' ? 'user' : 'assistant',
      content: message,
      messageRender: () => messageRender({ role: status === 'local' ? 'user' : 'assistant', content: message }),
    }) as Message)
  })

  function restoreChatHistory(chatHistory: Message[]) {
    if (!chatHistory || chatHistory.length === 0) {
      return
    }

    messages.value = []
    chatHistory.forEach((msg, index) => {
      messages.value.push({
        id: `restored_${index}`,
        message: msg.content,
        status: msg.role === 'user' ? 'local' : 'success',
      })
    })
  }

  return {
    realMsgs,
    senderLoading,
    promptItmes,
    rolesAsFunction,
    sendChat,
    fixCode,
    restoreChatHistory,
  }
}

export type ChatContext = ReturnType<typeof useChatContext>

export function provideChatContext(context: ChatContext) {
  provide('chat', context)
}

// 聊天功能注入
export function injectChatContext() {
  const context = inject<ChatContext>('chat')
  if (!context) {
    throw new Error('injectChatContext must be used within SmartComponent Index component')
  }
  return context
}
