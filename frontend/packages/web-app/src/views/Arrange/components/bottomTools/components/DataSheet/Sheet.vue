<script lang="ts" setup>
import { Sheet, SheetLocaleType, useTheme } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { computed, shallowRef } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore.ts'

import { useDataSheetStore } from './useDataSheet'
import { transformToWorkbookData } from './utils'

const props = defineProps<{ height: number }>()

const { isDark } = useTheme()
const { i18next } = useTranslation()
const runningStore = useRunningStore()

const { sheetRef, handleReady, handleCellUpdate } = useDataSheetStore()

const defaultValue = shallowRef(transformToWorkbookData(runningStore.dataTable))

const locale = computed(() => {
  return i18next.language === 'zh-CN' ? SheetLocaleType.ZH_CN : SheetLocaleType.EN_US
})
</script>

<template>
  <Sheet
    ref="sheetRef"
    :style="{ height: `${props.height}px` }"
    :dark-mode="isDark"
    :locale="locale"
    :default-value="defaultValue"
    @ready="handleReady"
    @cell-update="handleCellUpdate"
  />
</template>
