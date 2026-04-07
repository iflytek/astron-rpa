import { message } from 'ant-design-vue'
import { uniq } from 'lodash-es'

import { betweenTowItem, getIdx, getMultiSelectIds } from '@/views/Arrange/utils/flowUtils'

export function changeSelectAtoms(curId: string | null, newIds, isSetLastClickItem = true) {
  // const flowStore = useFlowStore()
  // if (isSetLastClickItem)
  //   setLastClickAtomId(curId)
  // const selectedIds = newIds || (curId ? [curId] : [])
  // curId !== null && curId !== flowStore.activeAtom?.id && flowStore.setActiveAtom(flowStore.simpleFlowUIData.find(item => item.id === curId))
  // flowStore.setSelectedAtomIds(selectedIds)
}

// 记录鼠标最后一次点击的item数据信息
let lastClickAtomId = null
export function setLastClickAtomId(id: string) {
  lastClickAtomId = id
}

export function getLastClickAtomId() {
  return lastClickAtomId
}

// ctrl、shift多选
export function setMultiSelectByClick(item: any, index: number, ctrlKey, shiftKey) {
  // // 先得到已选中得节点
  // let newSelectIds = useFlowStore().selectedAtomIds || []

  // // 获取关联节点及子孙节点
  // const curIds = getMultiSelectIds(item.id)

  // let noShiftOps = true
  // if (shiftKey && lastClickAtomId) {
  //   noShiftOps = false
  //   // shift 连选 上一次点击和本次点击之间的全部选中
  //   if (lastClickAtomId === item.id) {
  //     newSelectIds = curIds
  //   }
  //   else {
  //     const lastIdx = getIdx(lastClickAtomId)
  //     const curStartIdx = getIdx(curIds[0])
  //     const curEndIdx = getIdx(curIds[curIds.length - 1])
  //     const firstIdx = Math.min(lastIdx, curStartIdx, curEndIdx)
  //     const secondIdx = Math.max(lastIdx, curStartIdx, curEndIdx)
  //     newSelectIds = betweenTowItem(firstIdx, secondIdx, useFlowStore().simpleFlowUIData).map(i => i.id)
  //   }
  //   console.log('shift多选ids：', newSelectIds)
  // }
  // else if (ctrlKey) {
  //   // ctrl多选
  //   if (!newSelectIds.includes(item.id)) {
  //     newSelectIds = newSelectIds.concat(curIds)
  //   }
  //   else {
  //     newSelectIds = newSelectIds.filter(sItem => !curIds.includes(sItem))
  //   }
  //   console.log('ctrl多选选择的', newSelectIds)
  // }
  // else {
  //   // 单选
  //   newSelectIds = curIds
  //   console.log('单选选择的', newSelectIds)
  // }

  // newSelectIds = uniq(newSelectIds)
  // console.log('选择的ids', newSelectIds)
  // changeSelectAtoms(item.id, newSelectIds, noShiftOps)
}
