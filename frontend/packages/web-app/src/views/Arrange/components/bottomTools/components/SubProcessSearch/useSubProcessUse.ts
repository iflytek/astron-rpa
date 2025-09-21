import { useProcessStore } from '@/stores/useProcessStore'

import type { TabConfig } from '../../types.ts'

import RightExtra from './RightExtra.vue'
import SubProcessSearch from './SubProcessSearch.vue'

export function useSubProcessUse() {
  const { processList, searchSubProcessId } = useProcessStore()
  const resourceCategory = processList.find((pItem: any) => pItem.resourceId === searchSubProcessId)?.resourceCategory

  const item: TabConfig = {
    text: resourceCategory === 'process' ? 'subProcessSearch' : 'subModuleSearch',
    key: 'subProcessSearch',
    icon: 'quote-process',
    hideCollapsed: true,
    component: SubProcessSearch,
    rightExtra: RightExtra,
  }

  return item
}
