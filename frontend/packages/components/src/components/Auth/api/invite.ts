import { http } from './http'
import { InviteInfo } from '../interface'

// 查询邀请信息
export const queryInviteData = async (params: { inviteKey: string }) => {
  const { data } = await http.post<InviteInfo>('/robot/market-invite/get-invite-info-by-invite-key', params)
  return data
}

export const acceptInvite = async (params: { inviteKey: string }) => {
  const { data } = await http.post('/robot/market-invite/accept-invite', params)
  return data
}
