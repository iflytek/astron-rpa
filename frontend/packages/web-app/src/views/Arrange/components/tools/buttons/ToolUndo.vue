<script setup lang="ts">
import { computed, toValue } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return !canvasManager?.activeTab?.undoManager.canUndo.value
})

const handleClick = () => {
  canvasManager?.activeTab?.undoManager.undo()
}
</script>

<template>
  <ToolButton :tooltip="$t('undo')" :disabled="disabled" icon="tools-undo" @click="handleClick" />
</template>
