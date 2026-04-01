import { difference, has, isArray, isEmpty, some } from 'lodash-es'

import { getConfigParams } from '@/api/atom'
import { getComponentDetail } from '@/api/project'
import { getProcessAndCodeList } from '@/api/resource'
import { addComponentUse, deleteComponentUse, getEditComponentDetail } from '@/api/robot'
import { ATOM_FORM_TYPE, OTHER_IN_TYPE } from '@/constants/atom'
import type { ProcessNode } from '@/corobot/type'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'

export const COMPONENT_KEY_PREFIX = 'Code.Component'

/**
 * 表单控件配置列表
 * 用于自定义组件的表单控件选择
 */
export const formItemConfigs: Array<{
  formType: RPA.AtomFormItemType
  title: string
  types: string[] // 使用 string[] 以支持所有类型，包括 DIRPATH、DocumentObject、IMGPick 等
  value: any
  options?: Array<{ label: string; value: string }>
}> = [
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PYTHON}_${ATOM_FORM_TYPE.VARIABLE}` },
    title: '标准输入框',
    types: ['Any', 'Float', 'Int', 'Str', 'List', 'Dict', 'PATH', 'DIRPATH', 'Date', 'URL', 'Password', 'Browser', 'DocumentObject', 'ExcelObj'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PYTHON}_${ATOM_FORM_TYPE.VARIABLE}_${ATOM_FORM_TYPE.TEXTAREAMODAL}` },
    title: '多行输入框',
    types: ['Any', 'Str', 'List', 'Dict'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.FONTSIZENUMBER },
    title: '数字输入框',
    types: ['Any', 'Float', 'Int'],
    value: 0,
  },
  {
    formType: { type: ATOM_FORM_TYPE.CHECKBOX },
    title: '复选框',
    types: ['Any', 'Bool'],
    value: false,
  },
  {
    formType: { type: ATOM_FORM_TYPE.SWITCH },
    title: '开关框',
    types: ['Any', 'Bool'],
    value: false,
  },
  {
    formType: { type: ATOM_FORM_TYPE.SELECT, params: { multiple: false } },
    title: '单选下拉框',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: ATOM_FORM_TYPE.SELECT, params: { multiple: true } },
    title: '多选下拉框',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: ATOM_FORM_TYPE.CHECKBOXGROUP },
    title: '复选框组',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.FILE}`, params: { file_type: 'file' } },
    title: '文件选择框',
    types: ['Any', 'PATH'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.FILE}`, params: { file_type: 'folder' } },
    title: '文件夹选择框',
    types: ['Any', 'DIRPATH'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.DATETIME}` },
    title: '日期时间选择器',
    types: ['Any', 'Date'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.DEFAULTDATEPICKER },
    title: '普通日期选择器',
    types: ['Any', 'Date'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.RANGEDATEPICKER },
    title: '范围日期选择器',
    types: ['Any', 'List'],
    value: [],
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.VARIABLE}_${ATOM_FORM_TYPE.PICK}` },
    title: '元素拾取框',
    types: ['Any', 'WebPick', 'WinPick'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.VARIABLE}` },
    title: '变量选择框',
    types: ['Any', 'WebPick', 'WinPick'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.CV_IMAGE}_${ATOM_FORM_TYPE.CVPICK}` },
    title: '图像拾取框',
    types: ['Any', 'IMGPick'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.DEFAULTPASSWORD },
    title: '密码输入框',
    types: ['Any', 'Password'],
    value: '',
  },
]

/**
 * 根据 varType 从 formItemConfigs 中找到第一个匹配的配置
 * @param varType 变量类型
 * @returns 匹配的表单控件配置，如果没有找到则返回 null
 */
export function findFormItemConfigByType(varType: RPA.VariableType | string) {
  return formItemConfigs.find(config => config.types.includes(varType)) || null
}

/**
 * @param key 为Code.Component和componentId拼接组成，如：Code.Component.1960590437807538176
 */
export function isComponentKey(key: string) {
  return key?.startsWith(COMPONENT_KEY_PREFIX)
}

/**
 * @param key 为Code.Component和componentId拼接组成，如：Code.Component.1960590437807538176
 */
export function getComponentId(key: string) {
  return key?.split(`${COMPONENT_KEY_PREFIX}.`)?.[1] || ''
}

/**
 * 从组件属性生成表单项列表
 */
function buildFormItemsFromAttrs(componentAttrs: RPA.ConfigParamData[]) {
  const inputFormItems = componentAttrs
    .filter(item => item.varDirection === 0)
    .map(item => mapAttrToFormItem(item))
  const outputFormItems = componentAttrs
    .filter(item => item.varDirection === 1)
    .map(item => mapAttrToFormItem(item))
  return { inputFormItems, outputFormItems }
}

/**
 * 将 INPUT_VARIABLE 类型的表单值数组转换为 renderAtomRemark 可解析的字符串格式
 * @param valueArray 表单值数组，例如: [{ type: "other", value: "将" }, { type: "p_var", value: "p_variable" }]
 * @returns 转换后的字符串，例如: "将@{p_variable}"
 */
export function convertInputVariableValueToComment(valueArray: Array<{ type: string; value: string }>): string {
  if (!Array.isArray(valueArray) || valueArray.length === 0) {
    return ''
  }

  return valueArray.map((item) => {
    if (item.type === 'p_var' || item.type === 'var') {
      // 变量类型转换为 @{variable} 格式
      return `@{${item.value}}`
    }
    // 其他类型（如 "other"）直接使用 value
    return item.value || ''
  }).join('')
}

/**
 * 将 comment 字符串转换为 INPUT_VARIABLE 类型的表单值数组格式
 * @param comment 字符串，例如: "将@{p_variable}"
 * @returns 转换后的数组，例如: [{ type: "other", value: "将" }, { type: "p_var", value: "p_variable" }]
 */
export function convertCommentToInputVariableValue(comment: string): Array<{ type: string; value: string }> {
  if (!comment || typeof comment !== 'string') {
    return []
  }

  const result: Array<{ type: string; value: string }> = []
  // 匹配 @{variable} 格式
  const variableRegex = /@\{([^}]+)\}/g
  let lastIndex = 0
  let match

  while ((match = variableRegex.exec(comment)) !== null) {
    // 添加 @{variable} 之前的文本
    if (match.index > lastIndex) {
      const text = comment.substring(lastIndex, match.index)
      if (text) {
        result.push({ type: 'other', value: text })
      }
    }
    // 添加变量
    result.push({ type: 'p_var', value: match[1] })
    lastIndex = match.index + match[0].length
  }

  // 添加剩余的文本
  if (lastIndex < comment.length) {
    const text = comment.substring(lastIndex)
    if (text) {
      result.push({ type: 'other', value: text })
    }
  }

  return result
}

/**
 * 构建组件表单数据结构
 */
function buildComponentFormData(params: {
  componentId: string
  componentAttrs: RPA.ConfigParamData[]
  title: string
  version?: string | number
  icon?: string
  comment?: string
}) {
  const { componentId, componentAttrs, title, version = '', icon = '', comment = '' } = params
  const { inputFormItems, outputFormItems } = buildFormItemsFromAttrs(componentAttrs)

  return {
    key: `${COMPONENT_KEY_PREFIX}.${componentId}`,
    title,
    alias: title,
    version,
    src: '',
    comment,
    inputList: inputFormItems,
    outputList: outputFormItems,
    icon,
    helpManual: '',
  }
}

/**
 * 获取自定义组件表单元数据
 * @param params.context: get是获取已使用的组件详情信息（可能是旧版本），而add和update总是获取最新的组件详情信息
 */
export async function getComponentForm(params: {
  componentId?: string
  version?: string | number
  context?: 'add' | 'get' | 'update'
}) {
  const processStore = useProcessStore()
  const { componentId, version, context = 'get' } = params
  const info = context === 'get'
    ? await getEditComponentDetail({ componentId, robotId: processStore.project.id, robotVersion: processStore.project.version })
    : await getComponentDetail({ componentId })
  const processList = await getProcessAndCodeList({ robotId: componentId, robotVersion: version as number })
  const mainProcessId = processList.find(item => item.name === '主流程')?.resourceId
  const componentAttrs = await getConfigParams({
    robotVersion: version as number,
    robotId: componentId,
    processId: mainProcessId,
  })

  return buildComponentFormData({
    componentId,
    componentAttrs,
    title: info.name,
    version: version || info.componentVersion || info.latestVersion,
    icon: info.icon,
    comment: info.comment
  }) as unknown as ProcessNode
}

/**
 * 获取"自定义组件设置预览弹窗"表单元数据
 */
export function getComponentPreviewForm(params: {
  componentAttrs?: RPA.ConfigParamData[]
  componentId: string
  componentName: string
}) {
  const { componentAttrs = [], componentId, componentName } = params

  return buildComponentFormData({
    componentId,
    componentAttrs,
    title: componentName,
  }) as unknown as RPA.Atom
}

/**
 * 将配置参数映射为表单项
 */
export function mapAttrToFormItem(attr: RPA.ConfigParamData): RPA.AtomDisplayItem {
  // 输出参数格式固定，直接返回
  if (attr.varDirection === 1) {
    const varName = attr.varName
    return {
      formType: { type: 'RESULT' },
      key: varName,
      name: varName,
      required: false,
      tip: attr.varDescribe,
      title: varName,
      types: attr.varType,
      value: [{ type: 'var', value: varName }],
    }
  }
  
  // 输入参数：优先使用 formItem，如果没有则使用默认生成逻辑作为兜底
  if (attr.formItem) {
    const formItemObj = typeof attr.formItem === 'string' 
      ? safeParse(attr.formItem) 
      : attr.formItem
    
    if (!formItemObj || typeof formItemObj !== 'object' || !formItemObj.formType) {
      return getDefaultFormItem(attr)
    }

    const varValue = safeParse(attr.varValue)
    const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))
    
    const formItem = {
      ...formItemObj,
      key: attr.varName,
      name: attr.varName,
      tip: attr.varDescribe,
      title: attr.varName,
      types: attr.varType,
      value: illegal ? [{ type: OTHER_IN_TYPE, value: attr.varValue ?? '' }] : varValue
    }
    
    return formItem
  }
  
  return getDefaultFormItem(attr)
}

/**
 * 生成默认的表单项
 */
function getDefaultFormItem(attr: RPA.ConfigParamData): RPA.AtomDisplayItem {
  // 根据 varType 从 formItemConfigs 中找到第一个匹配的配置作为默认配置
  const matchedConfig = findFormItemConfigByType(attr.varType)
  const varValue = safeParse(attr.varValue)
  const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))
  
  // 如果没有找到匹配的配置，使用标准输入框配置作为兜底
  const config = matchedConfig || formItemConfigs[0]
  
  return {
    formType: config.formType,
    key: attr.varName,
    name: attr.varName,
    required: true,
    tip: attr.varDescribe,
    title: attr.varName,
    types: attr.varType,
    value: illegal ? [{ type: OTHER_IN_TYPE, value: attr.varValue ?? '' }] : varValue,
    options: config.options,
  }
}

export function getUsedComponentKeySet() {
  const processStore = useProcessStore()
  const projectDocStore = useProjectDocStore()

  const usedkeySet = new Set(
    processStore.processList
      .flatMap(process => projectDocStore.getProcessNodes(process.resourceId))
      .filter(node => isComponentKey(node.key))
      .map(item => item.key),
  )

  return usedkeySet
}

export async function trackComponentUsageChange(operation: () => void | Promise<void>) {
  const beforeUsedKeys = getUsedComponentKeySet()
  await operation()
  const afterUsedKeys = getUsedComponentKeySet()
  const deletedKeys = new Set(difference([...beforeUsedKeys], [...afterUsedKeys]))
  const addedKeys = new Set(difference([...afterUsedKeys], [...beforeUsedKeys]))

  for (const key of addedKeys) {
    await addComponentUse({
      robotId: useProcessStore().project.id,
      robotVersion: useProcessStore().project.version,
      componentId: getComponentId(key),
    })
  }

  for (const key of deletedKeys) {
    await deleteComponentUse({
      robotId: useProcessStore().project.id,
      robotVersion: useProcessStore().project.version,
      componentId: getComponentId(key),
    })
  }
}

/**
 * 更新应用流程节点中使用到的组件数据
 */
export function updateFlowNodesComponent(componentId: string, defaultNode: ProcessNode) {
  const processStore = useProcessStore()
  const projectDocStore = useProjectDocStore()
  const flowStore = useFlowStore()

  const updateParams: { node: RPA.Atom, index: number, process: string }[] = []

  processStore.processList.forEach((process) => {
    const nodes = projectDocStore.getProcessNodes(process.resourceId)
    nodes.forEach((node, index) => {
      if (isComponentKey(node.key) && getComponentId(node.key) === componentId) {
        const oldFormItems = [...node.inputList, ...node.outputList]
        const newNode = {
          ...node,
          icon: defaultNode.icon,
          version: defaultNode.version,
          inputList: defaultNode.inputList.map(item => ({ ...item, value: oldFormItems.find(i => i.key === item.key)?.value || item.value })),
          outputList: defaultNode.outputList.map(item => ({ ...item, value: oldFormItems.find(i => i.key === item.key)?.value || item.value })),
        }
        updateParams.push({ node: newNode, index, process: process.resourceId })
      }
    })
  })

  flowStore.updataOriginFlowData(updateParams)
}

function safeParse(str) {
  try {
    return JSON.parse(str)
  }
  catch {
    return str
  }
}
