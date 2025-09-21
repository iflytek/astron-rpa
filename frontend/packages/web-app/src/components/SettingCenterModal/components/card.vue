<script setup lang="ts">
import { useSlots } from 'vue'

const props = defineProps<{ title: string, description?: string }>()
const slots = useSlots()
</script>

<template>
  <div
    class="rounded-lg flex items-center gap-[18px] bg-[#00000008] dark:bg-[#FFFFFF08]"
  >
    <slot name="prefix" />
    <div class="flex-1 overflow-hidden">
      <div
        class="text-sm leading-5 font-semibold text-[rgba(0,0,0,0.85)] dark:text-white"
      >
        {{ props.title }}
      </div>

      <slot v-if="slots.content" name="content" />
      <a-typography-paragraph
        v-else-if="props.description"
        :ellipsis="{ tooltip: props.description }"
        class="text-xs mt-[6px] leading-6 font-normal !mb-0 text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]"
        :content="props.description"
      />
    </div>
    <slot name="suffix" />
  </div>
</template>
