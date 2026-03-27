<script setup lang="ts">
import { FolderOpen } from 'lucide-vue-next'

import { Input } from '@/components/ui/input'

import type { AIStudioWorkspaceSuggestion } from '../registry'

const props = withDefaults(defineProps<{
  modelValue: string
  label: string
  placeholder?: string
  testIdPrefix: string
  rootTestId?: string
  inputTestId?: string
  suggestions?: AIStudioWorkspaceSuggestion[]
}>(), {
  placeholder: '~/Documents',
  suggestions: () => [],
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function applySuggestion(path: string) {
  emit('update:modelValue', path)
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-[12px] font-medium leading-4 text-black/76">{{ props.label }}</label>
    <div
      :data-testid="props.rootTestId || `${props.testIdPrefix}-field`"
      class="flex items-center gap-2.5 rounded-[16px] bg-[var(--ai-surface-soft)] px-3 py-2.5 shadow-[inset_0_0_0_1px_rgba(215,224,239,0.88)] focus-within:bg-white focus-within:shadow-[inset_0_0_0_1px_rgba(114,111,255,0.42),0_0_0_4px_rgba(114,111,255,0.08)]"
    >
      <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-[12px] bg-white text-[var(--color-primary)] shadow-[0_6px_14px_rgba(15,23,42,0.04)]">
        <FolderOpen class="h-4 w-4" />
      </div>
      <Input
        :model-value="props.modelValue"
        :data-testid="props.inputTestId || `${props.testIdPrefix}-input`"
        class="h-auto border-0 bg-transparent px-0 py-0 font-mono text-[12px] text-black/68 shadow-none focus-visible:ring-0"
        :placeholder="props.placeholder"
        @update:model-value="emit('update:modelValue', $event)"
      />
      <button
        type="button"
        class="shrink-0 rounded-[10px] px-2 py-1 text-[10px] font-medium text-black/38 transition-colors hover:bg-white hover:text-[var(--color-primary)]"
        @click="props.suggestions[0] && applySuggestion(props.suggestions[0].label)"
      >
        选择
      </button>
    </div>

    <div
      v-if="props.suggestions.length"
      :data-testid="`workspace-picker-panel-${props.testIdPrefix}`"
      class="rounded-[16px] bg-[rgba(255,255,255,0.72)] px-3 py-2.5 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.9)]"
    >
      <div class="mb-2 text-[10px] font-medium tracking-[0.06em] text-black/34">最近工作区</div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="suggestion in props.suggestions"
          :key="suggestion.id"
          :data-testid="`${props.testIdPrefix}-suggestion-${suggestion.id}`"
          type="button"
          class="inline-flex items-center gap-1.5 rounded-full bg-white px-2.5 py-1.5 text-left shadow-[0_6px_14px_rgba(15,23,42,0.035)] transition-all hover:-translate-y-[1px] hover:text-[var(--color-primary)]"
          @click="applySuggestion(suggestion.label)"
        >
          <span class="text-[11px] font-medium leading-4 text-black/72">{{ suggestion.label }}</span>
          <span class="text-[10px] leading-4 text-black/34">{{ suggestion.hint }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
