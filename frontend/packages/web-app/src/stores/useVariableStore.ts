import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

import { addGlobalVariable, deleteGlobalVariable, getGlobalVariable, saveGlobalVariable } from '@/api/resource'
import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import { caculateConditional } from '@/utils/selfExecuting'
import { get } from 'lodash-es'

// 定义流程变量store
export const useVariableStore = defineStore('variable', () => {
  // const flowStore = useFlowStore()
  const processStore = useProcessStore()
  // const projectDocStore = useProjectDocStore()

  const globalVariableList = ref<RPA.GlobalVariable[]>([]) // 全局变量列表

  //   设置流程变量列表
  const getFlowVariableList = (idx: number, processId: string) => {
    const localVariableList: any[] = [] // 流程变量列表

    const tab = processStore.canvasManager?.getTab(processId)
    if (!tab) return localVariableList

    const flowData = (tab.state.data as RPA.Atom[]).slice(0, idx)

    flowData.forEach((flow: RPA.Atom, pos: number) => {
      const { outputList, id, alias, title } = flow

      const formItemList = [
        ...get(flow, 'inputList', []),
        ...get(flow, 'outputList', []),
        ...get(flow, 'advanced', []),
      ]
      const formValues = formItemList.reduce((result, item) => {
        return Object.assign(result, { [item.key]: typeof item.value === 'string' ? { value: item.value } : item.value })
      }, {})

      outputList?.forEach((item: RPA.AtomDisplayItem, index: number) => {
        const { dynamics, value } = item

        let isShow = true
        if (dynamics && Array.isArray(dynamics)) {
          isShow = dynamics.every(dynamic => caculateConditional(dynamic.expression, formValues))
        }

        if (isShow) {
          const notNullArr = Array.isArray(value) ? value.filter((item: RPA.AtomFormItemResult) => item.value) : []
          const dialogResult = flow.key === 'Dialog.custom_box' ? flow.inputList?.find(input => input.key === 'design_interface')?.value : ''

          if (notNullArr.length > 0) {
            localVariableList.push({
              id: `${id}-${index}`,
              types: item.types,
              rowNum: pos + 1,
              anotherName: alias || title || '',
              atomId: id,
              value: notNullArr,
              dialogResult,
            })
          }
        }
      })
    })

    return localVariableList
  }

  //   获取当前原子能力的输入变量列表(不包含当前原子能力)
  const getBeforeCurrentVariableList = (rowNum: number, id: string) => {
    if (rowNum <= 0)
      return []
    return getFlowVariableList(rowNum, id)
  }

  //   获取当前原子能力的输出变量列表(包含当前原子能力)
  const getCurrentVariableList = (rowNum: number, id: string) => getFlowVariableList(rowNum + 1, id)

  //   筛选符合当前原子能力类型的变量
  const filterCurrentVariableListByType = (ioType: string, idx = getActiveAtomIndex(), processId = processStore.canvasManager?.activeTab?.id) => {
    if (Object.is(ioType, ATOM_FORM_TYPE.RESULT)) {
      return getCurrentVariableList(idx, processId)
    }

    return getBeforeCurrentVariableList(idx, processId)
  }

  // 获取全局变量列表
  const getGlobalVariableList = async (robotId: string, robotVersion: number) => {
    const { data = [] } = await getGlobalVariable({ robotId, robotVersion })
    return globalVariableList.value = data.reverse()
  }

  // 删除全局变量
  const deleteGlobalVariableList = async (globalId: string) => {
    await deleteGlobalVariable({
      robotId: processStore.project.id,
      globalId,
    })

    globalVariableList.value = globalVariableList.value.filter(item => item.globalId !== globalId)
  }

  // 生成唯一变量名
  const genUniqueVariableName = () => {
    const baseName = 'g_variable'
    let count = 0
    let variableName = baseName

    while (globalVariableList.value.some(variable => variable.varName === variableName)) {
      count += 1
      variableName = `${baseName}_${count}`
    }

    return variableName
  }

  // 新增全局变量
  const addGlobalVariableList = async () => {
    const newVariable: RPA.GlobalVariable = {
      robotId: processStore.project.id,
      globalId: '',
      varName: genUniqueVariableName(),
      varType: 'Any',
      varValue: '',
      varDescribe: '',
    }

    await addGlobalVariable(newVariable)
    const newVariableList = await getGlobalVariableList(processStore.project.id, processStore.project.version)

    return newVariableList[0]
  }

  // 修改/保存全局变量
  const saveGlobalVariableList = async (globalVariable: RPA.GlobalVariable) => {
    await saveGlobalVariable(globalVariable)
    await getGlobalVariableList(processStore.project.id, processStore.project.version)
  }

  const getActiveAtomIndex = () => {
    const activeTab = processStore.canvasManager?.activeTab
    if (!activeTab?.nodeParameter?.activeAtomId?.value) return 0

    return activeTab.state.data.findIndex((atom: RPA.Atom) => atom.id === activeTab.nodeParameter.activeAtomId.value)
  }

  watch(() => processStore.project.id, (robotId) => {
    if (robotId) {
      getGlobalVariableList(robotId, processStore.project.version)
    }
  }, { immediate: true })

  return {
    globalVariableList,
    addGlobalVariableList,
    deleteGlobalVariableList,
    saveGlobalVariableList,
    filterCurrentVariableListByType,
  }
})
