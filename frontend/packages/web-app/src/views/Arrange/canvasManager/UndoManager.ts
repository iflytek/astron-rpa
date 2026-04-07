export type Transaction<T> = T[]
export type ApplyOperationCallback<T> = (
  operation: T,
  isUndo: boolean
) => void

export class UndoManager<T> {
  private history: (T | Transaction<T>)[] = []
  private restoreStack: (T | Transaction<T>)[] = []
  private applyCallback: ApplyOperationCallback<T>

  constructor(applyCallback: ApplyOperationCallback<T>) {
    this.applyCallback = applyCallback
  }

  perform(operation: T): void {
    if (this.history.length > 50)
      this.history.shift()
    this.history.push(operation)
    this.restoreStack = []
    this.applyCallback(operation, false)
  }

  performTransaction(operations: Transaction<T>): void {
    this.history.push(operations)
    this.restoreStack = []
    operations.forEach(operation => this.applyCallback(operation, false))
  }

  canUndo(): boolean {
    return this.history.length > 0
  }

  undo(): boolean {
    if (this.history.length === 0)
      return false
    const last = this.history.pop()!
    this.restoreStack.push(last)
    if (Array.isArray(last)) {
      for (let i = last.length - 1; i >= 0; i--) {
        this.applyCallback(last[i], true)
      }
    }
    else {
      this.applyCallback(last, true)
    }
    return true
  }

  canRestore(): boolean {
    return this.restoreStack.length > 0
  }

  restore(): boolean {
    if (this.restoreStack.length === 0)
      return false

    const last = this.restoreStack.pop()!
    this.history.push(last)
    if (Array.isArray(last)) {
      last.forEach(operation => this.applyCallback(operation, false))
    }
    else {
      this.applyCallback(last, false)
    }
    return true
  }

  clear() {
    this.history.length = 0
    this.restoreStack.length = 0
  }
}
