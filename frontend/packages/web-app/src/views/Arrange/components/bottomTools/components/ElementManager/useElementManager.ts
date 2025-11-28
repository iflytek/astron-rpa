import { onMounted, onUnmounted, markRaw } from 'vue'

import { useElementsStore } from '@/stores/useElementsStore'

import type { TabConfig } from '../../types.ts'

import ElementManager from './ElementManager.vue'
import RightExtra from './RightExtra.vue'

export function useElementManager() {
  const useElements = useElementsStore()

  const item: TabConfig = {
    text: 'elementManagement',
    key: 'elements',
    icon: 'bottom-menu-ele-manage',
    component: markRaw(ElementManager),
    rightExtra: markRaw(RightExtra),
  }

  onMounted(() => {
    useElements.requestAllElements()
  })

  onUnmounted(() => {
    useElements.reset()
  })

  return item
}
