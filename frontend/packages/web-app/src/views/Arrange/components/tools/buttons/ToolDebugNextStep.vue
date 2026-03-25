<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { onBeforeUnmount } from 'vue'
import { useTranslation } from 'i18next-vue'

import { useRunningStore } from '@/stores/useRunningStore'
import { NEXT_DEBUG } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const runningStore = useRunningStore()
const { t } = useTranslation()

const show = computed(() => ['debug'].includes(runningStore.running))
const disabled = computed(() => ['free', 'run'].includes(runningStore.running) || !runningStore.debugData?.is_break)

function handleClick() {
  if (!show.value) {
    message.warning(t('toolsTips.enableDebugModeFirst'))
    return
  }
  if (disabled.value) {
    message.warning(t('toolsTips.debuggingPleaseWait'))
    return
  }
  useRunningStore().nextStepDebug()
}

registerHotkey(NEXT_DEBUG, handleClick)
onBeforeUnmount(() => unregisterHotkey(NEXT_DEBUG))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('debuggingNext')" :label="$t('debuggingNext')" :disabled="disabled" icon="tools-debug-next-step" @click="handleClick" />
</template>

