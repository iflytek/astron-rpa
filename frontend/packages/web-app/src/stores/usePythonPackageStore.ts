import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getPyPackageListApi } from '@/api/resource'
import { useProcessStore } from '@/stores/useProcessStore'

// 定义流程变量store
export const usePythonPackageStore = defineStore('pythonPackage', () => {
  const pythonPackageList = ref([]) // 包列表
  const pyLoadingType = ref('') // 存储当前安装、升级、删除的相关状态
  const selectedPackageIds = ref([]) // 存储当前选中的包id

  const setPythonPackageList = (list: any) => {
    pythonPackageList.value = list
  }

  const setPyLoadingType = (loadingType: string) => {
    pyLoadingType.value = loadingType
  }

  const setSelectedPackageIds = (list: any) => {
    selectedPackageIds.value = list
  }

  const getSelectedPackages = () => {
    return pythonPackageList.value.filter(i => selectedPackageIds.value.includes(i.id))
  }

  /**
   * 重置
   */
  const reset = () => {
    pyLoadingType.value = ''
    pythonPackageList.value = []
    selectedPackageIds.value = []
  }

  // 获取已安装的python包列表
  function getPythonList() {
    getPyPackageListApi({ robotId: useProcessStore().project.id }).then((res) => {
      setPythonPackageList(res.data)
    })
  }

  function updatePythonList() {
    getPythonList()
  }

  return {
    pythonPackageList,
    pyLoadingType,
    selectedPackageIds,
    setPyLoadingType,
    setSelectedPackageIds,
    getSelectedPackages,
    updatePythonList,
    reset,
  }
})
