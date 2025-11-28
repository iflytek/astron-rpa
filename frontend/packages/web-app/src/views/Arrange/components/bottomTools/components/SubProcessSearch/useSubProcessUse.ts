import { markRaw, computed } from 'vue'
import { sum } from 'lodash-es'
import { useTranslation } from 'i18next-vue'

import { useProcessStore } from '@/stores/useProcessStore'

import type { TabConfig } from '../../types.ts'

import RightExtra from './RightExtra.vue'
import SubProcessSearch from './SubProcessSearch.vue'

export function useSubProcessUse() {
  const { t } = useTranslation()
  const processStore = useProcessStore()
  // const resourceCategory = processList.find((pItem: any) => pItem.resourceId === searchSubProcessId)?.resourceCategory

  const searchSubProcessTotal = computed(() => {
    const total = sum(processStore.searchSubProcessResult.map(pItem => pItem.nodes?.length || 0))
    return `${t('searchSubProcessTotal')} ${total}`
  })

  const item: TabConfig = {
    // text: resourceCategory === 'process' ? 'subProcessSearch' : 'subModuleSearch',
    text: searchSubProcessTotal,
    key: 'subProcessSearch',
    icon: 'quote-process',
    hideCollapsed: true,
    component: markRaw(SubProcessSearch),
    rightExtra: markRaw(RightExtra),
  }

  return item
}
