import type { TenantItem } from '@rpa/components/auth'
import { Auth } from '@rpa/components/auth'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import i18next from '@/plugins/i18next'

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

  async function getUserInfo() {
    if (!currentUserInfo.value) {
      const data = await Auth.userInfo()
      currentUserInfo.value = data
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
        title: i18next.t('common.warning'),
        content: i18next.t('common.switchWorkspaceInterruptRunningConfirm'),
        okText: i18next.t('confirm'),
        cancelText: i18next.t('cancel'),
        maskClosable: false,
        onOk: async () => {
          const runningStore = useRunningStore()
          runningStore.stop(runningStore.getRunProjectId())
          modal.destroy()
          resolve()
        },
        onCancel: () => {
          modal.destroy()
          reject(new Error(i18next.t('common.userCancelSwitchWorkspace')))
        },
      })
    })
  }

  async function switchTenant(tenant: TenantItem) {
    if (currentTenant.value?.id === tenant.id)
      return

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

  getUserInfo()

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
