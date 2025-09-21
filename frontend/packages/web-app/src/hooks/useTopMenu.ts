import { useUserStore } from '@/stores/useUserStore'

import { useRouteList } from './useCommonRoute'

export function useTopMenu() {
  const userStore = useUserStore()
  const routes = useRouteList()

  const menuPermiss = {
    APPLICATIONMARKET: () => userStore.loginStatus,
    AIASSISTANT: () => userStore.loginStatus,
  }

  return routes
    .filter((route) => {
      const isShow = menuPermiss[route.name]?.() ?? true
      return route.meta?.show && isShow
    })
    .map(route => ({
      group: route.name as string,
      name: route.name as string,
      children: route.children,
    }))
}
