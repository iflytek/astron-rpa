<script lang="ts" setup>
import { sheetUtils } from '@rpa/components'

import { useDataSheetStore } from './useDataSheet'

const { sheetData, isReady } = useDataSheetStore();

const handleExport = async () => {
  const buffer = await sheetUtils.exportExcelFile(sheetData.value);
  console.log('buffer', buffer);
}
</script>

<template>
  <rpa-hint-icon name="move-folder" enable-hover-bg :disabled="!isReady" @click="handleExport">
    <template #suffix>
      <span class="ml-1 text-xs">导出</span>
    </template>
  </rpa-hint-icon>
</template>
