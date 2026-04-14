import { message } from 'ant-design-vue'
import { nextTick } from 'vue'

import i18next from '@/plugins/i18next'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { DISABLED_BREAKPOINT_TYPE, PAGE_LEVEL_INDENT } from '@/views/Arrange/config/flow'
import type { VisualEditor } from '@/views/Arrange/canvasManager'

export function getBreakpointClass(atomData?: RPA.Atom) {
  const cls = ['row-breakpoint']
  atomData?.breakpoint && cls.push('active')
  atomData?.key && DISABLED_BREAKPOINT_TYPE.includes(atomData.key) && cls.push('disabled')
  return cls.join(' ')
}

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

export function toggleBreakPoint(flowManager: VisualEditor, atomIds: string[], flag: boolean) {
  const breakList: Array<{ process_id: string, line: number }> = []

  for (const atomId of atomIds) {
    const atom = flowManager.state.data.find(item => item.id === atomId)
    if (!atom) {
      continue
    }
    if (DISABLED_BREAKPOINT_TYPE.includes(atom.key)) {
      message.warning(i18next.t('arrange.breakpointNotAllowed'))
      continue
    }

    const node = flowManager.astParser.getNode(atomId)
    if (!node) {
      continue
    }

    node.raw.breakpoint = flag
    breakList.push({
      process_id: flowManager.id,
      line: flowManager.state.data.findIndex(item => item.id === atomId) + 1,
    })
  }

  if (!breakList.length) {
    return
  }

  flowManager.updateData()
  flowManager.updateState({ isDirty: true })
  useRunningStore().breakPointDebug(flag, breakList)
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
