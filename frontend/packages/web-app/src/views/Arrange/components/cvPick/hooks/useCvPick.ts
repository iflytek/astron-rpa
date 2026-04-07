import { NiceModal } from '@rpa/components'
import { ref } from 'vue'

import { useCvPickStore } from '@/stores/useCvPickStore'
import { useCvStore } from '@/stores/useCvStore'
import type { Element, PickStepType } from '@/types/resource.d'

import { CvPickModal } from '../modals'

interface PickConfig {
  showCvModal?: boolean, 
  groupId?: string, 
  entry?: string, 
  pickStep?: PickStepType, 
  cvItem?: Element 
}

const defaultConfig: PickConfig = { showCvModal: true, groupId: '', entry: undefined, pickStep: 'new', cvItem: null }

function openCvPickModal(entry: string, groupId: string) {
  NiceModal.show(CvPickModal, { entry, groupId })
}

export function useCvPick() {
  const pickerType = ref('cv') // 拾取类型-cv
  const cvPickStore = useCvPickStore()

  // cv拾取
  const pick = (congfig: PickConfig = defaultConfig) => {
    const conf = { ...defaultConfig, ...congfig }
    const { showCvModal, pickStep, entry, groupId, cvItem } = conf

    return new Promise((resolve) => {
      const type = pickerType.value || ''
      cvPickStore.startCvPick(type, cvItem?.elementData || '', pickStep, (res) => {
        if (res.success) {
          const pickData = res.data
          // 重新拾取 更新数据, 图片名称不能修改
          useCvStore().setTempCvItem(pickData, pickStep)
          // 拾取结果弹窗
          if (showCvModal) {
            openCvPickModal(entry, groupId)
          }
          resolve(pickData)
        }
        else {
          resolve(false)
        }
      })
    })
  }

  // 拾取锚点
  const pickAnchor = (cvItem: Element) => {
    return pick({ showCvModal: false, pickStep: 'anchor', cvItem })
  }

  // cv重新拾取
  const rePick = (cvItem: Element, showCvModal = false) => {
    return pick({ showCvModal, pickStep: 'repick', cvItem, entry: 'edit' })
  }

  // cv校验元素
  const check = (elementData: Element) => {
    const element = JSON.stringify(elementData)
    cvPickStore.startCvCheck(pickerType.value, element, () => {
      console.log('校验成功')
    })
  }

  return {
    pick,
    pickAnchor,
    rePick,
    check,
  }
}
