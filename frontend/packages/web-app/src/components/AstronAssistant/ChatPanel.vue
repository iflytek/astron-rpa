<script setup lang="ts">
import { SettingOutlined } from '@ant-design/icons-vue'
import markdownit from 'markdown-it'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import type { OpenClawToolEvent } from '@/api/openclaw'
import { openclawChatCompletions } from '@/api/openclaw'
import { generateUUID } from '@/utils/common'
import IMConnectPanel from './IMConnectPanel.vue'

type ChatMessage =
  | {
    id: string
    role: 'user' | 'assistant'
    content: string
    createdAt: number
  }
  | {
    id: string
    role: 'tool'
    content: string
    createdAt: number
    toolCallId: string
    toolName: string
    toolStatus: 'running' | 'completed'
  }

const text = {
  title: 'Astron \u52a9\u7406',
  placeholder: '\u8bf7\u8f93\u5165\u6d88\u606f\uff0c\u56de\u8f66\u53d1\u9001',
  intro: '\u6211\u662f Astron \u52a9\u7406\u3002\u4f60\u53ef\u4ee5\u76f4\u63a5\u95ee\u6211\u5982\u4f55\u8bbe\u8ba1\u6d41\u7a0b\u3001\u6392\u67e5\u6267\u884c\u95ee\u9898\uff0c\u6216\u8ba9\u672c\u5730 openclaw \u5e2e\u4f60\u5206\u6790\u3002',
  sending: '\u6b63\u5728\u53d1\u9001...',
  send: '\u53d1\u9001',
  emptyResponse: '\u0028openclaw \u6ca1\u6709\u8fd4\u56de\u5185\u5bb9\u0029',
  sendFailed: '\u53d1\u9001\u5931\u8d25',
  requestFailedPrefix: '\u0028\u8bf7\u6c42 openclaw \u5931\u8d25\uff09',
  requestFailedSuffix: '\u3002\u8bf7\u786e\u8ba4 openclaw gateway \u5df2\u5728\u672c\u673a\u542f\u52a8\uff0c\u5e76\u76d1\u542c 18789 \u7aef\u53e3\u3002',
  toolCompleted: 'Completed',
  toolRunning: 'Running...',
  systemPrompt: '\u4f60\u662f Astron \u52a9\u7406\uff0c\u5e2e\u52a9\u7528\u6237\u4f7f\u7528 Astron RPA \u8bbe\u8ba1\u5668\u4e0e\u6267\u884c\u5668\u3002\u56de\u7b54\u8bf7\u4f7f\u7528\u4e2d\u6587\uff0c\u5e76\u5c3d\u91cf\u7ed9\u51fa\u53ef\u6267\u884c\u7684\u6b65\u9aa4\u3002',
} as const

const props = withDefaults(defineProps<{
  title?: string
  placeholder?: string
  openclawToken?: string
}>(), {
  title: 'Astron 助理',
  placeholder: '请输入消息，回车发送',
})

const openclawToken = ref<string | undefined>(props.openclawToken || import.meta.env.VITE_OPENCLAW_TOKEN)
const electronBridge = (window as any).electron

onMounted(async () => {
  if (!openclawToken.value && electronBridge?.openclaw?.getToken) {
    try {
      const token = await electronBridge.openclaw.getToken()
      if (token) {
        openclawToken.value = token
        console.log('OpenClaw token loaded from Electron')
      }
    }
    catch (err) {
      console.warn('Failed to load OpenClaw token from Electron:', err)
    }
  }
})

const messages = ref<ChatMessage[]>([
  {
    id: generateUUID(),
    role: 'assistant',
    content: text.intro,
    createdAt: Date.now(),
  },
])

const input = ref('')
const sending = ref(false)
const errorText = ref('')
const showImConfig = ref(false)
const scrollerRef = ref<HTMLElement | null>(null)
const textareaKey = ref(0)
const md = markdownit({
  breaks: true,
  linkify: true,
})

const canSend = computed(() => !sending.value && input.value.trim().length > 0)

function renderMarkdown(content: string) {
  return md.render(content || '')
}

function scrollToBottom() {
  const element = scrollerRef.value
  if (!element)
    return
  element.scrollTop = element.scrollHeight
}

watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

function upsertToolMessage(event: OpenClawToolEvent) {
  const index = messages.value.findIndex(message => message.role === 'tool' && message.toolCallId === event.toolCallId)
  const nextContent = event.output ?? (index >= 0 && messages.value[index].role === 'tool' ? messages.value[index].content : '')

  const nextMessage: ChatMessage = {
    id: index >= 0 ? messages.value[index].id : generateUUID(),
    role: 'tool',
    content: nextContent,
    createdAt: index >= 0 ? messages.value[index].createdAt : event.ts,
    toolCallId: event.toolCallId,
    toolName: event.name,
    toolStatus: event.phase === 'result' ? 'completed' : 'running',
  }

  if (index >= 0)
    messages.value.splice(index, 1, nextMessage)
  else
    messages.value.push(nextMessage)
}

async function send() {
  const textToSend = input.value.trim()
  if (!textToSend || sending.value)
    return

  errorText.value = ''
  sending.value = true
  input.value = ''
  textareaKey.value += 1

  messages.value.push({
    id: generateUUID(),
    role: 'user',
    content: textToSend,
    createdAt: Date.now(),
  })

  try {
    const result = await openclawChatCompletions({
      token: openclawToken.value,
      onToolEvent: upsertToolMessage,
      messages: [
        { role: 'system', content: text.systemPrompt },
        ...messages.value
          .filter(message => message.role !== 'tool')
          .map(message => ({ role: message.role, content: message.content })),
      ],
    })

    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: result.text || text.emptyResponse,
      createdAt: Date.now(),
    })
  }
  catch (error: any) {
    const reason = error?.message || text.sendFailed
    errorText.value = reason
    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: `${text.requestFailedPrefix}${reason}${text.requestFailedSuffix}`,
      createdAt: Date.now(),
    })
  }
  finally {
    sending.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void send()
  }
}
</script>

<template>
  <section class="astron-assistant h-full min-h-0 w-full rounded-[12px] bg-[#fff] dark:bg-[#1d1d1d] flex flex-col overflow-hidden">
    <div class="shrink-0 px-3 py-2 border-b border-[#ecedf4] dark:border-[#141414] flex items-center gap-2">
      <span class="font-semibold text-[14px]">{{ title }}</span>
      <span v-if="sending" class="text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">{{ text.sending }}</span>
      <span v-if="errorText" class="min-w-0 flex-1 truncate text-[12px] text-error">{{ errorText }}</span>
      <a-button type="text" shape="circle" @click="showImConfig = true">
        <template #icon>
          <SettingOutlined />
        </template>
      </a-button>
    </div>

    <IMConnectPanel v-model:open="showImConfig" />

    <div ref="scrollerRef" class="flex-1 min-h-0 overflow-auto px-3 py-3 space-y-3">
      <div
        v-for="message in messages"
        :key="message.id"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          v-if="message.role !== 'tool'"
          class="max-w-[92%] rounded-[12px] px-3 py-2 text-[13px] leading-[20px] break-words"
          :class="message.role === 'user'
            ? 'bg-primary/10 border border-primary/20 text-[rgba(0,0,0,0.85)] dark:text-white'
            : 'bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]'"
        >
          <div class="assistant-markdown" v-html="renderMarkdown(message.content)" />
        </div>

        <div
          v-else
          class="w-full max-w-[92%] rounded-[14px] border border-[#ece7e3] bg-[#fbfaf8] px-4 py-3 dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(255,255,255,0.04)]"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <div class="text-[13px] font-medium text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.88)]">
                {{ message.toolName }}
              </div>
              <div class="mt-1 text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
                {{ message.toolStatus === 'completed' ? text.toolCompleted : text.toolRunning }}
              </div>
            </div>
            <div class="h-2.5 w-2.5 rounded-full" :class="message.toolStatus === 'completed' ? 'bg-[#52c41a]' : 'bg-[#faad14]'" />
          </div>

          <pre
            v-if="message.content"
            class="mt-3 max-h-[220px] overflow-auto rounded-[10px] bg-[#f4f1ed] px-3 py-2 text-[12px] leading-[18px] whitespace-pre-wrap break-words text-[rgba(0,0,0,0.72)] dark:bg-[rgba(0,0,0,0.2)] dark:text-[rgba(255,255,255,0.78)]"
          >{{ message.content }}</pre>
        </div>
      </div>
    </div>

    <div class="shrink-0 border-t border-[#ecedf4] bg-[#fff] p-3 dark:border-[#141414] dark:bg-[#1d1d1d]">
      <a-textarea
        :key="textareaKey"
        v-model:value="input"
        :placeholder="placeholder"
        :auto-size="{ minRows: 2, maxRows: 6 }"
        :disabled="sending"
        @keydown="handleKeydown"
      />
      <div class="mt-2 flex justify-end">
        <a-button type="primary" :disabled="!canSend" :loading="sending" @click="send">
          {{ text.send }}
        </a-button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.assistant-markdown {
  word-break: break-word;
}

.assistant-markdown :deep(p) {
  margin: 0 0 8px;
}

.assistant-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-markdown :deep(ul),
.assistant-markdown :deep(ol) {
  margin: 0 0 8px;
  padding-left: 20px;
}

.assistant-markdown :deep(li + li) {
  margin-top: 4px;
}

.assistant-markdown :deep(pre) {
  overflow: auto;
  margin: 8px 0;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f4f1ed;
  font-size: 12px;
  line-height: 18px;
}

.assistant-markdown :deep(code) {
  padding: 1px 4px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.06);
  font-size: 12px;
}

.assistant-markdown :deep(pre code) {
  padding: 0;
  background: transparent;
}

.assistant-markdown :deep(blockquote) {
  margin: 8px 0;
  padding-left: 12px;
  border-left: 3px solid #d8dbe8;
  color: rgba(0, 0, 0, 0.6);
}

.assistant-markdown :deep(a) {
  color: #1677ff;
  text-decoration: underline;
}

.assistant-markdown :deep(table) {
  width: 100%;
  margin: 8px 0;
  border-collapse: collapse;
  font-size: 12px;
}

.assistant-markdown :deep(th),
.assistant-markdown :deep(td) {
  padding: 6px 8px;
  border: 1px solid #e5e7ef;
  text-align: left;
}

.dark .assistant-markdown :deep(pre) {
  background: rgba(0, 0, 0, 0.2);
}

.dark .assistant-markdown :deep(code) {
  background: rgba(255, 255, 255, 0.08);
}

.dark .assistant-markdown :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.62);
}

.dark .assistant-markdown :deep(th),
.dark .assistant-markdown :deep(td) {
  border-color: rgba(255, 255, 255, 0.12);
}
</style>
