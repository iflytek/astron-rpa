import { http } from './http'
import { InviteInfo } from '../interface'

// 查询邀请信息
export const queryInviteData = async (params: { inviteKey: string }) => {
  // const { data } = await http.get<InviteInfo>('/rpa-auth/invite-info', params)
  // return data
  const data: InviteInfo = await Promise.resolve({
    linkExpired: false,
    isJoined: false,
    isLimit: false,
    inviteType: 'market',
    marketName: '星辰RPA团队市场',
    marketId: '111',
    userId: '123',
    userName: '蔡文静'
  })
  return data
}

export const acceptInvite = async (params: { inviteKey: string }) => {
  // const { data } = await http.post('/rpa-auth/join-market', params)
  // return data
  return Promise.resolve({ marketId: '111' })
}
