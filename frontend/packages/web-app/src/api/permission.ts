import { ACTUATOR, APPLICATIONMARKET, DESIGNER } from '@/constants/menu'

import http from './http'

/**
 * 权限数据
 */
export async function permission() {
  const res = await http.get('/rpa-auth/user/entitlement')
  const entitlement = res.data

  const data = [
    { resource: DESIGNER, actions: ['all'], permissionKey: 'moduleDesigner' },
    { resource: ACTUATOR, actions: ['all'], permissionKey: 'moduleExecutor' },
    { resource: 'console', actions: ['all'], permissionKey: 'moduleConsole' },
    { resource: APPLICATIONMARKET, actions: ['all'], permissionKey: 'moduleMarket' },
  ].filter(i => entitlement[i.permissionKey])
  return data
}
