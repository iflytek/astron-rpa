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
        <span class="ml-1 text-xs">{{ $t('delete') }}</span>
      </template>
    </rpa-hint-icon>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleDeleteSelection">
          {{ $t('sheet.deleteSelection') }}
        </a-menu-item>
        <a-menu-item @click="handleClearAll">
          {{ $t('sheet.clearAllData') }}
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
