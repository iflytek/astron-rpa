<script setup lang="ts">
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()
const { t } = useTranslation()

const disabled = computed(() => {
  return canvasManager.getActionState('group').disabled
})

const handleClick = () => {
  const selectedAtomIds = canvasManager.activeTab?.state.selectedAtomIds ?? []
  if (selectedAtomIds.length === 0) {
    message.warning(t('toolsTips.selectNodeBeforeGroup'))
    return
  }
  canvasManager.activeTab?.group?.(selectedAtomIds)
}
</script>

<template>
  <ToolButton :tooltip="$t('group')" :disabled="disabled" icon="tools-group" @click="handleClick" />
</template>
