import { useProcessStore } from '@/stores/useProcessStore'

/**
 * 获取数组中和当前节点同一层级的节点
 * @param curItem 当前节点
 * @param lastId 尾节点id
 * @returns 同级列表Ids
 */
export function getCommonLevel(curItem: RPA.Atom, lastId: string) {
  // const flowStore = useFlowStore()
  // const findItem = flowStore.simpleFlowUIData.find(i => i.id === lastId)
  // if (findItem) {
  //   return findItem.level === curItem.level
  // }
}

export function backContainNodeIdx(idOrIndex: string | number) {
  // const flowStore = useFlowStore()
  // const nodeMap = flowStore.nodeContactMap
  // let findId = ''
  // if (typeof idOrIndex === 'number')
  //   idOrIndex = flowStore.simpleFlowUIData[idOrIndex].id
  // for (const key in nodeMap) {
  //   if (Object.prototype.hasOwnProperty.call(nodeMap, key)) {
  //     const element = nodeMap[key]
  //     if (idOrIndex === key) {
  //       findId = element
  //       break
  //     }
  //     if (idOrIndex === element) {
  //       findId = key
  //       break
  //     }
  //   }
  // }
  // return flowStore.simpleFlowUIData.findIndex(i => i.id === findId)
}

export function generateContactIds() {
  // const nodeMap = useFlowStore().nodeContactMap
  // const startKeys = Object.keys(nodeMap)
  // const endKeys = startKeys.map(key => nodeMap[key])
  // return {
  //   startKeys,
  //   endKeys,
  //   contactMap: nodeMap,
  // }
}

export function getIdx(id: string) {
  // return useFlowStore().simpleFlowUIData.findIndex(i => i.id === id)
  return 0
}

/**
 * 获取两个列表项之间的所有数据
 * @param first 第一个节点idx
 * @param second 第二个节点idx
 * @param arr 数组
 * @returns 两个列表项之间的节点id
 */
export function betweenTowItem(first, second, arr) {
  const firstIdx = Math.min(first, second)
  const secondIdx = Math.max(first, second)
  return arr.slice(firstIdx, secondIdx + 1)
}

export function isContinuous(arr: number[]) {
  const set = new Set(arr)
  return set.size === arr.length && Math.max(...set) - Math.min(...set) + 1 === arr.length
}

export function getProjectAllFlow() {
  const processStore = useProcessStore()
  const allFlowList = {}
  // processStore.processList.filter(i => i.resourceCategory !== 'module').forEach((item) => {
  //   allFlowList[item.resourceId] = useProjectDocStore().userFlowNode(item.resourceId)
  // })
  return { allFlowList }
}

// 获取流程数据种当前选择的节点、关联节点和其子节点
export function getMultiSelectIds(id: string) {
  if (!id)
    return []
  // const { startKeys, endKeys, contactMap } = generateContactIds()

  let currentIds = [id]

  let startId = ''
  let endId = ''
  // // 当前是嵌套类的起始节点
  // if (startKeys.includes(id)) {
  //   startId = id
  //   endId = contactMap[id]
  // }

  // // 当前是嵌套类的结束节点
  // if (endKeys.includes(id)) {
  //   startId = startKeys[endKeys.findIndex(endId => endId === id)]
  //   endId = id
  // }

  // // 一个结束节点可能对应多个起始节点，找出结束节点对应的所有的开始节点
  // const relatedStartKeys = [Catch, TryEnd].includes(useProjectDocStore().userFlowNode().find(n => n.id === id).key) ? startKeys.filter(key => contactMap[key] === endId) : []

  // const allIds = new Set([startId, ...relatedStartKeys, endId].filter(i => i))

  // if (allIds.size >= 2) {
  //   // 找到所有相关节点的起始和结束索引
  //   const allIdx = [...allIds].map(i => useProjectDocStore().userFlowNode().findIndex(n => n.id === i))
  //   const minIdx = Math.min(...allIdx)
  //   const maxIdx = Math.max(...allIdx)
  //   currentIds = useProjectDocStore().userFlowNode().slice(minIdx, maxIdx + 1).map(i => i.id)
  // }
  return currentIds
}
