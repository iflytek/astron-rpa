import { NiceModal } from '@rpa/components'
import { ref } from 'vue'

import { useCvPickStore } from '@/stores/useCvPickStore'
import { useCvStore } from '@/stores/useCvStore'
import type { Element, PickStepType } from '@/types/resource.d'

import { CvPickModal } from '../modals'

export function useCvPick() {
  const pickerType = ref('cv') // 拾取类型-cv
  const cvPickStore = useCvPickStore()

  function openCvPickModal({ entry, groupId }) {
    NiceModal.show(CvPickModal, { entry, groupId })
  }

  /**
   * @description cv拾取
   * @param congfig { showCvModal?: boolean, entry?: string, isRePick?: boolean, cvItem?: Element } showCvModal:是否显示拾取结果弹窗, isContinue: 是否继续拾取, isRePick: 是否重新拾取, cvItem: 重新拾取的cvItem
   * @returns {Promise<Element | boolean>}
   */
  interface pickConfig { showCvModal?: boolean, groupId?: string, entry?: string, pickStep?: PickStepType, cvItem?: Element }
  const defaultConfig: pickConfig = { showCvModal: true, groupId: '', entry: undefined, pickStep: 'new', cvItem: null }
  const pick = (congfig: pickConfig = defaultConfig) => {
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
            openCvPickModal({ entry, groupId })
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
