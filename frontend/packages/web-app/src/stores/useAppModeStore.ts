import { defineStore } from 'pinia'
import { ref } from 'vue'

// app 模式信息
export const useAppModeStore = defineStore('appMode', () => {
  const appMode = ref('normal') // normal-普通模式 | scheduling-调度模式
  const setAppMode = (mode: string) => {
    appMode.value = mode
  }

  return {
    appMode,
    setAppMode,
  }
})
