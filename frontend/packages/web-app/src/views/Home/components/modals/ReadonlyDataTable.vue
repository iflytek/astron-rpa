<script setup lang="ts">
import { Sheet, SheetLocaleType, sheetUtils, useTheme } from '@rpa/components'
import type { ISheetWorkbookData } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { blob2File } from '@/utils/common'

import { fileRead } from '@/api/resource'

const props = defineProps<{ dataTablePath: string, class?: string }>()

const { isDark } = useTheme()
const { i18next } = useTranslation()

const { state: workbookData } = useAsyncState<ISheetWorkbookData>(async () => {
  const { data } = await fileRead({ path: props.dataTablePath })
  const file = blob2File(data, 'data-table.xlsx')
  return sheetUtils.transformExcelToUniver(file)
}, null)

const locale = computed(() => {
  return i18next.language === 'zh-CN' ? SheetLocaleType.ZH_CN : SheetLocaleType.EN_US
})
</script>

<template>
  <Sheet
    v-if="workbookData"
    readonly
    :class="props.class"
    :default-value="workbookData"
    :dark-mode="isDark"
    :locale="locale"
  />
</template>
