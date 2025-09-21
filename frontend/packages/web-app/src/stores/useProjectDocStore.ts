import { defineStore } from 'pinia'
import { ref } from 'vue'

import { trackComponentUsageChange } from '@/utils/customComponent'

import { IncrementalASTParser } from '@/ast/IncrementalASTParser'
import type { IProjectDocument, ProcessNodeVM } from '@/corobot'
import { ProjectDocument } from '@/corobot'
import type { ProcessNode } from '@/corobot/type'
import { createSingleNode, processNodeToASTProcessNode, processNodeToList } from '@/corobot/utils/processNode'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { getMultiSelectIds } from '@/views/Arrange/utils/flowUtils'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const useProjectDocStore = defineStore('projectDoc', () => {
  const processStore = useProcessStore()
  const flowStore = useFlowStore()
  let parser: IncrementalASTParser
  const _canUndo = ref(false)
  const _canRestore = ref(false)
  let document: IProjectDocument
  let refreshFlowList = false

  function updateState(processId) {
    _canUndo.value = document.processNodeActor.canUndo(processId)
    _canRestore.value = document.processNodeActor.canRestore(processId)
  }

  function addProcessNode(index: number | number[], node: ProcessNodeVM | ProcessNodeVM[], options = {}) {
    trackComponentUsageChange(() => {
      const idxArr = Array.isArray(index) ? index : [index]
      const nodeArr = Array.isArray(node) ? node : [node]
      document.processNodeActor.add(idxArr, nodeArr, { ...options, processId: processStore.activeProcessId })
      processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
    })
  }

  function deleteProcessNode(nodeId: string[]) {
    trackComponentUsageChange(() => {
      document.processNodeActor.delete(nodeId, { processId: processStore.activeProcessId })
      processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
    })
  }

  function updateProcessNode(index: number[], node: ProcessNode[], processId: string = processStore.activeProcessId) {
    document.processNodeActor.update(index, node, { processId })
    processStore.setSavingType(processId, saveProcess, true, false, 5000)
  }

  function moveProcessNode(from: number, to: number, dragId: string) {
    if (from === to)
      return
    const endIds = getMultiSelectIds(dragId)
    document.processNodeActor.move(from, to, { processId: processStore.activeProcessId, conditionId: endIds })
    parser.moveNodeAfter(dragId, to - 1 < 0 ? '' : flowStore.simpleFlowUIData[to - 1].id, to)
    if (endIds.length > 1) {
      const start = flowStore.simpleFlowUIData.findIndex(item => item.id === endIds[1])
      const end = flowStore.simpleFlowUIData.findIndex(item => item.id === endIds[endIds.length - 1])
      const elementsToMove = flowStore.simpleFlowUIData.splice(start, end - start + 1)
      elementsToMove.forEach(item => item.level = parser.getNode(item.id).level)
      const insertIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === dragId)
      flowStore.setSimpleFlowUIDataByType(elementsToMove, insertIdx + 1, false)
    }
    const curIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === dragId)
    const atom = { ...flowStore.simpleFlowUIData[curIdx], level: parser.getNode(dragId).level }
    flowStore.setSimpleFlowUIDataByType(atom, curIdx, true)
    console.log('UI结构', flowStore.simpleFlowUIData)
    processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
  }
  function clearNode(processId = processStore.activeProcessId) {
    document.processNodeActor.clear(processId)
    parser.clear()
  }
  function clearAllData() {
    parser.clear()
    document.processNodeActor.clearAll()
    document.processEmitter.$off('open', processListener_open)
    document.processNodeEmitter.$off('add', processNodeListener_add)
    document.processNodeEmitter.$off('delete', processNodeListener_del)
    document.processNodeEmitter.$off('update', processNodeListener_update)
    document = null
    parser = null
    _canUndo.value = false
    _canRestore.value = false
  }
  function clear() {
    clearNode()
    flowStore.setSimpleFlowUIData([], 0)
    updateState(processStore.activeProcessId)
    processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
  }

  function undo() {
    refreshFlowList = true
    document.processNodeActor.undo(processStore.activeProcessId)
    refreshFlowList = false
    processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
  }

  function insertASTFlowNode(id: string, insertIdx: number, data, isUINull: boolean) {
    parser.insertNodeAfter(id, insertIdx, processNodeToASTProcessNode(data), isUINull)
  }

  function insertASTGroupNode(groupIds: string[], insertIds: string[]) {
    parser.createGroup(groupIds, insertIds)
  }

  function deleteASTFlowNode(ids: string[]) {
    ids.forEach(item => parser.deleteNode(item))
  }

  function redo() {
    refreshFlowList = true
    document.processNodeActor.restore(processStore.activeProcessId)
    refreshFlowList = false
    processStore.setSavingType(processStore.activeProcessId, saveProcess, true, false, 5000)
  }
  function changeUI(orderList: number[], node: ProcessNode | ProcessNode[]) {
    const nodes = Array.isArray(node) ? node : [node]
    let listIdx = orderList
    if (orderList.length < nodes.length) {
      listIdx = nodes.map(node => userFlowNode().findIndex(item => item.id === node.id))
    }
    if (flowStore.simpleFlowUIData.length < 1) {
      insertASTFlowNode(nodes[0].id, 0, nodes, true)
    }
    else {
      listIdx.forEach((idx, i) => {
        const node = nodes[i]
        let id = node.id
        const contactId = flowStore.nodeContactMap[id]
        if (id.includes('group_') && listIdx.length === 2 && contactId) {
          const endGroupIdx = listIdx[nodes.findIndex(item => item.id === contactId)]
          insertASTGroupNode([id, contactId], [flowStore.simpleFlowUIData[idx].id, flowStore.simpleFlowUIData[endGroupIdx - 2].id])
          flowStore.setSimpleFlowUIDataProps(idx, endGroupIdx - 1, item => item.level = parser.getNode(item.id).level)
        }
        else {
          id = userFlowNode()[userFlowNode().findIndex(item => item.id === id) - 1]?.id
          insertASTFlowNode(id, idx, node, false)
        }
      })
    }
    listIdx.forEach((idx, i) => {
      const node = nodes[i]
      const nodeAbility = ProjectDocument.nodeAbility[`${node.key}***${node.version}`]
      flowStore.setSimpleFlowUIDataByType(createSingleNode(node, parser.getNode(node.id), nodeAbility), idx, false)
    })
  }

  function createProjectDoc() {
    document = new ProjectDocument(processStore.project.id)
    document.processEmitter.$on('open', processListener_open)
    document.processNodeEmitter.$on('add', processNodeListener_add)
    document.processNodeEmitter.$on('delete', processNodeListener_del)
    document.processNodeEmitter.$on('update', processNodeListener_update)

    document.loadProject().then((project) => {
      flowStore.reset()
      processStore.getProcessList(project.processes)

      processStore.processList
        .filter(it => it.resourceCategory === 'process')
        .forEach((item, i) => setTimeout(async () => {
          await document.processActor.loadProcess(item.resourceId)
          const activeProcess = processStore.processList.find(it => it.resourceId === item.resourceId)
          activeProcess.isLoading = false
        }, (i) * 50))
    })
  }

  function processListener_open(_processId, nodes, type) {
    const flag = _processId === processStore.activeProcessId
    if (type === 'init' && flag) {
      const toASTNode = processNodeToASTProcessNode(nodes)
      parser = new IncrementalASTParser(toASTNode)
    }
    const gNode = processNodeToList(flag ? parser.getAllNodeMap() : new Map(), nodes, ProjectDocument, _processId)
    if (!flag)
      return
    flowStore.setSimpleFlowUIData(gNode, type === 'init' ? 0 : flowStore.simpleFlowUIData.length, type !== 'init')
    console.log('parser opened', parser)
    flowStore.generateContactMap(flowStore.simpleFlowUIData)
    const conditionId = getMultiSelectIds(flowStore.activeAtom?.id)
    changeSelectAtoms(flowStore.activeAtom?.id, conditionId, true)
  }
  function processNodeListener_add(index, node, options) {
    updateState(options.processId)
    if (!refreshFlowList)
      return
    changeUI(index, node)
  }
  function processNodeListener_del(index, node, options) {
    updateState(options.processId)
    if (!refreshFlowList)
      return
    const ids = node.map(i => i.id)
    deleteASTFlowNode(ids)
    const startIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === ids[0])
    const lastIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === ids[ids.length - 1])
    const filterList = flowStore.simpleFlowUIData.filter(item => !ids.includes(item.id))
    console.log('删除后', filterList)
    flowStore.setSimpleFlowUIData(filterList, index[0])
    if (ids[0].includes('group_') && ids.length === 2) {
      flowStore.setSimpleFlowUIDataProps(startIdx, lastIdx - 1, item => item.level -= 1)
    }
  }
  function processNodeListener_update(index: number[], node: ProcessNode[], options) {
    index.forEach((i, idx) => flowStore.setSimpleFlowUIDataByType(node[idx], i, true))
    updateState(options.processId)
  }
  function saveProcess() {
    const saveRequest = document.processActor.saveProcess(processStore.activeProcessId)
    saveRequest.then(() => {
      processStore.setSavingType(processStore.activeProcessId, null, false, false)
    })
    return saveRequest
  }
  function addProcessOrModule(type: RPA.Flow.ProcessModuleType, name: string) {
    document.processActor.addProcessOrModule(type, name).then((id) => {
      document.processActor.loadProcess(id).then(() => {
        processStore.processOrModule({ resourceId: id, name, type })
      })
    })
  }
  function renameProcessOrModule(type: RPA.Flow.ProcessModuleType, name: string, id: string) {
    document.processActor.updateProcessOrModule(type, id, name).then(() => {
      processStore.renameModule(name, id)
    })
  }
  function copyProcessOrModule(type: RPA.Flow.ProcessModuleType, id: string) {
    document.processActor.copyProcessOrModule(type, id).then((res: { id: string, name: string }) => {
      document.processActor.loadProcess(res.id).then(() => {
        processStore.processOrModule({ resourceId: res.id, name: res.name, type })
      })
    })
  }
  function removeProcessOrModule(data: RPA.Flow.ProcessModule) {
    document.processActor.deleteProcessOrModule(data).then((flag) => {
      if (flag)
        delete ProjectDocument.nodeAbilityMap[data.resourceId]
      processStore.deleteProcess(data.resourceId, flag)
    })
  }
  function userFlowNode(id = processStore.activeProcessId) {
    return id ? document.processActor.gainProcess(id) : []
  }
  function getProcessNodes(processId: string) {
    return document.getProcessNodes(processId)
  }
  return {
    canUndo: _canUndo,
    canRestore: _canRestore,
    nodeAbility: () => ProjectDocument.nodeAbility,
    noVersionMap: () => ProjectDocument.noVersionMap,
    undo,
    redo,
    clear,
    createProjectDoc,
    clearNode,
    clearAllData,
    saveProcess,
    gainASTNodeById: (id: string) => parser.getNode(id),
    insertASTGroupNode,
    insertASTFlowNode,
    deleteASTFlowNode,
    checkProcess: () => document.processEmitter.$emit('open', processStore.activeProcessId, userFlowNode(), 'init'),
    gainLastNodeAbility: (key: string, flag?: boolean) => ProjectDocument.gainLastNodeAbility(key, flag),
    addProcessOrModule,
    copyProcessOrModule,
    genProcessOrModuleName: (type: RPA.Flow.ProcessModuleType) => document.processActor.genProcessOrModuleName(type),
    renameProcessOrModule,
    removeProcessOrModule,
    addProcessNode,
    deleteProcessNode,
    updateProcessNode,
    moveProcessNode,
    userFlowNode,
    getProcessNodes,
  }
})

export default useProjectDocStore
