import type { TabConfig } from '../../types.ts'

import Log from './Log.vue'
import RightExtra from './RightExtra.vue'

export function useLog() {
  const item: TabConfig = {
    text: 'log',
    key: 'logs',
    icon: 'bottom-menu-log-manage',
    component: Log,
    rightExtra: RightExtra,
  }
  return item
}
