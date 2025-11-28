import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useCvStore } from '@/stores/useCvStore'
import { useElementsStore } from '@/stores/useElementsStore'

// 拾取类型文本映射
const PICK_TYPE_TEXT: Record<ATOM_FORM_TYPE.CVPICK | ATOM_FORM_TYPE.PICK, string> = {
  [ATOM_FORM_TYPE.CVPICK]: '图像',
  [ATOM_FORM_TYPE.PICK]: '元素',
} as const

// 拾取操作类型
type PickOperatorKey = 'editPick' | 'pick' | 'selectPick'

interface PickOperator {
  label: string
  key: PickOperatorKey
}

// 拾取类型
type PickType = ATOM_FORM_TYPE.CVPICK | ATOM_FORM_TYPE.PICK

/**
 * 自定义表单项排序 Hook
 */
export function useRenderPick() {
  const cvStore = useCvStore()
  const elementsStore = useElementsStore()

  /**
   * 获取拾取操作下拉列表
   * @param notEmpty 是否非空
   * @param itemType 拾取类型
   * @returns 操作选项列表
   */
  const getOperators = (notEmpty: boolean, itemType: PickType): PickOperator[] => {
    const text = PICK_TYPE_TEXT[itemType]
    
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

  /**
   * 获取默认文本
   * @param itemType 拾取类型
   * @returns 默认文本
   */
  const getDefaultText = (itemType: PickType): string => {
    return `拾取${PICK_TYPE_TEXT[itemType]}`
  }

  /**
   * 判断拾取值是否非空
   * @param itemData 表单项数据
   * @returns 是否非空
   */
  const notEmpty = (itemData: RPA.AtomDisplayItem): boolean => {
    if (!itemData.value || !Array.isArray(itemData.value)) {
      return false
    }
    return itemData.value.some(item => item.value)
  }

  /**
   * 获取拾取图片 URL
   * @param itemData 表单项数据
   * @param itemType 拾取类型
   * @returns 图片 URL，如果未找到则返回空字符串
   */
  const getPickImg = (itemData: RPA.AtomDisplayItem, itemType: PickType): string => {
    // 验证数据有效性
    if (!itemData.value || !Array.isArray(itemData.value) || itemData.value.length === 0) {
      return ''
    }

    const firstValue = itemData.value[0]
    if (!firstValue?.data) {
      return ''
    }

    // 根据类型选择对应的树数据
    const treeData = itemType === ATOM_FORM_TYPE.CVPICK 
      ? cvStore.cvTreeData 
      : elementsStore.elements

    // 查找包含目标元素的树项
    const treeItem = treeData.find(item =>
      item.elements?.some(element => element.id === firstValue.data)
    )

    // 查找并返回图片 URL
    return treeItem?.elements?.find(
      element => element.id === firstValue.data
    )?.imageUrl || ''
  }

  return {
    getOperators,
    getDefaultText,
    notEmpty,
    getPickImg,
    PickTypeText: PICK_TYPE_TEXT,
  }
}
