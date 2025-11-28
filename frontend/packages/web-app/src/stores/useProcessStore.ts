import { useAsyncState } from '@vueuse/core'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { flatAtomicTree } from '@/utils/common'
import { trackComponentUsageChange } from '@/utils/customComponent'

import { getAtomsMeta, getComponentList, getFavoriteList, getModuleMeta } from '@/api/atom'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import { querySubProcessQuote } from '@/views/Arrange/utils'
import { useCanvasManagerStore } from '@/views/Arrange/canvasManager'

interface ProjectData {
  id: string
  name: string
  version: number
}

export const useProcessStore = defineStore('process', () => {
  const project = ref<ProjectData>({ id: '', name: '工程名称', version: 0 })
  /** 右侧tab栏激活的key */
  const rightTabActiveKey = ref<string>('')
  const canvasManager = useCanvasManagerStore(project)

  const route = useRoute()
  const isComponent = computed(() => route?.query?.type === 'component')

  const atomMeta = useAsyncState<RPA.AtomMetaData>(() => getAtomsMeta(), {
    atomicTree: [],
    atomicTreeExtend: [],
    commonAdvancedParameter: [],
    types: {},
  })

  const searchSubProcessId = ref('')
  const searchSubProcessResult = ref([])
  
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
      processId: ""
      // processId: activeProcessId.value,
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
  const setProject = (info: Partial<ProjectData>) => {
    project.value = { ...project.value, ...info }
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

  const reset = () => {}

  return {
    rightTabActiveKey,
    searchSubProcessId,
    searchSubProcessResult,
    canvasManager,
    project,
    globalVarTypeList,
    globalVarTypeOption,
    attributes,
    commonAdvancedParameter,
    atomicTreeDataFlat,
    atomicTreeData,
    favorite,
    atomMeta,
    extendTree,
    componentTree,
    isComponent,
    
    updateAttribute,
    deleteAttribute,
    createAttribute,
    reset,
    setProject,
    searchSubProcess,
    closeSearchSubProcess,
  }
})
