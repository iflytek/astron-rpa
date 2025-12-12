<script lang="ts" setup>
import { theme } from 'ant-design-vue'
import { useTemplateRef, onBeforeUnmount, onMounted, watch } from 'vue'
import type { FUniver, Univer, IWorkbookData } from '@univerjs/presets'
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core'
import UniverPresetSheetsCoreZhCN from '@univerjs/preset-sheets-core/locales/zh-CN'
import UniverPresetSheetsCoreEnUS from '@univerjs/preset-sheets-core/locales/en-US'
import { createUniver, LocaleType, mergeLocales, defaultTheme } from '@univerjs/presets'
import { generate } from '@ant-design/colors';

import '@univerjs/preset-sheets-core/lib/index.css'

interface SheetProps {
  darkMode?: boolean
  data?: Partial<IWorkbookData>
  locale?: LocaleType
}

const props = withDefaults(defineProps<SheetProps>(), {
  darkMode: false,
  locale: LocaleType.ZH_CN,
  data: () => ({}),
})

const container = useTemplateRef<HTMLElement>('container')

const { token } = theme.useToken()

let univerInstance: Univer | null = null
let univerAPIInstance: FUniver | null = null

onMounted(() => {
  const colors = generate(token.value.colorPrimary);

  const themeToUse = {
    ...defaultTheme,
    primary: {
      50: colors[0],
      100: colors[1],
      200: colors[2],
      300: colors[3],
      400: colors[4],
      500: colors[5],
      600: colors[6],
      700: colors[7],
      800: colors[8],
      900: colors[9],
    }
  }

  const { univer, univerAPI } = createUniver({
    theme: themeToUse,
    darkMode: props.darkMode,
    locale: props.locale,
    locales: {
      [LocaleType.ZH_CN]: mergeLocales(
        UniverPresetSheetsCoreZhCN,
      ),
      [LocaleType.EN_US]: mergeLocales(
        UniverPresetSheetsCoreEnUS,
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

watch(() => props.locale, (locale) => {
  univerAPIInstance?.setLocale(locale)
})
</script>

<template>
  <div ref="container" class="h-full" />
</template>
