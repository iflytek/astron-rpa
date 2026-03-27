<script setup lang="ts">
import { RadioGroupRoot, useForwardPropsEmits } from 'reka-ui'

const props = defineProps<{
  modelValue?: string
  class?: string
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <RadioGroupRoot
    data-slot="radio-group"
    v-bind="forwarded"
    :class="props.class"
  >
    <slot />
  </RadioGroupRoot>
</template>
