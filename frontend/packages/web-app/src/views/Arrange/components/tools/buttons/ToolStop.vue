<script setup lang="ts">
import { computed } from 'vue'
import { throttle } from 'lodash-es'
import { onBeforeUnmount } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { STOP_RUN } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()

const show = computed(() => ['debug', 'run'].includes(runningStore.running))
const disabled = computed(() => ['free'].includes(runningStore.running))

const handleConfirmStop = throttle(() => {
  useRunningStore().stop(processStore.project.id)
}, 1500, { leading: true, trailing: false })

function handleClick() {
  handleConfirmStop()
}

registerHotkey(STOP_RUN, handleClick)
onBeforeUnmount(() => unregisterHotkey(STOP_RUN))
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('stop')" :label="$t('stop')" :disabled="disabled" icon="tools-stop" color="#EC483E" @click="handleClick" />
</template>

