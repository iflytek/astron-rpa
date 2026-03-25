import { nextTick } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { PAGE_LEVEL_INDENT } from '@/views/Arrange/config/flow'

// 拖动时，修改占位缩进
export function draggableAddStyle(flowManager?: { containerRef?: { value: HTMLElement | null } }) {
  nextTick(() => {
    const ghost = flowManager?.containerRef?.value?.querySelector('.sortable-ghost') as HTMLElement
    if (!ghost)
      return
    const prevNode = ghost.previousSibling
    const nextNode = ghost.nextSibling
    const level = Math.max(
      Reflect.get(prevNode || {}, '__draggable_context')?.element.level || 1,
      Reflect.get(nextNode || {}, '__draggable_context')?.element.level || 1,
    )
    ghost.style.setProperty('--indent', `${82 + (level - 1) * PAGE_LEVEL_INDENT}px`)
  })
}

export function recordFromHere(atomIds: any) {
  console.log('recordFromHere', atomIds)
}

export function runFromHere(atomIds: string[]) {
  const processStore = useProcessStore()

  // processStore.saveProject().then(() => {
  //   useRunningStore().startRun(useProcessStore().project.id, useProcessStore().activeProcessId, useFlowStore().simpleFlowUIData.findIndex(ui => ui.id === atomIds[0]) + 1)
  // })
}
