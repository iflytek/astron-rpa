import type { TabConfig } from '../../types.ts'

import Sheet from './Sheet.vue'

export function useDataSheet() {
  const item: TabConfig = {
    text: 'debugLog',
    key: 'debugLog',
    icon: 'tools-debug',
    component: Sheet,
  }

  return item
}
