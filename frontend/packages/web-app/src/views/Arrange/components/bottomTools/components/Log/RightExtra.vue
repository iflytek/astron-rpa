<script lang="ts" setup>
import { useRunlogStore } from '@/stores/useRunlogStore'

function clearLog() {
  useRunlogStore().clearLogs()
}
</script>

<template>
  <rpa-hint-icon
    name="clear-outlined"
    title="清除日志"
    class="mr-[-8px]"
    enable-hover-bg
    @click="() => clearLog()"
  />
</template>
