import type { type ICellValue, type ISheetWorkbookData, Sheet as SheetComponent } from '@rpa/components'
import { createInjectionState } from '@vueuse/core'
import { get, isEmpty } from 'lodash-es'
import { markRaw, ref, shallowRef, watch } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore.ts'

import type { TabConfig } from '../../types.ts'

import RightExtra from './RightExtra.vue'
import Sheet from './Sheet.vue'

type SheetType = InstanceType<typeof SheetComponent>

const [useProvideDataSheetStore, useDataSheetStore] = createInjectionState(() => {
  const runningStore = useRunningStore()

  const sheetRef = shallowRef<SheetType>()
  const isReady = ref(false)

  const dataSheetConfig: TabConfig = {
    text: 'dataSheet',
    key: 'dataSheet',
    icon: 'sheet',
    component: markRaw(Sheet),
    rightExtra: markRaw(RightExtra),
  }

  const handleUndo = () => sheetRef.value?.undo()

  const handleRedo = () => sheetRef.value?.redo()

  const handleFind = () => sheetRef.value?.openFindDialog()

  const handleClearAll = () => {
    runningStore.clearDataTable()
  }

  const handleReady = () => {
    isReady.value = true
  }

  const createWorkbook = (workbookData: ISheetWorkbookData) => {
    sheetRef.value?.createWorkbook(workbookData)
  }

  const handleCellUpdate = (data: ICellValue[]) => {
    runningStore.updateDataTableCell(data.map(it => ({ row: it.row, col: it.column, value: it.value })))
  }

  watch(runningStore.dataTable, (newValue, oldValue) => {
    if (isEmpty(newValue) || isEmpty(oldValue)) {
      sheetRef.value?.clearAll()
    }

    if (isEmpty(newValue)) {
      return
    }

    const cellValue: ICellValue[] = []

    const maxRow = Math.max(newValue.max_row, oldValue?.max_row ?? 0)
    const maxCol = Math.max(newValue.max_column, oldValue?.max_column ?? 0)

    for (let row = 0; row < maxRow; row++) {
      for (let col = 0; col < maxCol; col++) {
        const newCellValue = get(newValue, [row, col])
        const oldCellValue = get(oldValue, [row, col])

        if (newCellValue !== oldCellValue) {
          cellValue.push({
            row,
            column: col,
            value: newCellValue,
          })
        }
      }
    }

    sheetRef.value?.updateCellValues(cellValue)
  })

  return {
    isReady,
    dataSheetConfig,
    sheetRef,
    handleUndo,
    handleRedo,
    handleFind,
    handleReady,
    handleCellUpdate,
    handleClearAll,
    createWorkbook,
  }
})

export { useDataSheetStore, useProvideDataSheetStore }
