<script lang="ts" setup>
import DeleteAction from './DeleteAction.vue'
import ExportAction from './ExportAction.vue'
import ImportAction from './ImportAction.vue'
import { useDataSheetStore } from './useDataSheet'

const { isReady, handleUndo, handleRedo, handleFind } = useDataSheetStore()
</script>

<template>
  <div class="flex items-center gap-2">
    <rpa-hint-icon name="tools-undo" :title="$t('undo')" enable-hover-bg :disabled="!isReady" @click="handleUndo" />
    <rpa-hint-icon name="tools-recover" :title="$t('redo')" enable-hover-bg :disabled="!isReady" @click="handleRedo" />

    <ImportAction />
    <ExportAction />

    <DeleteAction />

    <rpa-hint-icon name="bottom-pick-menu-search" enable-hover-bg :disabled="!isReady" @click="handleFind">
      <template #suffix>
        <span class="ml-1 text-xs">查找替换</span>
      </template>
    </rpa-hint-icon>
  </div>
</template>
