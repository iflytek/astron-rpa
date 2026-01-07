<script lang="ts" setup>
import { Sheet, SheetLocaleType, useTheme } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { computed, ref, shallowRef } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore.ts'

import { useDataSheetStore } from './useDataSheet'
import { transformToWorkbookData } from './utils'

const props = defineProps<{ height: number }>()

const { isDark } = useTheme()
const { i18next } = useTranslation()
const runningStore = useRunningStore()

const loading = ref(true)

const { sheetRef, handleReady, handleCellUpdate } = useDataSheetStore()

const defaultValue = shallowRef(transformToWorkbookData(runningStore.dataTable))

const locale = computed(() => {
  return i18next.language === 'zh-CN' ? SheetLocaleType.ZH_CN : SheetLocaleType.EN_US
})

function handleRendered() {
  loading.value = false
}
</script>

<template>
  <a-spin :spinning="loading">
    <div :style="{ height: `${props.height}px` }">
      <Sheet
        ref="sheetRef"
        :dark-mode="isDark"
        :locale="locale"
        :default-value="defaultValue"
        @rendered="handleRendered"
        @ready="handleReady"
        @cell-update="handleCellUpdate"
      />
    </div>
  </a-spin>
</template>
