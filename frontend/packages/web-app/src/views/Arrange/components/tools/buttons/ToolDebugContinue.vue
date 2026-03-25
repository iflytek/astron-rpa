<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { onBeforeUnmount } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore'
import { CONTINUE_DEBUG } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const runningStore = useRunningStore()

const show = computed(() => ['debug'].includes(runningStore.running))
const disabled = computed(() => ['free', 'run'].includes(runningStore.running) || !runningStore.debugData?.is_break)

function handleClick() {
  if (!show.value) {
    message.warning('请先开启调试模式, 再进行调试操作')
    return
  }
  if (disabled.value) {
    message.warning('正在运行调试, 请稍后')
    return
  }
  useRunningStore().continueDebug()
}

registerHotkey(CONTINUE_DEBUG, handleClick)
onBeforeUnmount(() => unregisterHotkey(CONTINUE_DEBUG))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('debuggingContinues')" :label="$t('debuggingContinues')" :disabled="disabled" icon="tools-debug-continue" @click="handleClick" />
</template>

