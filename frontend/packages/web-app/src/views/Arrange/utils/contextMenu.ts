import { message } from 'ant-design-vue'
import hotkeys from 'hotkeys-js'

import { SCOPE } from '@/constants/shortcuts'
import { useFlowStore } from '@/stores/useFlowStore'
import { batchToggleNode, copy, cut, debug, deleteAtomData, group, paste, runFromHere, ungroup /* TODO: 临时注释掉，后续再打开从此处开始录制功能  recordFromHere */ } from '@/views/Arrange/components/flow/hooks/useFlow'
import { Group, GroupEnd } from '@/views/Arrange/config/atomKeyMap'
import type { ContextmenuInfo } from '@/views/Arrange/types/flow'
import { findPairId, getIdx, getMultiSelectIds } from '@/views/Arrange/utils/flowUtils'
import { setMultiSelectByClick, setSelectAll } from '@/views/Arrange/utils/selectItemByClick'

export function getContextMenuList() {
  return [
    {
      key: 'runHere',
      title: 'runFromHere',
      icon: 'tools-run',
      disable: (atom: RPA.Atom) => useFlowStore().multiSelect || atom.disabled || atom.level !== 1,
      disableTip: '不可从此处运行',
      clickFn: runFromHere,
      shortcutKey: 'Ctrl+Alt+H',
    },
    /* TODO: 临时注释掉，后续再打开从此处开始录制功能，勿删
    {
      key: 'recordingHere',
      title: 'startRecordingHere',
      clickFn: recordFromHere, // 从此处开始录制快捷键
      shortcutKey: 'Ctrl+Alt+N',
    }, */
    {
      key: 'runDebug',
      title: 'runDebug',
      icon: 'tools-debug',
      disable: (atom: RPA.Atom) => useFlowStore().multiSelect || atom.disabled || atom?.key === Group || atom?.key === GroupEnd,
      disableTip: '多选模式/分组/禁用状态不支持运行调试',
      clickFn: debug,
      actionicon: 'tools-run',
      actionOper: true,
      shortcutKey: 'Ctrl+Alt+R',
    },
    {
      key: 'enableToggle',
      title: (atom: RPA.Atom) => atom.disabled ? 'enableAtom' : 'disableAtom',
      icon: 'tools-disabled',
      disable: false,
      clickFn: batchToggleNode,
      shortcutKey: 'Ctrl+B',
    },
    {
      type: 'divider',
    },
    {
      key: 'copy',
      title: 'copy',
      icon: 'tools-copy',
      disable: false,
      clickFn: copy,
      shortcutKey: 'Ctrl+C',
    },
    {
      key: 'cut',
      title: 'cut',
      icon: 'tools-cut',
      disable: false,
      clickFn: cut,
      shortcutKey: 'Ctrl+X',
    },
    {
      key: 'paste',
      title: 'paste',
      icon: 'tools-paste',
      disable: () => useFlowStore().multiSelect,
      disableTip: '多选模式不支持粘贴',
      clickFn: paste,
      shortcutKey: 'Ctrl+V',
    },
    {
      type: 'divider',
    },
    {
      key: 'mergeGroup',
      title: 'group',
      icon: 'tools-group',
      disable: false,
      clickFn: group,
      shortcutKey: 'Ctrl+G',
    },
    {
      key: 'unGroup',
      title: 'releaseGrouping',
      icon: 'tools-un-group',
      disable: (atom: RPA.Atom) => !(atom?.key === Group || atom?.key === GroupEnd),
      disableTip: '非编组节点不可释放编组',
      clickFn: ungroup,
      shortcutKey: 'Ctrl+Shift+G',
    },
    {
      type: 'divider',
    },
    {
      key: 'deleteNode',
      title: 'deleteNode',
      disable: false,
      clickFn: deleteAtomData,
      icon: 'atom-delete',
      actionicon: 'atom-delete',
      actionOper: true, // 是否是便捷操作类按钮，是-则显示在便捷操作栏(运行、删除、更多)
      shortcutKey: 'Delete',
    },
    {
      key: 'selectAll',
      title: 'selectAll',
      disable: false,
      onlyShortcutKey: true, // 只支持快捷键, 不显示在界面上
      clickFn: setSelectAll,
      shortcutKey: 'Ctrl+A',
    },
  ]
}

// 鼠标右键点击设置右键菜单
let contextmenuRef = null
export function setContextMenu(contextRef) {
  contextmenuRef = contextRef
}

// 切换鼠标右键菜单
export function toggleContextmenu(data: ContextmenuInfo) {
  if (contextmenuRef) {
    const contextMenuInfo: any = {
      visible: data.visible,
    }
    if (data.visible) {
      const listWarpperDom = document.getElementById('listwrapper')
      const fitTop = data.$event.clientY - 143
      const fitBottom = listWarpperDom.clientHeight - fitTop
      contextMenuInfo.x = data.$event.clientX + 10
      contextMenuInfo.y = fitBottom > fitTop ? data.$event.clientY : data.$event.clientY - 300
      contextMenuInfo.atom = data.atom

      const selectedAtomIds = useFlowStore().selectedAtomIds || []
      if (!selectedAtomIds.includes(data.atom.id)) {
        setMultiSelectByClick(data.atom, getIdx(data.atom.id), false, false)
      }
    }
    contextmenuRef.value = contextMenuInfo
  }
}

export function getDisabled(contextItem: any, atom?: RPA.Atom) {
  return typeof contextItem.disable === 'function' ? contextItem.disable(atom) : contextItem.disable
}

export function getTitle(contextItem: any, atom?: RPA.Atom) {
  return typeof contextItem.title === 'function' ? contextItem.title(atom) : contextItem.title
}

export function getSelected() {
  const activeAtom = useFlowStore().activeAtom
  const selectedAtomIds = useFlowStore().selectedAtomIds
  let selectedIds = []
  if (selectedAtomIds?.length > 0)
    selectedIds = selectedAtomIds
  else if (activeAtom)
    selectedIds = [activeAtom.id]
  return selectedIds
}

// 右键菜单回调
export function clickContextItem(contextItem: any, atom?: RPA.Atom, from = 'contextMenu') {
  if (getDisabled(contextItem, atom))
    return message.warning(contextItem.disableTip)
  let atomIds = []
  // 释放编组等特殊处理
  const specialContexts = ['unGroup', 'runHere', 'recordingHere']
  if (specialContexts.includes(contextItem.key)) {
    if (atom) {
      const { key, id } = atom
      // const index = useFlowStore().simpleFlowUIData.findIndex(i => i.id === id)
      if (contextItem.key === 'unGroup' && [Group, GroupEnd].includes(key)) {
        const nodeMap = useFlowStore().nodeContactMap
        const mapId = findPairId(nodeMap, id)
        atomIds = key === Group ? [id, mapId] : [mapId, id]
      }
      if (['runHere', 'recordingHere'].includes(contextItem.key)) {
        atomIds = [id]
      }
    }
  }
  else {
    atomIds = atom && from === 'action' ? getMultiSelectIds(atom.id) : getSelected()
  }
  if (atomIds.length === 0 && !['paste', 'selectAll'].includes(contextItem.key))
    message.warning(`请先选中一个节点再${contextItem.title}`)

  contextItem.clickFn && contextItem.clickFn(atomIds, atom)
}

/** 右键菜单快捷键 */
let isInListContainer = true
function clickFunc(e: MouseEvent) {
  isInListContainer = [...(e.composedPath() as any)].some((i) => {
    let cls = i.className || ''
    if (i.className && i.className.baseVal !== undefined) {
      // 兼容svg元素
      cls = i.className.baseVal
    }
    return cls.includes('list-items-container') || cls.includes('link-select') || cls.includes('editor-tool') || i.id === 'listwrapper'
  })
}

export function enableContextMenuKeyboard(contextMenus) {
  document.onmousedown = clickFunc
  document.ondrop = clickFunc

  contextMenus.forEach((contextItem) => {
    const shortcutKey = contextItem.shortcutKey
    hotkeys.unbind(shortcutKey, SCOPE) // 先注销掉后绑定
    hotkeys(shortcutKey, SCOPE, () => {
      if (isInListContainer) {
        clickContextItem(contextItem, useFlowStore().activeAtom)
      }
    })
  })
}
/**
 * 禁用右键菜单快捷键
 */
export function disableContextMenuKeyboard(contextMenus) {
  document.onmousedown = null
  contextMenus.forEach(({ shortcutKey }) => {
    hotkeys.unbind(shortcutKey, SCOPE)
  })
}
