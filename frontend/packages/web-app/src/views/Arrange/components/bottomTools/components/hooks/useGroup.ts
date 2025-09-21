import { NiceModal } from '@rpa/components'

import { ElementGroupFormModal } from '@/components/ElementGroupFormModal'
import GlobalModal from '@/components/GlobalModal'
import { useCvStore } from '@/stores/useCvStore.ts'
import { useElementsStore } from '@/stores/useElementsStore'

export function useGroupManager() {
  const useElements = useElementsStore()
  const useCv = useCvStore()
  const elementGroupFormModal = NiceModal.useModal(ElementGroupFormModal)

  // 新增分组
  const addGroup = (type: 'cv' | 'common') => {
    elementGroupFormModal.show({
      onConfirm: (gname) => {
        // 新增或重命名分组
        if (type === 'cv') {
          useCv.addGroup(gname).then(() => {
            elementGroupFormModal.hide()
          })
        }
        if (type === 'common') {
          console.log('useElements.addGroup')
          useElements.addGroup(gname).then(() => {
            elementGroupFormModal.hide()
          })
        }
      },
    })
  }

  // 重命名分组
  const renameGroup = (groupItem, type: 'cv' | 'common') => {
    elementGroupFormModal.show({
      groupItem,
      onConfirm: (gname) => {
        // 重命名分组
        if (type === 'cv') {
          useCv.renameGroup(groupItem.id, gname).then(() => {
            elementGroupFormModal.hide()
          })
        }
        if (type === 'common') {
          useElements.renameGroup(groupItem.id, gname).then(() => {
            elementGroupFormModal.hide()
          })
        }
      },
    })
  }

  // 删除分组
  const delGroup = (groupItem, type: 'cv' | 'common') => {
    const typeStr = type === 'cv' ? '图像' : '元素'
    const modal = GlobalModal.confirm({
      title: `删除${typeStr}分组`,
      content: `当前分组${groupItem.name}及分组下${typeStr}将被删除，删除后无法恢复，请确认`,
      onOk() {
        if (type === 'cv') {
          useCv.deleteGroup(groupItem.id)
        }
        if (type === 'common') {
          useElements.deleteGroup(groupItem.id)
        }
        modal.destroy()
      },
      closable: true,
      centered: true,
      keyboard: false,
    })
  }
  // 移动到分组
  const move2Group = (originId: string, targetId: string, type: 'cv' | 'common') => {
    if (type === 'cv') {
      useCv.moveCvItem(originId, targetId)
    }

    if (type === 'common') {
      useElements.moveGroup(originId, targetId)
    }
  }

  return {
    addGroup,
    renameGroup,
    delGroup,
    move2Group,
  }
}
