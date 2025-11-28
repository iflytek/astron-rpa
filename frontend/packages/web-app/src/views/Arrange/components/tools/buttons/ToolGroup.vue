<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return canvasManager.getActionState('group').disabled
})

const handleClick = () => {
  const selectedAtomIds = canvasManager.activeTab?.state.selectedAtomIds ?? []
  if (selectedAtomIds.length === 0) {
    message.warning(`请先选中一个节点再编组`)
    return
  }
  canvasManager.activeTab?.group?.(selectedAtomIds)
}
</script>

<template>
  <ToolButton :tooltip="$t('group')" :disabled="disabled" icon="tools-group" @click="handleClick" />
</template>
