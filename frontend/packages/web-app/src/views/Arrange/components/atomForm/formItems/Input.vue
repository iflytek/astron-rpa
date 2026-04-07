<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { throttle } from 'lodash-es'

import { ATOM_FORM_TYPE, ELEMENT_IN_TYPE, GLOBAL_VAR_IN_TYPE, OTHER_IN_TYPE, PARAMETER_VAR_IN_TYPE, PY_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import { INPUT_NUMBER_TYPE_ARR } from '@/views/Arrange/config/atom'

import type { FormItemProps, FormItemEmits } from './index'

// 常量定义
const HAS_DATA_CATEGORY_TYPES = [VAR_IN_TYPE, GLOBAL_VAR_IN_TYPE, PARAMETER_VAR_IN_TYPE, ELEMENT_IN_TYPE] as const
const NUMBER_PATTERN = /^-?\d*\.?\d*$/
const THROTTLE_DELAY = 500
const NODE_TYPE_TEXT = Node.TEXT_NODE
const NODE_TYPE_ELEMENT = Node.ELEMENT_NODE
const BR_TAG_NAME = 'BR'
const UI_AT_CLASS = 'ui-at'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

// 计算属性：是否可编辑
const isEdit = computed(() => !props.item?.noInput)

const generateContainerText = (value: RPA.AtomFormBaseForm['value']): string => {
  if (!Array.isArray(value)) {
    return value == null ? '' : String(value)
  }

  return value
    .map((item) => {
      // 变量类型需要添加特殊样式标记
      if (HAS_DATA_CATEGORY_TYPES.includes(item.type as typeof HAS_DATA_CATEGORY_TYPES[number])) {
        const { data, type, value: itemValue } = item
        const dataId = data ? `data-id='${data}'` : ''
        return `<hr class="${UI_AT_CLASS}" ${dataId} data-category='${type}' data-name='${itemValue}'></hr>`
      }
      return item.value ?? ''
    })
    .join('')
}

let localValue = props.item.value
const containerText = ref(generateContainerText(localValue))

/**
 * 节流处理输入事件
 */
const handleInput = throttle((event: Event) => {
  const target = event.target as HTMLDivElement
  if (target) {
    generateHtmlVal(target)
  }
}, THROTTLE_DELAY)

/**
 * 从DOM节点生成表单值
 */
function generateHtmlVal(target: HTMLDivElement) {
  const { isExpr, formType, types } = props.item
  const nodeList = target.childNodes

  // 清除之前的自定义提示
  // if (itemData.customizeTip) {
  //   delete itemData.customizeTip
  // }

  const result: RPA.AtomFormItemResult[] = []

  // 处理空内容（只有一个BR标签）
  if (nodeList.length === 1 && nodeList[0].nodeName === BR_TAG_NAME) {
    result.push({ type: OTHER_IN_TYPE, value: '' })
  } else {
    // 遍历所有子节点
    nodeList.forEach((node) => {
      const obj: RPA.AtomFormItemResult = { type: OTHER_IN_TYPE, value: '' }

      if (node.nodeType === NODE_TYPE_TEXT) {
        // 文本节点处理
        const textNode = node as Text
        const textValue = textNode.nodeValue ?? ''

        if (!textValue) {
          return
        }

        obj.value = textValue

        // 数字类型校验
        if (
          INPUT_NUMBER_TYPE_ARR.includes(types) &&
          formType.type !== ATOM_FORM_TYPE.RESULT &&
          !isExpr
        ) {
          // if (!NUMBER_PATTERN.test(textValue)) {
          //   itemData.customizeTip = '只能填入数字'
          // }
        }

        result.push(obj)
      } else if (node.nodeType === NODE_TYPE_ELEMENT) {
        // 元素节点处理
        const elementNode = node as HTMLElement

        if (elementNode.classList.contains(UI_AT_CLASS)) {
          // 变量标记元素
          const id = elementNode.dataset.id
          const category = elementNode.dataset.category
          obj.type = (category as string) || VAR_IN_TYPE
          obj.value = elementNode.dataset.name ?? ''

          if (id && id !== 'undefined') {
            obj.data = id
          }

          result.push(obj)
        } else if (elementNode.nodeName !== BR_TAG_NAME) {
          // 其他非BR元素
          result.push(obj)
        }
      }
    })
  }

  // 输出类型特殊处理
  if (formType.type === ATOM_FORM_TYPE.RESULT && result.length > 0) {
    result[0].type = VAR_IN_TYPE
  }

  setModeVal(result)
}

/**
 * 设置Python模式的值
 */
function setModeVal(result: RPA.AtomFormItemResult[]) {
  const { isExpr } = props.item

  let lastResult = result;

  // Python模式处理
  if (isExpr) {
    lastResult = [{
      type: PY_IN_TYPE,
      value: result.map((item) => item.value ?? '').join('') // Python模式将所有值拼接成一个字符串
    }]
  }

  localValue = lastResult
  props.item.value = lastResult
  emits('update', props.item.key, lastResult)
}

/**
 * 处理粘贴事件
 */
function handlePaste(event: ClipboardEvent) {
  event.preventDefault()

  const textData = event.clipboardData?.getData('text/plain')
  if (!textData) {
    return
  }

  insertHtmlAtCaret(textData)

  let target = event.currentTarget as HTMLDivElement
  if (target.nodeName === BR_TAG_NAME) {
    target = target.parentNode as HTMLDivElement
  }

  if (target) {
    generateHtmlVal(target)
  }
}

/**
 * 在光标位置插入HTML内容
 */
function insertHtmlAtCaret(html: string) {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) {
    return
  }

  const range = selection.getRangeAt(0)
  range.deleteContents()

  // 创建临时容器解析HTML
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html

  // 将节点移动到文档片段
  const fragment = document.createDocumentFragment()
  while (tempDiv.firstChild) {
    fragment.appendChild(tempDiv.firstChild)
  }

  // 插入片段并更新光标位置
  range.insertNode(fragment)
  range.collapse(false)

  // 更新选择范围
  selection.removeAllRanges()
  selection.addRange(range)
}

watch(() => props.item.value, (newVal) => {
  const newText = generateContainerText(newVal)
  const localText = generateContainerText(localValue)

  if (newText !== localText) {
    containerText.value = newText
  }
})
</script>

<template>
  <div
    :id="`rpa_input_${props.item.key}`"
    class="editor flex-1 min-h-5"
    :class="{ 'cursor-not-allowed': !isEdit }"
    :contenteditable="isEdit"
    v-html="containerText"
    @input="(e) => handleInput(e)"
    @paste="(e) => handlePaste(e)"
  />
</template>

<style lang="scss" scoped>
.editor {
  --custom-cursor-size: 18px;

  white-space: pre-wrap;
  max-height: 300px;
  overflow: auto;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &:focus {
    outline: none;
  }

  :deep(p) {
    margin: 0;
  }
}
</style>
