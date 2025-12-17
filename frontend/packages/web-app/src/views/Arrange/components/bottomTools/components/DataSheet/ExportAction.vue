<script lang="ts" setup>
import { sheetUtils } from '@rpa/components'

import { useDataSheetStore } from './useDataSheet'

const { sheetData, isReady } = useDataSheetStore();

const handleExport = async (widthIncludeHeader: boolean) => {
  console.log('export', sheetData, widthIncludeHeader);
  await sheetUtils.exportExcelFile(sheetData.value);
}
</script>

<template>
  <a-dropdown>
    <rpa-hint-icon name="move-folder" enable-hover-bg :disabled="!isReady">
      <template #suffix>
        <span class="ml-1 text-xs">导出</span>
      </template>
    </rpa-hint-icon>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleExport(false)">导出数据</a-menu-item>
        <a-menu-item @click="handleExport(true)">导出数据（含列名）</a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
