import { useAsyncState, useDebounceFn } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'
import { defineStore } from 'pinia'
import { computed, ref, watchEffect, watchPostEffect } from 'vue'
import { useRoute } from 'vue-router'

import { flatAtomicTree } from '@/utils/common'
import { trackComponentUsageChange } from '@/utils/customComponent'
import { LRUCache } from '@/utils/lruCache'

import {
  createConfigParam,
  deleteConfigParam,
  getAtomsMeta,
  getComponentList,
  getConfigParams,
  getFavoriteList,
  getModuleMeta,
  updateConfigParam,
} from '@/api/atom'
import { getProcessPyCode, saveProcessPyCode } from '@/api/resource'
import { PROCESS_OPEN_KEYS } from '@/constants'
import { useFlowStore } from '@/stores/useFlowStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import {
  delectSubProcessQuote,
  querySubProcessQuote,
} from '@/views/Arrange/utils'

interface ProjectData {
  id: string
  name: string
}

// 判断是否是代码模块
export function isPyModel(category: RPA.Flow.ProcessModuleType) {
  return category === 'module'
}

export const useProcessStore = defineStore('process', () => {
  const openProcessLRUCache = new LRUCache<string[]>(PROCESS_OPEN_KEYS, 10, [])

  const docStore = useProjectDocStore()
  const flowStore = useFlowStore()
  const route = useRoute()
  const isComponent = computed(() => route?.query?.type === 'component')

  const atomMeta = useAsyncState<RPA.AtomMetaData>(() => getAtomsMeta(), {
    atomicTree: [],
    atomicTreeExtend: [],
    commonAdvancedParameter: [],
    types: {},
  })

  const project = ref<ProjectData>({ id: '', name: '工程名称' })
  const activeProcessId = ref('')
  const processList = ref<RPA.Flow.ProcessModule[]>([])
  const searchSubProcessId = ref('')
  const searchSubProcessResult = ref([])
  const pyCodeText = ref('')
  const changeFlag = ref(false)
  // 配置参数列表
  const parameters = ref<RPA.ConfigParamData[]>([])
  // 组件属性列表
  const attributes = ref<RPA.ComponentAttrData[]>([])
  // 原子能力 tree 列表
  const atomicTreeData = computed<RPA.AtomTreeNode[]>(
    () => atomMeta.state.value.atomicTree || [],
  )
  // 我的收藏 tree 列表
  const favorite = useAsyncState(getFavoriteList, [], { immediate: false })
  // 扩展组件 tree 列表
  const extendTree = useAsyncState(getModuleMeta, [], { immediate: false })
  // 自定义组件 tree 列表
  const componentTree = useAsyncState(() => getComponentList({ robotId: project.value.id }), [], { immediate: false })
  // 全局变量模板列表
  const globalVarTypeList = computed<Record<string, RPA.VariableValueType>>(
    () => atomMeta.state.value?.types || {},
  )
  // 高级参数和异常处理表单公共配置
  const commonAdvancedParameter = computed<RPA.AtomFormBaseForm[]>(
    () => atomMeta.state.value?.commonAdvancedParameter || [],
  )

  // 拍平后的原子能力 tree 列表 (不包含父节点)
  const atomicTreeDataFlat = computed<RPA.AtomTreeNode[]>(() =>
    flatAtomicTree(atomicTreeData.value, false),
  )

  // 配置参数接口参数
  const cofnigParamIdOption = computed(() => {
    const isPy = isPyModel(activeProcess.value?.resourceCategory)
    return isPy ? { moduleId: activeProcessId.value } : { processId: activeProcessId.value }
  })

  // 依赖刷新后自动请求
  watchEffect(async () => {
    if (project.value.id && activeProcessId.value) {
      parameters.value = await getConfigParams({
        ...cofnigParamIdOption.value,
        robotId: project.value.id,
      })
    }
  })

  watchPostEffect(() => {
    if (isEmpty(processList.value))
      return

    const openKeys = processList.value
      .filter(it => it.isOpen)
      .map(it => it.resourceId)
    openProcessLRUCache.debouncedSet(project.value.id, openKeys)
  })

  // 生成唯一的配置参数名称
  const generateParameterName = () => {
    const baseName = 'p_variable'
    let count = 0
    let variableName = baseName

    while (
      parameters.value.some(variable => variable.varName === variableName)
    ) {
      count += 1
      variableName = `${baseName}_${count}`
    }

    return variableName
  }

  // 添加参数
  const createParameter = async () => {
    const data: RPA.CreateConfigParamData = {
      ...cofnigParamIdOption.value,
      varName: generateParameterName(),
      varDirection: 0,
      varType: 'Str',
      varDescribe: '',
      varValue: '',
      robotId: project.value.id,
    }
    const id = await createConfigParam(data)

    parameters.value.push({ id, ...data })
  }

  // 删除参数
  const deleteParameter = async (item: RPA.ConfigParamData) => {
    await deleteConfigParam(item.id)
    parameters.value = parameters.value.filter(it => item.id !== it.id)
  }

  // 更新参数
  const updateParameter = async (data: RPA.ConfigParamData) => {
    await updateConfigParam({ ...data, ...cofnigParamIdOption.value, robotId: project.value.id })
    const target = parameters.value.find(item => item.id === data.id)
    Object.assign(target, data)
  }

  // 生成唯一的组件属性名称
  const generateAttributeName = () => {
    const baseName = 'p_variable'
    let count = 0
    let variableName = baseName

    while (
      attributes.value.some(variable => variable.varName === variableName)
    ) {
      count += 1
      variableName = `${baseName}_${count}`
    }

    return variableName
  }

  // 添加属性
  const createAttribute = async () => {
    const data: RPA.CreateComponentAttrData = {
      varName: generateAttributeName(),
      varDirection: 0,
      varType: 'Str',
      varDescribe: '',
      varValue: '',
      varFormType: {
        type: 'other',
        value: [],
      },
      robotId: project.value.id,
      processId: activeProcessId.value,
    }
    // const id = await createComponentAttr(data)
    const id = Date.now().toString()

    attributes.value.push({ id, ...data })
  }

  // 删除属性
  const deleteAttribute = async (item: RPA.ComponentAttrData) => {
    // await deleteComponentAttr(item.id)
    attributes.value = attributes.value.filter(it => item.id !== it.id)
  }

  // 更新属性
  const updateAttribute = async (data: RPA.ComponentAttrData) => {
    // await updateComponentAttr({ ...data, robotId: project.value.id })
    attributes.value = attributes.value.map(item =>
      item.id === data.id ? { ...item, ...data } : item,
    )
  }

  const globalVarTypeOption = computed(() => {
    // 后端返回的全局变量列表只有 channel 等于 global 的才允许在变量管理中新增
    return Object.values(globalVarTypeList.value).filter(
      item => item.channel.split(',').includes('global'),
    )
  })

  // 设置工程信息
  const setProject = (projectInfo: ProjectData) => {
    project.value = projectInfo
  }

  // 设置工程id
  const setProjectId = (id: string) => {
    project.value.id = id
  }

  const reset = () => {
    processList.value = []
    activeProcessId.value = ''
  }

  const getProcessList = (list: RPA.Flow.ProcessModule[]) => {
    // 从缓存中获取打开的流程
    const openProcessKeys = openProcessLRUCache.get(project.value.id) ?? []

    processList.value = list
      .map(it => ({
        ...it,
        isLoading: true,
        isOpen: it.name === '主流程' || openProcessKeys.includes(it.resourceId),
        isMain: it.name === '主流程', // 第一个流程是主流程
      }))
      .sort((a, b) => (b.isMain ? 1 : 0) - (a.isMain ? 1 : 0)) // 根据 isMain 进行排序

    activeProcessId.value = processList.value[0]?.resourceId ?? ''
  }

  const activeProcess = computed(() => {
    return processList.value.find(
      it => it.resourceId === activeProcessId.value,
    )
  })

  // 全局的操作，例如流程的保存，运行是否可以进行
  const operationDisabled = computed(() => {
    return isEmpty(processList.value) || !!activeProcess.value?.isLoading
  })

  const checkActiveProcess = (id: string) => {
    activeProcessId.value = id
    flowStore.reset()

    // 检查打开是否是流程
    const activeProcess = processList.value.find(it => it.resourceId === id)
    if (activeProcess.resourceCategory === 'process') {
      docStore.checkProcess()
    }
  }

  // 打开流程
  const openProcess = (id: string) => {
    const process = processList.value.find(it => it.resourceId === id)
    process.isOpen = true
    checkActiveProcess(id)
  }

  // 关闭流程
  const closeProcess = (id: string, isDelete = false) => {
    if (isDelete) {
      processList.value = processList.value.filter(
        it => it.resourceId !== id,
      )
    }
    else {
      processList.value = processList.value.map(it => ({
        ...it,
        isOpen: it.resourceId === id ? false : it.isOpen,
      }))
    }

    if (id === activeProcessId.value) {
      activeProcessId.value = processList.value[0]?.resourceId ?? ''
    }
    checkActiveProcess(activeProcessId.value)
  }

  // 关闭所有子流程
  const closeAllChildProcess = () => {
    processList.value = processList.value.map((item, index) => ({
      ...item,
      isOpen: index === 0,
    }))
    activeProcessId.value = processList.value[0].resourceId
  }

  // 删除流程
  const deleteProcess = (resourceId: string, flag: boolean) => {
    flag ? message.success('删除成功') : message.error('删除失败')
    if (flag) {
      trackComponentUsageChange(() => {
        closeProcess(resourceId, true)
        delectSubProcessQuote(resourceId)
        changeFlag.value = !changeFlag.value
      })
    }
  }

  // 子流程使用情况
  const searchSubProcess = (id: string) => {
    searchSubProcessId.value = id
    searchSubProcessResult.value = querySubProcessQuote(id)
  }

  // 关闭子流程使用情况
  const closeSearchSubProcess = () => {
    searchSubProcessId.value = ''
    searchSubProcessResult.value = []
  }

  const getPyCodeText = async (resourceId = activeProcess.value.resourceId) => {
    activeProcess.value.isLoading = true
    pyCodeText.value = await getProcessPyCode({
      moduleId: resourceId,
      robotId: project.value.id,
    })
    activeProcess.value.isLoading = false
  }

  const setCodeText = (text: string) => {
    pyCodeText.value = text
  }

  const savePyCode = () => {
    return saveProcessPyCode({
      moduleId: activeProcess.value.resourceId,
      robotId: project.value.id,
      moduleContent: pyCodeText.value,
    })
  }

  const saveProject = () => {
    let saveFn = Promise.resolve<void | boolean>(true)

    if (isPyModel(activeProcess.value?.resourceCategory)) {
      saveFn = savePyCode()
    }
    else {
      saveFn = docStore.saveProcess()
    }

    return saveFn
  }

  // 添加流程或模块
  const processOrModule = ({ resourceId, name, type }) => {
    const process: RPA.Flow.ProcessModule = {
      resourceId,
      name,
      resourceCategory: type,
      isOpen: true,
      isLoading: false,
    }
    processList.value.push(process)
    checkActiveProcess(resourceId)
    changeFlag.value = !changeFlag.value
  }

  // 重命名流程
  const renameModule = async (name: string, id: string) => {
    const process = processList.value.find(it => it.resourceId === id)
    if (process) {
      process.name = name
      changeFlag.value = !changeFlag.value
    }
  }

  // 设置保存状态
  let timer = null
  const canSave = (isSaveing = true, ignoreAutoSave = false) => {
    if (ignoreAutoSave)
      return isSaveing
    // 设置中心的自动保存是否启用
    return (
      isSaveing && useUserSettingStore().userSetting.commonSetting.autoSave
    )
  }
  const setSavingType = useDebounceFn(
    async (
      id: string,
      saveCallback: () => Promise<unknown>,
      isSaveing = true,
      ignoreAutoSave = true,
      delayTime = 0,
    ) => {
      const process = processList.value.find(it => it.resourceId === id)
      if (!process)
        return
      process.isSaveing = isSaveing
      if (!canSave(isSaveing, ignoreAutoSave)) {
        timer && clearTimeout(timer)
        return
      }
      timer = setTimeout(async () => {
        clearTimeout(timer)
        if (canSave(process.isSaveing, ignoreAutoSave)) {
          await saveCallback()
          process.isSaveing = false
        }
      }, delayTime)
    },
    500,
  )

  return {
    operationDisabled,
    project,
    changeFlag,
    activeProcessId,
    processList,
    activeProcess,
    pyCodeText,
    getPyCodeText,
    globalVarTypeList,
    globalVarTypeOption,
    parameters,
    attributes,
    commonAdvancedParameter,
    atomicTreeDataFlat,
    atomicTreeData,
    favorite,
    atomMeta,
    extendTree,
    componentTree,
    isComponent,
    updateParameter,
    deleteParameter,
    createParameter,
    updateAttribute,
    deleteAttribute,
    createAttribute,
    searchSubProcessId,
    searchSubProcessResult,
    reset,
    savePyCode,
    saveProject,
    setCodeText,
    setProject,
    setProjectId,
    getProcessList,
    checkActiveProcess,
    closeProcess,
    openProcess,
    deleteProcess,
    searchSubProcess,
    closeSearchSubProcess,
    processOrModule,
    renameModule,
    closeAllChildProcess,
    setSavingType,
  }
})
