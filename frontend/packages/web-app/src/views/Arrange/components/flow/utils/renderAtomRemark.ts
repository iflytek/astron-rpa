import i18next from '@/plugins/i18next'

import { ATOM_KEY_MAP } from '@/constants/atom'
import {
  CONDITION_OPTIONS_DATAFRAME_TYPE,
  CONDITION_OPTIONS_EXCEL_TYPE,
  DEFAULT_DESC_TEXT,
  defaultValueText,
} from '@/views/Arrange/config/flow'
import { IncrementalASTParser } from '@/views/Arrange/canvasManager'
import { varHtmlToStr } from '@/views/Arrange/utils'

import { getValue } from './atomDescUtils'

// 结果片段类型：字符串或变量对象
type ResultSegment = string | {
  variable: true
  displayValue: string
  formItem: RPA.AtomDisplayItem
}

// 获取表单值的显示文本
const getFormItemDisplayValue = (item: RPA.AtomDisplayItem): string => {
  const rawValue = item.value === '""' ? '' : item.value

  // 处理选项类型：从 options 中查找对应的 label
  if (item.options && rawValue) {
    const matchedOption = item.options.find(opt => opt.value === rawValue)
    return matchedOption ? i18next.translate(matchedOption.label) : String(rawValue ?? '')
  }
  // 处理数组类型：提取数组中的 value 并拼接
  if (Array.isArray(rawValue)) {
    return rawValue.map(i => i.value).join('')
  }
  // 处理其他类型：直接使用原值
  return String(rawValue ?? '')
}

// 渲染原子能力的备注
export function renderAtomRemark(item: RPA.Atom, astParser: IncrementalASTParser) {
  const { key, isOpen = true, id, inputList, outputList, advanced } = item
  if (!id) {
    return
  }

  if (key === ATOM_KEY_MAP.GroupEnd || (key === ATOM_KEY_MAP.Group && isOpen)) {
    return
  }

  if (key === ATOM_KEY_MAP.Group) {
    const node = astParser.getNode(id)
    const childrenLength = node.children.length - 1
    return `共${childrenLength}条指令`
  }

  const desc = i18next.translate(item.comment)
  const title = i18next.translate(item.alias)

  if (!desc)
    return title

  // 收集所有表单项（inputList、outputList、advancedItems）
  const allFormItems = [
    ...(inputList || []),
    ...(outputList || []),
    ...(advanced || []),
  ]

  // 构建表单项映射对象，便于快速查找
  const formItemsObj: Record<string, RPA.AtomDisplayItem> = {}
  allFormItems.forEach((item) => {
    if (item?.key) {
      formItemsObj[item.key] = item
    }
  })

  // 根据条件选择有效的 key（支持 || 分隔的多个 key）
  const selectValidKey = (keys: string[]): string | null => {
    for (const k of keys) {
      if (!k) continue

      const formItem = formItemsObj[k]
      if (!formItem) continue

      // 如果表单项显示，直接使用
      if (formItem.show !== false) return k
    }
    return null
  }

  // 处理特殊类型的值格式化（logic_text, url 等）
  const formatSpecialValue = (key: string, value: any, placeholder: string): string => {
    // logic_text 特殊处理
    if (key === 'logic_text' && Array.isArray(value) && value.length > 0) {
      const targetConditionButton = inputList?.find(it => it.key === key)
      return value
        .map((i, idx) => {
          let res: string
          // 遇到包含和不包含前后要对调
          if (i.logic === 'in' || i.logic === 'notIn') {
            res = `${i.reducedValue} ${i.logic} ${i.conditionalValue}`
          }
          else if (i.logic === '!') {
            res = `${i.logic} ${i.conditionalValue}`
          }
          else if (i.logic === 'notNull') {
            res = `${i.conditionalValue} != null`
          }
          else if (i.logic === 'null') {
            res = `${i.conditionalValue} == null`
          }
          else if (i.logic === 'true') {
            res = `${i.conditionalValue} == true`
          }
          else if (i.logic === 'false') {
            res = `${i.conditionalValue} == false`
          }
          else {
            const specialItem = CONDITION_OPTIONS_DATAFRAME_TYPE.find(cItem => cItem.operator === i.logic)
            if (i.sort && !i.childCondition) {
              res = `筛选列号为${i.sort}的值${specialItem?.label}${i.conditionalValue}`
            }
            else if (i.sort && i.childCondition) {
              const tips = i.childCondition.map((child) => {
                const condition: string[] = []
                if (child.conditionValue !== '' && child.conditionValue !== defaultValueText) {
                  varHtmlToStr(child.conditionValue)?.forEach((conditionItem) => {
                    condition.push(conditionItem.value)
                  })
                }
                const specialItemExcel = CONDITION_OPTIONS_EXCEL_TYPE.find(option => option.operator === child.expression)
                return `筛选列号为${i.sort}的值${specialItemExcel?.label}${condition.join(' ')}`
              })
              res = tips.join('')
            }
            else {
              res = `${i.conditionalValue} ${i.logic} ${i.reducedValue}`
            }
          }
          const separator = idx === value.length - 1 ? '' : (targetConditionButton?.inputLogicOperator || '')
          return `（${res}）${separator}`
        })
        .join('')
    }

    // url 特殊处理
    if (key === 'url') {
      const specialItem = inputList?.find(data => data.key === 'url')
      if (specialItem && specialItem.formType?.type === 'INPUT_SELECT') {
        const valueArray = varHtmlToStr(value)
        const des = getValue(valueArray)
        return `${specialItem.selectValue}${des}`
      }
    }

    // 数组类型
    if (Array.isArray(value)) {
      return value.length > 0 ? getValue(value) : placeholder
    }

    // 默认返回原值或占位符
    return value || placeholder
  }

  // 解析变量并构建结果数组
  const variablePattern = /@\{([^}]+)\}/g
  const result: ResultSegment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  // 重置正则表达式的 lastIndex
  variablePattern.lastIndex = 0

  while ((match = variablePattern.exec(desc)) !== null) {
    // 添加变量前的文本
    if (match.index > lastIndex) {
      const textSegment = desc.slice(lastIndex, match.index)
      if (textSegment) {
        result.push(textSegment)
      }
    }

    // 解析变量
    const content = match[1] // 获取 @{...} 中的内容
    const [keyPart, ...placeholderParts] = content.split(':')
    const key = keyPart.trim()
    const placeholderText = placeholderParts.join(':').trim()
    const placeholder = placeholderText === 'null' ? '' : (placeholderText || DEFAULT_DESC_TEXT)
    const keyArr = key.split('||').map(k => k.trim())

    // 选择有效的 key
    const validKey = selectValidKey(keyArr)
    const formItem = formItemsObj[validKey]

    if (validKey && formItem) {
      const rawValue = getFormItemDisplayValue(formItem)
      const displayValue = formatSpecialValue(validKey, rawValue, placeholder)

      // 创建变量对象（保持与原始格式一致）
      result.push({
        variable: true,
        displayValue,
        formItem: { ...formItem, ...formItemsObj[formItem.key] },
      })
    }
    else {
      // 没有有效的 key，使用占位符
      result.push(placeholder || DEFAULT_DESC_TEXT)
    }

    lastIndex = variablePattern.lastIndex
  }

  // 添加最后剩余的文本
  if (lastIndex < desc.length) {
    const textSegment = desc.slice(lastIndex)
    if (textSegment) {
      result.push(textSegment)
    }
  }

  // 如果没有匹配到变量，直接返回原文本
  if (result.length === 0) {
    return [desc]
  }

  return result
}
