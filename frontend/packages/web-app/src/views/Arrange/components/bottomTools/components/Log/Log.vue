<script lang="ts" setup>
import { nextTick } from 'vue'

import RunLog from '@/components/RunLog/index.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import { clickAtom } from '@/views/Arrange/components/flow/hooks/useFlow'
import { atomScrollIntoView } from '@/views/Arrange/utils'

const processStore = useProcessStore()

function handleRowClick(row: any) {
  // TODO - 点击日志聚焦原子能力
  if (!row.lineNum || row.lineNum === '--')
    return

  if (row.processId !== processStore.activeProcessId)
    processStore.checkActiveProcess(row.processId)
  clickAtom(({ ctrlKey: false, shiftKey: false } as MouseEvent), {
    id: row.id,
    key: '',
    icon: '',
    title: '',
    level: 1,
    version: '',
    alias: '',
    advanced: [],
    exception: [],
    inputList: [],
    outputList: [],
  })
  nextTick(() => {
    atomScrollIntoView(row.id)
  })
}
</script>

<template>
  <div class="logs-manager">
    <RunLog @row-click="handleRowClick" />
  </div>
</template>
