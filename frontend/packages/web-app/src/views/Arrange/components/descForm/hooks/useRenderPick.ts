import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useCvStore } from '@/stores/useCvStore.ts'
import { useElementsStore } from '@/stores/useElementsStore'

// 自定义表单项排序
export function useRenderPick() {
  const PickTypeText = {
    [ATOM_FORM_TYPE.CVPICK]: '图像',
    [ATOM_FORM_TYPE.PICK]: '元素',
  }

  // 拾取操作下拉列表
  const getOperators = (notEmpty: boolean, itemType: any) => {
    const text = PickTypeText[itemType]
    if (notEmpty) {
      return [
        { label: `编辑${text}`, key: 'editPick' },
        { label: `拾取${text}`, key: 'pick' },
        { label: `选择${text}`, key: 'selectPick' },
      ]
    }
    return [
      { label: `拾取${text}`, key: 'pick' },
      { label: `选择${text}`, key: 'selectPick' },
    ]
  }

  // 获取默认文本
  const getDefaultText = (itemType: any) => {
    return `拾取${PickTypeText[itemType]}`
  }

  // 非空判断
  const notEmpty = (itemData: RPA.AtomDisplayItem) => {
    return itemData.value
      && Array.isArray(itemData.value)
      && itemData.value.filter(i => i.value).length > 0
  }

  // 获取拾取图片url
  const getPickImg = (itemData: RPA.AtomDisplayItem, itemType: string) => {
    const treeData = itemType === ATOM_FORM_TYPE.CVPICK ? useCvStore().cvTreeData : useElementsStore().elements
    const treeItem = itemData.value
      ? treeData.find(item =>
          item.elements.some(i => i.id === itemData.value[0]?.data),
        )
      : null
    const imageUrl = treeItem
      ? treeItem.elements.find(
        i => i.id === itemData.value[0].data,
      )?.imageUrl
      : ''
    return imageUrl
  }

  return {
    getOperators,
    getDefaultText,
    notEmpty,
    getPickImg,
    PickTypeText,
  }
}
