import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'

const LoginComponent = () => import('@/views/Login/Index.vue')
const InviteComponent = () => import('@/views/Invite/Index.vue')

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: `login`,
    component: LoginComponent,
  },
  {
    path: `/invite`,
    name: `invite`,
    component: InviteComponent,
  },
]
// hash router
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
