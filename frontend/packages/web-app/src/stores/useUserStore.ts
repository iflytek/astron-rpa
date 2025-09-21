import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const loginStep = ref('login') // 登录步骤
  const loginType = ref('self') // 登录类型

  const loginStatus = computed(() => {
    return loginType.value !== 'offline'
  }) // 登录状态 false离线true在线

  // 设置登录类型
  const setLoginType = (val: string) => {
    loginType.value = val
  }

  // 设置登录步骤
  const setLoginStep = (val: string) => {
    loginStep.value = val
  }

  return {
    loginStep,
    loginType,
    loginStatus,
    setLoginType,
    setLoginStep,
  }
})
