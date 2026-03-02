export const WINELEVALUE = 'winElement'
export const WEBELEVALUE = 'webElement'
export const SAPELEVALUE = 'sapElement'
export const AIELEVALUE = 'aiElement'
export const VALID_POSITION = 'check_position'
export const VALID_CLICK = 'check_click'
export const VALID_INPUT = 'check_input'
export const VALID_HOVER = 'check_hover'
export const VALID_OPTIONS = [
  {
    label: 'location',
    value: VALID_POSITION,
  },
  // {
  //   label: 'click-1',
  //   value: VALID_CLICK,
  // },
  // {
  //   label: 'input',
  //   value: VALID_INPUT,
  // },
  // {
  //   label: 'hover',
  //   value: VALID_HOVER,
  // },
]

export const PICK_WINDOW = 'window' // 桌面窗口拾取
export const PICK_ITEM = 'item' // 桌面元素拾取
export const PICK_MOUSE = 'mouse' // 鼠标坐标拾取
export const PICK_SAP = 'sap' // sap拾取
export const PICK_CV = 'cv' // cv拾取
export const PICK_SIMILAR_ITEM = 'similarItem'
export const PICK_SIMILAR = 'similar' // 相似元素拾取
export const PICK_EXCEL = 'excel' // excel拾取
export const PICK_SIMPLE_ITEM = 'simpleItem' // 区分ai元素的传统拾取
export const PICK_DATA = 'data' // 数据拾取
export const PICK_DATA_SIMILAR = 'dataSimilar' // 数据相似元素拾取
export const PICKTYPE_NOVISUAL_LIST = [PICK_MOUSE, PICK_CV, PICK_WINDOW]

export const SMART_XPATH = 'smartXPath' // 智能路径
export const CUSTOM_XPATH = 'customXPath' // 自定义路径

export const VISUALIZATION = 'visualization'
export const CUSTOMIZATION = 'customization'

export const CUSTOM_OPTIONS = [
  {
    label: 'visualEditing',
    value: 'visualization',
  },
  {
    label: 'customEditing',
    value: 'customization',
  },
]

// 匹配方式
export const MATCH_OPTIONS = [
  {
    label: 'onlyPosition',
    value: 'onlyPosition',
  },
  {
    label: 'scrollPosition',
    value: 'scrollPosition',
  },
]

export const PATTERN_RULES = [
  {
    label: '等于',
    key: 'equals',
    value: 0,
  },
]

export const PATTERN_RULES_WEB = [
  {
    label: '等于',
    key: 'equals',
    value: 0,
  },
  {
    label: '通配',
    key: 'includes',
    value: 1,
  },
  {
    label: '正则',
    key: 'regex',
    value: 2,
  },
]

export const PATTERN_RULES_TYPE = {
  0: ' equals ',
  1: ' includes ',
  2: ' regex ',
}

export const PATTERN_RULES_UIA = [
  {
    label: '等于',
    key: 'equals',
    value: 0,
  },
  {
    label: '通配',
    key: 'includes',
    value: 1,
  },
  {
    label: '正则',
    key: 'regex',
    value: 2,
  },
]
export const PATTERN_RULES_JAB = [
  {
    label: '等于',
    key: 'equals',
    value: 0,
  },
]

export const PATTERN_RULES_IE = [
  {
    label: '等于',
    key: 'equals',
    value: 0,
  },
]
