import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'


const AuthComponent = () => import('@/views/Auth/Index.vue')
const MarketInviteComponent = () => import('@/views/MarketInvite/Index.vue')
const EnterpriseInviteComponent = () => import('@/views/EnterpriseInvite/Index.vue')

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: `/auth`,
  },
  {
    path: `/auth`,
    name: `auth`,
    component: AuthComponent,
  },
  {
    path: `/marketInvite`,
    name: `marketInvite`,
    component: MarketInviteComponent,
  },
  {
    path: `/enterpriseInvite`,
    name: `enterpriseInvite`,
    component: EnterpriseInviteComponent,
  },
]
// hash router
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
