import { isArray, isEmpty } from 'lodash-es'

import { DesktopRecordActionType, RecordActionType, WebRecordActionType } from '@/constants/record'
import { useElementsStore } from '@/stores/useElementsStore'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import type { PickElementType } from '@/types/resource'
import { addAtomData, group } from '@/views/Arrange/components/flow/hooks/useFlow'

/**
 * 添加智能录制的原子能力
 * 将录制的原子能力添加到一个编组中
 */
export async function addRecordAtomData(data: { action: RecordActionType, pickInfo: string }[]) {
  if (isEmpty(data))
    return

  const { addNewElement, requestAllElements } = useElementsStore()

  // TODO: 必须要先保存一下，才可以，不然会报错，后面重构
  useProcessStore().saveProject()

  /**
   * 1. 过滤出需要添加的原子能力
   * 在当前选中的原子能力后插入新的原子能力，会导致显示的顺序颠倒，因此需要最后的原子能力最先插入
   */
  const newData = data.map((item) => {
    const pickInfo = JSON.parse(item.pickInfo) as PickElementType
    const actions = pickInfo.type === 'web' ? WebRecordActionType : DesktopRecordActionType
    const addAtomType = actions[item.action]

    return { ...item, pickInfo, addAtomType }
  }).filter(item => !!item.addAtomType).reverse()

  // 添加原子能力和编组
  const addAtom = async () => {
    const list = await Promise.all(newData.map(item => addAtomData(item.addAtomType)))
    group(list.flat(1).map(atom => atom.id))
    return list
  }

  // 2. 添加拾取元素和原子能力
  const [pickElements, atoms] = await Promise.all([
    Promise.all(newData.map(item => addNewElement(item.pickInfo))),
    addAtom(),
  ])

  // 刷新元素管理列表
  requestAllElements()

  // 4. 将新增的拾取元素添加到原子能力表单中
  pickElements.forEach((item, index) => {
    const atom = atoms[index]
    const action = newData[index].action
    const elementValue: RPA.AtomFormItemResult[] = [{ type: 'element', value: item.name, data: item.elementId }]
    isArray(atom) && atom.forEach(it => modifyFormConfig(it, elementValue, action))
  })
}

// 根据不同的原子能力，修改表单的配置
function modifyFormConfig(atom: RPA.Atom, elementValue: RPA.AtomFormItemResult[], action: RecordActionType) {
  const { setFormItemValue } = useFlowStore()

  // 获取文字内容 / 网页 - 元素操作
  if (action === RecordActionType.GET_ELEMENT_TEXT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('get_type', 'getText', atom.id)
    return
  }
  // 获取源代码 / 网页 - 元素操作
  if (action === RecordActionType.GET_ELEMENT_CODE && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('get_type', 'getHtml', atom.id)
    return
  }
  // 获取链接地址 / 网页 - 元素操作
  if (action === RecordActionType.GET_ELEMENT_LINK && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('get_type', 'getLink', atom.id)
    return
  }
  // 获取元素属性 / 网页 - 元素操作
  if (action === RecordActionType.GET_ELEMENT_ATTR && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('get_type', 'getAttribute', atom.id)
    return
  }
  // 输入 / 网页 - 填写输入框
  if (action === RecordActionType.INPUT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    return
  }
  // 鼠标移动到这里 / 网页 - 鼠标悬停在元素上
  if (action === RecordActionType.MOUSE_MOVE && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    return
  }
  // 点击(左键) / 网页 - 点击元素
  if (action === RecordActionType.CLICK_LEFT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('button_type', 'click', atom.id)
    return
  }
  // 双击 / 网页 - 点击元素
  if (action === RecordActionType.CLICK_LEFT_RIGHT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('button_type', 'dbclick', atom.id)
    return
  }
  // 右键点击 / 网页 - 点击元素
  if (action === RecordActionType.CLICK_RIGHT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('button_type', 'right', atom.id)
    return
  }
  // 等待元素出现 / 网页 - 等待元素
  if (action === RecordActionType.WAIT_ELEMENT_SHOW && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('ele_status', 'y', atom.id)
    return
  }
  // 等待元素消失 / 网页 - 等待元素
  if (action === RecordActionType.WAIT_ELEMENT_HIDE && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
    setFormItemValue('ele_status', 'n', atom.id)
    return
  }
  // 截图 / 网页 - 拾取元素截图
  if (action === RecordActionType.SNAPSHOT && atom.key === WebRecordActionType[action]) {
    setFormItemValue('element_data', elementValue, atom.id)
  }

  // ************************************************* 桌面 ***************************************************

  // 获取文字内容 / 桌面 - 获取元素文本
  if (action === RecordActionType.GET_ELEMENT_TEXT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    return
  }
  // 输入 / 桌面 - 填写输入框
  if (action === RecordActionType.INPUT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    return
  }
  // 鼠标移动到这里 / 桌面 - 鼠标悬停元素
  if (action === RecordActionType.MOUSE_MOVE && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    return
  }
  // 点击(左键) / 桌面 - 点击元素
  if (action === RecordActionType.CLICK_LEFT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    setFormItemValue('click_button', 'left', atom.id)
    setFormItemValue('click_type', 'click', atom.id)
    return
  }
  // 双击 / 桌面 - 点击元素
  if (action === RecordActionType.CLICK_LEFT_RIGHT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    setFormItemValue('click_button', 'left', atom.id)
    setFormItemValue('click_type', 'double_click', atom.id)
    return
  }
  // 右键点击 / 桌面 - 点击元素
  if (action === RecordActionType.CLICK_RIGHT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
    setFormItemValue('click_button', 'right', atom.id)
    setFormItemValue('click_type', 'click', atom.id)
    return
  }
  // 截图 / 桌面 - 元素截图
  if (action === RecordActionType.SNAPSHOT && atom.key === DesktopRecordActionType[action]) {
    setFormItemValue('pick', elementValue, atom.id)
  }
}
