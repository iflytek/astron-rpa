import { getConfigParams } from '@/api/atom'
import { getComponentDetail } from '@/api/project'
import { getProcessAndCodeList } from '@/api/resource'
import { addComponentUse, deleteComponentUse, getEditComponentDetail } from '@/api/robot'
import { OTHER_IN_TYPE } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import { isArray, difference, has, isEmpty, some } from 'lodash-es'

export const COMPONENT_KEY_PREFIX = 'Code.Component'

export const varTypeToFormTypeMap = {
  Any: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Float: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Int: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Bool: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Str: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  List: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Dict: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  Browser: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  URL: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  DocxObj: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  ExcelObj: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
  DIRPATH: {
    type: 'INPUT_VARIABLE_PYTHON_FILE',
    params: {
      filters: [],
      file_type: 'folder',
    },
  },
  PATH: {
    type: 'INPUT_VARIABLE_PYTHON_FILE',
    params: {
      file_type: 'file',
    },
  },
  WebPick: {
    type: 'PICK',
    params: [{
      use: 'ELEMENT',
    }],
  },
  WinPick: {
    type: 'PICK',
    params: [{
      use: 'ELEMENT',
    }],
  },
  IMGPick: {
    type: 'PICK',
    params: [{
      use: 'CV',
    }],
  },
  Date: {
    type: 'INPUT_VARIABLE_PYTHON_DATETIME',
  },
  Password: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
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
 * 获取自定义组件表单元数据
 */
export async function getComponentForm(params: {
  componentId?: string
  version?: string | number
  context?: 'add' | 'get' | 'update'
}) {
  const processStore = useProcessStore()
  const { componentId, version, context = 'get' } = params
  const info = context === 'get'
    ? await getEditComponentDetail({ componentId, robotId: processStore.project.id })
    : await getComponentDetail({ componentId })
  const processList = await getProcessAndCodeList({ robotId: componentId })
  const mainProcessId = processList.find(item => item.name === '主流程')?.resourceId
  const componentAttrs = await getConfigParams({
    robotVersion: version,
    robotId: componentId,
    processId: mainProcessId,
  })

  const inputFormItems = componentAttrs.filter(item => item.varDirection === 0).map(item => mapAttrToFormItem(item))
  const outputFormItems = componentAttrs.filter(item => item.varDirection === 1).map(item => mapAttrToFormItem(item))

  return {
    key: `${COMPONENT_KEY_PREFIX}.${componentId}`,
    title: info.name || '组件名称',
    version: version || info.componentVersion || info.latestVersion,
    src: '',
    comment: '',
    inputList: inputFormItems,
    outputList: outputFormItems,
    icon: info.icon,
    helpManual: '',
    noAdvanced: true,
  } as unknown
}

/**
 * 获取“自定义组件设置预览弹窗”表单元数据，
 */
export function getComponentPreviewForm(params: {
  componentAttrs?: RPA.ConfigParamData[]
  componentId: string
  componentName: string
}) {
  const { componentAttrs, componentId, componentName } = params

  const inputFormItems = componentAttrs.filter(item => item.varDirection === 0).map(item => mapAttrToFormItem(item))
  const outputFormItems = componentAttrs.filter(item => item.varDirection === 1).map(item => mapAttrToFormItem(item))

  return {
    key: `${COMPONENT_KEY_PREFIX}.${componentId}`,
    title: componentName || '组件名称',
    version: '',
    src: '',
    comment: '',
    inputList: inputFormItems,
    outputList: outputFormItems,
    icon: '',
    helpManual: '',
    noAdvanced: true,
  }
}

export function mapAttrToFormItem(attr: RPA.ConfigParamData) {
  if (attr.varDirection === 1) {
    const varName = attr.varName.replace('p_variable', 'c_variable')
    return {
      types: attr.varType,
      formType: { type: 'RESULT' },
      key: varName,
      title: attr.varDescribe || attr.varName,
      name: varName,
      default: attr.varValue,
      required: false,
      value: [{ type: 'var', value: varName }],
    }
  }
  else {
    const varValue = safeParse(attr.varValue)
    const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))
    
    return {
      types: attr.varType,
      formType: varTypeToFormTypeMap[attr.varType] || { type: 'INPUT_VARIABLE_PYTHON' },
      key: attr.varName,
      title: attr.varDescribe || attr.varName,
      name: attr.varName,
      required: true,
      value: illegal ? [{ type: OTHER_IN_TYPE, value: attr.varValue ?? '' }] : varValue
    }
  }
}

export function getUsedComponentKeySet() {
  const processStore = useProcessStore()
  const usedkeySet = new Set(
    processStore.canvasManager.processList
      .filter(process => process.state.resourceCategory === 'process')
      .flatMap(process => (Array.isArray(process.state.data) ? process.state.data : []))
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
      componentId: getComponentId(key),
    })
  }

  for (const key of deletedKeys) {
    await deleteComponentUse({
      robotId: useProcessStore().project.id,
      componentId: getComponentId(key),
    })
  }
}

/**
 * 更新应用流程节点中使用到的组件数据
 */
export function updateFlowNodesComponent(componentId: string, defaultNode: RPA.Flow.FlowItemValue) {
  const processStore = useProcessStore()
  const processTabs = processStore.canvasManager.processList.filter(
    process => process.state.resourceCategory === 'process',
  )

  processTabs.forEach((tab) => {
    const nodes = Array.isArray(tab.state.data) ? tab.state.data : []
    let hasChanged = false

    const nextNodes = nodes.map((node) => {
      if (!isComponentKey(node.key) || getComponentId(node.key) !== componentId) {
        return node
      }

      hasChanged = true
      const oldFormItems = [
        ...(Array.isArray(node.inputList) ? node.inputList : []),
        ...(Array.isArray(node.outputList) ? node.outputList : []),
        ...(Array.isArray(node.advanced) ? node.advanced : []),
        ...(Array.isArray(node.exception) ? node.exception : []),
      ]

      const mapValue = (item: RPA.AtomFormBaseForm) => ({
        ...item,
        value: oldFormItems.find(i => i.key === item.key)?.value ?? item.value,
      })

      return {
        ...node,
        icon: defaultNode.icon,
        version: defaultNode.version,
        inputList: (defaultNode.inputList || []).map(mapValue),
        outputList: (defaultNode.outputList || []).map(mapValue),
        advanced: (defaultNode.advanced || []).map(mapValue),
        exception: (defaultNode.exception || []).map(mapValue),
      }
    })

    if (!hasChanged) return

    tab.updateState({ data: nextNodes, isDirty: true })

    const visualTab = tab as RPA.Process.TabInstance<RPA.Atom[]> & {
      astParser?: { getSubtreeNodes?: () => { raw: RPA.Atom }[] }
      updateData?: () => void
    }
    if (!visualTab.astParser?.getSubtreeNodes) return

    const nextNodeMap = new Map(nextNodes.map(it => [it.id, it]))
    const parserNodes = visualTab.astParser.getSubtreeNodes().slice(1)
    parserNodes.forEach((it) => {
      const target = nextNodeMap.get(it.raw.id)
      if (target) {
        Object.assign(it.raw, target)
      }
    })
    visualTab.updateData?.()
  })
}

function safeParse(str) {
  try {
    return JSON.parse(str)
  } catch {
    return str
  }
}
