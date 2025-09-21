import { CATCH_TEXT, ELSE_IF_TEXT, ELSE_TEXT, FINALLY_TEXT } from '@/views/Arrange/config/atomKeyMap'

export type NodeID = string

export interface ProcessNode {
  id: NodeID
  type: string
  [key: string]: any
}

export class ASTNode {
  public readonly id: NodeID
  public type: string
  // public level: number = 1;
  private _cachedLevel: number | null = null
  private _cacheHitCount: number = 0
  private _parent: ASTNode | null = null
  private _children: ASTNode[] = []
  private _structureVersion: number = 0
  private _dirtyFlags: {
    level: boolean
    structure: boolean
    error: boolean
  } = {
    level: true,
    structure: true,
    error: true,
  }

  constructor(public raw: ProcessNode) {
    this.id = raw.id
    this.type = raw.type
  }

  get level(): number {
    if (!this._dirtyFlags.level && this._cachedLevel !== null) {
      this._cacheHitCount++
    }
    if (this._dirtyFlags.level || this._cachedLevel === null) {
      this._cachedLevel = this.calculateLevel()
      this.clearDirty('level')
    }
    return this._cachedLevel
  }

  set level(value: number) {
    this._cachedLevel = value
  }

  get parent(): ASTNode | null {
    return this._parent
  }

  set parent(newParent: ASTNode | null) {
    if (this._parent === newParent)
      return
    this.detachFromParent()
    this.attachToParent(newParent)
    this.markDirty('level', true)
  }

  private detachFromParent() {
    if (!this._parent)
      return
    this._parent.markDirty('level')
    const index = this._parent._children.indexOf(this)
    if (index > -1) {
      this._parent._children.splice(index, 1)
      this._parent.markDirty('structure')
    }
    this._parent = null
  }

  private attachToParent(newParent: ASTNode | null) {
    if (!newParent)
      return
    newParent.markDirty('level')
    this._parent = newParent
    if (!newParent._children.includes(this)) {
      newParent._children.push(this)
      newParent.markDirty('structure')
    }
  }

  get children(): ASTNode[] {
    return this._children
  }

  public insertChild(index: number, nodes: ASTNode[]) {
    nodes.forEach((node) => {
      if (node.parent) {
        node.parent.removeChild(node)
      }
    })
    this._children.splice(index, 0, ...nodes)
    nodes.forEach((node) => {
      node.parent = this
    })
    this.markDirty('structure')
  }

  public removeChild(node: ASTNode) {
    const index = this._children.indexOf(node)
    if (index > -1) {
      this._children.splice(index, 1)
      node.parent = null
      this.markDirty('structure')
    }
  }

  markDirty(
    flag: 'level' | 'structure' | 'error',
    propagate: boolean = false,
  ) {
    if (flag === 'level') {
      this._cachedLevel = null
    }
    this._dirtyFlags[flag] = true
    if (propagate && flag === 'level') {
      this._children.forEach(child =>
        child.markDirty('level', true),
      )
    }
  }

  clearDirty(flag: keyof typeof this._dirtyFlags) {
    this._dirtyFlags[flag] = false
  }

  isDirty(flag: keyof typeof this._dirtyFlags): boolean {
    return this._dirtyFlags[flag]
  }

  calculateLevel(): number {
    if (!this.parent)
      return 0
    if (this.parent.type === 'root')
      return this.parent.level + 1
    return [ELSE_IF_TEXT, ELSE_TEXT, CATCH_TEXT, FINALLY_TEXT].includes(this.raw.type) ? this.parent.level : this.parent.level + 1
  }

  get structureVersion(): number {
    return this._structureVersion
  }

  incrementStructureVersion() {
    this._structureVersion++
    this.markDirty('structure')
  }
}
