import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useAsyncState } from '@vueuse/core'
import authService from '@/auth/index'

export const useUserStore = defineStore('user', () => {
  const auth = authService.getAuth()

  const loginStep = ref('login') // 登录步骤
  const loginType = ref('self') // 登录类型

  // 获取用户名
  const userNameState = useAsyncState(() => auth.getUserName(), '')

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
    userNameState,
    loginStep,
    loginType,
    loginStatus,
    setLoginType,
    setLoginStep,
  }
})
