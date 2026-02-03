<script setup lang="ts">
import { Sheet, SheetLocaleType, useTheme } from '@rpa/components'
import type { ISheetWorkbookData } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { useTranslation } from 'i18next-vue'
import { computed, useTemplateRef } from 'vue'

import { blob2File } from '@/utils/common'
import { fileRead } from '@/api/resource'

const props = defineProps<{ dataTablePath: string, class?: string }>()

const { isDark } = useTheme()
const { i18next } = useTranslation()
const sheetRef = useTemplateRef('sheetRef')

const { state: workbookData } = useAsyncState<ISheetWorkbookData>(async () => {
  const { data } = await fileRead({ path: props.dataTablePath })
  const file = blob2File(data, 'data-table.xlsx')
  return sheetRef.value.utils.transformExcelToUniver(file)
}, null)

const locale = computed<SheetLocaleType>(() => {
  return (i18next.language === 'zh-CN' ? 'zhCN' : 'enUS') as SheetLocaleType
})
</script>

<template>
  <Sheet
    v-if="workbookData"
    ref="sheetRef"
    readonly
    :class="props.class"
    :default-value="workbookData"
    :dark-mode="isDark"
    :locale="locale"
  />
</template>
