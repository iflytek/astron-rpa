import { getContextMenuList } from '@/views/Arrange/utils/contextMenu'

export const SCOPE = 'global'

export const RUN = 'run'
export const STOP_RUN = 'stopRun'
export const DEBUG = 'debug'
export const CONTINUE_DEBUG = 'continueDebug'
export const NEXT_DEBUG = 'nextDebug'
export const STOP_DEBUG = 'stopDebug'
export const SAVE = 'save'
export const UNDO = 'undo'
export const REDO = 'redo'

export const shortcuts = {
  [RUN]: {
    id: RUN,
    name: 'run',
    value: 'F5',
    text: 'F5',
    validate: '',
    active: false,
    showSettingCenter: true, // 是否在设置中心显示
  },
  [DEBUG]: {
    id: DEBUG,
    name: 'debug',
    value: 'F10',
    text: 'F10',
    validate: '',
    active: false,
    showSettingCenter: true,
  },
  [CONTINUE_DEBUG]: {
    id: CONTINUE_DEBUG,
    name: 'debuggingContinues',
    value: 'F9',
    text: 'F9',
    validate: '',
    active: false,
    showSettingCenter: true,
  },
  [NEXT_DEBUG]: {
    id: NEXT_DEBUG,
    name: 'debuggingNext',
    value: 'F8',
    text: 'F8',
    validate: '',
    active: false,
    showSettingCenter: true,
  },
  [STOP_RUN]: {
    id: STOP_RUN,
    name: 'stop',
    value: 'Shift + F5',
    text: 'Shift + F5',
    validate: '',
    active: false,
    showSettingCenter: true,
  },
  [SAVE]: {
    id: SAVE,
    name: '保存',
    value: 'Ctrl + S',
    text: 'Ctrl + S',
    validate: '',
    active: false,
    showSettingCenter: false,
  },
  [UNDO]: {
    id: UNDO,
    name: '撤销',
    value: 'Ctrl + Z',
    text: 'Ctrl + Z',
    validate: '',
    active: false,
    showSettingCenter: false,
  },
  [REDO]: {
    id: REDO,
    name: '重做',
    value: 'Ctrl + Shift + Z',
    text: 'Ctrl + Shift + Z',
    validate: '',
    active: false,
    showSettingCenter: false,
  },
}

// 设置中心快捷键设置,不可使用的快捷键
const contextKeys = getContextMenuList().filter(i => i.shortcutKey).map(i => i.shortcutKey) // 编排页面右键菜单快捷键
export const commonKeys = [
  ...contextKeys,
  'ctrl+w',
  'ctrl+r',
  'ctrl+s',
  'ctrl+z',
  'ctrl+shift+z',
  'f3',
  'esc',
  'ctrl+tab',
  'ctrl+shift+tab',
  'f1',
  'alt+h',
  'ctrl+q',
  'shift+esc',
  'alt+a',
]
