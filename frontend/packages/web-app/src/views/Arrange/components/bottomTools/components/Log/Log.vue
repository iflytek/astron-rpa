<script lang="ts" setup>
import { nextTick } from 'vue'

import RunLog from '@/components/RunLog/index.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import { atomScrollIntoView } from '@/views/Arrange/utils'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const { canvasManager } = useProcessStore()

async function handleRowClick(row: any) {
  // TODO - 点击日志聚焦原子能力
  if (!row.lineNum || row.lineNum === '--')
    return

  await canvasManager.activateTab(row.processId)
  changeSelectAtoms(row.id, null, false)

  nextTick(() => atomScrollIntoView(row.id))
}
</script>

<template>
  <div class="logs-manager">
    <RunLog @row-click="handleRowClick" />
  </div>
</template>
