<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import {
  Collapsible,
  CollapsibleContent,
} from '@/ai-components/ui/collapsible'
import { cn } from '@/ai-components/lib/utils'
import { useChainOfThought } from './context'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const { isOpen } = useChainOfThought()
</script>

<template>
  <Collapsible :open="isOpen">
    <CollapsibleContent
      :class="
        cn(
          'mt-2 space-y-3',
          'data-[state=closed]:fade-out-0 data-[state=closed]:slide-out-to-top-2 data-[state=open]:slide-in-from-top-2 text-popover-foreground outline-none data-[state=closed]:animate-out data-[state=open]:animate-in',
          props.class,
        )
      "
      v-bind="$attrs"
    >
      <slot />
    </CollapsibleContent>
  </Collapsible>
</template>
