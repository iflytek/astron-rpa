import { defineStore } from 'pinia'
import { ref } from 'vue'

import { permission } from '@/api/permission' // 换成你的请求实例

export interface PermItem {
  resource: string
  actions: string[]
}

export const usePermissionStore = defineStore('permission', () => {
  const permissionAction = ref<PermItem[]>([])
  const fetched = ref(false)

  const initPermission = async () => {
    if (fetched.value)
      return
    try {
      const data = await permission()
      setPermission(data)
      fetched.value = true
    }
    catch (e) {
      console.error('[Permission] fetch failed', e)
    }
  }

  const setPermission = (value: PermItem[]) => {
    permissionAction.value = value
  }

  const can = (resource: string, action = 'all'): boolean => {
    return permissionAction.value.some(
      p => p.resource === resource && p.actions?.includes(action),
    )
  }

  const reset = () => {
    permissionAction.value = []
    fetched.value = false
  }

  return {
    initPermission,
    setPermission,
    permissionAction,
    can,
    reset,
    fetched,
  }
})
