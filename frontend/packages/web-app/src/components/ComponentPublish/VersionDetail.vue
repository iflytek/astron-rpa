<script setup lang="ts">
import { useToggle } from '@vueuse/core'
import dayjs from 'dayjs'

const props = defineProps<{
  data: {
    version: number
    createTime: string
    updateLog: string
  }
}>()

const [expand, toggle] = useToggle(false)
</script>

<template>
  <div class="">
    <div class="flex items-center gap-2">
      <rpa-hint-icon
        :name="expand ? 'chevron-up' : 'chevron-down'"
        enable-hover-bg
        class="p-0.5"
        @click="toggle()"
      />
      <span class="text-sm font-semibold">版本 {{ props.data.version }}</span>
    </div>

    <div class="text-xs leading-6 text-text-secondary mt-1">
      {{ dayjs(props.data.createTime).format('YYYY-MM-DD HH:mm') }}
    </div>

    <div
      class="whitespace-pre-line mt-2 text-xs leading-6"
      :class="{ 'line-clamp-2 truncate': !expand }"
    >
      {{ props.data.updateLog }}
    </div>
  </div>
</template>
