import { AST_NODE_TYPE } from './constants'
import type { NodeID, ProcessNode } from './ASTNode'
import { ASTNode } from './ASTNode'

/**
 * 增量AST解析器
 *
 * 负责构建和维护抽象语法树(AST)，支持增量更新操作
 * 主要功能包括：
 * - 构建完整的AST树结构
 * - 支持节点的增删改操作
 * - 维护节点间的父子关系
 * - 验证语法结构完整性
 * - 批量更新优化
 */
export class IncrementalASTParser {
  /** AST树的根节点 */
  private root: ASTNode
  /** 节点ID到ASTNode对象的映射表，用于快速查找 */
  private nodeMap = new Map<NodeID, ASTNode>()
  /** 脏节点队列，存储需要重新验证的节点 */
  private dirtyQueue = new Set<ASTNode>()
  /** 是否处于批量更新模式 */
  private isBatching = false
  /** 待处理的批量更新请求ID */
  private pendingBatch: number | null = null

  /**
   * 构造函数
   * @param initialNodes 初始节点数据，用于构建完整的AST树
   */
  constructor(initialNodes: ProcessNode[]) {
    this.root = this.buildFullTree(initialNodes)
  }

  /**
   * 构建完整的AST树
   * @param nodes 原始节点数据数组
   * @returns 构建完成的AST根节点
   */
  private buildFullTree(nodes: ProcessNode[]): ASTNode {
    const root = new ASTNode({ id: 'root', type: 'root' })
    const stack: ASTNode[] = [root]

    // 使用栈结构构建AST树，处理嵌套结构
    nodes.forEach((rawNode) => {
      const node = new ASTNode(rawNode)
      this.nodeMap.set(rawNode.id, node)
      node.parent = stack[stack.length - 1]

      // 如果是容器类型节点，压入栈中
      if (this.isContainerType(rawNode.type)) {
        stack.push(node)
      }
      // 如果是结束类型节点，从栈中弹出
      else if (this.isEndType(rawNode.type)) {
        stack.pop()
      }
      this.finalizeNode(node)
    })
    this.flushChanges()

    return root
  }

  /**
   * 批量更新操作
   * 将多个更新操作合并为一次处理，提高性能
   * @param callback 包含多个更新操作的回调函数
   */
  public batchUpdate(callback: () => void) {
    this.isBatching = true
    callback()
    this.isBatching = false
    this.flushUpdates()
  }

  /**
   * 立即处理所有脏节点
   */
  private flushChanges() {
    this.processDirtyQueue()
  }

  /**
   * 延迟处理更新，使用requestAnimationFrame优化性能
   */
  private flushUpdates() {
    if (this.pendingBatch) {
      cancelAnimationFrame(this.pendingBatch)
    }
    this.pendingBatch = requestAnimationFrame(() => {
      this.processDirtyQueue()
      this.pendingBatch = null
    })
  }

  /**
   * 移动节点到指定位置
   * @param originId 要移动的节点ID
   * @param afterId 目标节点ID，移动到此节点之后（如果为 null 或 undefined，则移动到根节点开头）
   */
  public moveNodeAfter(originId: string, afterId: string | null | undefined) {
    const originNode = this.nodeMap.get(originId)
    if (!originNode)
      return
    const parent = originNode.parent
    parent.removeChild(originNode)
    this.insertNodeAfter(afterId, [originNode], false, false)
    this.traverseSubtree(originNode, (n) => {
      this.finalizeNode(n)
    })
  }

  /**
   * 删除指定节点
   * @param nodeId 要删除的节点ID
   * @param deleteChildren 是否删除节点的子节点。如果节点是容器节点，为 true 时删除节点及其子节点，为 false 时只删除节点本身并将子节点提升到父级
   */
  public deleteNode(nodeId: string, deleteChildren: boolean = true) {
    const node = this.nodeMap.get(nodeId)
    if (!node)
      return
    if (!node.parent)
      throw new Error('不能移除根节点')

    const nodeType = node.type
    const parent = node.parent
    const isContainer = this.isContainerType(nodeType)
    const idx = parent.children.indexOf(node)

    // 如果是容器节点且不删除子节点，需要保存子节点（排除结束节点）
    let children: ASTNode[] = []
    if (isContainer && !deleteChildren) {
      children = node.children.slice(0, -1)
      // 清空子节点数组，避免在删除时影响
      node.children.length = 0
    }

    // 从父节点移除当前节点
    parent.removeChild(node)

    // 如果是容器节点且不删除子节点，将子节点提升到父级
    if (isContainer && !deleteChildren) {
      parent.insertChild(idx, children)
      children.forEach((child) => {
        this.traverseSubtree(child, (n) => {
          this.finalizeNode(n)
        })
      })
    }

    // 遍历子树，清理节点映射和父级引用
    this.traverseSubtree(node, (n) => {
      this.nodeMap.delete(n.id)
      n.parent = null
    })
    this.finalizeNode(parent)
    this.flushChanges()
  }

  /**
   * 创建分组节点
   * @param groups 分组节点数据 [开始节点数据, 结束节点数据]
   * @param insertIds 要包含在分组中的节点ID数组 [起始节点ID, 结束节点ID]
   */
  public createGroup(groups: [ProcessNode, ProcessNode], insertIds: string[]) {
    const insertFirstNode = this.nodeMap.get(insertIds[0])
    let insertLastNode = this.nodeMap.get(insertIds[1]) ?? insertFirstNode
    if (!insertFirstNode)
      return

    const groupParent = insertFirstNode.parent
    const firstIndex = insertFirstNode.parent.children.indexOf(insertFirstNode)
    let lastIndex = -1
    const startNode = new ASTNode({ ...groups[0], type: AST_NODE_TYPE.GROUP_TEXT })
    const endNode = new ASTNode({ ...groups[1], type: AST_NODE_TYPE.GROUP_END_TEXT })

    // 安全插入分组开始和结束节点
    this.safeInsert({
      parent: groupParent,
      index: firstIndex,
      nodes: [startNode, endNode],
    })

    // 处理分组内的节点移动
    if (this.isContainerType(insertFirstNode.type) && this.isEndType(insertLastNode.type)) {
      // 如果第一个节点是容器类型，最后一个节点是结束类型，直接将第一个节点移到分组内
      startNode.insertChild(0, [insertFirstNode])
    }
    else {
      // 否则将指定范围内的节点移到分组内
      let insertNode = insertLastNode
      if (this.isEndType(insertLastNode.type)) {
        insertNode = insertLastNode.parent
      }
      lastIndex = groupParent.children.indexOf(insertNode)
      const child = groupParent.children.slice(firstIndex + 1, lastIndex + 1)
      startNode.insertChild(0, child)
    }

    this.traverseSubtree(startNode, (n) => {
      this.finalizeNode(n)
    })
    this.flushChanges()
  }

  /**
   * 在指定节点后插入新节点
   * @param targetId 目标节点ID，如果为 null 或 undefined，则插入到根节点开头
   * @param newNodeData 新节点数据
   * @param isUINull 是否清空节点映射表
   * @param isAdd 是否为新增节点（true: 创建新节点，false: 使用现有节点）
   */
  public insertNodeAfter(targetId: string | null | undefined, newNodeData: ProcessNode[] | ASTNode[], isUINull?: boolean, isAdd: boolean = true) {
    let parentNode = this.root
    let targetIndex = 0

    if (isUINull)
      this.nodeMap.clear()

    // 确定插入位置和父节点
    if (targetId != null && this.nodeMap.size !== 0) {
      const targetNode = this.nodeMap.get(targetId)
      if (!targetNode)
        throw new Error(`目标节点 ${targetId} 不存在`)
      parentNode = this.defineParent(targetNode, newNodeData[0].type)
      if (!parentNode)
        throw new Error(`目标节点 ${targetId} 没有父节点`)
      const siblings = parentNode.children
      targetIndex = siblings.indexOf(this.isEndType(targetNode.type) ? targetNode.parent : targetNode)
    }

    // 创建新节点或使用现有节点
    const newNodes = isAdd
      ? (newNodeData as ProcessNode[]).map(node => new ASTNode(node))
      : (newNodeData as ASTNode[])

    // 安全插入节点
    this.safeInsert({
      parent: parentNode,
      index: targetId == null ? targetIndex : targetIndex + 1,
      nodes: newNodes,
    })

    this.markRelatedDirty(newNodes)
    if (newNodes.length < 2) {
      this.finalizeNode(newNodes[0])
    }
    else {
      newNodes.forEach((node) => { this.finalizeNode(node) })
    }
    this.flushChanges()
  }

  /**
   * 安全插入节点，防止循环引用
   * @param params 插入参数 {parent: 父节点, index: 插入位置, nodes: 要插入的节点数组}
   */
  private safeInsert(params: {
    parent: ASTNode
    index: number
    nodes: ASTNode[]
  }) {
    const { parent, index, nodes } = params

    // 检查循环引用
    nodes.some((node) => {
      if (this.checkCyclic(parent, node)) {
        throw new Error('存在循环引用')
      }
      return false
    })

    // 使用栈结构处理嵌套插入
    const stack: ASTNode[] = [parent]
    let idx = index
    nodes.forEach((node) => {
      this.nodeMap.set(node.id, node)
      stack[stack.length - 1].insertChild(idx, [node])
      idx = stack[stack.length - 1].children.indexOf(node) + 1

      // 如果是容器类型节点，压入栈中
      if (this.isContainerType(node.type)) {
        stack.push(node)
        idx = 0
      }
      // 如果是结束类型节点，从栈中弹出
      else if (this.isEndType(node.type)) {
        stack.pop()
      }
    })
  }

  /**
   * 检查循环引用
   * @param parent 父节点
   * @param node 要检查的节点
   * @returns 是否存在循环引用
   */
  private checkCyclic(parent: ASTNode, node: ASTNode): boolean {
    let current: ASTNode | null = parent
    while (current) {
      if (current === node)
        return true
      current = current.parent
    }
    return false
  }

  /**
   * 标记相关节点为脏状态
   * @param nodes 要标记的节点数组
   */
  private markRelatedDirty(nodes: ASTNode[]) {
    nodes.forEach((node) => {
      if (!node.isDirty('structure')) {
        node.markDirty('structure')
      }
      // 向上遍历父节点链，标记层级为脏状态
      let current: ASTNode | null = node
      while (current) {
        if (!node.isDirty('level')) {
          node.markDirty('level')
        }
        current = current.parent
      }
    })
  }

  /**
   * 遍历子树（深度优先遍历）
   * @param root 子树根节点
   * @param callback 对每个节点执行的回调函数
   */
  private traverseSubtree(root: ASTNode, callback: (node: ASTNode) => void) {
    const stack = [root]
    while (stack.length > 0) {
      const node = stack.shift()
      callback(node)
      stack.unshift(...node.children)
    }
  }

  /**
   * 获取一个树下的所有节点
   * @param root 子树根节点
   * @returns 子树下的所有节点
   */
  public getSubtreeNodes(root: ASTNode = this.root): ASTNode[] {
    const nodes: ASTNode[] = []
    this.traverseSubtree(root, (node) => nodes.push(node))
    return nodes
  }

  /**
   * 处理脏节点队列
   * 按层级排序处理，确保父节点先于子节点处理
   */
  private processDirtyQueue() {
    const levelMap = new Map<number, ASTNode[]>()

    // 按层级分组脏节点
    this.dirtyQueue.forEach((node) => {
      const level = node.level
      if (!levelMap.has(level)) {
        levelMap.set(level, [])
      }
      levelMap.get(level).push(node)
    })

    // 按层级升序排序处理
    const sortedLevels = Array.from(levelMap.keys()).sort((a, b) => a - b)
    sortedLevels.forEach((level) => {
      levelMap.get(level).forEach((node) => {
        // 处理层级脏标记
        if (node.isDirty('level')) {
          const newLevel = node.calculateLevel()
          if (node.level !== newLevel) {
            node.level = newLevel
            node.markDirty('level', true)
          }
          node.clearDirty('level')
        }

        // 处理结构脏标记
        if (node.isDirty('structure')) {
          this.validateNodeStructure(node)
          node.clearDirty('structure')
        }

        // 处理错误脏标记（暂未实现）
        // if (node.isDirty('error')) {
        //     this.validateNodeErrors(node);
        //     node.clearDirty('error');
        // }
      })
    })
    this.dirtyQueue.clear()
  }

  /**
   * 验证节点结构完整性
   * 检查各种控制结构节点的开始和结束标记是否匹配
   * @param node 要验证的节点
   */
  private validateNodeStructure(node: ASTNode) {
    switch (node.type) {
      case AST_NODE_TYPE.IF_TEXT:
        // 检查if语句是否有对应的结束标记
        this.hasRelatedChild(node, AST_NODE_TYPE.IF_END_TEXT)
        break
      case AST_NODE_TYPE.ELSE_IF_TEXT:
      case AST_NODE_TYPE.ELSE_TEXT:
      case AST_NODE_TYPE.IF_END_TEXT:
        // 检查else/else if/if结束节点是否有对应的if开始节点
        this.hasRelatedParent(node, [AST_NODE_TYPE.IF_TEXT])
        break
      case AST_NODE_TYPE.FOR_STEP_TEXT:
      case AST_NODE_TYPE.FOR_DICT_TEXT:
      case AST_NODE_TYPE.FOR_EXCEL_CONTENT:
      case AST_NODE_TYPE.FOR_BRO_SIMILAR:
      case AST_NODE_TYPE.FOR_LIST_TEXT:
      case AST_NODE_TYPE.WHILE_TEXT:
        // 检查循环语句是否有对应的结束标记
        this.hasRelatedChild(node, AST_NODE_TYPE.FOR_END_TEXT)
        break
      case AST_NODE_TYPE.FOR_END_TEXT:
        // 检查for结束节点是否有对应的循环开始节点
        this.hasRelatedParent(node, [AST_NODE_TYPE.FOR_STEP_TEXT, AST_NODE_TYPE.FOR_DICT_TEXT, AST_NODE_TYPE.FOR_EXCEL_CONTENT, AST_NODE_TYPE.FOR_BRO_SIMILAR, AST_NODE_TYPE.FOR_LIST_TEXT, AST_NODE_TYPE.WHILE_TEXT])
        break
      case AST_NODE_TYPE.GROUP_TEXT:
        // 检查分组是否有对应的结束标记
        this.hasRelatedChild(node, AST_NODE_TYPE.GROUP_END_TEXT)
        break
      case AST_NODE_TYPE.GROUP_END_TEXT:
        // 检查分组结束节点是否有对应的分组开始节点
        this.hasRelatedParent(node, [AST_NODE_TYPE.GROUP_TEXT])
        break
      case AST_NODE_TYPE.TRY_TEXT:
        // 检查try语句是否有对应的结束标记
        this.hasRelatedChild(node, AST_NODE_TYPE.TRY_END_TEXT)
        break
      case AST_NODE_TYPE.CATCH_TEXT:
      case AST_NODE_TYPE.FINALLY_TEXT:
      case AST_NODE_TYPE.TRY_END_TEXT:
        // 检查catch/finally/try结束节点是否有对应的try开始节点
        this.hasRelatedParent(node, [AST_NODE_TYPE.TRY_TEXT])
        break
      default:
        break
    }
  }

  // private validateNodeErrors(node: ASTNode) {
  //     console.log(node);
  // }

  /**
   * 完成节点的初始化处理
   * @param node 要处理的节点
   * @param parentLevel 可选的父级层级
   */
  private finalizeNode(node: ASTNode, parentLevel?: number) {
    // 设置节点层级
    if (parentLevel) {
      node.level = parentLevel
    }
    else if (this.isEndType(node.raw.type)) {
      // 结束类型节点与父节点层级相同
      node.level = node.parent.level
    }
    else {
      // 计算节点层级
      node.level = node.calculateLevel()
    }
    node.clearDirty('level')
    this.dirtyQueue.add(node)
  }

  /**
   * 根据目标节点和新节点类型确定插入的父节点
   * @param targetNode 目标节点
   * @param newNodeType 新节点类型
   * @returns 应该插入的父节点
   */
  private defineParent(targetNode: ASTNode, newNodeType: string) {
    const { raw } = targetNode

    // 处理else/else if/catch/finally等中间节点
    if ([AST_NODE_TYPE.ELSE_IF_TEXT, AST_NODE_TYPE.ELSE_TEXT, AST_NODE_TYPE.CATCH_TEXT, AST_NODE_TYPE.FINALLY_TEXT].includes(raw.type)) {
      return [AST_NODE_TYPE.IF_END_TEXT, AST_NODE_TYPE.ELSE_TEXT, AST_NODE_TYPE.ELSE_IF_TEXT, AST_NODE_TYPE.TRY_END_TEXT].includes(newNodeType) ? targetNode.parent : targetNode
    }
    // 处理开始类型节点
    else if ([AST_NODE_TYPE.IF_TEXT, AST_NODE_TYPE.TRY_TEXT, AST_NODE_TYPE.FOR_STEP_TEXT, AST_NODE_TYPE.FOR_DICT_TEXT, AST_NODE_TYPE.FOR_EXCEL_CONTENT, AST_NODE_TYPE.FOR_BRO_SIMILAR, AST_NODE_TYPE.FOR_LIST_TEXT, AST_NODE_TYPE.WHILE_TEXT, AST_NODE_TYPE.GROUP_TEXT].includes(raw.type)) {
      return targetNode
    }
    // 处理结束类型节点
    else if ([AST_NODE_TYPE.IF_END_TEXT, AST_NODE_TYPE.FOR_END_TEXT, AST_NODE_TYPE.GROUP_END_TEXT, AST_NODE_TYPE.TRY_END_TEXT].includes(raw.type)) {
      return targetNode.parent.parent
    }
    // 默认情况
    else {
      return targetNode.parent
    }
  }

  /**
   * 判断是否为容器类型节点（可以包含子节点的节点）
   * @param type 节点类型
   * @returns 是否为容器类型
   */
  public isContainerType(type: string): boolean {
    return [AST_NODE_TYPE.IF_TEXT, AST_NODE_TYPE.FOR_STEP_TEXT, AST_NODE_TYPE.FOR_DICT_TEXT, AST_NODE_TYPE.FOR_EXCEL_CONTENT, AST_NODE_TYPE.FOR_BRO_SIMILAR, AST_NODE_TYPE.FOR_LIST_TEXT, AST_NODE_TYPE.WHILE_TEXT, AST_NODE_TYPE.TRY_TEXT, AST_NODE_TYPE.GROUP_TEXT].includes(type)
  }

  /**
   * 判断是否为结束类型节点
   * @param type 节点类型
   * @returns 是否为结束类型
   */
  public isEndType(type: string): boolean {
    return [AST_NODE_TYPE.IF_END_TEXT, AST_NODE_TYPE.GROUP_END_TEXT, AST_NODE_TYPE.FOR_END_TEXT, AST_NODE_TYPE.TRY_END_TEXT].includes(type)
  }

  /**
   * 检查节点是否有指定类型的父节点
   * @param node 要检查的节点
   * @param types 允许的父节点类型数组
   */
  private hasRelatedParent(node: ASTNode, types: string[]) {
    const current = node.parent
    const flag = types.includes(current?.type)
    const text = node.type === AST_NODE_TYPE.FOR_END_TEXT ? 'for' : types[0]
    if (flag) {
      current.raw.error = ''
    }
    else {
      node.raw.error = `${node.type}缺少对应的${text}节点`
    }
  }

  /**
   * 检查节点是否有指定类型的子节点
   * @param node 要检查的节点
   * @param type 要查找的子节点类型
   */
  private hasRelatedChild(node: ASTNode, type: string) {
    const flag = node.children.some(c => c.type === type)
    if (flag) {
      node.raw.error = `${node.type}缺少${type}结束标记`
    }
  }

  /**
   * 根据ID获取节点
   * @param id 节点ID
   * @returns 对应的ASTNode对象，如果不存在则返回undefined
   */
  getNode(id: NodeID): ASTNode | undefined {
    const node = this.nodeMap.get(id)
    return node
  }

  /**
   * 获取所有节点的映射表
   * @returns 节点ID到ASTNode的映射表
   */
  getAllNodeMap() {
    return this.nodeMap
  }

  /**
   * 清空解析器状态，重置为初始状态
   */
  clear() {
    this.nodeMap.clear()
    this.dirtyQueue.clear()
    this.root = new ASTNode({ id: 'root', type: 'root' })
  }
}
