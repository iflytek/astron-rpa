<script setup lang="ts">
import type { HtmlHTMLAttributes } from 'vue'
import {
  Collapsible,
  CollapsibleTrigger,
} from '@/ai-components/ui/collapsible'
import { cn } from '@/ai-components/lib/utils'
import { BrainIcon, ChevronDownIcon } from 'lucide-vue-next'
import { useChainOfThought } from './context'

const props = defineProps<{
  class?: HtmlHTMLAttributes['class']
}>()

const { isOpen, setIsOpen } = useChainOfThought()
</script>

<template>
  <Collapsible :open="isOpen" @update:open="setIsOpen">
    <CollapsibleTrigger
      :class="
        cn(
          'flex w-full items-center gap-2 text-muted-foreground text-sm transition-colors hover:text-foreground',
          props.class,
        )
      "
      v-bind="$attrs"
    >
      <BrainIcon class="size-4" />
      <span class="flex-1 text-left">
        <slot>Chain of Thought</slot>
      </span>
      <ChevronDownIcon
        :class="
          cn(
            'size-4 transition-transform',
            isOpen ? 'rotate-180' : 'rotate-0',
          )
        "
      />
    </CollapsibleTrigger>
  </Collapsible>
</template>
