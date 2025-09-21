import { getComponentForm, getComponentId, isComponentKey } from '@/utils/customComponent'
import { Bus as Emittery } from '@/utils/eventBus'

import type { IProjectDocument, ProcessActor, ProcessEvent, ProcessNodeActor, ProcessNodeEvent } from '@/corobot/IProjectDocument'
import * as service from '@/corobot/store/service'
import { shapeUIData } from '@/corobot/utils/processNode'
import type { ProcessNodeVM, ProjectVM } from '@/corobot/vm'
import { MAX_ATOM_NUM } from '@/views/Arrange/components/flow/hooks/useFlow'
import { createComponentAbility } from '@/views/Arrange/utils/generateData'

import { ProcessEditor } from './ProcessEditor'

export class ProjectDocument implements IProjectDocument {
  id: string
  private project: ProjectVM
  static nodeAbility: Record<string, any> = {}
  static noVersionMap: Record<string, string> = {}
  static loadedKeys: Record<string, any> = {}
  static loadedIds: string[] = []
  static nodeAbilityMap: {
    [key: string]: {
      currentPage: number
      totalPage: number
      loadOver: boolean
    }
  } = {}

  static loadNumber = 2000

  processEmitter = new Emittery<ProcessEvent>()
  processNodeEmitter = new Emittery<ProcessNodeEvent>()

  processActor: ProcessActor = {
    loadProcess: this.loadProcess.bind(this),
    saveProcess: this.saveProcess.bind(this),
    gainProcess: this.gainProcess.bind(this),
    addProcessOrModule: this.addProcessOrModule.bind(this),
    copyProcessOrModule: this.copyProcessOrModule.bind(this),
    genProcessOrModuleName: this.genProcessOrModuleName.bind(this),
    deleteProcessOrModule: this.deleteProcessOrModule.bind(this),
    updateProcessOrModule: this.updateProcessOrModule.bind(this),
  }

  processNodeActor: ProcessNodeActor = {
    add: this.addNode.bind(this),
    delete: this.deleteNode.bind(this),
    update: this.updateNode.bind(this),
    move: this.moveNode.bind(this),
    canUndo: this.canUndo.bind(this),
    undo: this.undo.bind(this),
    canRestore: this.canRestore.bind(this),
    restore: this.restore.bind(this),
    clear: this.clear.bind(this),
    clearAll: this.clearAll.bind(this),
  }

  private processEditorMap = new Map<string, ProcessEditor>()

  constructor(id: string) {
    this.id = id
  }

  async loadProject() {
    this.project = await service.loadProject(this.id)
    return this.project
  }

  async loadNodeAbilityList(list: ProcessNodeVM[], processId: string, type: string) {
    if (list.length < 1)
      return this.processEmitter.$emit('open', processId, list, type)
    if (ProjectDocument.nodeAbilityMap[processId].currentPage > ProjectDocument.nodeAbilityMap[processId].totalPage) {
      ProjectDocument.nodeAbilityMap[processId].currentPage = 1
      ProjectDocument.nodeAbilityMap[processId].totalPage = 1
      ProjectDocument.nodeAbilityMap[processId].loadOver = true
      return
    }
    const atomMap = list.slice(ProjectDocument.loadNumber * (ProjectDocument.nodeAbilityMap[processId].currentPage - 1), ProjectDocument.loadNumber * ProjectDocument.nodeAbilityMap[processId].currentPage).reduce((acc, node) => {
      const { key, version } = node
      const keys = `${key}***${version}`
      if (!ProjectDocument.loadedKeys[keys]) {
        acc.push({ key, version })
        ProjectDocument.loadedKeys[keys] = true
      }
      return acc
    }, [])
    ProjectDocument.nodeAbilityMap[processId].currentPage += 1
    if (atomMap.length > 0) {
      const data = await service.getAtomicSchemaByVersion(atomMap)
      data.forEach((node) => {
        if (!node)
          return
        const { key, version } = node
        const keys = `${key}***${version}`
        if (!ProjectDocument.nodeAbility[keys])
          ProjectDocument.nodeAbility[keys] = node
      })
      for (const { key, version } of atomMap) {
        if (isComponentKey(key)) {
          await createComponentAbility(key, version)
        }
      }
    }
    this.processEmitter.$emit('open', processId, list, type)
    setTimeout(() => {
      const nodes = list
      this.loadNodeAbilityList(nodes, processId, 'append')
    }, 50)
  }

  private async loadProcess(processId: string) {
    const nodes = await service.loadProcess(processId, this.id)
    const obj = {
      currentPage: 1,
      totalPage: 1,
      loadOver: false,
    }
    obj.totalPage = Math.ceil(nodes.length / ProjectDocument.loadNumber)
    ProjectDocument.nodeAbilityMap[processId] = obj
    console.log('流程数据', nodes)
    const editor = new ProcessEditor(processId, nodes)
    this.processEditorMap.set(processId, editor)
    this.loadNodeAbilityList(nodes, processId, 'init')

    // 转发其他编辑事件
    editor.emitter.$on('add', this.editorAddEventListener.bind(this))
    editor.emitter.$on('delete', this.editorDeleteEventListener.bind(this))
    editor.emitter.$on('update', this.editorUpdateEventListener.bind(this))
  }

  private editorAddEventListener(index, node, options) {
    this.processNodeEmitter.$emit('add', index, node, options)
  }

  private editorDeleteEventListener(index, node, options) {
    this.processNodeEmitter.$emit('delete', index, node, options)
  }

  private editorUpdateEventListener(index, node, options) {
    this.processNodeEmitter.$emit('update', index, node, options)
  }

  static gainLastNodeAbility(key: string, sigle: boolean = false) {
    if (ProjectDocument.loadedIds.includes(key))
      return
    ProjectDocument.loadedIds.push(key)
    const fn = sigle ? service.getSigleNodeAbility : service.getAtomBykey
    return fn(key).then((res) => {
      res.forEach((node) => {
        const { key, version } = node
        const keys = `${key}***${version}`
        ProjectDocument.noVersionMap[key] = version
        if (!ProjectDocument.nodeAbility[keys]) {
          ProjectDocument.nodeAbility[keys] = node
        }
      })
    })
  }

  static gainComponentAbility(key: string, version?: string | number) {
    const componentId = getComponentId(key)
    return getComponentForm({ componentId, version }).then((node) => {
      const keys = `${node.key}***${node.version}`
      ProjectDocument.noVersionMap[key] = node.version
      if (!ProjectDocument.nodeAbility[keys]) {
        ProjectDocument.nodeAbility[keys] = node
      }
      return node
    })
  }

  public getProcessNodes(processId: string) {
    const editor = this.processEditorMap.get(processId)
    const nodes = editor?.getNodes() || []
    return nodes
  }

  private gainProcess(processId: string) {
    const { loadOver, currentPage } = ProjectDocument.nodeAbilityMap[processId]
    const nodes = this.getProcessEditor(processId).getNodes()
    return loadOver ? nodes : nodes.slice(0, ProjectDocument.loadNumber * currentPage)
  }

  private saveProcess(processId: string) {
    const nodes = this.gainProcess(processId).slice(0, MAX_ATOM_NUM)
    return service.saveProcess(processId, this.id, nodes.map(item => shapeUIData(item)))
  }

  private getProcessEditor(processId: string) {
    const editor = this.processEditorMap.get(processId)
    if (!editor) {
      console.error(`process ${processId} not found`)
      throw new Error(`process ${processId} not found`)
    }
    return editor
  }

  private addProcessOrModule(type: string, processName: string) {
    const genFns: Record<RPA.Flow.ProcessModuleType, () => Promise<string>> = {
      process: () => service.addProcess(this.id, processName),
      module: () => service.addModule(this.id, processName),
    }
    return genFns[type]()
  }

  private copyProcessOrModule(type: string, processId: string) {
    const genFns: Record<RPA.Flow.ProcessModuleType, () => Promise<unknown>> = {
      process: () => service.copyProcess(this.id, processId),
      module: () => service.copyModule(this.id, processId),
    }
    return genFns[type]()
  }

  private genProcessOrModuleName(type: string) {
    const genFns: Record<RPA.Flow.ProcessModuleType, () => Promise<string>> = {
      process: () => service.genProcessName(this.id),
      module: () => service.genModuleName(this.id),
    }
    return genFns[type]()
  }

  private updateProcessOrModule(type: RPA.Flow.ProcessModuleType, processId: string, name: string) {
    const genFns: Record<RPA.Flow.ProcessModuleType, () => Promise<unknown>> = {
      process: () => service.renameProcessName(this.id, processId, name),
      module: () => service.renameModuleName(this.id, processId, name),
    }
    return genFns[type]()
  }

  private deleteProcessOrModule(data: RPA.Flow.ProcessModule) {
    const deleteFuns: Record<RPA.Flow.ProcessModuleType, () => Promise<boolean>> = {
      process: () => service.deleteProcess(this.id, data.resourceId, data.name),
      module: () => service.deleteModule(data.resourceId),
    }
    return deleteFuns[data.resourceCategory]()
  }

  private addNode(index: number[], node: ProcessNodeVM[], option: any) {
    const { processId } = option
    const editor = this.getProcessEditor(processId)
    editor.addNode(node, index, option)
  }

  private deleteNode(nodeIds: string[], option: any) {
    const { processId } = option
    const editor = this.getProcessEditor(processId)
    editor.deleteNode(nodeIds)
  }

  private updateNode(index: number[], node: ProcessNodeVM[], option: any) {
    const { processId } = option
    const editor = this.getProcessEditor(processId)
    editor.updateNode(node, index)
  }

  private moveNode(from: number, to: number, option: any) {
    const { processId, conditionId } = option
    const editor = this.getProcessEditor(processId)
    editor.moveNode(from, to, conditionId)
  }

  private canUndo(processId: string) {
    const editor = this.getProcessEditor(processId)
    return editor.canUndo()
  }

  private undo(processId: string) {
    const editor = this.getProcessEditor(processId)
    return editor.undo()
  }

  private canRestore(processId: string) {
    const editor = this.getProcessEditor(processId)
    return editor.canRestore()
  }

  private restore(processId: string) {
    const editor = this.getProcessEditor(processId)
    return editor.restore()
  }

  private clear(processId: string) {
    ProjectDocument.nodeAbilityMap[processId] = {
      currentPage: 1,
      totalPage: 1,
      loadOver: false,
    }
    const editor = this.getProcessEditor(processId)
    return editor.clear()
  }

  private clearAll() {
    Object.keys(ProjectDocument.nodeAbilityMap).forEach((key) => {
      const editor = this.getProcessEditor(key)
      editor.emitter.$off('add', this.editorAddEventListener.bind(this))
      editor.emitter.$off('delete', this.editorDeleteEventListener.bind(this))
      editor.emitter.$off('update', this.editorUpdateEventListener.bind(this))
      editor.clear()
    })
    ProjectDocument.noVersionMap = {}
    ProjectDocument.loadedIds = []
    ProjectDocument.nodeAbility = {}
    ProjectDocument.loadedKeys = {}
    ProjectDocument.nodeAbilityMap = {}
    this.processEditorMap.clear()
  }
}
