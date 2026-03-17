import type { InviteInfo } from '../interface'

import { http } from './http'

// 查询邀请信息
export async function queryMarketInviteData(params: { inviteKey: string }) {
  const { data } = await http.post<InviteInfo>('/robot/market-invite/get-invite-info-by-invite-key', params)
  return data
}

export async function acceptMarketInvite(params: { inviteKey: string }) {
  const { data } = await http.post('/robot/market-invite/accept-invite', params)
  return data
}

// 查询邀请信息
export async function queryEnterpriseInviteData(params: { inviteKey: string }) {
  const { data } = await http.post<InviteInfo>('/admin/enterprise-user-manage/invite/get-invite-info-by-invite-key', params)
  return data
}

export async function acceptEnterpriseInvite(params: { inviteKey: string }) {
  const { data } = await http.post('/admin/enterprise-user-manage/invite/accept-invite', params)
  return data
}
