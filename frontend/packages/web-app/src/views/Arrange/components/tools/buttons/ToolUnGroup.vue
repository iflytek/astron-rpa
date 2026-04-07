<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return canvasManager.getActionState('ungroup').disabled
})

const handleClick = () => {
  const selectedAtomIds = canvasManager.activeTab?.state.selectedAtomIds ?? []
  canvasManager.activeTab?.ungroup?.(selectedAtomIds)
}
</script>

<template>
  <ToolButton :tooltip="$t('releaseGrouping')" :disabled="disabled" icon="tools-un-group" @click="handleClick" />
</template>
