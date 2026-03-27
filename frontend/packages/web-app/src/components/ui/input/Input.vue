<script setup lang="ts">
import type { HTMLAttributes, InputHTMLAttributes } from 'vue'

import { cn } from '@/lib/utils'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  class?: HTMLAttributes['class']
  modelValue?: InputHTMLAttributes['value']
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<template>
  <input
    data-slot="input"
    v-bind="$attrs"
    :value="modelValue"
    :class="cn('flex h-11 w-full rounded-2xl border border-black/[0.06] bg-[linear-gradient(180deg,#fbfbfe_0%,#ffffff_100%)] px-4 py-2 text-[15px] text-black/80 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] outline-none transition-all placeholder:text-black/30 focus:border-[var(--color-primary)]/70 focus:bg-white focus:ring-4 focus:ring-[var(--color-primary)]/8 disabled:cursor-not-allowed disabled:opacity-50', props.class)"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  >
</template>
