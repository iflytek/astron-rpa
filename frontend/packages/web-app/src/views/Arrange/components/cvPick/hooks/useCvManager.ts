import { NiceModal } from '@rpa/components'

import GlobalModal from '@/components/GlobalModal/index.ts'
import { useCvStore } from '@/stores/useCvStore.ts'
import type { Element } from '@/types/resource.d'

import { CvPickModal } from '../modals'

export function useCvManager() {
  // 编辑cv拾取数据
  const editCvItem = (itemData: Element, groupId: string) => {
    useCvStore().getCvItemDetail(itemData.id).then((res: any) => {
      useCvStore().setCurrentCvItem({ ...res })
      NiceModal.show(CvPickModal, { groupId, entry: 'edit' })
    })
  }
  // 删除cv拾取数据
  const delCvItem = (itemData: Element) => {
    const modal = GlobalModal.confirm({
      title: '删除图像',
      content: `当前图像将被删除，删除后无法恢复，请确认`,
      onOk() {
        useCvStore().deleteCvItem(itemData)
        modal.destroy()
      },
      closable: true,
      centered: true,
      keyboard: false,
    })
  }

  // 查看流程中元素引用情况
  const setQuotedItem = (itemData: Element) => {
    useCvStore().setQuotedItem(itemData)
  }

  return {
    editCvItem,
    delCvItem,
    setQuotedItem,
  }
}
