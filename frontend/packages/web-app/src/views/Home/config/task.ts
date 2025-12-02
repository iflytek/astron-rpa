// 计划任务触发器类型
export const TASK_FILE = 'file'
export const TASK_MAIL = 'mail'
export const TASK_TIME = 'schedule'
export const TASK_MANUAL = 'manual'
export const TASK_HOTKEY = 'hotKey'

export enum TASK_TYPE {
  TASK_FILE = 'file',
  TASK_MAIL = 'mail',
  TASK_TIME = 'schedule',
  TASK_MANUAL = 'manual',
  TASK_HOTKEY = 'hotKey',
}

export const TASK_TYPE_TEXT = {
  [TASK_FILE]: '文件触发',
  [TASK_MAIL]: '邮箱触发',
  [TASK_TIME]: '时间触发',
  [TASK_MANUAL]: '手动触发',
  [TASK_HOTKEY]: '热键触发',
}

export const TASK_TYPE_OPTION = [
  { label: '手动触发', value: TASK_MANUAL },
  { label: '时间触发', value: TASK_TIME },
  { label: '文件触发', value: TASK_FILE },
  { label: '邮箱触发', value: TASK_MAIL },
  { label: '热键触发', value: TASK_HOTKEY },
]

export const FileEvents = [
  {
    label: '创建',
    value: 'create',
  },
  {
    label: '删除',
    value: 'delete',
  },
  {
    label: '更新',
    value: 'update',
  },
  {
    label: '重命名',
    value: 'rename',
  },
]

export const WEEK_OPTIONS = [
  { label: '周一', value: 0 },
  { label: '周二', value: 1 },
  { label: '周三', value: 2 },
  { label: '周四', value: 3 },
  { label: '周五', value: 4 },
  { label: '周六', value: 5 },
  { label: '周日', value: 6 },
]

export const WEEK_MAP = {
  0: '周一',
  1: '周二',
  2: '周三',
  3: '周四',
  4: '周五',
  5: '周六',
  6: '周日',
}
export const WEEK_MAP_EN = {
  0: 'monday',
  1: 'tuesday',
  2: 'wednesday',
  3: 'thursday',
  4: 'friday',
  5: 'saturday',
  6: 'sunday',
}
export const WEEK_MAP_INDAYJS = {
  0: 1,
  1: 2,
  2: 3,
  3: 4,
  4: 5,
  5: 6,
  6: 0,
}

export const DAYJS_WEEK_MAP = {
  0: 6, // 周日
  1: 0, // 周一
  2: 1, // 周二
  3: 2, // 周三
  4: 3, // 周四
  5: 4, // 周五
  6: 5, // 周六
}

/**
 * @returns F1-F12、0-9、A-Z
 */
export function Hotkeys() {
  const keys = []
  for (let i = 1; i <= 12; i++) {
    keys.push({ label: `F${i}`, value: `F${i}` })
  }
  for (let i = 0; i <= 9; i++) {
    keys.push({ label: `${i}`, value: `${i}` })
  }
  for (let i = 65; i <= 90; i++) {
    keys.push({ label: String.fromCharCode(i), value: String.fromCharCode(i) })
  }
  return keys
}
