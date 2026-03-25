import { markRaw, shallowReactive, shallowRef } from 'vue'
import { isNil, uniq, isEmpty, last, keyBy, forEach, set } from 'lodash-es'
import { message } from 'ant-design-vue'
import EventEmitter from 'eventemitter3'
import hotkeys from 'hotkeys-js'

import { flowSave, getProcessFormValue, renameProcess } from '@/api/resource'
import { ATOM_KEY_MAP, LOOP_END_MAP } from '@/constants/atom'
import { CANVAS_SHORTCUTS, SCOPE } from '@/constants/shortcuts'
import { generateName } from '@/views/Arrange/utils'
import { caculateConditional, caculateResultKey } from '@/utils/selfExecuting'

import FlowList from '../../../components/flow/FlowList.vue'
import { AST_NODE_TYPE, IncrementalASTParser, ProcessNode } from '../../ast'
import { CONVERT_MAP } from './constants'
import { AbilityInfoCache, mergeAtomFormToAtomMeta, generateId, isContinuous, normalizeAtomFormLists } from './utils'
import { ConfigParameter } from './ConfigParameter'
import { nodeParameter } from './NodeParameter'
import { UndoManager } from './UndoManager'

type VisualEditorState = RPA.Process.ProcessModule<RPA.Atom[]>

export const MAX_ATOM_NUM = 2000

// if (newLength > MAX_ATOM_NUM) {
//     message.warning(`流程节点数量超出限制, 最大数量为{${MAX_ATOM_NUM}}，超出部分将不会进行保存`)
//   }

export class VisualEditor extends EventEmitter implements RPA.Process.TabInstance<RPA.Atom[]> {
  /** 跨实例共享数据 */
  // 剪贴板数据
  static clipBoardData: RPA.Atom[] = []

  component = markRaw(FlowList)

  id: string
  state: VisualEditorState
  abilityInfo = markRaw(new AbilityInfoCache())
  astParser: IncrementalASTParser
  // 记录上次 selected 的 atomId
  lastSelectedAtomId: string | undefined
  containerRef = shallowRef<HTMLElement | null>(null)
  /** 配置参数管理 */
  configParameter: ConfigParameter
  /** 节点参数管理 */
  nodeParameter = nodeParameter
  /** 撤销管理 */
  undoManager: UndoManager

  constructor(public projectId: string, config: RPA.Process.ProcessModule) {
    super()

    this.id = config.resourceId
    this.configParameter = new ConfigParameter(projectId, config.resourceId)
    this.undoManager = new UndoManager(this)

    this.state = shallowReactive(config)
    this.init()
  }

  // 激活时，监听快捷键
  onActivate() {
    Object.values(CANVAS_SHORTCUTS).forEach(shortcutKey => {
      hotkeys(shortcutKey, SCOPE, () => this.emit('shortcut', shortcutKey))
    })
  }

  // 失活时，注销快捷键
  onDeactivate() {
    Object.values(CANVAS_SHORTCUTS).forEach(shortcutKey => {
      hotkeys.unbind(shortcutKey, SCOPE)
    })
  }

  updateState(updates: Partial<VisualEditorState>): void {
    Object.assign(this.state, updates)
  }

  private convertAtomToProcessNode(atom: RPA.Atom, forceUpdateId: boolean = false): ProcessNode {
    return {
      ...atom,
      id: forceUpdateId ? generateId(atom.key) : (atom.id || generateId(atom.key)),
      type: CONVERT_MAP[atom.key] || 'action'
    }
  }

  updateData() {
    const [_root, ...list] = this.astParser.getSubtreeNodes();
    this.state.data = list.map((it) => ({
      ...it.raw,
      level: it.level,
      isOpen: it.raw.isOpen ?? true, // 是否展开
      hasFold: !isEmpty(it.children), // 是否可折叠
    })) as unknown as RPA.Atom[] ?? []
  }

  /**
   * 检查选中的节点是否满足以下条件：所有子节点均包含在选中节点中
   * @param atomIds 选中的节点 ID 数组
   * @returns 如果所有选中节点的子节点（包括嵌套容器内的所有后代节点）都在选中列表中，返回 true；否则返回 false
   */
  private checkAllChildrenSelected(atomIds: string[]): boolean {
    if (!atomIds || atomIds.length === 0) {
      return true
    }

    const selectedIdSet = new Set(atomIds)

    for (const atomId of atomIds) {
      const node = this.astParser.getNode(atomId)
      if (!node) {
        continue
      }

      // 获取该节点的所有子树节点（包括嵌套容器内的所有后代节点）
      const subtreeNodes = this.astParser.getSubtreeNodes(node)

      // 排除节点本身，只检查其所有后代节点
      for (const descendant of subtreeNodes) {
        // 跳过节点本身和结束节点
        if (descendant.id === atomId || this.astParser.isEndType(descendant.type)) {
          continue
        }

        // 如果任何一个后代节点不在选中列表中，返回 false
        if (!selectedIdSet.has(descendant.id)) {
          return false
        }
      }
    }

    return true
  }

  /**
   * 生成编组名称
   * @returns 编组名称
   */
  private generateGroupName(): string {
    // 获取既有的编组名称
    const groupNames = this.state.data.filter(it => it.key === ATOM_KEY_MAP.Group).map(it => it.alias)
    return generateName(groupNames, '编组', '-')
  }

  /**
   * 重命名
   * @param name 新名称
   */
  async rename(name: string) {
    await renameProcess({ robotId: this.projectId, processId: this.id, processName: name })
    this.updateState({ name })
  }

  private getSavePayload(): RPA.Flow.FlowItemValue[] {
    const [_root, ...nodes] = this.astParser.getSubtreeNodes()
    return nodes.map((node) => {
      const raw = { ...(node.raw as any) }
      delete raw.level
      delete raw.isHide
      delete raw.isOpen
      delete raw.hasFold
      delete raw.showInput
      delete raw.debugging
      return raw as RPA.Flow.FlowItemValue
    })
  }

  getSelectedAtoms() {
    return this.state.data.filter(it => this.state.selectedAtomIds?.includes(it.id))
  }

  getActionState(actionType: RPA.Process.TabActionType): RPA.Process.TabActionState {
    const defaultState: RPA.Process.TabActionState = {
      visible: true,
      disabled: false,
    }

    return defaultState
  }

  async save(): Promise<boolean> {
    try {
      await flowSave({
        robotId: this.projectId,
        processId: this.id,
        processJson: JSON.stringify(this.getSavePayload()),
      })
      return true
    }
    catch {
      return false
    }
  }

  async init() {
    const formValues = await getProcessFormValue({ robotId: this.projectId, processId: this.id })
    const atomInfoMap = await this.abilityInfo.getAbilityInfoWithCache(formValues)

    // 遍历 formValues，根据 cacheKey 从 atomInfoMap 中获取元数据并合并
    const mergedAtoms = formValues
      .map((formValue) => {
        const cacheKey = this.abilityInfo.getCacheKey(formValue)
        const atomMeta = atomInfoMap[cacheKey]
        // 将表单数据合并到元数据中
        return atomMeta ? mergeAtomFormToAtomMeta(atomMeta, formValue) : null
      })
      .filter(Boolean)
      .map(it => this.validateAtom(it))
      .map(it => this.executeDynamicScript(it))

    this.astParser = markRaw(new IncrementalASTParser(mergedAtoms.map(it => this.convertAtomToProcessNode(it))))

    this.updateData()
  }

  /**
   * 校验原子能力
   */
  private validateAtom(atom: RPA.Atom): RPA.Atom {
    const normalizedAtom = normalizeAtomFormLists(atom)
    const { inputList, outputList, advanced, exception } = normalizedAtom

    return Object.assign(normalizedAtom, {
      inputList: inputList.map(it => Object.assign(it, { errors: nodeParameter.validateFormItems(it) })),
      outputList: outputList.map(it => Object.assign(it, { errors: nodeParameter.validateFormItems(it) })),
      advanced: advanced.map(it => Object.assign(it, { errors: nodeParameter.validateFormItems(it) })),
      exception: exception.map(it => Object.assign(it, { errors: nodeParameter.validateFormItems(it) })),
    })
  }

  /**
   * 执行原子能力参数的动态脚本
   * @param atom 原子能力
   * @returns 
   */
  private executeDynamicScript(atom: RPA.Atom): RPA.Atom {
    const { inputList, outputList, advanced, exception } = atom

    const dynamicInputList = [inputList, outputList, advanced, exception].flat()
    const dynamicInputMap = keyBy(dynamicInputList, 'key')

    forEach(dynamicInputMap, (item) => {
      if (isEmpty(item.dynamics)) return

      item.dynamics.forEach(it => {
        const resultKey = caculateResultKey(it.key)
        const value = caculateConditional(it.expression, dynamicInputMap);
        set(dynamicInputMap, resultKey, value)
      })
    })

    return atom
  }

  /**
   * 更新原子能力表单项值
   * @param key 表单项key
   * @param value 表单项值
   */
  updateFormItemValue(atomId: string, key: string, value: any) {
    const activeNode = this.astParser.getNode(atomId)
    if (!activeNode) return

    const activeAtom = activeNode.raw as unknown as RPA.Atom

    set(activeAtom, key, value)

    // 重新校验表单项和执行动态脚本
    this.validateAtom(activeAtom)
    this.executeDynamicScript(activeAtom)

    this.updateData()
  }

  /**
   * 切换多选状态
   * @param value 是否开启多选
   */
  toggleMultiSelect(value?: boolean) {
    const multiSelect = value ?? !this.state.multiSelect;
    this.updateState({ multiSelect })

    // 关闭多选模式时，只保留最后一项选中
    if (!multiSelect && this.lastSelectedAtomId) {
      this.toggleAtomSelected(this.lastSelectedAtomId, true)
    }
  }

  /**
   * 切换原子能力选中状态
   * @param id 原子能力ID
   * @param _selected 是否选中
   */
  toggleAtomSelected(id: string, _selected?: boolean) {
    const isSelected = !isNil(_selected) ? _selected : this.state.multiSelect ? !this.state.selectedAtomIds?.includes(id) : true;
    const node = this.astParser.getNode(id)
    const atom = this.state.data.find(it => it.id === id)
    let ids = [id];

    // 当点击容器节点的开始/结束节点时，需要选中容器下的所有节点
    if (this.astParser.isContainerType(node.type)) {
      ids = this.astParser.getSubtreeNodes(node).map(it => it.id)
    } else if (this.astParser.isEndType(node.type)) {
      ids = this.astParser.getSubtreeNodes(node.parent).map(it => it.id)
    }

    let selectedAtomIds = this.state.multiSelect ? (this.state.selectedAtomIds || []) : [];

    if (isSelected) {
      selectedAtomIds = [...selectedAtomIds, ...ids]
    } else {
      selectedAtomIds = selectedAtomIds.filter(it => !ids.includes(it))
    }

    this.updateState({ selectedAtomIds })

    if (isSelected) {
      this.lastSelectedAtomId = id
      this.nodeParameter.toggleAtomActive(this, id)
    }
  }

  /**
   * 添加原子能力元数据
   * @param key 原子能力 key
   * @param index 插入位置索引
   */
  async add(key: string, index: number = 0) {
    const addKeys = [key];
    // 如果是容器类的节点,开始和结束节点需要一起添加
    const endKey = LOOP_END_MAP[key]
    if (endKey) {
      addKeys.push(endKey)
    }

    const atomAbilityInfos = await Promise.all(addKeys.map(it => this.abilityInfo.getLatestAbilityInfo(it)))
    const processNodes = atomAbilityInfos
      .map(it => normalizeAtomFormLists(it))
      .map(it => this.convertAtomToProcessNode(it, true))
    const preNodeId = this.state.data[index - 1]?.id;

    this.undoManager.update({ type: 'insert', targetId: preNodeId, item: processNodes })
  }

  /**
   * 移动原子能力
   * @param fromIndex 移动的节点索引
   * @param toIndex 目标节点索引
   */
  move(fromIndex: number, toIndex: number) {
    const fromId = this.state.data[fromIndex]?.id;
    const fromPreId = this.state.data[fromIndex - 1]?.id;
    const afterId = this.state.data[toIndex > fromIndex ? toIndex : toIndex - 1]?.id;

    if (!fromId) return
    this.undoManager.update({ type: 'move', fromId, afterId, fromPreId })
  }

  /**
   * 删除原子能力
   * @param id 要删除的节点ID
   */
  delete(id: string | string[]) {
    const ids = Array.isArray(id) ? id : [id];

    // 如果删除的是容器的开始/结束节点, 需要删除容器下的所有节点
    const deleteIds = ids.reduce((acc, it) => {
      const node = this.astParser.getNode(it)
      if (!node) return acc

      if (this.astParser.isContainerType(node.type)) {
        acc.push(...this.astParser.getSubtreeNodes(node).map(it => it.id))
      } else if (this.astParser.isEndType(node.type)) {
        acc.push(...this.astParser.getSubtreeNodes(node.parent).map(it => it.id))
      } else {
        acc.push(it)
      }

      return acc
    }, [] as string[])

    uniq(deleteIds).forEach(it => this.astParser.deleteNode(it))
    this.updateData()
  }

  /**
   * 编组
   * @param ids 要编组的节点ID列表
   * @returns 
   */
  async group(id: string | string[]) {
    const children = Array.isArray(id) ? id : [id];

    const idIndexList = children.map(it => this.state.data.findIndex(item => item.id === it))
    if (!isContinuous(idIndexList)) {
      message.error('所选节点不连续')
      return
    }

    // 生成新的编组别名
    const groupName = this.generateGroupName()
    const groupAtomAbilityInfos = await Promise.all([ATOM_KEY_MAP.Group, ATOM_KEY_MAP.GroupEnd].map(it => this.abilityInfo.getLatestAbilityInfo(it)))
    const groupProcessNodes = groupAtomAbilityInfos.map(it => this.convertAtomToProcessNode({ ...it, alias: groupName }, true)) as [ProcessNode, ProcessNode]

    this.undoManager.update({ type: 'group', children, items: groupProcessNodes })
  }

  /**
   * 解组
   * @param id 要解组的节点ID
   */
  ungroup(id: string | string[]) {
    const ids = Array.isArray(id) ? id : [id];

    const groups = uniq(ids)
      .map(it => this.astParser.getNode(it))
      .filter(node => node?.type === AST_NODE_TYPE.GROUP_TEXT)

    if (isEmpty(groups)) {
      message.warning('请先选择一个分组，再释放分组')
      return
    }

    const groupItems = groups.map(item => {
      // 获取分组结束节点
      const endNode = last(item.children)
      const children = item.children.slice(0, -1)
      return {
        items: [item.raw, endNode.raw] as [ProcessNode, ProcessNode],
        children: children.map(it => it.id),
      }
    })

    this.undoManager.update({ type: 'ungroup', items: groupItems })
  }

  /**
   * 
   * @param id 要切换 enable 状态的节点ID列表
   * @param enable 是否启用
   * @returns 
   */
  toggleEnable(id: string | string[], enable: boolean) {
    const ids = Array.isArray(id) ? id : [id];

    // 判断 enable 状态是否一致
    const hasDifferent = this.state.data.some(it => ids.includes(it.id) && it.disabled === enable)
    if (!hasDifferent) return

    this.state.data.forEach(it => {
      if (ids.includes(it.id)) {
        it.disabled = !enable
      }
    })

    this.updateData()
  }

  /**
   * 复制节点
   * @param id 要复制的节点ID
   * @returns 
   */
  copy(id: string | string[]) {
    const ids = Array.isArray(id) ? id : [id];
    const atoms = this.state.data.filter(it => ids.includes(it.id))
    if (!atoms) return

    VisualEditor.clipBoardData = atoms
    message.success('复制成功')
  }

  /**
   * 剪切节点
   * @param id 要剪切的节点ID
   */
  cut(id: string | string[]) {
    const ids = Array.isArray(id) ? id : [id];

    // 剪切时,如果剪切一个容器节点,需要一并剪切其所有的子节点
    const allChildrenSelected = this.checkAllChildrenSelected(ids)
    if (!allChildrenSelected) {
      message.warning('所选原子能力中存在未选择的子级，不可操作')
      return
    }

    const atoms = this.state.data.filter(it => ids.includes(it.id))
    VisualEditor.clipBoardData = atoms

    this.delete(ids)
  }

  /**
   * 粘贴节点
   * @param id 要粘贴的节点ID
   */
  paste(id: string | string[]) {
    const ids = Array.isArray(id) ? id : [id];

    if (isEmpty(VisualEditor.clipBoardData)) {
      message.warning('剪切板为空，不可粘贴')
      return
    }

  
    if (ids.length > 1) {
      message.warning('多选模式不支持粘贴')
      return
    }

    const targetId = ids[0];
    const processNodes = VisualEditor.clipBoardData.map(it => this.convertAtomToProcessNode(it, true))
    this.astParser.insertNodeAfter(targetId, processNodes, false, true)
    this.updateData()
  }

  /**
   * 全选
   * @returns 
   */
  selectAll() {
    if (isEmpty(this.state.data)) {
      message.error('当前流程还没添加原子能力')
      return
    }

    this.updateState({ selectedAtomIds: this.state.data.map(it => it.id) })
  }

  /**
   * 展开/折叠节点
   */
  toggleFold(id: string) {
    const node = this.astParser.getNode(id)
    const children = this.astParser.getSubtreeNodes(node).slice(1, -1)

    const isOpen = node.raw.isOpen ?? true
    node.raw.isOpen = !isOpen
    children.forEach(it => {
      it.raw.isHide = isOpen
    })

    this.updateData()
  }
}
