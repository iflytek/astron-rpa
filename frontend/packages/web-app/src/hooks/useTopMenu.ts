import { usePermissionStore } from '@/stores/usePermissionStore'

import { useRouteList } from './useCommonRoute'

export function useTopMenu() {
  const permStore = usePermissionStore()
  const routes = useRouteList()

  return routes
    .filter(route => {
      if (!route.meta?.show) return false
      if (route.meta?.permission) {
        const res = typeof route.meta.resource === 'string'
          ? route.meta.resource
          : String(route.name)
        return permStore.can(res, 'all')
      }
      return true
    })
    .map(route => ({
      group: route.name as string,
      name: route.name as string,
      children: route.children,
    }))
}