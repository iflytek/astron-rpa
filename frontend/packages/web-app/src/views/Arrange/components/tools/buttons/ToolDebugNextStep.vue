<script setup lang="ts">
import { computed } from 'vue'
import { onBeforeUnmount } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore'
import { NEXT_DEBUG } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const runningStore = useRunningStore()

const show = computed(() => ['debug'].includes(runningStore.running))
const disabled = computed(() => ['free', 'run'].includes(runningStore.running) || !runningStore.debugData?.is_break)

function handleClick() {
  useRunningStore().nextStepDebug()
}

registerHotkey(NEXT_DEBUG, handleClick)
onBeforeUnmount(() => unregisterHotkey(NEXT_DEBUG))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('debuggingNext')" :label="$t('debuggingNext')" :disabled="disabled" icon="tools-debug-next-step" @click="handleClick" />
</template>

