import { onMounted } from 'vue'

import { useCvStore } from '@/stores/useCvStore.ts'

import type { TabConfig } from '../../types.ts'

import CvManager from './CvManager.vue'
import RightExtra from './RightExtra.vue'

export function useCVManager() {
  const item: TabConfig = {
    text: 'cvManagement',
    key: 'cvManagement',
    icon: 'bottom-menu-img-manage',
    component: CvManager,
    rightExtra: RightExtra,
  }

  onMounted(() => {
    useCvStore().getCvTreeData()
  })

  return item
}
