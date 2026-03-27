<script setup lang="ts">
import { ScrollAreaCorner, ScrollAreaRoot, ScrollAreaScrollbar, ScrollAreaThumb, ScrollAreaViewport } from 'reka-ui'

import { cn } from '@/lib/utils'

defineProps<{
  class?: string
  viewportClass?: string
}>()
</script>

<template>
  <ScrollAreaRoot
    data-slot="scroll-area"
    :class="cn('relative overflow-hidden', $props.class)"
  >
    <ScrollAreaViewport :class="cn('h-full w-full rounded-[inherit]', $props.viewportClass)">
      <slot />
    </ScrollAreaViewport>
    <ScrollAreaScrollbar
      orientation="vertical"
      class="flex w-2.5 touch-none select-none p-[1px] transition-colors"
    >
      <ScrollAreaThumb class="relative flex-1 rounded-full bg-black/[0.12]" />
    </ScrollAreaScrollbar>
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>
