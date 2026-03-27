<script setup lang="ts">
import { Users } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import ModalActionBar from './ModalActionBar.vue'
import ModalShell from './ModalShell.vue'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', ids: string[]): void
}>()

const selected = ref<string[]>([])

const candidates = [
  { id: 'code', name: '代码助手', short: '代', desc: '代码审查、接口修复、SQL 优化' },
  { id: 'doc', name: '文档助手', short: '文', desc: '报告撰写、摘要生成、资料整理' },
  { id: 'data', name: '数据分析师', short: '数', desc: '数据建模、趋势判断、图表建议' },
]

const canSubmit = computed(() => selected.value.length > 0)

function toggle(id: string) {
  selected.value = selected.value.includes(id)
    ? selected.value.filter(item => item !== id)
    : [...selected.value, id]
}

function handleSubmit() {
  if (!canSubmit.value)
    return
  emit('submit', selected.value)
}
</script>

<template>
  <ModalShell
    title="邀请助手加入会话"
    description="多助手将共享当前对话上下文"
    width-class="w-[420px]"
    close-label="关闭邀请助手"
    @close="emit('close')"
  >
    <div class="space-y-2 px-5 py-5">
      <button
        v-for="candidate in candidates"
        :key="candidate.id"
        :class="selected.includes(candidate.id)
          ? 'border-[var(--color-primary)] bg-[#F8F7FF] shadow-[0_0_0_3px_rgba(114,111,255,0.08)]'
          : 'border-[var(--ai-line)] bg-[var(--ai-surface-soft)] hover:border-[var(--color-primary)]/35'"
        class="flex w-full items-center gap-3 rounded-[16px] border px-3.5 py-3 text-left transition-all"
        @click="toggle(candidate.id)"
      >
        <div class="flex h-8 w-8 items-center justify-center rounded-[12px] bg-[#EEF2FF] text-[var(--color-primary)]">
          <span class="text-[12px] font-semibold">{{ candidate.short }}</span>
        </div>
        <div class="min-w-0 flex-1">
          <div class="text-[13px] font-medium text-black/82">
            {{ candidate.name }}
          </div>
          <div class="mt-0.5 truncate text-[11px] text-black/38">
            {{ candidate.desc }}
          </div>
        </div>
        <div
          :class="selected.includes(candidate.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-[var(--ai-line-strong)] bg-white'"
          class="flex h-4 w-4 items-center justify-center rounded-full border-2"
        >
          <Users
            v-if="selected.includes(candidate.id)"
            class="h-2.5 w-2.5 text-white"
          />
        </div>
      </button>
    </div>

    <ModalActionBar
      test-id="invite-assistant"
      submit-label="邀请助手"
      :submit-disabled="!canSubmit"
      @cancel="emit('close')"
      @submit="handleSubmit"
    />
  </ModalShell>
</template>
