import { message } from 'ant-design-vue'

import { CANVAS_SHORTCUTS } from '@/constants/shortcuts'
// import { debug, runFromHere } from '@/views/Arrange/components/flow/hooks/useFlow'
import { ATOM_KEY_MAP } from '@/constants/atom'
import type { ContextmenuInfo } from '@/views/Arrange/types/flow'
import { getIdx, getMultiSelectIds } from '@/views/Arrange/utils/flowUtils'
import { setMultiSelectByClick } from '@/views/Arrange/utils/selectItemByClick'

import { useFlowState } from '../hooks/useFlowState'
import { VisualEditor } from '@/views/Arrange/canvasManager'

export interface ContextMenuItem {
  key: string;
  title: string | ((atom: RPA.Atom) => string);
  icon?: string;
  disable?: boolean | ((atom: RPA.Atom) => boolean);
  disableTip?: string;
  shortcutKey?: string;
  actionicon?: string;
  clickFn?: (atom: RPA.Atom | RPA.Atom[]) => void;
}

export const useContextMenuList = () => {
  const { flowManager } = useFlowState()

  const getAtomIds = (atom: RPA.Atom | RPA.Atom[]) => {
    return Array.isArray(atom) ? atom.map(it => it.id) : [atom.id]
  }

  const runHere: ContextMenuItem = {
    key: 'runHere',
    title: 'runFromHere',
    icon: 'tools-run',
    // disable: (atom: RPA.Atom) => useFlowStore().multiSelect || atom.disabled || atom.level !== 1,
    disableTip: '不可从此处运行',
    clickFn: () => {},
    shortcutKey: CANVAS_SHORTCUTS.runHere,
  }

  const runDebug: ContextMenuItem = {
    key: 'runDebug',
    title: 'runDebug',
    icon: 'tools-debug',
    // disable: (atom: RPA.Atom) => useFlowStore().multiSelect || atom.disabled || atom?.key === Group || atom?.key === GroupEnd,
    disableTip: '多选模式/分组/禁用状态不支持运行调试',
    // clickFn: debug,
    actionicon: 'tools-run',
    shortcutKey: CANVAS_SHORTCUTS.runDebug,
  }

  const enableToggle: ContextMenuItem = {
    key: 'enableToggle',
    title: (atom: RPA.Atom) => atom.disabled ? 'enableAtom' : 'disableAtom',
    icon: 'tools-disabled',
    disable: false,
    shortcutKey: CANVAS_SHORTCUTS.enableToggle,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      const enable = Array.isArray(atom) ? atom.every(it => it.disabled) : atom.disabled
      flowManager.toggleEnable(getAtomIds(atom), enable)
    },
  }

  const copy: ContextMenuItem = {
    key: 'copy',
    title: 'copy',
    icon: 'tools-copy',
    disable: false,
    shortcutKey: CANVAS_SHORTCUTS.copy,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.copy(getAtomIds(atom))
    },
  }

  const cut: ContextMenuItem = {
    key: 'cut',
    title: 'cut',
    icon: 'tools-cut',
    disable: false,
    shortcutKey: CANVAS_SHORTCUTS.cut,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.cut(getAtomIds(atom))
    },
  }

  const paste: ContextMenuItem = {
    key: 'paste',
    title: 'paste',
    icon: 'tools-paste',
    disable: () => flowManager.state.multiSelect,
    disableTip: '多选模式不支持粘贴',
    shortcutKey: CANVAS_SHORTCUTS.paste,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.paste(getAtomIds(atom))
    },
  }

  const mergeGroup: ContextMenuItem = {
    key: 'mergeGroup',
    title: 'group',
    icon: 'tools-group',
    disable: false,
    shortcutKey: CANVAS_SHORTCUTS.mergeGroup,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.group(getAtomIds(atom))
    },
  }

  const unGroup: ContextMenuItem = {
    key: 'unGroup',
    title: 'releaseGrouping',
    icon: 'tools-un-group',
    disable: (atom: RPA.Atom) => !(atom?.key === ATOM_KEY_MAP.Group || atom?.key === ATOM_KEY_MAP.GroupEnd),
    disableTip: '非编组节点不可释放编组',
    shortcutKey: CANVAS_SHORTCUTS.unGroup,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.ungroup(getAtomIds(atom))
    },
  }

  const deleteNode: ContextMenuItem = {
    key: 'deleteNode',
    title: 'deleteNode',
    disable: false,
    icon: 'atom-delete',
    actionicon: 'atom-delete',
    shortcutKey: CANVAS_SHORTCUTS.deleteNode,
    clickFn: (atom: RPA.Atom | RPA.Atom[]) => {
      flowManager.delete(getAtomIds(atom))
    },
  }

  const selectAll: ContextMenuItem = {
    key: 'selectAll',
    title: 'selectAll',
    disable: false,
    clickFn: () => flowManager.selectAll(),
    shortcutKey: CANVAS_SHORTCUTS.selectAll,
  }

  return { runHere, runDebug, enableToggle, copy, cut, paste, mergeGroup, unGroup, deleteNode, selectAll }
}

export function getDisabled(contextItem: ContextMenuItem, atom?: RPA.Atom) {
  return typeof contextItem.disable === 'function' ? contextItem.disable(atom) : contextItem.disable
}

export function getTitle(contextItem: ContextMenuItem, atom?: RPA.Atom) {
  return typeof contextItem.title === 'function' ? contextItem.title(atom) : contextItem.title
}
