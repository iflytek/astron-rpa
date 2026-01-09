<script lang="ts" setup>
import { sheetUtils } from '@rpa/components'
import { message } from 'ant-design-vue'
import { to } from 'await-to-js'

import { utilsManager } from '@/platform'

import { useDataSheetStore } from './useDataSheet'

const { sheetRef, isReady } = useDataSheetStore()

async function handleExport() {
  const data = sheetRef.value?.getWorkbookData()
  if (!data)
    return

  const buffer = await sheetUtils.exportExcelFile(data)
  const [error] = await to<void, string>(utilsManager.saveFile('data.xlsx', buffer))
  if (error) {
    message.error(error)
  }
  else {
    message.success('导出成功')
  }
}
</script>

<template>
  <rpa-hint-icon name="move-folder" enable-hover-bg :disabled="!isReady" @click="handleExport">
    <template #suffix>
      <span class="ml-1 text-xs">导出</span>
    </template>
  </rpa-hint-icon>
</template>
