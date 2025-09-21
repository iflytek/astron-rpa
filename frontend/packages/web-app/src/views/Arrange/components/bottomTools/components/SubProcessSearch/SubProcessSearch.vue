<script lang="ts" setup>
import { computed, inject, nextTick, ref } from 'vue'
import type { Ref } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { atomScrollIntoView } from '@/views/Arrange/utils'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const height = inject<Ref<number>>('logTableHeight', ref(180)) // 若没有注入，默认值为320

const processStore = useProcessStore()

const searchSubProcessName = computed(() => {
  return processStore.processList.find((pItem: any) => pItem.resourceId === processStore.searchSubProcessId)?.name
})

function clickSearchNode(pitem: any, node: any) {
  processStore.openProcess(pitem.processId)
  changeSelectAtoms(node.id, null, false)
  nextTick(() => {
    atomScrollIntoView(node.id)
  })
}
</script>

<template>
  <div class="sub-process-use" :style="`height: ${height}px;`">
    <template v-for="item in processStore.searchSubProcessResult" :key="item.processId">
      <a-row
        v-for="node in item.nodes" :key="node.id" class="sub-process-use-item"
        @click="clickSearchNode(item, node)"
      >
        <a-col span="6" class="sub-process-use-col">
          {{ item.processName }}
        </a-col>
        <a-col span="6" class="sub-process-use-col">
          行：{{ node.row }}
        </a-col>
        <a-col span="12" class="sub-process-use-col">
          {{ node.alias }}: {{ searchSubProcessName }}
        </a-col>
      </a-row>
    </template>
    <a-empty v-if="processStore.searchSubProcessResult.length === 0" />
  </div>
</template>

<style lang="scss" scoped>
.sub-process-use {
  overflow-y: auto;

  &-item {
    height: 34px;
    line-height: 34px;
    border-bottom: 1px solid #eee;
    padding-left: 20px;
    cursor: pointer;

    &:hover {
      background: #f8f8f8;
    }
  }

  &-col {
    font-size: 12px;
  }

  :deep(.ant-empty) {
    margin-top: 15px;
  }
}
</style>
