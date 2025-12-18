import { ref } from 'vue'
import { userInfo } from '../../../api/login'
import { queryInviteData, acceptInvite } from '../../../api/invite'
import { loginStatus, } from '../../../api/login'
import { getQuery } from '../../../utils/index'
import { message } from 'ant-design-vue'
import type { InviteInfo } from '../../../interface'

type PageStatus = 'linkExpired' | 'needLogin' | 'showUserInfo' | 'joinSuccess' | 'joined' | 'reachLimited'

export function useInviteFlow(emits: {(e: 'joinSuccess', marketId: string): void}) {
  const inviteKey = getQuery().inviteKey as string
  const currentStatus = ref<PageStatus>('needLogin')
  const inviteInfo = ref<InviteInfo>({
    linkExpired: false,
    isJoined: false,
    isLimit: false,
    inviteType: 'market',
    enterpriseId: '',
    enterpriseName: '星辰RPA团队',
    marketId: '',
    marketName: '团队市场',
    userId: '',
    userName: '蔡文静'
  })
  const currentUser = ref<{ userName: string, phone: string }>({ userName: '', phone: '' })

  const switchPage = (status: PageStatus) => {
    currentStatus.value = status
  }

  const getInviteInfo = async () => {
    if (!inviteKey) {
      switchPage('linkExpired')
      return
    }
    const data = await queryInviteData({ inviteKey })
    inviteInfo.value = data
    const isLogin = await loginStatus()
    if(data.linkExpired) {
      switchPage('linkExpired')
      return
    }
    if(data.isLimit) {
      switchPage('reachLimited')
      return
    }
    if(!isLogin) {
      switchPage('needLogin')
      return
    }
    if(data.isJoined) {
      switchPage('joined')
      return
    }
    const user = await userInfo()
    currentUser.value = user
    switchPage('showUserInfo')
  }

  const switchToLogin = () => {
    switchPage('needLogin')
  }

  const toJoin = async () => {
    try {
      const data = await acceptInvite({ inviteKey })
      if (data) {
        switchPage('joinSuccess')
        emits('joinSuccess', data.marketId)
      }
    } catch (e) {
      console.error('加入失败')
    }
  }

  const openApp = () => {
    window.open('astronrpa://')
  }

  getInviteInfo()

  return {
    currentStatus,
    inviteInfo,
    currentUser,
    switchToLogin,
    toJoin,
    openApp,
  }
}