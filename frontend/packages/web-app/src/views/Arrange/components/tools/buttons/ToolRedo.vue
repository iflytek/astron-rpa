<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { REDO } from '@/constants/shortcuts'
import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return !canvasManager?.activeTab?.undoManager.canRestore.value
})

const handleClick = () => {
  canvasManager?.activeTab?.undoManager.restore()
}

registerHotkey(REDO, handleClick)
onBeforeUnmount(() => unregisterHotkey(REDO))
</script>

<template>
  <ToolButton :tooltip="$t('redo')" :disabled="disabled" icon="tools-recover" @click="handleClick" />
</template>
