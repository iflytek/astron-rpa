<script setup lang="ts">
import { computed } from 'vue'

import { usePickStore } from '@/stores/usePickStore'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const runningStore = useRunningStore()
const pickStore = usePickStore()
const createWindow = useCreateWindow()

const disabled = computed(() => ['debug', 'run'].includes(runningStore.running) || pickStore.isDataPicking)

async function handleClick() {
  await createWindow.openDataPickWindow()
}
</script>

<template>
  <ToolButton :tooltip="$t('dataScraping')" :label="$t('dataScraping')" :disabled="disabled" icon="tools-data-pick" @click="handleClick" />
</template>

