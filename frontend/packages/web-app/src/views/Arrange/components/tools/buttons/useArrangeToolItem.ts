import { computed } from 'vue'

import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

type CheckFn = boolean | ((data: { status: string, isBreak?: boolean, canUndo?: boolean, canRestore?: boolean }) => boolean)

function toolBtnFn(fn: CheckFn | undefined, data: { status: string, isBreak?: boolean, canUndo?: boolean, canRestore?: boolean }): boolean {
  if (typeof fn === 'function')
    return fn(data)
  return fn || false
}

export function useArrangeToolItemState(item: ArrangeTools) {
  const runningStore = useRunningStore()

  const show = computed(() => {
    const status = runningStore.running
    return toolBtnFn(item.show, { status })
  })

  const disabled = computed(() => {
    const status = runningStore.running
    const isBreak = runningStore.debugData?.is_break || false
    return toolBtnFn(item.disable, { status, isBreak })
  })

  const handleClick = () => {
    const allow = item.validateFn?.({ disable: disabled.value, show: show.value }) ?? true
    if (!allow)
      return
    item.clickFn?.()
  }

  return {
    show,
    disabled,
    handleClick,
  }
}

