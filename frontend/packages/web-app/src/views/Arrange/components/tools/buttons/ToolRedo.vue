<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return !canvasManager?.activeTab?.undoManager.canRestore.value
})

const handleClick = () => {
  canvasManager?.activeTab?.undoManager.restore()
}
</script>

<template>
  <ToolButton :tooltip="$t('redo')" :disabled="disabled" icon="tools-recover" @click="handleClick" />
</template>
