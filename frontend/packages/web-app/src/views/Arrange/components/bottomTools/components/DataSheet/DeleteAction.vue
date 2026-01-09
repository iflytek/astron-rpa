<script lang="ts" setup>
import { useDataSheetStore } from './useDataSheet'

const { sheetRef, isReady, handleClearAll } = useDataSheetStore()

function handleDeleteSelection() {
  sheetRef.value?.deleteSelection()
}
</script>

<template>
  <a-dropdown :disabled="!isReady">
    <rpa-hint-icon name="atom-delete" enable-hover-bg :disabled="!isReady">
      <template #suffix>
        <span class="ml-1 text-xs">删除</span>
      </template>
    </rpa-hint-icon>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleDeleteSelection">
          删除选中区域
        </a-menu-item>
        <a-menu-item @click="handleClearAll">
          清除全部数据
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
