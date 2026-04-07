import { createInjectionState } from '@vueuse/core'
import { computed, ref } from 'vue'

import { IncrementalASTParser, VisualEditor } from '../../../canvasManager'

interface InitParams {
  resourceId: string
  manage: VisualEditor
}

const [useFlowStateProvide, useFlowState] = createInjectionState((params: InitParams) => {
  // 右键选中的 atom
  let rightClickSelectedAtomTimer: NodeJS.Timeout | null = null
  const rightClickSelectedAtom = ref<RPA.Atom | null>(null)
  const contextMenuVisible = ref(false)

  const astParser = computed<IncrementalASTParser>(() => params.manage.astParser)
  const rawList = computed<RPA.Atom[]>(() => params.manage.state.data ?? [])

  const hideContextMenu = () => {
    contextMenuVisible.value = false

    // 等收起动画结束后再清空选中状态
    rightClickSelectedAtomTimer = setTimeout(() => {
      rightClickSelectedAtom.value = undefined
    }, 200)
  }

  const setRightClickSelectedAtom = (atom: RPA.Atom) => {
    rightClickSelectedAtom.value = atom
    clearTimeout(rightClickSelectedAtomTimer)
  }

  return {
    flowManager: params.manage,
    resourceId: params.resourceId,
    rightClickSelectedAtom,
    contextMenuVisible,
    astParser,
    rawList,
    hideContextMenu,
    setRightClickSelectedAtom,
  }
})

export { useFlowState, useFlowStateProvide }
