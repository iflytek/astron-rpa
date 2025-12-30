import type { InviteInfo } from '../interface'

import { http } from './http'

// 查询邀请信息
export async function queryInviteData(params: { inviteKey: string }) {
  const { data } = await http.post<InviteInfo>('/robot/market-invite/get-invite-info-by-invite-key', params)
  return data
}

export async function acceptInvite(params: { inviteKey: string }) {
  const { data } = await http.post('/robot/market-invite/accept-invite', params)
  return data
}
