<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { onBeforeUnmount } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { DEBUG } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()

const show = computed(() => ['free'].includes(runningStore.running))
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

function handleClick() {
  if (disabled.value || !show.value) {
    message.warning('当前正在运行/调试, 请勿重复操作')
    return
  }
  // await processStore.saveProject()
  const processId = processStore.canvasManager.activeTab?.id || ''
  useRunningStore().startDebug(processStore.project.id, processId)
}

registerHotkey(DEBUG, handleClick)
onBeforeUnmount(() => unregisterHotkey(DEBUG))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('debug')" :label="$t('debug')" :disabled="disabled" icon="tools-debug" @click="handleClick" />
</template>

