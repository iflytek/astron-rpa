<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { UNDO } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => !canvasManager?.activeTab?.undoManager.canUndo.value)

const handleClick = () => {
  canvasManager?.activeTab?.undoManager.undo()
}

registerHotkey(UNDO, handleClick)
onBeforeUnmount(() => unregisterHotkey(UNDO))
</script>

<template>
  <ToolButton :tooltip="$t('undo')" :disabled="disabled" icon="tools-undo" @click="handleClick" />
</template>
