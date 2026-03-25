<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { useRouteBack } from '@/hooks/useCommonRoute'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { useRunlogStore } from '@/stores/useRunlogStore'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const { canvasManager } = processStore
const runningStore = useRunningStore()
const { t } = useTranslation()

const disabled = computed(() => {
  return ['debug', 'run'].includes(runningStore.running)
})

const handleClick = async () => {
  if (disabled.value) {
    message.warning(t('toolsTips.runningOrDebuggingStopFirst'))
    return
  }

  try {
    await canvasManager.saveTab()
    await message.success('保存成功', 0.5)
    canvasManager.activeTab?.toggleMultiSelect?.(false)
    useRunlogStore().clearLogs()
    useRouteBack()
  }
  catch {
    message.error(t('toolsTips.saveFailedRetry'))
  }
}
</script>

<template>
  <ToolButton :tooltip="$t('goBack')" size="24" :disabled="disabled" icon="chevron-left" @click="handleClick" />
</template>
