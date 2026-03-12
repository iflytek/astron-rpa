<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'

import { openclawChatCompletions } from '@/api/openclaw'
import { generateUUID } from '@/utils/common'

type ChatRole = 'user' | 'assistant' | 'system'

type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  createdAt: number
}

const props = withDefaults(defineProps<{
  title?: string
  placeholder?: string
  openclawToken?: string
}>(), {
  title: 'Astron助理',
  placeholder: '输入消息，回车发送',
})

const openclawToken = props.openclawToken || import.meta.env.VITE_OPENCLAW_TOKEN

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
const errorText = ref<string>('')
const scrollerRef = ref<HTMLElement | null>(null)

const canSend = computed(() => !sending.value && input.value.trim().length > 0)

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

async function send() {
  const text = input.value.trim()
  if (!text || sending.value)
    return

  errorText.value = ''
  sending.value = true
  input.value = ''

  const userMsg: ChatMessage = {
    id: generateUUID(),
    role: 'user',
    content: text,
    createdAt: Date.now(),
  }
  messages.value.push(userMsg)

  try {
    const assistantText = await openclawChatCompletions({
      token: openclawToken,
      messages: [
        { role: 'system', content: '你是 Astron 助理，帮助用户使用 Astron RPA 设计器与执行器。回答用中文，尽量给出可执行的步骤。' },
        ...messages.value
          .filter(m => m.role !== 'system')
          .map(m => ({ role: m.role, content: m.content })),
      ],
    })

    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: assistantText || '（openclaw 没有返回内容）',
      createdAt: Date.now(),
    })
  }
  catch (e: any) {
    errorText.value = e?.message || '发送失败'
    messages.value.push({
      id: generateUUID(),
      role: 'assistant',
      content: '（请求 openclaw 失败，请确认 openclaw gateway 已在本机启动，并监听 18789 端口）',
      createdAt: Date.now(),
    })
  }
  finally {
    sending.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    void send()
  }
}
</script>

<template>
  <section class="astron-assistant h-full w-full bg-[#fff] dark:bg-[#1d1d1d] flex flex-col">
    <div class="px-3 py-2 border-b border-[#ecedf4] dark:border-[#141414] flex items-center gap-2">
      <span class="font-semibold text-[14px]">{{ title }}</span>
      <span v-if="sending" class="text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">正在发送…</span>
      <span v-if="errorText" class="text-[12px] text-error truncate">{{ errorText }}</span>
    </div>

    <div ref="scrollerRef" class="flex-1 overflow-auto px-3 py-2 space-y-2">
      <div
        v-for="m in messages"
        :key="m.id"
        class="flex"
        :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[92%] rounded-[10px] px-3 py-2 text-[13px] leading-[20px] whitespace-pre-wrap break-words"
          :class="m.role === 'user'
            ? 'bg-primary text-white'
            : 'bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]'"
        >
          {{ m.content }}
        </div>
      </div>
    </div>

    <div class="p-3 border-t border-[#ecedf4] dark:border-[#141414]">
      <a-textarea
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

