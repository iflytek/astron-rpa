import { AST_NODE_TYPE } from './constants'

/** 节点ID类型 */
export type NodeID = string

/**
 * 处理节点接口
 * 定义AST节点的基本数据结构
 */
export interface ProcessNode {
  /** 节点唯一标识 */
  id: NodeID
  /** 节点类型 */
  type: string
  /** 其他自定义属性 */
  [key: string]: any
}

interface DirtyFlags {
  level: boolean
  structure: boolean
  error: boolean
}

/**
 * AST节点类
 *
 * 表示抽象语法树中的一个节点，包含节点数据、层级信息、父子关系等
 * 支持脏标记机制，用于增量更新和性能优化
 */
export class ASTNode<T extends ProcessNode = ProcessNode> {
  /** 节点唯一标识 */
  public readonly id: NodeID
  /** 节点类型 */
  public type: string
  // public level: number = 1;

  /** 缓存的层级值，用于性能优化 */
  private _cachedLevel: number | null = null
  /** 缓存命中次数统计 */
  private _cacheHitCount: number = 0
  /** 父节点引用 */
  private _parent: ASTNode<T> | null = null
  /** 子节点数组 */
  private _children: ASTNode<T>[] = []
  /** 结构版本号，用于检测结构变化 */
  private _structureVersion: number = 0
  /** 脏标记对象，记录需要更新的状态 */
  private _dirtyFlags: DirtyFlags = {
    level: true,
    structure: true,
    error: true,
  }

  /**
   * 构造函数
   * @param raw 原始节点数据
   */
  constructor(public raw: T) {
    this.id = raw.id
    this.type = raw.type
  }

  /**
   * 获取节点层级
   * 使用缓存机制优化性能，只在脏标记时重新计算
   */
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

  /**
   * 设置节点层级
   * 主要用于手动设置层级，绕过自动计算
   */
  set level(value: number) {
    this._cachedLevel = value
  }

  /**
   * 获取父节点
   */
  get parent(): ASTNode<T> | null {
    return this._parent
  }

  /**
   * 设置父节点
   * 自动处理父子关系的断开和连接
   */
  set parent(newParent: ASTNode<T> | null) {
    if (this._parent === newParent)
      return
    this.detachFromParent()
    this.attachToParent(newParent)
    this.markDirty('level', true)
  }

  /**
   * 从当前父节点分离
   * 清理父子关系并标记相关节点为脏状态
   */
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

  /**
   * 连接到新的父节点
   * 建立父子关系并标记相关节点为脏状态
   */
  private attachToParent(newParent: ASTNode<T> | null) {
    if (!newParent)
      return
    newParent.markDirty('level')
    this._parent = newParent
    if (!newParent._children.includes(this)) {
      newParent._children.push(this)
      newParent.markDirty('structure')
    }
  }

  /**
   * 获取子节点数组
   */
  get children(): ASTNode<T>[] {
    return this._children
  }

  /**
   * 在指定位置插入子节点
   * @param index 插入位置
   * @param nodes 要插入的节点数组
   */
  public insertChild(index: number, nodes: ASTNode<T>[]) {
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

  /**
   * 移除指定的子节点
   * @param node 要移除的子节点
   */
  public removeChild(node: ASTNode<T>) {
    const index = this._children.indexOf(node)
    if (index > -1) {
      this._children.splice(index, 1)
      node.parent = null
      this.markDirty('structure')
    }
  }

  /**
   * 标记节点为脏状态
   * @param flag 脏标记类型：level(层级)、structure(结构)、error(错误)
   * @param propagate 是否传播到子节点（仅对level类型有效）
   */
  markDirty(
    flag: 'level' | 'structure' | 'error',
    propagate: boolean = false,
  ) {
    if (flag === 'level') {
      this._cachedLevel = null
    }
    this._dirtyFlags[flag] = true
    if (propagate && flag === 'level') {
      this._children.forEach((child) => { child.markDirty('level', true) })
    }
  }

  /**
   * 清除脏标记
   * @param flag 要清除的脏标记类型
   */
  clearDirty(flag: keyof typeof this._dirtyFlags) {
    this._dirtyFlags[flag] = false
  }

  /**
   * 检查节点是否处于脏状态
   * @param flag 要检查的脏标记类型
   * @returns 如果指定标记为脏则返回true
   */
  isDirty(flag: keyof typeof this._dirtyFlags): boolean {
    return this._dirtyFlags[flag]
  }

  /**
   * 计算节点层级
   * 特殊处理else/else if/catch/finally等节点，它们与父节点层级相同
   * @returns 计算得到的层级值
   */
  calculateLevel(): number {
    if (!this.parent)
      return 0
    if (this.parent.type === 'root')
      return this.parent.level + 1
    return [AST_NODE_TYPE.ELSE_IF_TEXT, AST_NODE_TYPE.ELSE_TEXT, AST_NODE_TYPE.CATCH_TEXT, AST_NODE_TYPE.FINALLY_TEXT].includes(this.raw.type) ? this.parent.level : this.parent.level + 1
  }

  /**
   * 获取结构版本号
   * 用于检测节点结构是否发生变化
   */
  get structureVersion(): number {
    return this._structureVersion
  }

  /**
   * 递增结构版本号
   * 当节点结构发生变化时调用
   */
  incrementStructureVersion() {
    this._structureVersion++
    this.markDirty('structure')
  }
}
