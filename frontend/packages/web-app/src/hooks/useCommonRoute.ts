import type { RouteLocationAsRelativeGeneric } from 'vue-router'
import { useRoute } from 'vue-router'

import { refreshModal } from '@/utils/antd.common'

import router from '@/router'
import { useUserStore } from '@/stores/useUserStore'

// 返回对应路由的name
export function useRouteName() {
  const route = useRoute()
  return route.name
}

// 根据需要判断是否为对应路由
export function useCounterRoute(name = 'Login') {
  const route = useRoute()
  return Object.is(route.name, name)
}

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

// 根据路由判断是否显示视图
export function useRouteByView(target: string = ''): boolean {
  const route = useRoute()
  const name = route.name
  const userStore = useUserStore()
  const routeName = name !== 'Login'

  switch (target) {
    case 'excellenceCenter':
      return userStore.loginStatus && routeName
    default:
      return routeName
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
