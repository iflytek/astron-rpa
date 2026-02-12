import type { RouteLocationAsRelativeGeneric } from 'vue-router'

import { refreshModal } from '@/utils/antd.common'

import router from '@/router'

// 跳转到对应路由
export async function useRoutePush(to: RouteLocationAsRelativeGeneric) {
  const currentName = router.currentRoute.value.name
  // debugger
  if (currentName === to.name)
    return // 防止重复跳转

  try {
    await router.push(to)
  }
  catch (err) {
    if (err.toString().includes('Failed to fetch dynamically')) {
      refreshModal()
    }
  }
}

// 获取路由表
export function useRouteList() {
  return router.getRoutes()
}

// 回退
export function useRouteBack() {
  router.back()
}
