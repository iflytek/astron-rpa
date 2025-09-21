import { message } from 'ant-design-vue'
import { isUndefined, last } from 'lodash-es'
import { nextTick } from 'vue'

import { recordAtomUsage } from '@/utils/atomHistory'
import BUS from '@/utils/eventBus'

import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { changeDisable } from '@/views/Arrange/components/flow/hooks/useChangeStatus'
import { createFlowNode, deleteFlowNode } from '@/views/Arrange/components/flow/hooks/useFlowItem'
import { Group } from '@/views/Arrange/config/atomKeyMap'
import { ERR_PARENT_NOT_CONTAINS_ALL_CHILD } from '@/views/Arrange/config/errors'
import { DISABLED_BREAKPOINT_TYPE, PAGE_LEVEL_INDENT } from '@/views/Arrange/config/flow'
import { getClipBoardData, setClipBoardData } from '@/views/Arrange/utils/clipbord'
import { toggleContextmenu } from '@/views/Arrange/utils/contextMenu'
import { backContainNodeIdx, getMultiSelectIds, isContinuous, validateSelectedNodes } from '@/views/Arrange/utils/flowUtils'
import { loopAtomByKey } from '@/views/Arrange/utils/generateData'
import { generatePasteAtoms } from '@/views/Arrange/utils/generatePasteData'
import { addMultiSelectId, changeSelectAtoms, deleteMultiSelectId, getLastClickAtomId, setMultiSelectByClick } from '@/views/Arrange/utils/selectItemByClick'

export const MAX_ATOM_NUM = 2000

export function getBreakpointClass(atomData?: any) {
  // console.log('断点')
  const cls = ['row-breakpoint']
  atomData.breakpoint && cls.push('active')
  DISABLED_BREAKPOINT_TYPE.includes(atomData.key) && cls.push('disabled')
  return cls.join(' ')
}

// 拖动时，修改占位缩进
export function draggableAddStyle() {
  nextTick(() => {
    const ghost = document.querySelector('#listwrapper .sortable-ghost') as HTMLElement
    const prevNode = ghost.previousSibling
    const nextNode = ghost.nextSibling
    const level = Math.max(
      Reflect.get(prevNode || {}, '__draggable_context')?.element.level || 1,
      Reflect.get(nextNode || {}, '__draggable_context')?.element.level || 1,
    )
    ghost.style.setProperty('--indent', `${82 + (level - 1) * PAGE_LEVEL_INDENT}px`)
  })
}

// 添加原子能力
export async function addAtomData(key: string, preIndex?: number | number[], isDrag = false) {
  const { simpleFlowUIData, activeAtom } = useFlowStore()

  let idx = preIndex
  if (isUndefined(idx)) {
    idx = activeAtom ? simpleFlowUIData.findIndex(i => i.id === activeAtom.id) + 1 : simpleFlowUIData.length
  }

  const atom = await createFlowNode(key, idx, isDrag)
  // 记录原子能力使用历史
  if (key) {
    const atom = useProcessStore().atomicTreeDataFlat.find(atom => atom.key === key)
    atom && recordAtomUsage(atom)
  }
  BUS.$emit('toggleAtomForm', true)

  return atom
}

// 移动原子能力
export function moveAtomData(from: number, to: number, dragId: string) {
  const endIdx = backContainNodeIdx(dragId)
  const conditionId = getMultiSelectIds(dragId)
  if ((endIdx > -1 && from < to && endIdx >= to) || (to > 0 && useFlowStore().simpleFlowUIData[to - 1].id === conditionId[conditionId.length - 1])) {
    const dragAtom = useFlowStore().simpleFlowUIData.splice(to, 1)
    useFlowStore().setSimpleFlowUIDataByType(dragAtom, from, false)
    return
  }
  useProjectDocStore().moveProcessNode(from, to, dragId)
  changeSelectAtoms(dragId, conditionId, true)
}

// 编组
export function group(atomIds: string[]) {
  let allIds = atomIds
  if (atomIds.length === 2 && atomIds.every(id => id.startsWith('group_'))) {
    allIds = getMultiSelectIds(atomIds[0])
  }
  let idxList = allIds.map(i => useFlowStore().simpleFlowUIData.findIndex(ui => ui.id === i))
  if (!isContinuous(idxList)) {
    message.error('所选节点不连续')
    return false
  }
  idxList = idxList.sort((a, b) => a - b)
  addAtomData(Group, [idxList[0], last(idxList) + 2])
  toggleContextmenu({ visible: false })
}

// 解组
export function ungroup(atomIds: string[]) {
  deleteFlowNode(atomIds)
  toggleContextmenu({ visible: false })
}

function validateAndDeleteNodes(atomIds: string[], isCut: boolean = false) {
  const errors = validateSelectedNodes(atomIds)

  if (errors.includes(ERR_PARENT_NOT_CONTAINS_ALL_CHILD)) {
    message.warning('所选原子能力中存在未选择的子级，不可操作')
    return false
  }

  if (isCut) {
    const allSelectItem = atomIds.map(i => useProjectDocStore().userFlowNode().find(item => item.id === i))
    setClipBoardData(useProcessStore().project.id, allSelectItem, 'cut')
  }

  deleteFlowNode(atomIds)
  toggleContextmenu({ visible: false })
  return true
}

// 删除原子能力
export function deleteAtomData(deleteNodes: string[]) {
  validateAndDeleteNodes(deleteNodes)
  if (useFlowStore().simpleFlowUIData.length < 1) {
    BUS.$emit('toggleAtomForm', false)
  }
}

// 批量启用/禁用
export function batchToggleNode(atomIds: string[], atom: any) {
  const flag = atom.disabled
  changeDisable(atomIds, !flag)
  const idxArr = []
  const nodes = []
  atomIds.forEach((i) => {
    const idx = useFlowStore().simpleFlowUIData.findIndex(ui => ui.id === i)
    idxArr.push(idx)
    nodes.push(useFlowStore().simpleFlowUIData[idx])
  })
  useProjectDocStore().updateProcessNode(idxArr, nodes)
  if (atomIds.includes(useFlowStore().activeAtom?.id)) {
    useFlowStore().activeAtom.disabled = !flag
  }
  toggleContextmenu({ visible: false })
}

export function toggleBreakPoint(atomIds: string[], flag: boolean) {
  const flowUIData = useFlowStore().simpleFlowUIData
  const docStore = useProjectDocStore()
  atomIds.forEach((i) => {
    const findIdx = flowUIData.findIndex(ui => ui.id === i)
    if (DISABLED_BREAKPOINT_TYPE.includes(flowUIData[findIdx]?.key)) {
      return message.warning('该节点不可添加/移除断点')
    }
    flowUIData[findIdx].breakpoint = flag
    docStore.updateProcessNode([findIdx], [flowUIData[findIdx]])
  })
  useRunningStore().breakPointDebug(flag, atomIds.map((i) => { return { process_id: useProcessStore().activeProcessId, line: flowUIData.findIndex(ui => ui.id === i) + 1 } }))
  toggleContextmenu({ visible: false })
}

// 展开折叠
export function toggleFold(atom: RPA.Atom) {
  atom.isOpen = !atom.isOpen
  useFlowStore().setFlowNodeExpand(atom)
  toggleContextmenu({ visible: false })
};

// 点击原子能力
export function clickAtom($event: MouseEvent, atomData?: RPA.Atom) {
  toggleContextmenu({
    visible: false,
  })
  const findIdx = useFlowStore().simpleFlowUIData.findIndex(i => i.id === atomData?.id)
  if (findIdx === -1)
    return
  if (useFlowStore().multiSelect) {
    console.log('选中状态', atomData.checked)
    // 开启多选模式时-不支持ctrl、shift多选，如果已经选中，则取消选中，否则选中
    atomData.checked ? deleteMultiSelectId(atomData.id) : addMultiSelectId(atomData.id)
    useFlowStore().setActiveAtom(useFlowStore().simpleFlowUIData[findIdx])
  }
  else {
    // 未开启多选模式时，支持ctrl、shift多选
    setMultiSelectByClick(atomData, findIdx, $event.ctrlKey, $event.shiftKey)
  }
}

// 双击原子能力
export function dbclickAtom($event: MouseEvent, atomData?: RPA.Atom) {
  toggleContextmenu({
    visible: false,
  })
  const findIdx = useFlowStore().simpleFlowUIData.findIndex(i => i.id === atomData?.id)
  if (useFlowStore().multiSelect) {
    // 开启多选模式时-不支持ctrl、shift多选，如果未选中，则选中
    !atomData.checked && addMultiSelectId(atomData.id)
    useFlowStore().setActiveAtom(useFlowStore().simpleFlowUIData[findIdx])
  }
  else {
    setMultiSelectByClick(atomData, findIdx, $event.ctrlKey, $event.shiftKey)
  }
  BUS.$emit('toggleAtomForm', true)
}

// 开启多选模式，复选框change
export function checkboxChange(checkValue: boolean, atomData?: any) {
  checkValue ? addMultiSelectId(atomData.id) : deleteMultiSelectId(atomData.id)
}

// 右键菜单
export function contextmenu($event: MouseEvent, atomData?: any) {
  toggleContextmenu({
    visible: true,
    $event,
    atom: atomData,
  })
}

export function copy(atomIds: string[]) {
  const flowStore = useFlowStore()
  const processStore = useProcessStore()
  const allSelectUserItem = flowStore.simpleFlowUIData.reduce((acc, item) => {
    if (atomIds.includes(item.id))
      acc.push(item)
    return acc
  }, [] as any[])
  setClipBoardData(processStore.project.id, allSelectUserItem, 'copy')
  toggleContextmenu({ visible: false })
  message.success('复制成功')
}

export function cut(atomIds: string[]) {
  validateAndDeleteNodes(atomIds, true)
}

export function paste() {
  const flowStore = useFlowStore()
  toggleContextmenu({ visible: false })
  getClipBoardData((clipBoardData) => {
    const clipBoardAtoms = clipBoardData.atoms
    const lastSelectId = getLastClickAtomId() ?? flowStore.selectedAtomIds[flowStore.selectedAtomIds.length - 1]
    if (!clipBoardAtoms) {
      message.warning('剪切板为空，不可粘贴')
      return
    }
    if (flowStore.simpleFlowUIData.length && !flowStore.activeAtom) {
      message.warning('请选中一个节点，在后面粘贴')
      return
    }
    const pasteAtoms = generatePasteAtoms(clipBoardAtoms)
    Promise.allSettled(pasteAtoms.map(i => loopAtomByKey(i.key))).then(() => {
      let idx = flowStore.simpleFlowUIData.findIndex(i => i.id === lastSelectId) + 1
      useProjectDocStore().insertASTFlowNode(lastSelectId, idx, pasteAtoms, false)
      useProjectDocStore().addProcessNode(idx, pasteAtoms)
      pasteAtoms.forEach((item) => {
        item.level = useProjectDocStore().gainASTNodeById(item.id).level
        flowStore.setSimpleFlowUIDataByType(item, idx, false)
        idx++
      })
      changeSelectAtoms(pasteAtoms[pasteAtoms.length - 1].id, pasteAtoms.map(i => i.id), true)
    })
  })
}

export function debug(atomIds: any) {
  const processStore = useProcessStore()

  const idxList = atomIds.map(i => useFlowStore().simpleFlowUIData.findIndex(ui => ui.id === i))
  if (atomIds.length > 0 && !isContinuous(idxList)) {
    message.warning('当前选择的节点不相连，不可运行调试')
    return false
  }
  processStore.saveProject().then(() => {
    const startLine = idxList[0] + 1
    const endLine = atomIds.length === 1 ? startLine : idxList[idxList.length - 1] + 1
    useRunningStore().startRun(useProcessStore().project.id, useProcessStore().activeProcessId, startLine, endLine)
  })
}

export function recordFromHere(atomIds: any) {
  console.log('recordFromHere', atomIds)
}

export function runFromHere(atomIds: string[]) {
  const processStore = useProcessStore()

  processStore.saveProject().then(() => {
    useRunningStore().startRun(useProcessStore().project.id, useProcessStore().activeProcessId, useFlowStore().simpleFlowUIData.findIndex(ui => ui.id === atomIds[0]) + 1)
  })
}

export function addDataBatchAtomData() {
  addAtomData('BrowserElement.data_batch')
}
