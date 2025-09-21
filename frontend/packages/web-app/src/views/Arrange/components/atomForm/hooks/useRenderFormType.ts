import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'

import BUS from '@/utils/eventBus'

import { validateContractResult } from '@/api/contract'
import { getHTMLClip } from '@/api/resource'
import { ATOM_FORM_TYPE, ELEMENT_IN_TYPE, GLOBAL_VAR_IN_TYPE, OTHER_IN_TYPE, PARAMETER_VAR_IN_TYPE, PY_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import { utilsManager } from '@/platform'
import { useFlowStore } from '@/stores/useFlowStore'
import { CustomDialog } from '@/views/Arrange/components/customDialog'
import { UserFormDialogModal } from '@/views/Arrange/components/customDialog/components'
import { ContractValidateModal, EmailTextReplaceModal, TextareaModal } from '@/views/Arrange/components/tools/components'
import { INPUT_NUMBER_TYPE_ARR, ORIGIN_SPECIAL, ORIGIN_VAR, PROCESS_VAR_TYPE } from '@/views/Arrange/config/atom'
import { backContainNodeIdx } from '@/views/Arrange/utils/flowUtils'
import type { resOption } from '@/views/Home/types'

import { createDom, setEditTextContent } from './useAtomVarPopover'
import useFormPick from './useFormPick'
import { getRealValue, getUserFormOption } from './usePreview'

const hasDataCategoryType = [VAR_IN_TYPE, GLOBAL_VAR_IN_TYPE, PARAMETER_VAR_IN_TYPE, ELEMENT_IN_TYPE]

export function generateInputVal(itemData: RPA.AtomDisplayItem) {
  let result = ''
  const { formType: { type, params }, value } = itemData
  if (!Array.isArray(value))
    return value
  if (Object.is(type, ATOM_FORM_TYPE.RANGEDATEPICKER)) {
    return [itemData.value[0], itemData.value[1]]
  }
  if ((Object.is(type, ATOM_FORM_TYPE.SELECT) && params?.multiple) || (Object.is(type, ATOM_FORM_TYPE.CHECKBOXGROUP))) {
    return itemData.value
  }
  value.forEach((item) => {
    // 是变量类型且不是输出变量那才加样式
    if (hasDataCategoryType.includes(item.type) && !Object.is(type, ATOM_FORM_TYPE.RESULT)) {
      const { data, type, value } = item
      const dataId = data ? `data-id='${data}'` : ''
      result += `<hr class="ui-at" ${dataId} data-category='${type}' data-name='${value}'></hr>`
    }
    else {
      result += item.value
    }
  })

  return result
}

export function handlePaste(event: ClipboardEvent, itemData: RPA.AtomDisplayItem) {
  event.preventDefault()
  const clipboardData = event.clipboardData
  if (!clipboardData)
    return
  const textData = clipboardData.getData('text/plain')
  if (textData) {
    insertHtmlAtCaret(textData)
    let target = event.currentTarget as HTMLDivElement
    if (target.nodeName === 'BR') {
      target = target.parentNode as HTMLDivElement
    }
    generateHtmlVal(target as HTMLDivElement, itemData)
  }
}

function insertHtmlAtCaret(html: string) {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0)
    return
  const range = selection.getRangeAt(0)
  range.deleteContents()
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  const fragment = document.createDocumentFragment()
  let node = tempDiv.firstChild
  while (node) {
    fragment.appendChild(node)
    node = tempDiv.firstChild
  }
  range.insertNode(fragment)
  range.collapse(false)
  selection.removeAllRanges()
  selection.addRange(range)
}

export const handleInput = throttle((event: Event, itemData: RPA.AtomDisplayItem) => {
  const target = event.target as HTMLDivElement
  generateHtmlVal(target, itemData)
}, 500)

export function generateHtmlVal(target: HTMLDivElement, itemData: RPA.AtomDisplayItem) {
  const { isExpr, formType, types } = itemData
  const nodeList = target.childNodes

  if (itemData.customizeTip)
    delete itemData.customizeTip
  const result: RPA.AtomFormItemResult[] = []
  if (nodeList.length === 1 && nodeList[0].nodeName === 'BR') {
    result.push({ type: OTHER_IN_TYPE, value: '' })
  }
  else {
    nodeList.forEach((node) => {
      const obj: RPA.AtomFormItemResult = { type: OTHER_IN_TYPE, value: '' } // 默认是other类型
      if (node.nodeType === Node.TEXT_NODE) { // 表示是文本节点
        const textNode = node as Text
        obj.value = textNode.nodeValue
        // 该值需要传数字类型且模式既不是变量也不是py
        if (INPUT_NUMBER_TYPE_ARR.includes(types) && !Object.is(formType.type, ATOM_FORM_TYPE.RESULT) && Object.is(obj.type, OTHER_IN_TYPE) && !isExpr) {
          const numberPattern = /^-?\d*\.?\d*$/
          if (!numberPattern.test(obj.value))
            itemData.customizeTip = '只能填入数字'
        }
        if (obj.value)
          result.push(obj)
      }
      else if (node.nodeType === Node.ELEMENT_NODE) { // 表示是元素节点
        const elementNode = node as HTMLElement
        if (elementNode.classList.contains('ui-at')) {
          const id = elementNode.dataset.id
          const category = elementNode.dataset.category
          obj.type = category || VAR_IN_TYPE
          obj.value = elementNode.dataset.name
          if (id && id !== 'undefined')
            obj.data = id
          result.push(obj)
        }
        else {
          elementNode.nodeName !== 'BR' && result.push(obj)
        }
      }
    })
  }

  if (Object.is(formType.type, ATOM_FORM_TYPE.RESULT)) {
    // 是输出那该值是变量类型
    result[0].type = VAR_IN_TYPE
  }

  itemData.value = result

  if (isExpr)
    setPyModeVal(itemData) // 该值是python类型

  syncCurrentAtomData(itemData, false)
}

export function setPyModeVal(itemData: RPA.AtomDisplayItem) {
  const { value, isExpr } = itemData
  const obj = { type: isExpr ? PY_IN_TYPE : OTHER_IN_TYPE, value: '' }
  // py模式只有一个值
  if (Array.isArray(value)) {
    value.forEach((item) => {
      obj.value += item.value
    })
  }
  itemData.value = [obj]
}

// 根据类型输出表单不同结果
export function formBtnHandle(itemData: RPA.AtomDisplayItem, itemType: string, extraProp: any) {
  const { pickLoading, elementPickModal, id } = extraProp
  const flowStore = useFlowStore()

  switch (itemType) {
    case ATOM_FORM_TYPE.PYTHON:
      itemData.isExpr = !itemData.isExpr
      setPyModeVal(itemData)
      setEditTextContent(itemData.key, itemData.value[0].value)
      syncCurrentAtomData(itemData, false)
      break
    case ATOM_FORM_TYPE.PICK:
      BUS.$once('batch-done', (res: any) => {
        if (itemData.key === 'batch_data') {
          itemData.value = [{ type: ELEMENT_IN_TYPE, value: res.value, data: res.data }]
          flowStore.setFormItemValue(itemData.key, itemData.value, id || flowStore.activeAtom.id)
        }
      })
      BUS.$once('pick-done', (res: any) => {
        if (itemData.key === 'batch_data')
          return // 抓取不在这里处理
        itemData.value = [{ type: ELEMENT_IN_TYPE, value: res.value, data: res.data }]
        flowStore.setFormItemValue(itemData.key, itemData.value, id || flowStore.activeAtom.id)
      })
      useFormPick(itemData.formType.params.use, pickLoading, elementPickModal)
      break
    case ATOM_FORM_TYPE.CVPICK:
      BUS.$once('cv-pick-done', (res: any) => {
        itemData.value = [{ type: ELEMENT_IN_TYPE, value: res.value, data: res.data }]
        flowStore.setFormItemValue(itemData.key, itemData.value, id || flowStore.activeAtom.id)
      })
      break
    case ATOM_FORM_TYPE.MOUSEPOSITION:
      BUS.$once('pick-done', (res: any) => {
        const { data: { x, y } } = res
        console.log('MOUSEPOSITION res', res)
        flowStore.activeAtom.inputList.forEach((item) => {
          if (item.key === 'position_x' || item.key === 'position_y') {
            const val = item.key === 'position_x' ? x : y
            item.value = val
            createDom({ val }, item, ORIGIN_SPECIAL)
          }
        })
      })
      useFormPick('POINT')
      break
    case ATOM_FORM_TYPE.FILE:
      utilsManager.showDialog(itemData.formType.params).then((res) => {
        if (res) {
          const strVal = Array.isArray(res) ? res.join(',') : res
          flowStore.setFormItemValue(itemData.key, strVal, id || flowStore.activeAtom.id)
        }
      })
      break
    default:
      break
  }
}

// 同步当前原子能力的值
export function syncCurrentAtomData(itemData: RPA.AtomDisplayItem, flush = true) {
  const flowStore = useFlowStore()
  const idx = flowStore.simpleFlowUIData.findIndex(item => item.id === flowStore.activeAtom.id)
  let alias = ''
  let flag = true
  if (itemData.key === 'anotherName') {
    flag = false
    alias = Array.isArray(itemData.value) ? itemData.value.reduce((cur, pre) => cur += pre.value, '') : itemData.value as string
  }
  if (itemData.groupId) {
    flowStore.setFormItemValue('anotherName', alias, backContainNodeIdx(itemData.groupId), flush)
  }
  flowStore.setFormItemValue(flag ? itemData.key : 'anotherName', flag ? itemData.value : alias, idx, flush)
}

function useRenderFormType() {
  // 处理类似预览、自定义对话框设计界面等弹窗按钮处理逻辑
  function handleModalButton(itemData: RPA.AtomDisplayItem) {
    const { activeAtom } = useFlowStore()
    if (itemData.key === 'design_interface') {
      const title = getRealValue(activeAtom.inputList.find(item => item.key === 'box_title')?.value)
      NiceModal.show(CustomDialog, {
        title,
        option: itemData.value as string,
        onOk: (data) => {
          itemData.value = data
          syncCurrentAtomData(itemData)
        },
      })
    }
    else if (itemData.key === 'preview_button') {
      const { key, inputList } = activeAtom
      NiceModal.show(UserFormDialogModal, {
        option: { mode: 'modal', buttonType: 'confirm_cancel', ...getUserFormOption({ key, inputList }) },
      })
    }
    else if (itemData.key === 'contract_validate') {
      const flowStore = useFlowStore()
      const { activeAtom } = flowStore
      const { inputList } = activeAtom
      const target = inputList.find(item => item.key === 'custom_factors')
      // 前置判断是否有要素
      if (!target.value) {
        message.warning('请先添加要素')
        return
      }
      let hasProcessVarType = false // 是否有流程变量
      const params = inputList.reduce((res, curr) => {
        res[curr.key] = getRealValue(curr.value, PROCESS_VAR_TYPE)
        if (res[curr.key].includes(PROCESS_VAR_TYPE)) {
          hasProcessVarType = true
        }
        return res
      }, {})
      if (hasProcessVarType) {
        message.warning('存在流变量无法验证效果')
        return
      }
      itemData.formType.params.loading = true
      validateContractResult(params).then((res: resOption) => {
        NiceModal.show(ContractValidateModal, { dataList: res.data })
      }).finally(() => {
        itemData.formType.params.loading = false
      })
    }
    else if (itemData.key === 'replace_table') {
      NiceModal.show(EmailTextReplaceModal, {
        option: itemData.value as string,
        onOk: (data) => {
          itemData.value = data
          syncCurrentAtomData(itemData)
        },
      })
    }
  }

  function handleTextareaModal(e: Event, itemData: RPA.AtomDisplayItem) {
    NiceModal.show(TextareaModal, {
      itemDataVal: itemData.value as RPA.AtomFormItemResult[],
      onOk: (data) => {
        itemData.value = data
        const target = e.target as HTMLElement
        const targetNode = (target.parentNode as HTMLElement).previousElementSibling as HTMLElement
        if (targetNode) {
          targetNode.innerHTML = String(generateInputVal(itemData))
          syncCurrentAtomData(itemData)
        }
      },
    })
  }

  function handleHTMLContentPaste() {
    return new Promise((resolve) => {
      const flowStore = useFlowStore()
      const { activeAtom } = flowStore
      const { inputList } = activeAtom
      const is_html = inputList.find(item => item.key === 'is_html')?.value
      getHTMLClip({ is_html }).then((res: resOption) => {
        const { data } = res
        const { content } = data
        resolve(content)
      })
    })
  }
  return {
    handleModalButton,
    handleTextareaModal,
    handleHTMLContentPaste,
  }
}

function batchDone(itemData: RPA.AtomDisplayItem) {
  BUS.$off('batch-done')
  BUS.$on('batch-done', (res: any) => {
    console.log('on batch-done')
    itemData.value = [{ type: ELEMENT_IN_TYPE, value: res.value, data: res.data }]
    createDom({ val: res.value, elementId: res.data, category: ELEMENT_IN_TYPE }, itemData, ORIGIN_VAR)
  })
}

export function inputListListener(itemData: RPA.AtomDisplayItem, itemType: string) {
  if (itemData?.key === 'batch_data' && itemType === 'PICK') {
    batchDone(itemData)
  }
}

export default useRenderFormType
