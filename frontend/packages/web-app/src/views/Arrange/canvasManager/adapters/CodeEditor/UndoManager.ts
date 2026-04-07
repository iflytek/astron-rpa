import { ref } from 'vue'

import { UndoManager as BaseUndoManager } from '../../UndoManager'

import type { CodeEditor } from '.'

export class UndoManager implements RPA.Process.UndoManager {
  public canUndo = ref(false)
  public canRestore = ref(false)

  private undoManager: BaseUndoManager<string>

  constructor(private editor: CodeEditor) {
    this.undoManager = new BaseUndoManager(this.applyOperation.bind(this))
  }

  private applyOperation(code: string) {
    this.editor.updateState({ data: code, isDirty: true })
    this.canUndo.value = this.undoManager.canUndo()
    this.canRestore.value = this.undoManager.canRestore()
  }

  update(code: string) {
    this.undoManager.perform(code)
  }

  undo(): boolean {
    return this.undoManager.undo()
  }

  restore(): boolean {
    return this.undoManager.restore()
  }
}
