import { createInjectionState } from '@vueuse/core'
import { shallowRef, markRaw, ref } from 'vue'
import { NiceModal, Sheet as SheetComponent, sheetUtils } from '@rpa/components'

import _ImportModal from './ImportModal.vue'
import type { TabConfig } from '../../types.ts'

import Sheet from './Sheet.vue'
import RightExtra from './RightExtra.vue'

const ImportModal = NiceModal.create(_ImportModal)

type SheetType = InstanceType<typeof SheetComponent>

const [useProvideDataSheetStore, useDataSheetStore] = createInjectionState(() => {
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

  const handleImport = async () => {
    const workbookData = await sheetUtils.importExcelFile()
    NiceModal.show(ImportModal, { workbookData })
  }

  return { isReady, dataSheetConfig, sheetRef, handleUndo, handleRedo, handleFind, handleReady, handleImport }
})

export { useProvideDataSheetStore, useDataSheetStore }
