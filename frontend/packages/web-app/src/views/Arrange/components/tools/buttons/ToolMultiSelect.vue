<script setup lang="ts">
import { computed } from 'vue'
import { useTranslation } from 'i18next-vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()
const { t } = useTranslation()

const tooltip = computed(() => {
  return canvasManager?.activeTab?.state.multiSelect ? t('deselect') : t('multiSelect')
})

const disabled = computed(() => {
  return canvasManager.getActionState('multiSelect').disabled
})

const handleClick = () => {
  canvasManager?.activeTab?.toggleMultiSelect?.()
}
</script>

<template>
  <ToolButton :tooltip="tooltip" :disabled="disabled" icon="tools-multi-select" @click="handleClick" />
</template>
