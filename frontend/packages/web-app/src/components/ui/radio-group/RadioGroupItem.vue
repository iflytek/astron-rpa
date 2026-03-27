<script setup lang="ts">
import { Dot } from 'lucide-vue-next'
import { RadioGroupIndicator, RadioGroupItem } from 'reka-ui'

import { cn } from '@/lib/utils'

defineProps<{
  value: string
  class?: string
}>()
</script>

<template>
  <RadioGroupItem
    data-slot="radio-group-item"
    :value="value"
    :class="cn('relative flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[#CBD5E1] bg-white text-[var(--color-primary)] shadow-[inset_0_1px_2px_rgba(15,23,42,0.05)] outline-none transition-all focus-visible:ring-2 focus-visible:ring-[#726FFF]/24 focus-visible:ring-offset-2 focus-visible:ring-offset-white data-[state=checked]:border-[var(--color-primary)] data-[state=checked]:bg-[#F5F3FF] data-[state=checked]:shadow-[0_0_0_4px_rgba(114,111,255,0.10)]', $props.class)"
  >
    <RadioGroupIndicator class="flex h-full w-full items-center justify-center">
      <Dot class="h-3 w-3 fill-current text-current" />
    </RadioGroupIndicator>
  </RadioGroupItem>
</template>
