<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { cn } from '@/lib/utils'

defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="card"
    :class="cn('rounded-[24px] border border-black/[0.05] bg-white shadow-[0_20px_40px_rgba(17,24,39,0.045),0_4px_10px_rgba(17,24,39,0.02)]', $props.class)"
  >
    <slot />
  </div>
</template>
