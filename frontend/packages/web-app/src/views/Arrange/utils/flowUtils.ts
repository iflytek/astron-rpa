import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { Catch, CvImageExist, ForBrowserSimilar, ForDataTableLoop, ForDict, ForExcelContent, ForList, ForStep, Group, If, Try, TryEnd, While } from '@/views/Arrange/config/atomKeyMap'
import { ERR_PARENT_NOT_CONTAINS_ALL_CHILD } from '@/views/Arrange/config/errors'

/**
 * 获取数组中和当前节点同一层级的节点
 * @param curItem 当前节点
 * @param lastId 尾节点id
 * @returns 同级列表Ids
 */
export function getCommonLevel(curItem: RPA.Atom, lastId: string) {
  const flowStore = useFlowStore()
  const findItem = flowStore.simpleFlowUIData.find(i => i.id === lastId)
  if (findItem) {
    return findItem.level === curItem.level
  }
}

export function backContainNodeIdx(idOrIndex: string | number) {
  const flowStore = useFlowStore()
  const nodeMap = flowStore.nodeContactMap
  let findId = ''
  if (typeof idOrIndex === 'number')
    idOrIndex = flowStore.simpleFlowUIData[idOrIndex].id
  for (const key in nodeMap) {
    if (Object.prototype.hasOwnProperty.call(nodeMap, key)) {
      const element = nodeMap[key]
      if (idOrIndex === key) {
        findId = element
        break
      }
      if (idOrIndex === element) {
        findId = key
        break
      }
    }
  }
  return flowStore.simpleFlowUIData.findIndex(i => i.id === findId)
}

export function generateContactIds() {
  const nodeMap = useFlowStore().nodeContactMap
  const startKeys = Object.keys(nodeMap)
  const endKeys = startKeys.map(key => nodeMap[key])
  return {
    startKeys,
    endKeys,
    contactMap: nodeMap,
  }
}

export function getIdx(id: string) {
  return useFlowStore().simpleFlowUIData.findIndex(i => i.id === id)
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
  processStore.processList.filter(i => i.resourceCategory !== 'module').forEach((item) => {
    allFlowList[item.resourceId] = useProjectDocStore().userFlowNode(item.resourceId)
  })
  return { allFlowList }
}

// 获取流程数据种当前选择的节点、关联节点和其子节点
export function getMultiSelectIds(id: string) {
  if (!id)
    return []
  const { startKeys, endKeys, contactMap } = generateContactIds()

  let currentIds = [id]

  let startId = ''
  let endId = ''
  // // 当前是嵌套类的起始节点
  if (startKeys.includes(id)) {
    startId = id
    endId = contactMap[id]
  }

  // 当前是嵌套类的结束节点
  if (endKeys.includes(id)) {
    startId = startKeys[endKeys.findIndex(endId => endId === id)]
    endId = id
  }

  // 一个结束节点可能对应多个起始节点，找出结束节点对应的所有的开始节点
  const relatedStartKeys = [Catch, TryEnd].includes(useProjectDocStore().userFlowNode().find(n => n.id === id).key) ? startKeys.filter(key => contactMap[key] === endId) : []

  const allIds = new Set([startId, ...relatedStartKeys, endId].filter(i => i))

  if (allIds.size >= 2) {
    // 找到所有相关节点的起始和结束索引
    const allIdx = [...allIds].map(i => useProjectDocStore().userFlowNode().findIndex(n => n.id === i))
    const minIdx = Math.min(...allIdx)
    const maxIdx = Math.max(...allIdx)
    currentIds = useProjectDocStore().userFlowNode().slice(minIdx, maxIdx + 1).map(i => i.id)
  }
  return currentIds
}

/**
 * 判断节点是否为嵌套节点（需要检查子节点）。
 *
 * @param key 节点的 key
 * @returns 是否为嵌套节点
 */
function isComplexNode(key: string): boolean {
  return [
    Group,
    ForStep,
    ForDict,
    ForList,
    ForExcelContent,
    ForBrowserSimilar,
    ForDataTableLoop,
    While,
    If,
    Try,
    CvImageExist,
  ].includes(key)
}

/**
 * 检查子节点是否全部包含在选中节点中。
 *
 * @param childIds 子节点 ID 数组
 * @param selectedIds 选中节点 ID 数组
 * @returns 是否全部包含
 */
function areAllChildrenSelected(childIds: string[], selectedIds: string[]): boolean {
  return childIds.every(id => selectedIds.includes(id))
}

/**
 * 过滤掉已处理的子节点 ID。
 *
 * @param currentIds 当前选中节点 ID 数组
 * @param processedIds 已处理的子节点 ID 数组
 * @returns 过滤后的节点 ID 数组
 */
function filterProcessedIds(currentIds: string[], processedIds: string[]): string[] {
  return currentIds.filter(id => !processedIds.includes(id))
}

/**
 * 检查选中的节点是否满足以下条件：所有子节点均包含在选中节点中
 * @param atomIds 选中的节点 ID 数组
 * @returns 错误信息数组
 */
export function validateSelectedNodes(atomIds: string[]): string[] {
  const flowStore = useFlowStore()
  const allNodes = flowStore.simpleFlowUIData
  let currentIds = [...atomIds] // 复制选中节点 ID 数组,
  const errors: string[] = []

  // 遍历所有节点，检查选中节点的层级和子节点
  for (const node of allNodes) {
    if (!currentIds.includes(node.id))
      continue

    // 检查当前节点级子节点是否全部选中
    const childIds = getMultiSelectIds(node.id)
    if (isComplexNode(node.key) && !areAllChildrenSelected(childIds, atomIds)) {
      errors.push(ERR_PARENT_NOT_CONTAINS_ALL_CHILD)
      console.log('所选原子能力存在未选择的子级')
      break
    }

    // 过滤掉已处理的子节点，减少计算量
    currentIds = filterProcessedIds(currentIds, childIds)
  }

  return errors
}

/**
 * 根据 id 或 endid 查找对应的 endid 或 id
 * @param mapObj 形如 {id: endid, id2: endid2} 的对象
 * @param value 需要查找的 id 或 endid
 * @returns 对应的 endid 或 id，找不到返回 undefined
 */
export function findPairId(mapObj: Record<string, string>, value: string): string | undefined {
  // 先正向查找
  if (mapObj[value])
    return mapObj[value]
  // 反向查找
  const entry = Object.entries(mapObj).find(([_k, v]) => v === value)
  return entry ? entry[0] : undefined
}
