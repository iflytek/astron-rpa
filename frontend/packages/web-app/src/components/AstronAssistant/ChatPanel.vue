<script setup lang="ts">
import markdownit from 'markdown-it'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import type { OpenClawToolEvent } from '@/api/openclaw'
import { openclawChatCompletions } from '@/api/openclaw'
import { generateUUID } from '@/utils/common'

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

const props = withDefaults(defineProps<{
  title?: string
  placeholder?: string
  openclawToken?: string
}>(), {
  title: 'Astron助理',
  placeholder: '请输入消息，回车发送',
})

const openclawToken = ref<string | undefined>(props.openclawToken || import.meta.env.VITE_OPENCLAW_TOKEN)

// 在 Electron 环境下，尝试从主进程读取 OpenClaw token
onMounted(async () => {
  if (!openclawToken.value && window.electron?.openclaw?.getToken) {
    try {
      const token = await window.electron.openclaw.getToken()
      if (token) {
        openclawToken.value = token
        console.log('OpenClaw token loaded from Electron')
      }
    } catch (err) {
      console.warn('Failed to load OpenClaw token from Electron:', err)
    }
  }
})

const messages = ref<ChatMessage[]>([
  {
    id: generateUUID(),
    role: 'assistant',
    content: '我是 Astron助理。你可以直接问我如何设计流程、排查执行问题，或让本地 openclaw 帮你分析。',
    createdAt: Date.now(),
  },
])

const input = ref('')
const sending = ref(false)
const errorText = ref('')
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
  const el = scrollerRef.value
  if (!el)
    return
  el.scrollTop = el.scrollHeight
}

watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

function upsertToolMessage(event: OpenClawToolEvent) {
  const index = messages.value.findIndex(
    message => message.role === 'tool' && message.toolCallId === event.toolCallId,
  )

  const nextContent = event.output ?? (index >= 0 && messages.value[index].role === 'tool'
    ? messages.value[index].content
    : '')

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
  const text = input.value.trim()
  if (!text || sending.value)
    return

  errorText.value = ''
  sending.value = true
  input.value = ''
  textareaKey.value += 1

  messages.value.push({
    id: generateUUID(),
    role: 'user',
    content: text,
    createdAt: Date.now(),
  })

  try {
    const result = await openclawChatCompletions({
      token: openclawToken.value,
      onToolEvent: upsertToolMessage,
      messages: [
        { role: 'system', content: '你是 Astron 助理，帮助用户使用 Astron RPA 设计器与执行器。回答请使用中文，并尽量给出可执行的步骤。' },
        ...messages.value
          .filter(message => message.role !== 'tool')
          .map(message => ({ role: message.role, content: message.content })),
      ],
    })

    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: result.text || '（openclaw 没有返回内容）',
      createdAt: Date.now(),
    })
  }
  catch (error: any) {
    const reason = error?.message || '发送失败'
    errorText.value = reason
    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: `（请求 openclaw 失败：${reason}。请确认 openclaw gateway 已在本机启动，并监听 18789 端口）`,
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
  <section class="astron-assistant h-full min-h-0 w-full bg-[#fff] dark:bg-[#1d1d1d] flex flex-col overflow-hidden rounded-[12px]">
    <div class="shrink-0 px-3 py-2 border-b border-[#ecedf4] dark:border-[#141414] flex items-center gap-2">
      <span class="font-semibold text-[14px]">{{ title }}</span>
      <span v-if="sending" class="text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">正在发送...</span>
      <span v-if="errorText" class="text-[12px] text-error truncate">{{ errorText }}</span>
    </div>

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
          class="w-full max-w-[92%] rounded-[14px] border border-[#ece7e3] bg-[#fbfaf8] dark:border-[rgba(255,255,255,0.1)] dark:bg-[rgba(255,255,255,0.04)] px-4 py-3"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <div class="text-[13px] font-medium text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.88)]">
                {{ message.toolName }}
              </div>
              <div class="mt-1 text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">
                {{ message.toolStatus === 'completed' ? 'Completed' : 'Running...' }}
              </div>
            </div>
            <div
              class="h-2.5 w-2.5 rounded-full"
              :class="message.toolStatus === 'completed' ? 'bg-[#52c41a]' : 'bg-[#faad14]'"
            />
          </div>

          <pre
            v-if="message.content"
            class="mt-3 max-h-[220px] overflow-auto rounded-[10px] bg-[#f4f1ed] dark:bg-[rgba(0,0,0,0.2)] px-3 py-2 text-[12px] leading-[18px] whitespace-pre-wrap break-words text-[rgba(0,0,0,0.72)] dark:text-[rgba(255,255,255,0.78)]"
          >{{ message.content }}</pre>
        </div>
      </div>
    </div>

    <div class="shrink-0 p-3 border-t border-[#ecedf4] dark:border-[#141414] bg-[#fff] dark:bg-[#1d1d1d]">
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
          发送
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
