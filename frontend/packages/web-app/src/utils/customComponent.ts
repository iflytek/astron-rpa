import { getConfigParams } from '@/api/atom'
import { getComponentDetail } from '@/api/project'
import { getProcessAndCodeList } from '@/api/resource'
import { addComponentUse, deleteComponentUse } from '@/api/robot'
import type { ProcessNode } from '@/corobot/type'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'

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
}) {
  const { componentId, version } = params
  const info = await getComponentDetail({ componentId })
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
    version: (version || info.latestVersion) as unknown as string,
    src: '',
    comment: '',
    inputList: inputFormItems,
    outputList: outputFormItems,
    icon: info.icon,
    helpManual: '',
    noAdvanced: true,
  } as unknown as ProcessNode
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
      title: attr.varDescribe,
      name: varName,
      default: attr.varValue,
      required: false,
      value: [{ type: 'var', value: varName }],
    }
  }
  else {
    return {
      types: attr.varType,
      formType: varTypeToFormTypeMap[attr.varType],
      key: attr.varName,
      title: attr.varDescribe,
      name: attr.varName,
      default: attr.varValue,
      required: true,
    }
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

  const deletedKeys = beforeUsedKeys.difference(afterUsedKeys)
  const addedKeys = afterUsedKeys.difference(beforeUsedKeys)

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
 * 更新机器人流程节点中使用到的组件数据
 */
export function updateFlowNodesComponent(componentId: string, defaultNode: ProcessNode) {
  const processStore = useProcessStore()
  const projectDocStore = useProjectDocStore()

  processStore.processList.forEach((process) => {
    const nodes = projectDocStore.getProcessNodes(process.resourceId)
    nodes.forEach((node, index) => {
      if (isComponentKey(node.key) && getComponentId(node.key) === componentId) {
        const oldFormItems = [...node.inputList, ...node.outputList]
        const newNode = {
          ...node,
          version: defaultNode.version,
          inputList: defaultNode.inputList.map(item => ({ ...item, value: oldFormItems.find(i => i.key === item.key)?.value || item.value })),
          outputList: defaultNode.outputList.map(item => ({ ...item, value: oldFormItems.find(i => i.key === item.key)?.value || item.value })),
        }
        projectDocStore.updateProcessNode([index], [newNode], process.resourceId)
      }
    })
  })
}
