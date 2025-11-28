<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

const { canvasManager } = useProcessStore()

const renderTabs = computed(() => canvasManager.tabs.filter(item => item.component && item.state?.shouldRender))
</script>

<template>
  <div
    :class="[
      'postTask-canvas relative flex-1 bg-white dark:bg-[#FFFFFF]/[.12] overflow-hidden',
      { 'postTask-canvas__loading': canvasManager.activeTab?.state?.isLoading }
    ]"
  >
    <component
      v-for="item in renderTabs"
      :key="item.id"
      v-show="item.id === canvasManager.activeTabId"
      :is="item.component"
      :resourceId="item.id"
      :manage="item"
    />
  </div>
</template>

<style lang="scss" scoped>
.postTask-canvas {
  border-radius: 0px 8px 8px 8px;
  opacity: 1;
  transition: opacity 0.3s;

  &__loading {
    opacity: 0.6;
  }
}
</style>
