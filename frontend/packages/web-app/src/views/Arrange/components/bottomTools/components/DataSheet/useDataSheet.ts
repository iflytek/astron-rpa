import type { TabConfig } from '../../types.ts'

import Sheet from './Sheet.vue'

export function useDataSheet() {
  const item: TabConfig = {
    text: 'dataSheet',
    key: 'dataSheet',
    icon: 'sheet',
    component: Sheet,
  }

  return item
}
