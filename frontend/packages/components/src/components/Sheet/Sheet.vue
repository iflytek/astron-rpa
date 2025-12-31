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
import { set } from 'lodash-es'

import '@univerjs/preset-sheets-core/lib/index.css'
import '@univerjs/preset-sheets-find-replace/lib/index.css'

interface SheetProps {
  darkMode?: boolean
  locale?: LocaleType
  readonly?: boolean
  defaultValue?: Partial<IWorkbookData>
}

export interface ICellValue {
  row: number
  column: number
  value: CellValue | null
}

const props = withDefaults(defineProps<SheetProps>(), {
  darkMode: false,
  locale: LocaleType.ZH_CN,
  defaultValue: () => ({})
})

const emits = defineEmits<{
  (e: 'ready'): void
  (e: 'cellUpdate', data: ICellValue[]): void
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

  univerAPI.createWorkbook(props.defaultValue)

  univerAPI.addEvent(univerAPI.Event.SheetValueChanged, (params) => {
    const cellValues: ICellValue[] = params.effectedRanges.flatMap(it => {
      const { startRow, startColumn } = it.getRange();
      const values = it.getValues();
      
      // 将二维数组转换为 ICellValue 数组
      const result: ICellValue[] = []
      for (let i = 0; i < values.length; i++) {
        const row = startRow + i
        const rowValues = values[i] || []
        for (let j = 0; j < rowValues.length; j++) {
          const column = startColumn + j
          result.push({
            row,
            column,
            value: rowValues[j] ?? null
          })
        }
      }
      return result
    })
    
    emits('cellUpdate', cellValues)
  })

  univerInstance = univer
  univerAPIInstance = univerAPI
})

const getWorkbookData = () => {
  const fWorkbook = univerAPIInstance?.getActiveWorkbook()
  if (!fWorkbook) return
  return fWorkbook.save()
}

const createWorkbook = (workbookData: Partial<IWorkbookData>) => {
  univerAPIInstance?.createWorkbook(workbookData)
}

const updateCellValues = (values: ICellValue[]) => {
  const fWorkbook = univerAPIInstance?.getActiveWorkbook()
  const fWorksheet = fWorkbook?.getActiveSheet()
  const fRange = fWorksheet?.getRange('A1:B2')
  
  const cellValue: CellValue[][] = []
  values.forEach(it => set(cellValue, [it.row, it.column], it.value));

  fRange?.setValues(cellValue)
}

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
  getWorkbookData,
  createWorkbook,
  updateCellValues,
  undo: () => univerAPIInstance?.undo(),
  redo: () => univerAPIInstance?.redo(),
  // 打开查找替换弹窗
  openFindDialog: () => {
    univerAPIInstance?.executeCommand("ui.operation.open-find-dialog")
  },
  // 清空全部数据
  clearAll: () => createWorkbook({}),
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
