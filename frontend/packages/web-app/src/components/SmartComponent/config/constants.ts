export const WINDOW_WIDTH = 1056
export const WINDOW_HEIGHT = 700

export const SMART_COMPONENT_KEY_PREFIX = 'Smart.run_code'

export const SMART_CODE_BLOCK_REGEX = /```smart_code\s*?\n([\s\S]*?)```/
export const SMART_CODE_START_REGEX = /```smart_code[\s\S]*$/

export const modeOptions = [
  {
    // label: '可视化',
    value: 'visual',
    payload: {
      icon: 'eye',
      title: '可视化',
    },
  },
  {
    // label: '代码模式',
    value: 'code',
    payload: {
      icon: 'code-xml',
      title: '代码模式',
    },
  },
] as const
