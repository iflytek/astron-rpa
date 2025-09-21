import { message } from 'ant-design-vue'
import { last } from 'lodash-es'

import { isComponentKey } from '@/utils/customComponent'

import { useFlowStore } from '@/stores/useFlowStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { requiredItem } from '@/views/Arrange/components/flow/hooks/useValidate'
import { useToolsClear } from '@/views/Arrange/components/tools/hooks/useToolsClear'
import { Catch, Else, ElseIf, Finally, Group, GroupEnd, LOOP_END_MAP } from '@/views/Arrange/config/atomKeyMap'
import { getMultiSelectIds } from '@/views/Arrange/utils/flowUtils'
import { createComponentAbility, generateInputMap, loopAtomByKey, setAddAtomIdx } from '@/views/Arrange/utils/generateData'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

export async function createFlowNode(key: string, idx: number | number[], isDrag: boolean) {
  const flowStore = useFlowStore()
  const projectDocStore = useProjectDocStore()

  if (isComponentKey(key)) {
    await createComponentAbility(key)
  }
  else {
  // 加载原子能力配置
    await loopAtomByKey(key)
  }

  setAddAtomIdx(idx)

  const atom = generateInputMap(key, [Catch, Finally].includes(key))

  if (!atom)
    return message.error('该原子能力不存在')

  const arr = Array.isArray(idx) ? idx : [idx]
  let curIdx = arr[0]
  let groupSelectIds = []
  if (key === Group) {
    const id = flowStore.simpleFlowUIData[curIdx]?.id ?? ''
    projectDocStore.insertASTGroupNode([atom[0].id, atom[1].id], [id, flowStore.simpleFlowUIData[last(arr) - 2].id])
    flowStore.setSimpleFlowUIDataProps(curIdx, last(arr) - 1, item => item.level = projectDocStore.gainASTNodeById(item.id).level)
    groupSelectIds = flowStore.simpleFlowUIData.slice(curIdx, last(arr) - 1).map(i => i.id)
  }
  else {
    const id = flowStore.simpleFlowUIData[curIdx === 0 ? 1 : curIdx - 1]?.id ?? ''
    projectDocStore.insertASTFlowNode(id, curIdx, atom, false)
  }

  atom.forEach((i, atomIdx) => {
    if (i.key === GroupEnd)
      curIdx = last(arr)

    if (Object.keys(LOOP_END_MAP).concat([ElseIf, Else]).includes(i.key)) {
      i.hasFold = true
      i.isOpen = true
    }

    i.checked = true
    i.level = projectDocStore.gainASTNodeById(i.id).level
    i.nodeError = requiredItem(i)
    flowStore.setSimpleFlowUIDataByType(i, curIdx, isDrag && atomIdx === 0 && i.key !== Group)
    curIdx++
  })

  setTimeout(() => {
    projectDocStore.addProcessNode(idx, atom)
    changeSelectAtoms(atom[0].id, atom.map(i => i.id).concat(groupSelectIds), true)
  })

  return atom
}

export function deleteFlowNode(deleteNodes: string[]) {
  const arr = deleteNodes
  const flowStore = useFlowStore()
  if (arr.length === flowStore.simpleFlowUIData.length && flowStore.simpleFlowUIData.length > 50) {
    useToolsClear().clickFn()
    return
  }
  const findIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === arr[0])
  const lastIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === arr[arr.length - 1])
  const filterList = flowStore.simpleFlowUIData.filter(item => !arr.includes(item.id))
  const flag = findIdx >= filterList.length
  const startIdx = flag ? filterList.length - 1 : findIdx
  flowStore.setSimpleFlowUIData(filterList, flag ? startIdx : startIdx + 1)
  if (startIdx > -1) {
    if (arr[0].includes('group_') && arr.length === 2)
      flowStore.setSimpleFlowUIDataProps(startIdx, lastIdx - 1, item => item.level -= 1)
    const activeId = flowStore.simpleFlowUIData[startIdx].id
    if (activeId) {
      const conditionIds = getMultiSelectIds(activeId)
      changeSelectAtoms(activeId, conditionIds, true)
    }
  }
  setTimeout(() => {
    useProjectDocStore().deleteASTFlowNode(arr as string[])
    useProjectDocStore().deleteProcessNode(arr as string[])
  })
}
