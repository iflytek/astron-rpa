import type { TabConfig } from '../../types.ts'

import DebugLog from './DebugLog.vue'

export function useDebugLog() {
  const item: TabConfig = {
    text: 'debugLog',
    key: 'debugLog',
    icon: 'tools-debug',
    component: DebugLog,
  }
  return item
}
