<script setup lang="ts">
import { computed, nextTick, reactive, watch, useTemplateRef } from 'vue'
import draggable from 'vuedraggable'

import ProcessHeaderAdd from './ProcessHeaderAdd.vue'
import ProcessHeaderMore from './ProcessHeaderMore.vue'
import ProcessItem, { type ProcessItemState } from './ProcessItem.vue'
import { useProcessStore } from '@/stores/useProcessStore'

const { canvasManager } = useProcessStore()
const containerRef = useTemplateRef<HTMLDivElement>('container')
const visibleStateMap = reactive<Record<string, boolean>>({})

const openProcessList = computed<ProcessItemState[]>(() => {
  return canvasManager.tabs.map((item, index) => ({
    ...item.state,
    showDivider: ![item.id, canvasManager.tabs[index + 1]?.id].includes(canvasManager.activeTabId),
  }))
})
const inVisibleProcessList = computed(() => openProcessList.value.filter(item => visibleStateMap[item.resourceId] !== true))

function updateVisibleState(process: RPA.Process.ProcessModule, visible: boolean) {
  visibleStateMap[process.resourceId] = visible
}

watch(() => canvasManager.activeTabId, (val) => {
  nextTick(() => {
    const activeProcessDom = containerRef.value?.querySelector(`#process_${val}`)
    activeProcessDom?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    })
  })
})
</script>

<template>
  <div ref="container" class="process right-tab-close-area">
    <draggable id="drag" item-key="resourceId" :list="openProcessList" filter=".forbid" class="process_list whitespace-nowrap">
      <template #item="{ element }: { element: ProcessItemState }">
        <ProcessItem
          :key="`contextmenu${element.resourceId}`"
          :id="`process_${element.resourceId}`"
          :process-item="element"
          :is-active="canvasManager.activeTabId === element.resourceId"
          @visible-change="updateVisibleState(element, $event)"
        />
      </template>
    </draggable>
    <div class="process_action">
      <ProcessHeaderMore v-if="inVisibleProcessList.length" :in-visible-process-list="inVisibleProcessList" />
      <ProcessHeaderAdd />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.process {
  display: flex;
  align-items: center;

  &_list {
    /* 设置超出滚动 */
    overflow-x: auto;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  &_action {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 4px;
  }
}
</style>
