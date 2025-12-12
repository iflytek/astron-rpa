import { createInjectionState } from '@vueuse/core'
import { shallowRef, markRaw, ref } from 'vue'
import { Sheet as SheetComponent } from '@rpa/components'

import type { TabConfig } from '../../types.ts'

import Sheet from './Sheet.vue'
import RightExtra from './RightExtra.vue'

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

  return { isReady, dataSheetConfig, sheetRef, handleUndo, handleRedo, handleFind, handleReady }
})

export { useProvideDataSheetStore, useDataSheetStore }
