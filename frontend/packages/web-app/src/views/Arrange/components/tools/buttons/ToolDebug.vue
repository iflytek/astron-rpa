<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { onBeforeUnmount } from 'vue'
import { useTranslation } from 'i18next-vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { DEBUG } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()
const { t } = useTranslation()

const show = computed(() => ['free'].includes(runningStore.running))
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

async function handleClick() {
  if (disabled.value || !show.value) {
    message.warning(t('toolsTips.runningOrDebuggingNoRepeat'))
    return
  }
  const saved = await processStore.canvasManager.saveTab()
  if (!saved) {
    message.error(t('toolsTips.saveFailed'))
    return
  }
  const processId = processStore.canvasManager.activeTab?.id || ''
  useRunningStore().startDebug(processStore.project.id, processId)
}

registerHotkey(DEBUG, handleClick)
onBeforeUnmount(() => unregisterHotkey(DEBUG))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('debug')" :label="$t('debug')" :disabled="disabled" icon="tools-debug" @click="handleClick" />
</template>

