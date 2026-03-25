<script setup lang="ts">
import { computed } from 'vue'
import { throttle } from 'lodash-es'
import { message } from 'ant-design-vue'
import { onBeforeUnmount } from 'vue'
import { useTranslation } from 'i18next-vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { RUN } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()
const { t } = useTranslation()

const show = computed(() => ['free'].includes(runningStore.running))
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

const handleConfirmRun = throttle(async () => {
  const saved = await processStore.canvasManager.saveTab()
  if (!saved) {
    message.error(t('toolsTips.saveFailed'))
    return
  }
  const processId = processStore.canvasManager.activeTab?.id || ''
  useRunningStore().startRun(processStore.project.id, processId)
}, 1500, { leading: true, trailing: false })

function handleClick() {
  if (disabled.value || !show.value) {
    message.warning(t('toolsTips.runningOrDebuggingNoRepeat'))
    return
  }
  handleConfirmRun()
}

registerHotkey(RUN, handleClick)
onBeforeUnmount(() => unregisterHotkey(RUN))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('run')" :label="$t('run')" :disabled="disabled" icon="tools-run" @click="handleClick" />
</template>

