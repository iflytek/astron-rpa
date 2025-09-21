import { applyPatches, enablePatches, produceWithPatches } from 'immer'
import type { Patch } from 'immer'
import { computed, ref, shallowRef } from 'vue'

enablePatches()

const MAX_HISTORY_LENGTH = 100

export interface UndoStackItem {
  patches: Patch[]
  inversePatches: Patch[]
}

export function useHistory<T>(baseState: T) {
  // 历史记录
  const history = shallowRef<UndoStackItem[]>([])
  // 当前索引
  const currentIndex = ref(-1)

  const state = shallowRef(baseState)

  // 执行操作并记录补丁
  const perform = (operation: (draft: T) => void | Promise<void> | T) => {
    const [newState, patches, inversePatches] = produceWithPatches(operation)(state.value)

    // 如果状态没有变化，直接返回
    if (patches.length === 0)
      return

    // 清除当前索引之后的历史记录
    history.value = history.value.slice(0, currentIndex.value + 1)

    // 添加新补丁到历史记录
    history.value.push({ patches, inversePatches })
    currentIndex.value++

    // 限制历史记录大小
    if (history.value.length > MAX_HISTORY_LENGTH) {
      history.value.shift()
      currentIndex.value--
    }

    state.value = newState
  }

  // 撤销操作
  const undo = () => {
    if (!canUndo.value)
      return

    const { inversePatches } = history.value[currentIndex.value]
    state.value = applyPatches(state.value, inversePatches)
    currentIndex.value--
  }

  // 重做操作
  const redo = () => {
    if (!canRedo.value)
      return

    currentIndex.value++
    const { patches } = history.value[currentIndex.value]
    state.value = applyPatches(state.value, patches)
  }

  // 检查是否可以撤销
  const canUndo = computed<boolean>(() => {
    return currentIndex.value >= 0
  })

  // 检查是否可以重做
  const canRedo = computed<boolean>(() => {
    return currentIndex.value < history.value.length - 1
  })

  return { canUndo, canRedo, state, perform, undo, redo }
}
