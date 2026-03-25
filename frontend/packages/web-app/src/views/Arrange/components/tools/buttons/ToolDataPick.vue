<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { usePickStore } from '@/stores/usePickStore'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const runningStore = useRunningStore()
const pickStore = usePickStore()
const createWindow = useCreateWindow()
const { t } = useTranslation()

const show = computed(() => true)
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running) || pickStore.isDataPicking)

async function handleClick() {
  if (disabled.value) {
    message.warning(t('toolsTips.runningOrDebuggingStopFirst'))
    return
  }
  await createWindow.openDataPickWindow()
}
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('dataScraping')" :label="$t('dataScraping')" :disabled="disabled" icon="tools-data-pick" @click="handleClick" />
</template>

