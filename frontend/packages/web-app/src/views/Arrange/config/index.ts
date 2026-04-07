export const RIGHT_TAB_KEY = {
  NODE: 'node',
  PROCESS: 'process',
  VARIABLE: 'variable',
  PYTHON: 'python',
} as const

export type RightTabKey = typeof RIGHT_TAB_KEY[keyof typeof RIGHT_TAB_KEY]
