<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const { canvasManager } = useProcessStore()

const disabled = computed(() => {
  return false
})

const handleClick = () => {
}
</script>

<template>
  <ToolButton :tooltip="$t('goBack')" size="24" :disabled="disabled" icon="chevron-left" @click="handleClick" />
</template>
