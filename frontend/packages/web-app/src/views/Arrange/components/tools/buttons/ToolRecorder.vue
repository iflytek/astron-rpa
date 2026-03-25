<script setup lang="ts">
import { onBeforeUnmount, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'

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

const show = computed(() => true)
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

function handleClick() {
  if (disabled.value) {
    message.warning('正在运行/调试, 请先停止')
    return
  }
  open()
}
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('smartRecording')" :label="$t('smartRecording')" :disabled="disabled" icon="tools-record" @click="handleClick" />
</template>

