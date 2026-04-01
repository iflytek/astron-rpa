<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => canvasManager.getActionState('group').disabled)

const handleClick = () => {
  const selectedAtomIds = canvasManager.activeTab?.state.selectedAtomIds ?? []
  canvasManager.activeTab?.group?.(selectedAtomIds)
}
</script>

<template>
  <ToolButton :tooltip="$t('group')" :disabled="disabled" icon="tools-group" @click="handleClick" />
</template>
