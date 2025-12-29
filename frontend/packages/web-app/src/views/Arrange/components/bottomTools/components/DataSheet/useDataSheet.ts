import { createInjectionState } from '@vueuse/core'
import { shallowRef, markRaw, ref } from 'vue'
import { Sheet as SheetComponent, type ISheetWorkbookData, type ICellValue } from '@rpa/components'

import { useRunningStore } from '@/stores/useRunningStore.ts'

import type { TabConfig } from '../../types.ts'

import Sheet from './Sheet.vue'
import RightExtra from './RightExtra.vue'

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

  const handleReady = () => {
    isReady.value = true
  }

  const createWorkbook = (workbookData: ISheetWorkbookData) => {
    sheetRef.value?.createWorkbook(workbookData)
  }

  const handleCellUpdate = (data: ICellValue[]) => {
    // runningStore.updateDataTableCell({ row, col: column, value })
    console.log(data)
  }

  return {
    isReady,
    dataSheetConfig,
    sheetRef,
    handleUndo,
    handleRedo,
    handleFind,
    handleReady,
    handleCellUpdate,
    createWorkbook
  }
})

export { useProvideDataSheetStore, useDataSheetStore }
