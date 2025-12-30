import { ref } from 'vue'

import { acceptInvite, queryInviteData } from '../../../api/invite'
import { loginStatus, userInfo } from '../../../api/login'
import type { InviteInfo } from '../../../interface'
import { getQuery } from '../../../utils/index'

type PageStatus = 'linkExpired' | 'needLogin' | 'showUserInfo' | 'joinSuccess' | 'joined' | 'reachLimited' | 'marketFull'

export function useInviteFlow(emits: { (e: 'joinSuccess'): void }) {
  const inviteKey = getQuery().inviteKey as string
  const currentStatus = ref<PageStatus>()
  const inviteInfo = ref<InviteInfo>({
    resultCode: '',
    inviteType: 'market',
    enterpriseName: '',
    marketName: '',
    inviterName: '',
  })
  const currentUser = ref<{ userName: string, phone: string }>({ userName: '', phone: '' })

  const switchPage = (status: PageStatus) => {
    currentStatus.value = status
  }

  const updateInviteInfo = async (data: InviteInfo, needLogin = true) => {
    inviteInfo.value = { ...data, inviteType: data.inviteType || 'market' }
    let pageStatus: PageStatus = 'needLogin'
    switch (data.resultCode) {
      case '101':
        pageStatus = 'reachLimited'
        break
      case '102':
        pageStatus = 'linkExpired'
        break
      case '100':
        pageStatus = 'marketFull'
        break
      case '001':
        pageStatus = 'joined'
        break
      case '000':
        pageStatus = 'joinSuccess'
        emits('joinSuccess')
        break
      default:
        break
    }
    if (pageStatus !== 'needLogin') {
      switchPage(pageStatus)
      return
    }
    if (needLogin) {
      const isLogin = await loginStatus()
      if (!isLogin) {
        switchPage('needLogin')
        return
      }
      const user = await userInfo()
      currentUser.value = user
      switchPage('showUserInfo')
    }
  }

  const getInviteInfo = async () => {
    if (!inviteKey) {
      switchPage('linkExpired')
      return
    }
    const data = await queryInviteData({ inviteKey })
    updateInviteInfo(data)
  }

  const switchToLogin = () => {
    switchPage('needLogin')
  }

  const toJoin = async () => {
    try {
      const data = await acceptInvite({ inviteKey })
      updateInviteInfo(data, false)
    }
    catch (e) {
      console.error('加入失败', e)
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
