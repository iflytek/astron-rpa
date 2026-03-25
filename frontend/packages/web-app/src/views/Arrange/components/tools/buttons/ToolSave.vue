<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'
import { useTranslation } from 'i18next-vue'

import { SAVE } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { onBeforeUnmount } from 'vue'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()
const runningStore = useRunningStore()
const { t } = useTranslation()

const disabled = computed(() => {
  return !canvasManager?.activeTab || ['debug', 'run'].includes(runningStore.running)
})

const save = throttle(async () => {
  const ok = await canvasManager?.saveTab()
  if (ok) {
    message.success(t('toolsTips.saveSuccess'))
  }
  else {
    message.error(t('toolsTips.saveFailed'))
  }
}, 1500, { leading: true, trailing: false })

const handleClick = async () => {
  if (disabled.value) {
    message.warning(t('toolsTips.runningOrDebuggingCannotSave'))
    return
  }
  await save()
}

registerHotkey(SAVE, handleClick)
onBeforeUnmount(() => unregisterHotkey(SAVE))
</script>

<template>
  <ToolButton :tooltip="$t('save')" :label="$t('save')" :disabled="disabled" icon="tools-save" @click="handleClick" />
</template>
