import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSharedData = defineStore('sharedData', () => {
  const sharedVariables = ref<RPA.SharedVariableType[]>([]) // 共享数据列表
  const sharedFiles = ref<RPA.SharedFileType[]>([]) // 共享文件列表

  // 获取共享数据
  const getSharedVariables = () => {
    // getRemoteParams().then((res) => {
    //   const data = res.data || []
    //   sharedVariables.value = data.map((item: any) => ({
    //     // label: item.sharedVarName,
    //     value: item.id,
    //     label: item.sharedVarName,
    //     subVarList: item.subVarList || [],
    //   }))
    // })
  }

  // 获取共享文件夹文件数据
  const getSharedFiles = () => {
    // getRemoteFiles({ pageSize: 1000 }).then((res) => {
    //   sharedFiles.value = (res.data.records || []).map((item: any) => ({
    //     fileId: item.fileId,
    //     fileName: item.fileName,
    //   }))
    // })
  }

  return { sharedVariables, getSharedVariables, sharedFiles, getSharedFiles }
})
