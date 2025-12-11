<script lang="ts" setup>
import { useTemplateRef, onBeforeUnmount, onMounted, watch } from 'vue'
import type { FUniver, Univer, IWorkbookData } from '@univerjs/presets'
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core'
import UniverPresetSheetsCoreZhCN from '@univerjs/preset-sheets-core/locales/zh-CN'
import { createUniver, LocaleType, mergeLocales, defaultTheme } from '@univerjs/presets'

import '@univerjs/preset-sheets-core/lib/index.css'

const props = withDefaults(defineProps<{ darkMode?: boolean, data?: Partial<IWorkbookData> }>(), {
  darkMode: false,
  data: () => ({}),
})

const container = useTemplateRef<HTMLElement>('container')

let univerInstance: Univer | null = null
let univerAPIInstance: FUniver | null = null

onMounted(() => {
  const { univer, univerAPI } = createUniver({
    theme: defaultTheme,
    darkMode: props.darkMode,
    locale: LocaleType.ZH_CN,
    locales: {
      [LocaleType.ZH_CN]: mergeLocales(
        UniverPresetSheetsCoreZhCN,
      ),
    },
    presets: [
      UniverSheetsCorePreset({
        header: false,
        container: container.value as HTMLElement,
      }),
    ],
  })
  univerAPI.createWorkbook(props.data)

  univerInstance = univer
  univerAPIInstance = univerAPI
})

onBeforeUnmount(() => {
  univerInstance?.dispose()
  univerAPIInstance?.dispose()
  univerInstance = null
  univerAPIInstance = null
})

watch(() => props.darkMode, (isDarkMode) => {
  univerAPIInstance?.toggleDarkMode(isDarkMode)
})
</script>

<template>
  <div ref="container" class="h-full" />
</template>
