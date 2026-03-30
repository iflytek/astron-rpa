<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/ai-components/lib/utils'

const props = defineProps<{
  caption?: string
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    :class="cn('mt-2 space-y-2', props.class)"
    v-bind="$attrs"
  >
    <div
      class="relative flex max-h-[22rem] items-center justify-center overflow-hidden rounded-lg bg-muted p-3"
    >
      <slot />
    </div>
    <p v-if="caption" class="text-muted-foreground text-xs">
      {{ props.caption }}
    </p>
  </div>
</template>
