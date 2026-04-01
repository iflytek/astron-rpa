<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'

import BUS from '@/utils/eventBus'
import { useRecordWindow } from '@/views/Arrange/hook/useRecordWindow'
import { addRecordAtomData } from '@/views/Arrange/utils/record'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const { open } = useRecordWindow()
const runningStore = useRunningStore()

onMounted(() => {
  BUS.$off('record-save')
  BUS.$on('record-save', addRecordAtomData)
})
onBeforeUnmount(() => {
  BUS.$off('record-save')
})

const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

function handleClick() {
  open()
}
</script>

<template>
  <ToolButton :tooltip="$t('smartRecording')" :label="$t('smartRecording')" :disabled="disabled" icon="tools-record" @click="handleClick" />
</template>

