<script setup lang="ts">
import type { HTMLAttributes, Ref } from 'vue'
import { cn } from '@/ai-components/lib/utils'
import { useVModel } from '@vueuse/core'
import { provide } from 'vue'
import { ChainOfThoughtContextKey } from './context'

interface ChainOfThoughtProps {
  modelValue?: boolean
  defaultOpen?: boolean
  class?: HTMLAttributes['class']
}

const props = withDefaults(
  defineProps<ChainOfThoughtProps>(),
  {
    defaultOpen: false,
    modelValue: undefined,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const isOpen = useVModel(props, 'modelValue', emit, {
  defaultValue: props.defaultOpen,
  passive: true,
})

provide(ChainOfThoughtContextKey, isOpen as Ref<boolean>)
</script>

<template>
  <div
    :class="cn('not-prose space-y-4', props.class)"
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>
