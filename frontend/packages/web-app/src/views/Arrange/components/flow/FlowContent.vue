<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useProcessStore } from '@/stores/useProcessStore'

import FlowCode from './FlowCode.vue'
import FlowList from './FlowList.vue'

const processStore = useProcessStore()
const { activeProcess } = storeToRefs(processStore)
</script>

<template>
  <div class="relative flex-1 postTask-content-canvas bg-white dark:bg-[#FFFFFF]/[.12] overflow-hidden">
    <FlowCode
      v-if="activeProcess?.resourceCategory === 'module'"
      :key="activeProcess.resourceId"
      :resource-id="activeProcess.resourceId"
    />
    <FlowList v-else-if="activeProcess?.resourceCategory === 'process'" />
  </div>
</template>

<style scoped>
.postTask-content-canvas {
  border-radius: 0px 8px 8px 8px;
  opacity: v-bind('activeProcess?.isLoading ? 0.6 : 1');
  transition: opacity 0.3s;
}
</style>
