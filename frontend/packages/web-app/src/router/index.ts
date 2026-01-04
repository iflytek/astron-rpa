import type { RouteLocationAsRelativeGeneric, RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'

import {
  ACTUATOR,
  APPLICATION,
  APPLICATIONMARKET,
  ARRANGE,
  COMPONENTCREATED,
  COMPONENTMANAGEMENT,
  DESIGNER,
  EXCUTELIST,
  PROJECTCREATED,
  PROJECTMANAGEMENT,
  PROJECTMARKET,
  ROBOTLIST,
  TASKLIST,
  TEAMMARKETMANAGE,
  TEAMMARKETS,
} from '@/constants/menu'
import { usePermissionStore } from '@/stores/usePermissionStore'
// import { useUserStore } from '@/stores/useUserStore'

const ComponentManagement = () => import('@/views/Home/pages/ComponentManagement.vue')
const MyCreatedComponent = () => import('@/views/Home/pages/MyCreatedComponent.vue')
const DesignerComponent = () => import('@/views/Home/Index.vue')
const ProjectManagementComponent = () => import('@/views/Home/pages/ProjectManagement.vue')

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: `/${DESIGNER}`,
  },
  {
    path: `/${ARRANGE}`,
    name: ARRANGE,
    meta: {
      show: false,
      closeConfirm: false, // 关闭确认框
    },
    component: () => import('@/views/Arrange/index.vue'),
  },
  {
    path: `/${DESIGNER}`,
    name: DESIGNER,
    meta: {
      show: true,
      illustration: 'robot1',
      permission: true,
      resource: DESIGNER,
    },
    redirect: `/${DESIGNER}/${PROJECTMANAGEMENT}`,
    component: DesignerComponent,
    children: [
      {
        path: PROJECTMANAGEMENT,
        name: PROJECTMANAGEMENT,
        meta: {
          key: PROJECTMANAGEMENT,
          icon: PROJECTMANAGEMENT,
          group: DESIGNER,
        },
        redirect: `/${DESIGNER}/${PROJECTMANAGEMENT}/${PROJECTCREATED}`,
        component: ProjectManagementComponent,
        children: [
          {
            path: PROJECTCREATED,
            name: PROJECTCREATED,
            meta: {
              key: PROJECTCREATED,
              iconPark: 'user',
            },
            component: () => import('@/views/Home/pages/MyCreatedProject.vue'),
          },
          {
            path: PROJECTMARKET,
            name: PROJECTMARKET,
            meta: {
              key: PROJECTMARKET,
              iconPark: 'user-list',
            },
            component: () => import('@/views/Home/pages/MyGotProject.vue'),
          },
        ],
      },
      {
        path: COMPONENTMANAGEMENT,
        name: COMPONENTMANAGEMENT,
        meta: {
          key: COMPONENTMANAGEMENT,
          icon: COMPONENTMANAGEMENT,
          group: DESIGNER,
        },
        redirect: `/${DESIGNER}/${COMPONENTMANAGEMENT}/${COMPONENTCREATED}`,
        component: ComponentManagement,
        children: [
          {
            path: COMPONENTCREATED,
            name: COMPONENTCREATED,
            meta: {
              key: COMPONENTCREATED,
              iconPark: 'application',
            },
            component: MyCreatedComponent,
          },
        ],
      },
    ],
  },
  {
    path: `/${ACTUATOR}`,
    name: ACTUATOR,
    meta: {
      show: true,
      permission: true,
      resource: ACTUATOR,
    },
    redirect: `/${ACTUATOR}/${ROBOTLIST}`,
    component: () => import('@/views/Home/Index.vue'),
    children: [
      {
        path: ROBOTLIST,
        name: ROBOTLIST,
        meta: {
          key: ROBOTLIST,
          icon: ROBOTLIST,
          color: '#2C69FF',
          action: '',
          group: ACTUATOR,
          iconPark: 'bars-outlined',
          illustration: 'robot2',
        },
        component: () => import('@/views/Home/pages/RobotManagement.vue'),
      },
      {
        path: TASKLIST,
        name: TASKLIST,
        meta: {
          key: TASKLIST,
          icon: TASKLIST,
          color: '#1ED14C',
          action: '',
          group: ACTUATOR,
          iconPark: 'check-square-outlined',
        },
        component: () => import('@/views/Home/pages/TaskListManagement.vue'),
      },
      {
        path: EXCUTELIST,
        name: EXCUTELIST,
        meta: {
          key: EXCUTELIST,
          icon: EXCUTELIST,
          color: '#FFBE10',
          action: '',
          group: ACTUATOR,
          iconPark: 'file-text-outlined',
        },
        component: () => import('@/views/Home/pages/RecordManagement.vue'),
      },
    ],
  },
  {
    path: `/${APPLICATIONMARKET}`,
    name: APPLICATIONMARKET,
    meta: {
      show: true,
      permission: true,
      resource: APPLICATIONMARKET,
    },
    redirect: `/${APPLICATIONMARKET}/${TEAMMARKETS}`,
    component: () => import('@/views/Home/Index.vue'),
    children: [
      {
        path: TEAMMARKETS,
        name: TEAMMARKETS,
        meta: {
          key: TEAMMARKETS,
          icon: TEAMMARKETS,
          color: '#2C69FF',
          secret: 'market_team',
          group: APPLICATIONMARKET,
        },
        component: () => import('@/views/Home/pages/market/TeamMarketApp.vue'),
      },
      {
        path: TEAMMARKETMANAGE,
        name: TEAMMARKETMANAGE,
        meta: {
          key: TEAMMARKETMANAGE,
          icon: TEAMMARKETMANAGE,
          color: '#2C69FF',
          secret: 'market_team',
          group: APPLICATIONMARKET,
        },
        component: () => import('@/views/Home/pages/market/TeamMarketManage.vue'),
      },
      {
        path: APPLICATION,
        name: APPLICATION,
        meta: {
          key: APPLICATION,
          icon: APPLICATION,
          color: '#2C69FF',
          secret: 'market_team',
          group: APPLICATIONMARKET,
        },
        component: () => import('@/views/Home/pages/market/Application.vue'),
      },
    ],
  },
]
// hash router
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export function findFirstPermittedRoute(permStore: ReturnType<typeof usePermissionStore>): RouteLocationAsRelativeGeneric | null {
  const loop = (rs: RouteRecordRaw[]): RouteRecordRaw | null => {
    for (const r of rs) {
      if (r.meta?.permission) {
        const res = r.meta.resource || r.name
        if (res && permStore.can(res as string, 'all'))
          return r
      }
      if (r.children) {
        const child = loop(r.children)
        if (child)
          return child
      }
    }
    return null
  }
  const found = loop(routes)
  return found ? { name: found.name } : null
}

router.beforeEach(async (to, from, next) => {
  // const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // if (!userStore.loginStatus && to.name !== 'Login')
  //   return next({ name: 'Login', query: { redirect: to.fullPath } })

  if (to.meta?.permission) {
    if (!permissionStore.fetched)
      await permissionStore.initPermission()

    const resource = (to.meta.resource as string) || (to.name as string)
    if (permissionStore.can(resource, 'all'))
      return next()
    const first = findFirstPermittedRoute(permissionStore)
    if (first)
      return next(first)

    window.location.href = '/boot.html'
    return
  }
  next()
})

window.addEventListener('load', () => {
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(() => {
      import('@/views/Arrange/index.vue')
    })
  }
  else {
    setTimeout(() => {
      import('@/views/Arrange/index.vue')
    }, 0)
  }
})

export default router
