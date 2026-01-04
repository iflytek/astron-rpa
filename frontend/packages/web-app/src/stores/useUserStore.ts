import type { TenantItem } from '@rpa/components/auth'
import { Auth } from '@rpa/components/auth'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getTermianlStatus } from '@/api/engine'
import { taskNotify } from '@/api/task'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { useRoutePush } from '@/hooks/useCommonRoute'
import router, { findFirstPermittedRoute } from '@/router'
import { usePermissionStore } from '@/stores/usePermissionStore'
import { useRunningStore } from '@/stores/useRunningStore'

export const useUserStore = defineStore('user', () => {
  const currentUserInfo = ref()
  const currentTenant = ref<TenantItem | null>(null) // 当前租户

  const loginStatus = computed(() => {
    return currentUserInfo.value
  })

  function getUserInfo() {
    if (!currentUserInfo.value) {
      currentUserInfo.value = Auth.getUserInfo()
    }
    return currentUserInfo.value
  }

  async function beforeSwitch(): Promise<void> {
    const { data } = await getTermianlStatus()
    if (!data.running) {
      return Promise.resolve()
    }

    return new Promise<void>((resolve, reject) => {
      const modal = GlobalModal.confirm({
        title: '警告',
        content: '切换工作空间将中断正在运行的应用，请确认？',
        okText: '确定',
        cancelText: '取消',
        maskClosable: false,
        onOk: async () => {
          const runningStore = useRunningStore()
          runningStore.stop(runningStore.getRunProjectId())
          modal.destroy()
          resolve()
        },
        onCancel: () => {
          modal.destroy()
          reject(new Error('用户取消切换'))
        },
      })
    })
  }

  async function switchTenant(tenant: TenantItem) {
    currentTenant.value = tenant
    usePermissionStore().reset()
    await usePermissionStore().initPermission()
    const first = findFirstPermittedRoute(usePermissionStore())
    if (first && router.currentRoute.value.name !== first.name) {
      useRoutePush({ name: first.name })
    }
    return await taskNotify({ event: 'login' })
  }

  async function logout() {
    await Auth.logout()
  }

  return {
    currentTenant,
    currentUserInfo,
    loginStatus,
    getUserInfo,
    beforeSwitch,
    switchTenant,
    logout,
  }
})
