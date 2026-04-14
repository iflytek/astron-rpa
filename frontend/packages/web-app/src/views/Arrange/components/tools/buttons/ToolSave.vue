<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'
import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'
import { useTranslation } from 'i18next-vue'

import { SAVE } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()
const runningStore = useRunningStore()
const { t } = useTranslation()

const disabled = computed(() => {
  const tab = canvasManager?.activeTab
  if (!tab) return true

  if (['debug', 'run'].includes(runningStore.running)) return true

  // return canvasManager.getActionState('save').disabled
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
  await save()
}

registerHotkey(SAVE, handleClick)
onBeforeUnmount(() => unregisterHotkey(SAVE))
</script>

<template>
  <ToolButton :tooltip="$t('save')" :label="$t('save')" :disabled="disabled" icon="tools-save" @click="handleClick" />
</template>
