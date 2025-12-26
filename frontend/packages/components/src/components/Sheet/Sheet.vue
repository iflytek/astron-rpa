<script lang="ts" setup>
import { theme } from 'ant-design-vue'
import { useTemplateRef, onBeforeUnmount, onMounted, watch } from 'vue'
import type { FUniver, Univer, IWorkbookData, CellValue } from '@univerjs/presets'
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core'
import UniverPresetSheetsCoreZhCN from '@univerjs/preset-sheets-core/locales/zh-CN'
import UniverPresetSheetsCoreEnUS from '@univerjs/preset-sheets-core/locales/en-US'
import { createUniver, LocaleType, mergeLocales, defaultTheme, LogLevel } from '@univerjs/presets'
import { generate } from '@ant-design/colors';
import { UniverSheetsFindReplacePreset } from '@univerjs/preset-sheets-find-replace'
import sheetsFindReplaceZhCN from '@univerjs/preset-sheets-find-replace/locales/zh-CN'
import sheetsFindReplaceEnUS from '@univerjs/preset-sheets-find-replace/locales/en-US'

import '@univerjs/preset-sheets-core/lib/index.css'
import '@univerjs/preset-sheets-find-replace/lib/index.css'

interface SheetProps {
  darkMode?: boolean
  locale?: LocaleType
  readonly?: boolean
  deafaultValue?: Partial<IWorkbookData>
}

const props = withDefaults(defineProps<SheetProps>(), {
  darkMode: false,
  locale: LocaleType.ZH_CN,
  deafaultValue: () => ({})
})

const emits = defineEmits<{
  (e: 'ready'): void
  (e: 'cellUpdate', row: number, column: number, value: CellValue | null): void
}>()

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
    logLevel: LogLevel.WARN,
    theme: themeToUse,
    darkMode: props.darkMode,
    locale: props.locale,
    locales: {
      [LocaleType.ZH_CN]: mergeLocales(
        UniverPresetSheetsCoreZhCN,
        sheetsFindReplaceZhCN,
      ),
      [LocaleType.EN_US]: mergeLocales(
        UniverPresetSheetsCoreEnUS,
        sheetsFindReplaceEnUS,
      ),
    },
    presets: [
      UniverSheetsCorePreset({
        header: false,
        contextMenu: !props.readonly,
        footer: false,
        container: container.value as HTMLElement,
      }),
      UniverSheetsFindReplacePreset(),
    ],
  })

  // 添加生命周期监听事件
  univerAPI.addEvent(
    univerAPI.Event.LifeCycleChanged,
    ({ stage }) => {
      if (stage === univerAPI.Enum.LifecycleStages.Rendered) {
        if (!props.readonly) return

        const fWorkbook = univerAPI.getActiveWorkbook()!
        const unitId = fWorkbook.getId()

        // disable selection
        fWorkbook.disableSelection()

        // set read only
        const permission = fWorkbook.getPermission()
        permission.setWorkbookEditPermission(unitId, false)
        permission.setPermissionDialogVisible(false)
      } else if (stage === univerAPI.Enum.LifecycleStages.Steady) {
        emits('ready')
      }
    },
  )

  univerAPI.createWorkbook(props.deafaultValue)

  // univerAPI.addEvent(univerAPI.Event.SheetEditEnded, (params) => {
  //   const { worksheet, row, column } = params
  //   const cellValue = worksheet.getRange(row, column).getValue();
  //   emits('cellUpdate', row, column, cellValue)
  // })

  univerAPI.addEvent(univerAPI.Event.SheetValueChanged, (params) => {
    const fWorkbook = univerAPIInstance?.getActiveWorkbook()
    if (!fWorkbook) return

    const fWorksheet = fWorkbook.getActiveSheet()
    const values = params.effectedRanges.map(it => {
      const { startRow, startColumn, endColumn, endRow } = it.getRange();
      const values = it.getValues();
    })
    
    console.log(1111, values)
  })

  // univerAPI.addEvent(univerAPI.Event.CommandExecuted, (params) => {
  //   const { id } = params
  //   console.log(params)
  //   if (id === 'doc.command.insert-text' || id === 'doc.command.delete-text') {
  //     console.log(id)
  //   }
  // })

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

defineExpose({
  undo: () => univerAPIInstance?.undo(),
  redo: () => univerAPIInstance?.redo(),
  // 打开查找替换弹窗
  openFindDialog: () => {
    univerAPIInstance?.executeCommand("ui.operation.open-find-dialog")
  },
  createWorkbook: (workbookData: IWorkbookData) => {
    univerAPIInstance?.createWorkbook(workbookData)
  },
  // 清空全部数据
  clearAll: () => {
    univerAPIInstance?.createWorkbook({})
  },
  // 删除选中区域内容
  deleteSelection: () => {
    const fWorkbook = univerAPIInstance?.getActiveWorkbook()
    if (!fWorkbook) return

    const fWorksheet = fWorkbook.getActiveSheet()
    // 获取激活选区的范围
    const fSelection = fWorksheet.getSelection()
    const activeRange = fSelection?.getActiveRange()
    activeRange?.clear()
  },
})
</script>

<template>
  <div ref="container" class="h-full" />
</template>
