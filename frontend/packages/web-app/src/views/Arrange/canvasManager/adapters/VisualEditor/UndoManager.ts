import { ref } from 'vue'

import { UndoManager as BaseUndoManager } from '../../UndoManager'

import type { VisualEditor } from '.'
import { ProcessNode } from '../../ast'

interface DeleteItem<T> {
  id: string
  preId?: string
  item: [T]
}

interface UngroupItem<T> {
  items: [T, T]
  children: string[]
}

type Operation<T>
  = | { type: 'insert', targetId: string, item: T[] }
    | { type: 'delete', items: DeleteItem<T>[] }
    | { type: 'update', index: number[], oldItem: T[], newItem: T[] }
    | { type: 'group', children: string[], items: [T, T] }
    | { type: 'ungroup', items: UngroupItem<T>[] }
    | { type: 'move', fromId: string, afterId: string, fromPreId: string }

type AtomOperation = Operation<ProcessNode>

export class UndoManager implements RPA.Process.UndoManager {
  public canUndo = ref(false)
  public canRestore = ref(false)
  
  private undoManager: BaseUndoManager<AtomOperation>

  constructor(private editor: VisualEditor) {
    this.undoManager = new BaseUndoManager(this.applyOperation.bind(this))
  }

  private applyOperation(operation: AtomOperation, isUndo: boolean) {
    this.canUndo.value = this.undoManager.canUndo()
    this.canRestore.value = this.undoManager.canRestore()

    switch(operation.type) {
      case 'insert':
        if (isUndo) {
          this.delete(operation.item.map(it => it.id))
        } else {
          this.insert(operation.targetId, operation.item)
        }
        break
      case 'delete':
        if (isUndo) {
          operation.items.forEach(it => this.insert(it.preId, it.item))
        } else {
          operation.items.forEach(it => this.delete([it.id]))
        }
        break
      case 'group':
        if (isUndo) {
          this.editor.astParser.deleteNode(operation.items[0].id, false)
        } else {
          this.editor.astParser.createGroup(operation.items, operation.children)
        }
        break
      case 'ungroup':
        if (isUndo) {
          operation.items.forEach(it => this.editor.astParser.createGroup(it.items, it.children))
        } else {
          operation.items.forEach(it => this.editor.astParser.deleteNode(it.items[0].id, false))
        }
        break
      case 'move':
        if (isUndo) {
          this.editor.astParser.moveNodeAfter(operation.fromId, operation.fromPreId)
        } else {
          this.editor.astParser.moveNodeAfter(operation.fromId, operation.afterId)
        }
        break
    }

    this.editor.updateData()
  }

  private insert(targetId: string | undefined, processNodes: ProcessNode[]) {
    this.editor.astParser.insertNodeAfter(targetId, processNodes, false, true)
  }

  private delete(ids: string[]) {
    ids.forEach(id => this.editor.astParser.deleteNode(id))
  }

  update(operation: AtomOperation) {
    this.undoManager.perform(operation)
  }

  undo(): boolean {
    return this.undoManager.undo()
  }

  restore(): boolean {
    return this.undoManager.restore()
  }
}
