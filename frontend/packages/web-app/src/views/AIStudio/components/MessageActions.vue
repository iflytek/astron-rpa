<script setup lang="ts">
import { Copy, Check } from 'lucide-vue-next'
import { ref } from 'vue'

const props = defineProps<{
  messageId: string
  content: string
  tone?: 'user' | 'assistant'
}>()

const copied = ref(false)

async function handleCopy() {
  const normalized = props.content.trim()
  if (!normalized) return

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(normalized)
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = normalized
      textarea.setAttribute('readonly', 'true')
      textarea.style.position = 'absolute'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }

    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1400)
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}
</script>

<template>
  <div
    class="message-actions"
    :class="tone ? `is-${tone}` : ''"
    :data-testid="`message-actions-${messageId}`"
  >
    <button
      class="message-action"
      type="button"
      :aria-label="copied ? '已复制消息' : '复制消息'"
      :title="copied ? '已复制' : '复制'"
      :data-testid="`message-action-copy-${messageId}`"
      @click="handleCopy"
    >
      <Check v-if="copied" class="h-3.5 w-3.5" />
      <Copy v-else class="h-3.5 w-3.5" />
    </button>
  </div>
</template>

<style scoped>
.message-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s;
  margin-top: 4px;
}

.message-actions.is-user {
  justify-content: flex-end;
}

.message-actions.is-assistant {
  justify-content: flex-start;
}

/* 父容器 hover 时显示 */
:deep(.chat-row__stack:hover) .message-actions,
:deep(.flex:hover) .message-actions {
  opacity: 1;
}

.message-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.5);
  transition: all 0.15s;
}

.message-action:hover {
  background: white;
  border-color: rgba(0, 0, 0, 0.12);
  color: rgba(0, 0, 0, 0.7);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-action:active {
  transform: translateY(0);
}
</style>
