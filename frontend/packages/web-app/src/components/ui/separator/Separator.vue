<script setup lang="ts">
import { Separator } from 'reka-ui'

import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  class?: string
  orientation?: 'horizontal' | 'vertical'
}>(), {
  orientation: 'horizontal',
})
</script>

<template>
  <Separator
    data-slot="separator"
    decorative
    :orientation="props.orientation"
    :class="cn(props.orientation === 'horizontal' ? 'h-px w-full bg-black/[0.06]' : 'h-full w-px bg-black/[0.06]', props.class)"
  />
</template>
