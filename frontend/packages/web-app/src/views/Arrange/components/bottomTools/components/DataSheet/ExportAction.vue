<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { to } from 'await-to-js'
import { isString } from 'lodash-es'

import { utilsManager } from '@/platform'

import { useDataSheetStore } from './useDataSheet'

const { sheetRef, isReady } = useDataSheetStore()

async function handleExport(type: 'csv' | 'excel') {
  const data = sheetRef.value?.getWorkbookData()
  if (!data)
    return

  let saveContent: ArrayBuffer | string
  const saveFileName = type === 'csv' ? 'data.csv' : 'data.xlsx'

  if (type === 'excel') {
    saveContent = await sheetRef.value.utils.exportToExcelFile(data)
  }

  if (type === 'csv') {
    const csvContent = await sheetRef.value.utils.exportToCsvFile(data)
    const content = isString(csvContent) ? csvContent : Object.values(csvContent).join('\n')
    // 提取纯CSV内容（去掉data:text/csv;charset=utf-8,前缀）
    saveContent = content.replace('data:text/csv;charset=utf-8,', '')
  }

  const [error, saved] = await to<boolean, string>(utilsManager.saveFile(saveFileName, saveContent))
  if (error) {
    message.error(error)
  } else if (saved) {
    message.success('导出成功')
  }
}
</script>

<template>
  <a-dropdown :disabled="!isReady">
    <rpa-hint-icon name="move-folder" enable-hover-bg>
      <template #suffix>
        <span class="ml-1 text-xs">导出</span>
      </template>
    </rpa-hint-icon>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleExport('csv')">
          导出CSV
        </a-menu-item>
        <a-menu-item @click="handleExport('excel')">
          导出Excel
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
